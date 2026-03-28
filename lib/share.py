#!/usr/bin/env python3
"""
Social sharing functionality for scan results
"""

import urllib.parse

def generate_tweet(stats, repo_name=None):
    """Generate Twitter share text"""
    critical = stats.get('counts', {}).get('CRITICAL', 0)
    high = stats.get('counts', {}).get('HIGH', 0)
    medium = stats.get('counts', {}).get('MEDIUM', 0)
    risk_score = stats.get('risk_score', 0)
    
    # Determine grade
    if risk_score == 0:
        grade = "A+"
        emoji = "🏆"
    elif risk_score < 10:
        grade = "A"
        emoji = "✅"
    elif risk_score < 30:
        grade = "B"
        emoji = "👍"
    elif risk_score < 60:
        grade = "C"
        emoji = "⚠️"
    else:
        grade = "D"
        emoji = "❌"
    
    repo_text = f" for {repo_name}" if repo_name else ""
    
    text = f"""I just scanned my codebase{repo_text} with @verdictos

{emoji} Security Score: {risk_score}/100 (Grade {grade})

"""
    
    if critical == 0 and high == 0 and medium == 0:
        text += "✅ No vulnerabilities found!"
    else:
        if critical > 0:
            text += f"❌ {critical} CRITICAL issue{'s' if critical > 1 else ''}\n"
        if high > 0:
            text += f"⚠️ {high} HIGH issue{'s' if high > 1 else ''}\n"
        if medium > 0:
            text += f"ℹ️ {medium} MEDIUM issue{'s' if medium > 1 else ''}\n"
    
    text += "\nScan your code: https://verdictos.tech"
    
    return text

def generate_share_url(text, platform="twitter"):
    """Generate social share URL"""
    encoded_text = urllib.parse.quote(text)
    
    urls = {
        "twitter": f"https://twitter.com/intent/tweet?text={encoded_text}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url=https://verdictos.tech&summary={encoded_text}",
        "reddit": f"https://reddit.com/submit?title={encoded_text}&url=https://verdictos.tech"
    }
    
    return urls.get(platform, urls["twitter"])

def print_share_prompt(stats, repo_name=None):
    """Print share prompt at end of scan"""
    tweet_text = generate_tweet(stats, repo_name)
    twitter_url = generate_share_url(tweet_text, "twitter")
    
    print("\n" + "=" * 80)
    print("📱 SHARE YOUR RESULTS")
    print("=" * 80)
    print("\nShare on Twitter:")
    print(f"\n{tweet_text}\n")
    print(f"Click to tweet: {twitter_url}")
    print("\nOr run: verdictos-scan --path . --share")
    print("=" * 80)

if __name__ == "__main__":
    # Test
    test_stats = {
        'counts': {'CRITICAL': 0, 'HIGH': 2, 'MEDIUM': 5, 'LOW': 1},
        'risk_score': 23
    }
    
    print_share_prompt(test_stats, "myrepo")
