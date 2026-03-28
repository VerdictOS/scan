#!/usr/bin/env python3
"""
HTML Report Generator for VerdictOS Scan
Beautiful, interactive security reports
"""

import json
from datetime import datetime

def generate_html_report(findings, stats, output_path="verdictos-report.html"):
    """Generate beautiful HTML report"""
    
    counts = stats.get('counts', {})
    risk_score = stats.get('risk_score', 0)
    
    # Determine grade and color
    if risk_score == 0:
        grade = "A+"
        grade_color = "#10b981"
    elif risk_score < 10:
        grade = "A"
        grade_color = "#22c55e"
    elif risk_score < 30:
        grade = "B"
        grade_color = "#84cc16"
    elif risk_score < 60:
        grade = "C"
        grade_color = "#eab308"
    else:
        grade = "D"
        grade_color = "#ef4444"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VerdictOS Security Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0a1a 100%);
            color: #e5e5e5;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 60px;
        }}
        
        h1 {{
            font-size: 48px;
            font-weight: 800;
            background: linear-gradient(90deg, #6366f1, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 16px;
        }}
        
        .subtitle {{
            color: #9ca3af;
            font-size: 18px;
        }}
        
        .score-card {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-around;
            align-items: center;
        }}
        
        .grade {{
            text-align: center;
        }}
        
        .grade-letter {{
            font-size: 96px;
            font-weight: 800;
            color: {grade_color};
            line-height: 1;
        }}
        
        .grade-label {{
            color: #9ca3af;
            font-size: 14px;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .risk-score {{
            text-align: center;
        }}
        
        .risk-number {{
            font-size: 72px;
            font-weight: 800;
            color: {grade_color};
        }}
        
        .risk-label {{
            color: #9ca3af;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }}
        
        .stat-card.critical {{ border-color: #dc2626; }}
        .stat-card.high {{ border-color: #f59e0b; }}
        .stat-card.medium {{ border-color: #eab308; }}
        .stat-card.low {{ border-color: #10b981; }}
        
        .stat-number {{
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        
        .stat-number.critical {{ color: #dc2626; }}
        .stat-number.high {{ color: #f59e0b; }}
        .stat-number.medium {{ color: #eab308; }}
        .stat-number.low {{ color: #10b981; }}
        
        .stat-label {{
            color: #9ca3af;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .issues {{
            margin-bottom: 40px;
        }}
        
        .issue {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            border-left: 4px solid;
        }}
        
        .issue.critical {{ border-left-color: #dc2626; }}
        .issue.high {{ border-left-color: #f59e0b; }}
        .issue.medium {{ border-left-color: #eab308; }}
        .issue.low {{ border-left-color: #10b981; }}
        
        .issue-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 16px;
        }}
        
        .issue-title {{
            font-size: 20px;
            font-weight: 700;
        }}
        
        .issue-severity {{
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .issue-severity.critical {{ background: #dc2626; color: white; }}
        .issue-severity.high {{ background: #f59e0b; color: white; }}
        .issue-severity.medium {{ background: #eab308; color: black; }}
        .issue-severity.low {{ background: #10b981; color: white; }}
        
        .issue-file {{
            color: #9ca3af;
            font-size: 14px;
            margin-bottom: 12px;
            font-family: 'Monaco', 'Courier New', monospace;
        }}
        
        .issue-message {{
            color: #e5e5e5;
            margin-bottom: 12px;
        }}
        
        .issue-snippet {{
            background: #1a1a1a;
            border-radius: 6px;
            padding: 16px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            overflow-x: auto;
            color: #f87171;
        }}
        
        .actions {{
            display: flex;
            gap: 12px;
            justify-content: center;
            margin-top: 40px;
        }}
        
        .btn {{
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
        }}
        
        .btn-primary {{
            background: linear-gradient(90deg, #6366f1, #a855f7);
            color: white;
            border: none;
        }}
        
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 60px;
            color: #6b7280;
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            .score-card {{
                flex-direction: column;
                gap: 40px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Security Report</h1>
            <div class="subtitle">Generated by VerdictOS Scan on {datetime.now().strftime('%B %d, %Y at %H:%M')}</div>
        </div>
        
        <div class="score-card">
            <div class="grade">
                <div class="grade-letter">{grade}</div>
                <div class="grade-label">Security Grade</div>
            </div>
            <div class="risk-score">
                <div class="risk-number">{risk_score}</div>
                <div class="risk-label">Risk Score</div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card critical">
                <div class="stat-number critical">{counts.get('CRITICAL', 0)}</div>
                <div class="stat-label">Critical</div>
            </div>
            <div class="stat-card high">
                <div class="stat-number high">{counts.get('HIGH', 0)}</div>
                <div class="stat-label">High</div>
            </div>
            <div class="stat-card medium">
                <div class="stat-number medium">{counts.get('MEDIUM', 0)}</div>
                <div class="stat-label">Medium</div>
            </div>
            <div class="stat-card low">
                <div class="stat-number low">{counts.get('LOW', 0)}</div>
                <div class="stat-label">Low</div>
            </div>
        </div>
"""
    
    # Add issues
    if findings:
        html += '        <div class="issues">\n'
        html += '            <h2 style="margin-bottom: 24px; font-size: 32px;">Findings</h2>\n'
        
        for finding in findings:
            severity = finding['severity'].lower()
            html += f'''            <div class="issue {severity}">
                <div class="issue-header">
                    <div class="issue-title">{finding['rule_id']}</div>
                    <div class="issue-severity {severity}">{finding['severity']}</div>
                </div>
'''
            
            if 'file' in finding:
                html += f'                <div class="issue-file">{finding["file"]}:{finding.get("line", "?")}</div>\n'
            
            html += f'                <div class="issue-message">{finding["message"]}</div>\n'
            
            if finding.get('snippet'):
                html += f'                <div class="issue-snippet">{finding["snippet"]}</div>\n'
            
            html += '            </div>\n'
        
        html += '        </div>\n'
    else:
        html += '''        <div style="text-align: center; padding: 60px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
            <div style="font-size: 64px; margin-bottom: 16px;">✅</div>
            <h2 style="font-size: 32px; margin-bottom: 12px; color: #10b981;">No Vulnerabilities Found!</h2>
            <p style="color: #9ca3af;">Your codebase looks secure. Keep up the good work!</p>
        </div>
'''
    
    # Footer with actions
    html += '''        <div class="actions">
            <a href="https://twitter.com/intent/tweet?text=I%20just%20scanned%20my%20codebase%20with%20@verdictos%0A%0ASecurity%20Score%3A%20''' + str(risk_score) + '''%2F100%0A%0AScan%20your%20code%3A%20https%3A%2F%2Fverdictos.tech" class="btn btn-primary" target="_blank">Share on Twitter</a>
            <a href="https://github.com/VerdictOS/scan" class="btn btn-secondary" target="_blank">View on GitHub</a>
        </div>
        
        <div class="footer">
            <p>Generated by VerdictOS Scan v1.1.0</p>
            <p style="margin-top: 8px;">
                <a href="https://verdictos.tech" style="color: #6366f1; text-decoration: none;">verdictos.tech</a> • 
                <a href="https://github.com/VerdictOS/scan" style="color: #6366f1; text-decoration: none;">GitHub</a> • 
                <a href="mailto:admin@verdictos.tech" style="color: #6366f1; text-decoration: none;">Support</a>
            </p>
        </div>
    </div>
</body>
</html>
'''
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path

if __name__ == "__main__":
    # Test
    test_findings = [
        {
            "severity": "CRITICAL",
            "rule_id": "PY-EVAL",
            "file": "app/api.py",
            "line": 45,
            "message": "Use of eval() can lead to arbitrary code execution",
            "snippet": "result = eval(user_input)"
        }
    ]
    
    test_stats = {
        'counts': {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 5, 'LOW': 1},
        'risk_score': 23
    }
    
    output = generate_html_report(test_findings, test_stats)
    print(f"Generated: {output}")
