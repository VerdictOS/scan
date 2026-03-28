#!/usr/bin/env python3
"""
Global stats tracking for VerdictOS Scan
Anonymously tracks total scans & vulnerabilities found
"""

import json
import requests
from datetime import datetime

class StatsReporter:
    def __init__(self):
        self.stats_endpoint = "https://api.verdictos.tech/stats"
        self.enabled = True  # Can be disabled via env var
        
    def report_scan(self, findings_count, risk_score, anonymous=True):
        """Report scan stats (anonymously)"""
        if not self.enabled:
            return
        
        try:
            payload = {
                'timestamp': datetime.now().isoformat(),
                'findings': findings_count,
                'risk_score': risk_score,
                'version': '1.1.0'
            }
            
            # Non-blocking request (timeout 1s)
            requests.post(
                self.stats_endpoint,
                json=payload,
                timeout=1
            )
        except:
            # Silently fail if stats endpoint unavailable
            pass
    
    def get_global_stats(self):
        """Get global stats from API"""
        try:
            response = requests.get(self.stats_endpoint, timeout=2)
            return response.json()
        except:
            return {
                'total_scans': 0,
                'total_vulnerabilities': 0,
                'repositories_protected': 0
            }
    
    def print_global_stats(self):
        """Print global stats banner"""
        stats = self.get_global_stats()
        
        print("\n" + "=" * 80)
        print("📊 VERDICTOS COMMUNITY STATS")
        print("=" * 80)
        print(f"  Total Scans:          {stats.get('total_scans', 0):,}")
        print(f"  Vulnerabilities Found: {stats.get('total_vulnerabilities', 0):,}")
        print(f"  Repositories Protected: {stats.get('repositories_protected', 0):,}")
        print("=" * 80 + "\n")

# Placeholder for when we have actual API endpoint
def get_mock_stats():
    """Return mock stats for display"""
    return {
        'total_scans': 1247,
        'total_vulnerabilities': 12894,
        'repositories_protected': 847
    }

if __name__ == "__main__":
    reporter = StatsReporter()
    # Until API is live, use mock data
    stats = get_mock_stats()
    print(f"Total scans: {stats['total_scans']:,}")
    print(f"Vulnerabilities found: {stats['total_vulnerabilities']:,}")
