#!/usr/bin/env python3
"""
Security badge generator for VerdictOS Scan
"""

def get_badge_color(risk_score):
    """Get badge color based on risk score"""
    if risk_score == 0:
        return "brightgreen"  # Perfect
    elif risk_score < 10:
        return "green"        # Excellent
    elif risk_score < 30:
        return "yellowgreen"  # Good
    elif risk_score < 60:
        return "yellow"       # Fair
    elif risk_score < 100:
        return "orange"       # Poor
    else:
        return "red"          # Critical

def get_grade(risk_score):
    """Get letter grade from risk score"""
    if risk_score == 0:
        return "A+"
    elif risk_score < 10:
        return "A"
    elif risk_score < 30:
        return "B"
    elif risk_score < 60:
        return "C"
    else:
        return "D"

def generate_shields_url(risk_score, counts):
    """Generate shields.io badge URL"""
    grade = get_grade(risk_score)
    color = get_badge_color(risk_score)
    
    critical = counts.get('CRITICAL', 0)
    high = counts.get('HIGH', 0)
    
    # Determine label text
    if critical > 0:
        label_text = f"{critical} CRITICAL"
    elif high > 0:
        label_text = f"{high} HIGH"
    elif risk_score == 0:
        label_text = "SECURE"
    else:
        label_text = f"Grade {grade}"
    
    # shields.io format: https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>
    badge_url = f"https://img.shields.io/badge/VerdictOS-{label_text.replace(' ', '%20')}-{color}"
    
    return badge_url

def generate_markdown_badge(risk_score, counts, repo_url=None):
    """Generate markdown badge code"""
    badge_url = generate_shields_url(risk_score, counts)
    
    if repo_url:
        scan_url = f"https://verdictos.tech/scan?repo={repo_url}"
    else:
        scan_url = "https://verdictos.tech"
    
    markdown = f"[![VerdictOS Security]({badge_url})]({scan_url})"
    
    return markdown

def print_badge_instructions(risk_score, counts, repo_name=None):
    """Print badge installation instructions"""
    badge_url = generate_shields_url(risk_score, counts)
    markdown = generate_markdown_badge(risk_score, counts, repo_name)
    
    print("\n" + "=" * 80)
    print("🏆 SECURITY BADGE")
    print("=" * 80)
    print("\nAdd this to your README.md to show your security score:")
    print(f"\n{markdown}\n")
    print("This will display:")
    print(f"  {badge_url}\n")
    print("Badge updates when you re-scan your repository.")
    print("=" * 80)

if __name__ == "__main__":
    # Test
    test_counts = {'CRITICAL': 0, 'HIGH': 2, 'MEDIUM': 5, 'LOW': 1}
    test_score = 23
    
    print_badge_instructions(test_score, test_counts, "username/repo")
