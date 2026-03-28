#!/usr/bin/env python3
"""
VerdictOS Security Scanner v1.1.0
Enhanced with auto-fix suggestions

Usage:
    verdictos-scan --path /path/to/app
    verdictos-scan --path /path/to/app --with-fixes
    verdictos-scan --path . --json
"""

import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# Import original scanner
from verdictos_scan import *

# Import fix suggestions
try:
    from fixes import get_fix_suggestion
except ImportError:
    def get_fix_suggestion(rule_id):
        return {"fix": "No fix available", "example": ""}

# Override print_report to include fixes
original_print_report = print_report

def print_report_with_fixes(findings, show_fixes=True):
    """Enhanced report with fix suggestions"""
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
        
        # Add fix suggestion if enabled
        if show_fixes and sev in ("CRITICAL", "HIGH"):
            fix = get_fix_suggestion(f['rule_id'])
            if fix.get('fix'):
                print(f"\n  💡 Fix: {fix['fix']}")
            if fix.get('example'):
                print(f"\n  Example:")
                for line in fix['example'].split('\n'):
                    print(f"  {line}")
        
        print()

# Monkey-patch the global print_report
print_report = print_report_with_fixes

if __name__ == "__main__":
    # Run main with enhanced reporting
    main()
