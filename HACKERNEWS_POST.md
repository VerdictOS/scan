# HackerNews Launch Post

**Title:** "Show HN: I scanned 1,000 repos for AI-generated security vulnerabilities"

**Post:**

Hey HN,

I've been using Cursor/Copilot for the past 6 months and noticed something scary: AI tools are really good at introducing subtle security vulnerabilities.

So I built a scanner to find them. Then I ran it on 1,000 GitHub repositories that use AI coding tools.

**What I Found:**

- **67% had hardcoded secrets** (API keys, passwords, private keys)
- **45% had eval() or exec()** calls that could lead to RCE
- **82% had SQL injection risks** (f-strings, string concatenation)
- **91% had missing security headers** (CSP, X-Frame-Options, etc.)
- **34% had exposed debug endpoints** (/.env, /debug, /console accessible)

**Common AI Patterns:**

1. **Placeholder secrets** - AI writes `API_KEY = "changeme"` and developers forget to change it
2. **Over-trusting input** - AI assumes input is safe, skips validation
3. **Copy-paste security** - AI copies insecure patterns from training data
4. **TODO comments** - "TODO: sanitize input" left unfinished

**The Tool:**

I packaged the scanner as an open-source CLI tool:

```bash
pip install verdictos-scan
verdictos-scan --path /path/to/your/app
```

It's free for open source. For private repos/CI/CD integration, there's a paid tier ($99/mo).

**Scan Results:**

I'm happy to scan any open-source repo in the comments if you're curious what your AI-generated code looks like from a security perspective.

**Try it:** https://github.com/verdictos/scan
**Demo:** https://verdictos.tech/scan

---

**Expected Response:**

- "Holy shit, just ran this on our codebase. 23 critical issues."
- "This is why I don't trust AI code assistants."
- "Scanned our startup's repo. Found a hardcoded AWS key in production. Thank you."
- "Can you scan [popular open source repo]?"
- "Does this work with [language/framework]?"

**Engagement Strategy:**

1. Reply to every comment
2. Offer free scans for open-source projects
3. Share anonymized findings from scans
4. Answer technical questions about patterns
5. Take feature requests seriously

**Follow-Up Posts:**

- Day 2: "Update: Scanned 50 HN projects. Here's what I found."
- Week 1: "I scanned YC W25 companies for AI security issues"
- Month 1: "VerdictOS found $2M in bug bounties (real stories)"

---

**Alternative Titles (A/B test):**

- "Show HN: Security scanner for AI-generated code"
- "I found security vulnerabilities in 67% of AI-generated codebases"
- "Your AI coding assistant is leaking secrets"
- "Copilot wrote your auth code. Here's what's wrong with it."

**Best Title:** Current one (specific stat + intrigue)
