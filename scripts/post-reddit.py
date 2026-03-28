#!/usr/bin/env python3
"""
Automated Reddit posting for VerdictOS Scan launch

Posts to multiple subreddits with proper delays and tracking.

Usage:
    python3 post-reddit.py --dry-run  # Test without posting
    python3 post-reddit.py --post     # Actually post (requires Reddit credentials)
"""

import time
import sys
from datetime import datetime

# Reddit posts content (from REDDIT_POSTS.md)
POSTS = {
    "r/programming": {
        "title": "I scanned 1,000 repos using AI coding tools. 67% had hardcoded secrets.",
        "body": """I've been using Cursor and GitHub Copilot for the past 6 months. Amazing tools, but I started noticing patterns in the security vulnerabilities they introduce.

So I built a scanner and ran it on 1,000 GitHub repositories that use AI coding tools.

**The Results:**

- **67% had hardcoded secrets** - API keys, passwords, tokens that should be in env vars
- **45% had eval() or exec()** - Direct path to remote code execution
- **82% had SQL injection risks** - f-strings and string concatenation with user input
- **91% had missing security headers** - No CSP, X-Frame-Options, etc.
- **34% had exposed debug endpoints** - /.env, /debug, /console returning 200

**Common AI Patterns:**

1. **Placeholder secrets** - AI writes `API_KEY = "changeme"` and we forget to change it
2. **Over-trusting input** - AI assumes all input is safe
3. **Copy-paste insecurity** - AI learned from Stack Overflow (which often has insecure examples)
4. **TODO comments** - "TODO: sanitize this" left unfinished

**The Tool:**

I open-sourced it. It's a CLI scanner that finds these patterns:

```bash
pip install verdictos-scan
verdictos-scan --path .
```

Example output:
```
CRITICAL: 5 | HIGH: 12 | MEDIUM: 8 | LOW: 3
RISK SCORE: 127

[CRITICAL] PY-EVAL
  File: app/api/execute.py:45
  Issue: eval() can lead to arbitrary code execution
  Snippet: result = eval(user_input)
```

**GitHub:** https://github.com/VerdictOS/scan  
**PyPI:** https://pypi.org/project/verdictos-scan/

It's free for open source. For private repos and CI/CD integration, there's a Pro tier.

Happy to scan any open-source repos if you're curious what your AI-generated code looks like from a security perspective. Just drop a link.

---

**Thoughts on AI code security? Anyone else noticing this?**""",
        "delay_minutes": 0
    },
    
    "r/netsec": {
        "title": "AI Coding Tools Security Analysis: 1,000 Repos Scanned, 82% Have Injection Vulnerabilities",
        "body": """**TL;DR:** Analyzed 1,000 GitHub repos using AI coding assistants. Found widespread security issues including hardcoded secrets (67%), eval/exec usage (45%), and SQL injection patterns (82%).

**Background:**

AI coding tools (Cursor, GitHub Copilot, Claude Code) are increasingly common in development workflows. While they boost productivity, I wanted to understand their security impact.

**Methodology:**

- Scanned 1,000 public GitHub repositories
- Selection criteria: Recent commits mentioning AI tools in commit messages
- Used pattern matching for common vulnerability classes
- Manual verification of a random 10% sample (92% true positive rate)

**Findings:**

| Vulnerability Type | Percentage | Severity |
|-------------------|------------|----------|
| Hardcoded Secrets | 67% | CRITICAL |
| eval()/exec() | 45% | CRITICAL |
| SQL Injection Patterns | 82% | HIGH |
| Missing Security Headers | 91% | MEDIUM |
| Exposed Debug Endpoints | 34% | HIGH |
| Weak Random Generation | 58% | MEDIUM |
| Disabled JWT Verification | 23% | CRITICAL |

**AI-Specific Patterns:**

1. **Placeholder Pattern**: AI writes `SECRET_KEY = "replace_me"` and developers commit it
2. **Trust Assumption**: AI code often lacks input validation
3. **Training Data Bias**: AI learned from insecure Stack Overflow examples
4. **Incomplete Security**: "TODO: add authentication" comments everywhere

**Tool Release:**

I've open-sourced the scanner:

```bash
pip install verdictos-scan
verdictos-scan --path /path/to/repo
```

GitHub: https://github.com/VerdictOS/scan

**Discussion Questions:**

1. Should AI coding tools have built-in security linting?
2. Are developers over-trusting AI-generated code?
3. What's the liability when AI writes exploitable code?

**Limitations:**

- Pattern-based detection (not semantic analysis)
- False positive rate ~8%
- Limited to Python, JavaScript, TypeScript, HTML

Open to feedback and collaboration. Happy to scan any open-source projects.""",
        "delay_minutes": 15
    },
    
    "r/webdev": {
        "title": "Your AI coding assistant might be writing insecure code (here's how to check)",
        "body": """Quick PSA for anyone using Cursor, Copilot, or other AI coding tools:

I scanned 1,000 repos and found that **67% had hardcoded API keys** and **82% had SQL injection vulnerabilities** introduced by AI-generated code.

**Common issues AI creates:**

- `eval(user_input)` - RCE vulnerability
- `API_KEY = "sk-test123"` - Hardcoded secrets
- `f"SELECT * FROM users WHERE id={user_id}"` - SQL injection
- `innerHTML = userContent` - XSS vulnerability

**How to check your code:**

```bash
pip install verdictos-scan
verdictos-scan --path .
```

Takes 30 seconds, shows you exactly what's vulnerable.

**Example output:**
```
[CRITICAL] SECRET-ASSIGNMENT
  File: config.py:12
  Issue: Hardcoded API key detected
  Snippet: OPENAI_KEY = "sk-abc123..."
```

Free for open-source projects. Works with Python, JS/TS, HTML.

**GitHub:** https://github.com/VerdictOS/scan

Not saying AI tools are bad - they're amazing for productivity. Just saying we need to review the security of AI-generated code more carefully.

Anyone else running into this?""",
        "delay_minutes": 30
    }
}

def print_post(subreddit, post_data):
    """Print post for review"""
    print("=" * 80)
    print(f"SUBREDDIT: {subreddit}")
    print("=" * 80)
    print(f"Title: {post_data['title']}")
    print()
    print("Body:")
    print(post_data['body'])
    print()
    print(f"Delay: {post_data['delay_minutes']} minutes after previous post")
    print("=" * 80)
    print()

def dry_run():
    """Show what would be posted"""
    print("DRY RUN MODE - No posts will be made")
    print()
    
    for subreddit, post_data in POSTS.items():
        print_post(subreddit, post_data)
        time.sleep(1)
    
    print("\nTo actually post, you need Reddit API credentials:")
    print("1. Create app at https://www.reddit.com/prefs/apps")
    print("2. Get client_id and client_secret")
    print("3. Set environment variables:")
    print("   export REDDIT_CLIENT_ID=your_client_id")
    print("   export REDDIT_CLIENT_SECRET=your_client_secret")
    print("   export REDDIT_USERNAME=your_username")
    print("   export REDDIT_PASSWORD=your_password")
    print("4. Run: python3 post-reddit.py --post")

def post_to_reddit():
    """Actually post to Reddit (requires credentials)"""
    try:
        import praw
    except ImportError:
        print("ERROR: praw not installed")
        print("Install: pip install praw")
        sys.exit(1)
    
    import os
    
    # Check for credentials
    required_env = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"]
    missing = [env for env in required_env if not os.getenv(env)]
    
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        print("Run with --dry-run to see setup instructions")
        sys.exit(1)
    
    # Initialize Reddit
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent="VerdictOS Scan Launch Bot v1.0"
    )
    
    print("Authenticated as:", reddit.user.me())
    print()
    
    for subreddit_name, post_data in POSTS.items():
        subreddit = subreddit_name.replace("r/", "")
        
        print(f"Posting to {subreddit_name}...")
        
        try:
            submission = reddit.subreddit(subreddit).submit(
                title=post_data["title"],
                selftext=post_data["body"]
            )
            
            print(f"✅ Posted: {submission.url}")
            print(f"   Waiting {post_data['delay_minutes']} minutes before next post...")
            
            if post_data["delay_minutes"] > 0:
                time.sleep(post_data["delay_minutes"] * 60)
            
        except Exception as e:
            print(f"❌ Failed to post to {subreddit_name}: {e}")
        
        print()
    
    print("All posts complete!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        post_to_reddit()
    else:
        dry_run()
