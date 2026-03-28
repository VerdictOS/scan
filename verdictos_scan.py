#!/usr/bin/env python3
"""
AI Security Audit Script
Purpose:
- Scan a codebase for common insecure patterns often introduced by AI-generated code
- Optionally probe a live URL for weak HTTP security posture

Usage:
    python3 ai_security_audit.py --path /path/to/app
    python3 ai_security_audit.py --path /path/to/app --url https://yourapp.com
    python3 ai_security_audit.py --path . --json

Notes:
- This is NOT a substitute for full pentesting.
- This is an aggressive heuristic scanner: some findings are false positives.
- Use only on systems you own or are authorized to test.
"""

import argparse
import json
import os
import re
import sys
import socket
import ssl
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    requests = None

# ----------------------------
# Config
# ----------------------------

DEFAULT_EXCLUDE_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".mypy_cache", "coverage", ".idea", ".vscode"
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".htm", ".css", ".json",
    ".yaml", ".yml", ".env", ".ini", ".cfg", ".conf", ".sh", ".md", ".sql"
}

SEVERITY_WEIGHTS = {
    "CRITICAL": 10,
    "HIGH": 7,
    "MEDIUM": 4,
    "LOW": 1
}

# ----------------------------
# Patterns: common AI weak points
# ----------------------------

PATTERNS = [
    # Python RCE / Code Execution
    {
        "id": "PY-EVAL",
        "severity": "CRITICAL",
        "languages": {"py"},
        "regex": r"\beval\s*\(",
        "message": "Use of eval() can lead to arbitrary code execution."
    },
    {
        "id": "PY-EXEC",
        "severity": "CRITICAL",
        "languages": {"py"},
        "regex": r"\bexec\s*\(",
        "message": "Use of exec() can lead to arbitrary code execution."
    },
    {
        "id": "PY-SUBPROCESS-SHELL",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"subprocess\.(run|Popen|call|check_output|check_call)\s*\([^)]*shell\s*=\s*True",
        "message": "subprocess with shell=True may enable command injection."
    },
    {
        "id": "PY-OS-SYSTEM",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"\bos\.system\s*\(",
        "message": "os.system() can enable command injection if user input reaches it."
    },

    # Unsafe deserialization
    {
        "id": "PY-PICKLE",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"\bpickle\.(load|loads)\s*\(",
        "message": "pickle deserialization is unsafe with untrusted data."
    },
    {
        "id": "PY-YAML-UNSAFE",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"\byaml\.load\s*\(",
        "message": "yaml.load() can be unsafe; prefer yaml.safe_load()."
    },

    # Secrets / keys
    {
        "id": "SECRET-ASSIGNMENT",
        "severity": "HIGH",
        "languages": {"py", "js", "ts", "env", "json", "yaml", "yml", "ini", "cfg", "conf"},
        "regex": r"(?i)\b(api[_-]?key|secret|token|password|passwd|private[_-]?key|jwt[_-]?secret)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]",
        "message": "Possible hardcoded secret."
    },
    {
        "id": "PRIVATE-KEY-BLOCK",
        "severity": "CRITICAL",
        "languages": {"py", "js", "ts", "env", "json", "yaml", "yml", "ini", "cfg", "conf", "md"},
        "regex": r"-----BEGIN (RSA|EC|OPENSSH|DSA|PRIVATE) KEY-----",
        "message": "Private key material found in repository."
    },

    # Debug / insecure config
    {
        "id": "DEBUG-TRUE",
        "severity": "HIGH",
        "languages": {"py", "js", "ts", "json", "yaml", "yml"},
        "regex": r"(?i)\bDEBUG\b\s*[:=]\s*(True|true|1)",
        "message": "Debug mode enabled."
    },
    {
        "id": "FLASK-DEBUG-RUN",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"app\.run\s*\([^)]*debug\s*=\s*True",
        "message": "Flask app.run(debug=True) detected."
    },

    # JWT / auth issues
    {
        "id": "JWT-VERIFY-OFF",
        "severity": "CRITICAL",
        "languages": {"py", "js", "ts"},
        "regex": r"(?i)(verify_signature\s*[:=]\s*False|verify\s*[:=]\s*False|ignoreExpiration\s*:\s*true|algorithms\s*=\s*\[\s*\])",
        "message": "JWT verification may be disabled or misconfigured."
    },

    # Weak randomness
    {
        "id": "PY-WEAK-RANDOM",
        "severity": "MEDIUM",
        "languages": {"py"},
        "regex": r"\brandom\.(random|randint|choice|choices|randrange)\s*\(",
        "message": "random module used; unsafe for tokens/session secrets. Prefer secrets module."
    },
    {
        "id": "JS-MATH-RANDOM",
        "severity": "MEDIUM",
        "languages": {"js", "ts"},
        "regex": r"\bMath\.random\s*\(",
        "message": "Math.random() used; unsafe for tokens/session IDs."
    },

    # SQL injection heuristics
    {
        "id": "PY-SQL-FSTRING",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"(SELECT|INSERT|UPDATE|DELETE).*\{.*\}",
        "message": "Possible SQL built with f-string or format interpolation."
    },
    {
        "id": "PY-SQL-PERCENT",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"(SELECT|INSERT|UPDATE|DELETE).*(%s|%\()",
        "message": "Potential manual SQL formatting; verify parameterization."
    },
    {
        "id": "JS-SQL-CONCAT",
        "severity": "HIGH",
        "languages": {"js", "ts"},
        "regex": r"(SELECT|INSERT|UPDATE|DELETE).*(\+|\$\{)",
        "message": "Possible SQL string concatenation/interpolation."
    },

    # SSRF / Open redirect / URL fetch sinks
    {
        "id": "PY-REQUESTS-GET-VAR",
        "severity": "MEDIUM",
        "languages": {"py"},
        "regex": r"requests\.(get|post|put|delete|request)\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*",
        "message": "Dynamic outbound URL fetch; review for SSRF."
    },
    {
        "id": "PY-URLLIB-OPEN",
        "severity": "MEDIUM",
        "languages": {"py"},
        "regex": r"urllib\.request\.urlopen\s*\(",
        "message": "Outbound URL open; review for SSRF."
    },
    {
        "id": "JS-LOCATION-HREF",
        "severity": "MEDIUM",
        "languages": {"js", "ts"},
        "regex": r"(window\.)?location\.(href|assign|replace)\s*=",
        "message": "Potential open redirect if user-controlled."
    },

    # XSS / DOM sinks
    {
        "id": "JS-INNERHTML",
        "severity": "HIGH",
        "languages": {"js", "ts"},
        "regex": r"\.innerHTML\s*=",
        "message": "innerHTML assignment can create DOM XSS."
    },
    {
        "id": "JS-OUTERHTML",
        "severity": "HIGH",
        "languages": {"js", "ts"},
        "regex": r"\.outerHTML\s*=",
        "message": "outerHTML assignment can create DOM XSS."
    },
    {
        "id": "JS-DOC-WRITE",
        "severity": "HIGH",
        "languages": {"js", "ts"},
        "regex": r"document\.write\s*\(",
        "message": "document.write can create DOM XSS."
    },
    {
        "id": "JS-INSERT-ADJ-HTML",
        "severity": "HIGH",
        "languages": {"js", "ts"},
        "regex": r"insertAdjacentHTML\s*\(",
        "message": "insertAdjacentHTML can create DOM XSS."
    },
    {
        "id": "HTML-INLINE-ONHANDLER",
        "severity": "MEDIUM",
        "languages": {"html", "htm"},
        "regex": r"\son(click|load|error|mouseover|submit|change)\s*=",
        "message": "Inline event handlers can increase XSS risk."
    },

    # Template rendering issues
    {
        "id": "PY-JINJA-UNSAFE",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"render_template_string\s*\(",
        "message": "render_template_string() can be dangerous with user input."
    },
    {
        "id": "PY-MARKUPSAFE-BYPASS",
        "severity": "HIGH",
        "languages": {"py"},
        "regex": r"\bMarkup\s*\(",
        "message": "Markup() can bypass escaping if used on untrusted input."
    },

    # CORS / headers
    {
        "id": "CORS-WILDCARD",
        "severity": "HIGH",
        "languages": {"py", "js", "ts", "json", "yaml", "yml"},
        "regex": r"Access-Control-Allow-Origin['\"]?\s*[:=]\s*['\"]\*['\"]|origin\s*[:=]\s*['\"]\*['\"]",
        "message": "CORS wildcard detected."
    },

    # Insecure cookies
    {
        "id": "COOKIE-NO-HTTPONLY",
        "severity": "MEDIUM",
        "languages": {"py", "js", "ts"},
        "regex": r"set_cookie\s*\(",
        "message": "Review cookie flags: HttpOnly, Secure, SameSite."
    },
]

# ----------------------------
# Helpers
# ----------------------------

def ext_to_lang(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return ext if ext else "unknown"

def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {".env"}

def should_skip(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDE_DIRS for part in path.parts)

def safe_read(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

def line_number_from_pos(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1

def classify_file(path: Path):
    suffix = path.suffix.lower()
    if suffix in {".py"}:
        return "py"
    if suffix in {".js", ".jsx"}:
        return "js"
    if suffix in {".ts", ".tsx"}:
        return "ts"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in {".yaml"}:
        return "yaml"
    if suffix in {".yml"}:
        return "yml"
    if suffix == ".env":
        return "env"
    if suffix in {".json"}:
        return "json"
    if suffix in {".ini"}:
        return "ini"
    if suffix in {".cfg"}:
        return "cfg"
    if suffix in {".conf"}:
        return "conf"
    if suffix in {".md"}:
        return "md"
    return suffix.lstrip(".")

# ----------------------------
# Static scan
# ----------------------------

def scan_file(path: Path):
    findings = []
    if not is_text_file(path) or should_skip(path):
        return findings

    content = safe_read(path)
    if content is None:
        return findings

    lang = classify_file(path)

    for rule in PATTERNS:
        if lang not in rule["languages"]:
            continue

        for m in re.finditer(rule["regex"], content, flags=re.IGNORECASE | re.MULTILINE):
            line = line_number_from_pos(content, m.start())
            snippet = content[m.start():min(len(content), m.start()+180)].splitlines()[0].strip()
            findings.append({
                "type": "static",
                "rule_id": rule["id"],
                "severity": rule["severity"],
                "file": str(path),
                "line": line,
                "message": rule["message"],
                "snippet": snippet[:180]
            })

    # Extra AI-specific heuristics
    findings.extend(ai_specific_heuristics(path, content, lang))
    return findings

def ai_specific_heuristics(path: Path, content: str, lang: str):
    findings = []

    # Suspicious TODOs / placeholders left by AI
    placeholder_patterns = [
        (r"(?i)TODO:\s*sanitize", "MEDIUM", "AI-PLACEHOLDER-SANITIZE", "Placeholder sanitization comment; likely unfinished security logic."),
        (r"(?i)TODO:\s*validate", "MEDIUM", "AI-PLACEHOLDER-VALIDATE", "Placeholder validation comment; likely unfinished input validation."),
        (r"(?i)mock_secret|example_secret|changeme|replace_me", "HIGH", "AI-DEFAULT-SECRET", "Default/example secret or placeholder secret detected."),
        (r"(?i)trust.*proxy\s*=\s*True", "MEDIUM", "AI-PROXY-TRUST", "Proxy trust config detected; verify reverse proxy headers are locked down."),
    ]

    for regex, severity, rid, msg in placeholder_patterns:
        for m in re.finditer(regex, content):
            line = line_number_from_pos(content, m.start())
            findings.append({
                "type": "static",
                "rule_id": rid,
                "severity": severity,
                "file": str(path),
                "line": line,
                "message": msg,
                "snippet": content[m.start():min(len(content), m.start()+120)].splitlines()[0].strip()
            })

    return findings

def scan_path(root: Path):
    findings = []
    for p in root.rglob("*"):
        if p.is_file():
            findings.extend(scan_file(p))
    return findings

# ----------------------------
# Runtime probe
# ----------------------------

def http_probe(base_url: str):
    findings = []
    if requests is None:
        findings.append({
            "type": "runtime",
            "rule_id": "REQUESTS-MISSING",
            "severity": "LOW",
            "message": "requests not installed; skipping runtime probe."
        })
        return findings

    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "AI-Security-Audit/1.0"})

        # Basic GET
        r = session.get(base_url, timeout=8, allow_redirects=True)
        headers = {k.lower(): v for k, v in r.headers.items()}

        required_headers = {
            "content-security-policy": "Missing CSP header.",
            "x-frame-options": "Missing X-Frame-Options header.",
            "x-content-type-options": "Missing X-Content-Type-Options header.",
            "referrer-policy": "Missing Referrer-Policy header.",
        }

        for h, msg in required_headers.items():
            if h not in headers:
                findings.append({
                    "type": "runtime",
                    "rule_id": f"HEADER-{h.upper()}",
                    "severity": "MEDIUM",
                    "message": msg
                })

        if headers.get("server"):
            findings.append({
                "type": "runtime",
                "rule_id": "SERVER-BANNER",
                "severity": "LOW",
                "message": f"Server header exposed: {headers.get('server')}"
            })

        if "access-control-allow-origin" in headers and headers["access-control-allow-origin"] == "*":
            findings.append({
                "type": "runtime",
                "rule_id": "RUNTIME-CORS-WILDCARD",
                "severity": "HIGH",
                "message": "Runtime response includes Access-Control-Allow-Origin: *"
            })

        # Debug leak probes
        debug_paths = ["/debug", "/__debug__", "/console", "/.env", "/config", "/api/docs", "/openapi.json"]
        for path in debug_paths:
            try:
                rr = session.get(urljoin(base_url, path), timeout=5, allow_redirects=False)
                if rr.status_code == 200 and len(rr.text) > 0:
                    if path in {"/.env", "/config"}:
                        findings.append({
                            "type": "runtime",
                            "rule_id": "EXPOSED-SENSITIVE-PATH",
                            "severity": "CRITICAL",
                            "message": f"Sensitive path exposed: {path} (HTTP 200)"
                        })
                    else:
                        findings.append({
                            "type": "runtime",
                            "rule_id": "EXPOSED-DEBUG-PATH",
                            "severity": "HIGH",
                            "message": f"Potential debug/docs path exposed: {path} (HTTP 200)"
                        })
            except Exception:
                pass

        # OPTIONS probe
        try:
            opt = session.options(base_url, timeout=5)
            allow = opt.headers.get("Allow", "")
            if allow:
                dangerous = [m for m in ["PUT", "DELETE", "TRACE"] if m in allow.upper()]
                if dangerous:
                    findings.append({
                        "type": "runtime",
                        "rule_id": "HTTP-ALLOW-METHODS",
                        "severity": "MEDIUM",
                        "message": f"Potentially risky methods advertised: {', '.join(dangerous)}"
                    })
        except Exception:
            pass

        # TRACE probe
        try:
            tr = session.request("TRACE", base_url, timeout=5)
            if tr.status_code < 400:
                findings.append({
                    "type": "runtime",
                    "rule_id": "TRACE-ENABLED",
                    "severity": "HIGH",
                    "message": "TRACE method appears enabled."
                })
        except Exception:
            pass

    except Exception as e:
        findings.append({
            "type": "runtime",
            "rule_id": "HTTP-PROBE-FAILED",
            "severity": "LOW",
            "message": f"Runtime probe failed: {e}"
        })

    # TLS probe
    findings.extend(tls_probe(base_url))
    return findings

def tls_probe(base_url: str):
    findings = []
    parsed = urlparse(base_url)
    if parsed.scheme != "https":
        findings.append({
            "type": "runtime",
            "rule_id": "NO-HTTPS",
            "severity": "HIGH",
            "message": "Base URL is not HTTPS."
        })
        return findings

    host = parsed.hostname
    port = parsed.port or 443

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=6) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                proto = ssock.version()

                if proto in {"TLSv1", "TLSv1.1"}:
                    findings.append({
                        "type": "runtime",
                        "rule_id": "WEAK-TLS",
                        "severity": "HIGH",
                        "message": f"Weak TLS version negotiated: {proto}"
                    })

                if not cert:
                    findings.append({
                        "type": "runtime",
                        "rule_id": "NO-CERT",
                        "severity": "CRITICAL",
                        "message": "No certificate presented."
                    })
    except Exception as e:
        findings.append({
            "type": "runtime",
            "rule_id": "TLS-PROBE-FAILED",
            "severity": "LOW",
            "message": f"TLS probe failed: {e}"
        })

    return findings

# ----------------------------
# Reporting
# ----------------------------

def summarize(findings):
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        sev = f.get("severity", "LOW")
        counts[sev] = counts.get(sev, 0) + 1
    risk_score = sum(SEVERITY_WEIGHTS.get(f.get("severity", "LOW"), 1) for f in findings)
    return counts, risk_score

def sort_findings(findings):
    return sorted(findings, key=lambda f: (-SEVERITY_WEIGHTS.get(f["severity"], 0), f.get("file", ""), f.get("line", 0)))

def print_report(findings):
    counts, risk_score = summarize(findings)
    findings = sort_findings(findings)

    print("=" * 80)
    print("AI SECURITY AUDIT REPORT")
    print("=" * 80)
    print(f"CRITICAL: {counts['CRITICAL']} | HIGH: {counts['HIGH']} | MEDIUM: {counts['MEDIUM']} | LOW: {counts['LOW']}")
    print(f"RISK SCORE: {risk_score}")
    print()

    if not findings:
        print("No findings.")
        return

    for f in findings:
        sev = f["severity"]
        print(f"[{sev}] {f['rule_id']}")
        if "file" in f:
            print(f"  File: {f['file']}:{f.get('line', '?')}")
        print(f"  Issue: {f['message']}")
        if f.get("snippet"):
            print(f"  Snippet: {f['snippet']}")
        print()

def print_json(findings):
    print(json.dumps({
        "summary": {
            "counts": summarize(findings)[0],
            "risk_score": summarize(findings)[1]
        },
        "findings": sort_findings(findings)
    }, indent=2))

# ----------------------------
# Main
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Audit app for common security weaknesses, especially AI-generated code patterns.")
    parser.add_argument("--path", required=True, help="Path to source tree")
    parser.add_argument("--url", help="Optional live URL to probe")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    findings = scan_path(root)

    if args.url:
        findings.extend(http_probe(args.url))

    if args.json:
        print_json(findings)
    else:
        print_report(findings)

    # Exit non-zero if serious issues exist
    if any(f["severity"] in {"CRITICAL", "HIGH"} for f in findings):
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()