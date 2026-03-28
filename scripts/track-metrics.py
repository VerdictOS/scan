#!/usr/bin/env python3
"""
Real-time metrics tracker for VerdictOS Scan launch

Tracks:
- PyPI downloads
- GitHub stars/forks
- Reddit engagement
- Twitter metrics (if API available)

Usage:
    python3 track-metrics.py --dashboard
    python3 track-metrics.py --alert discord
"""

import requests
import json
import time
from datetime import datetime
import sys

class MetricsTracker:
    def __init__(self):
        self.github_repo = "VerdictOS/scan"
        self.pypi_package = "verdictos-scan"
        
    def get_github_stats(self):
        """Fetch GitHub stars, forks, watchers"""
        try:
            url = f"https://api.github.com/repos/{self.github_repo}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "watchers": data.get("subscribers_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "updated_at": data.get("updated_at", "")
            }
        except Exception as e:
            print(f"GitHub API error: {e}")
            return None
    
    def get_pypi_stats(self):
        """Fetch PyPI download stats"""
        try:
            # PyPI recent downloads (last day/week/month)
            url = f"https://pypistats.org/api/packages/{self.pypi_package}/recent"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            return {
                "last_day": data.get("data", {}).get("last_day", 0),
                "last_week": data.get("data", {}).get("last_week", 0),
                "last_month": data.get("data", {}).get("last_month", 0)
            }
        except Exception as e:
            # PyPI stats might not be available immediately after publish
            print(f"PyPI stats not ready yet: {e}")
            return {
                "last_day": 0,
                "last_week": 0,
                "last_month": 0
            }
    
    def get_github_traffic(self):
        """Fetch GitHub traffic (requires auth token)"""
        # This requires GitHub token with repo access
        # Will implement if token provided
        return None
    
    def calculate_targets(self, stats):
        """Calculate progress toward week 1 targets"""
        targets = {
            "conservative": {
                "downloads": 10000,
                "stars": 500,
                "pro_signups": 50  # Manual tracking
            },
            "realistic": {
                "downloads": 50000,
                "stars": 2000,
                "pro_signups": 200
            },
            "optimistic": {
                "downloads": 100000,
                "stars": 5000,
                "pro_signups": 500
            }
        }
        
        current_downloads = stats["pypi"]["last_week"]
        current_stars = stats["github"]["stars"]
        
        progress = {
            "conservative": {
                "downloads_pct": (current_downloads / targets["conservative"]["downloads"]) * 100,
                "stars_pct": (current_stars / targets["conservative"]["stars"]) * 100
            },
            "realistic": {
                "downloads_pct": (current_downloads / targets["realistic"]["downloads"]) * 100,
                "stars_pct": (current_stars / targets["realistic"]["stars"]) * 100
            },
            "optimistic": {
                "downloads_pct": (current_downloads / targets["optimistic"]["downloads"]) * 100,
                "stars_pct": (current_stars / targets["optimistic"]["stars"]) * 100
            }
        }
        
        return targets, progress
    
    def generate_dashboard(self):
        """Generate text dashboard"""
        print("=" * 80)
        print("VERDICTOS SCAN - LAUNCH METRICS DASHBOARD")
        print("=" * 80)
        print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        github_stats = self.get_github_stats()
        pypi_stats = self.get_pypi_stats()
        
        if github_stats:
            print("🌟 GITHUB STATS")
            print(f"  Stars:        {github_stats['stars']:,}")
            print(f"  Forks:        {github_stats['forks']:,}")
            print(f"  Watchers:     {github_stats['watchers']:,}")
            print(f"  Issues:       {github_stats['open_issues']:,}")
            print()
        
        if pypi_stats:
            print("📦 PYPI DOWNLOADS")
            print(f"  Last 24h:     {pypi_stats['last_day']:,}")
            print(f"  Last 7 days:  {pypi_stats['last_week']:,}")
            print(f"  Last 30 days: {pypi_stats['last_month']:,}")
            print()
        
        # Calculate progress
        stats = {
            "github": github_stats or {},
            "pypi": pypi_stats or {}
        }
        
        targets, progress = self.calculate_targets(stats)
        
        print("🎯 WEEK 1 TARGET PROGRESS")
        print()
        print("Conservative Target:")
        print(f"  Downloads: {progress['conservative']['downloads_pct']:.1f}% ({stats['pypi'].get('last_week', 0):,} / {targets['conservative']['downloads']:,})")
        print(f"  Stars:     {progress['conservative']['stars_pct']:.1f}% ({stats['github'].get('stars', 0):,} / {targets['conservative']['stars']:,})")
        print()
        print("Realistic Target:")
        print(f"  Downloads: {progress['realistic']['downloads_pct']:.1f}% ({stats['pypi'].get('last_week', 0):,} / {targets['realistic']['downloads']:,})")
        print(f"  Stars:     {progress['realistic']['stars_pct']:.1f}% ({stats['github'].get('stars', 0):,} / {targets['realistic']['stars']:,})")
        print()
        print("Optimistic Target:")
        print(f"  Downloads: {progress['optimistic']['downloads_pct']:.1f}% ({stats['pypi'].get('last_week', 0):,} / {targets['optimistic']['downloads']:,})")
        print(f"  Stars:     {progress['optimistic']['stars_pct']:.1f}% ({stats['github'].get('stars', 0):,} / {targets['optimistic']['stars']:,})")
        print()
        
        # Velocity estimate
        if pypi_stats.get('last_day', 0) > 0:
            daily_velocity = pypi_stats['last_day']
            week_projection = daily_velocity * 7
            print("📈 PROJECTIONS (Based on Current Velocity)")
            print(f"  Daily downloads: {daily_velocity:,}")
            print(f"  Week 1 projection: {week_projection:,}")
            print()
        
        print("=" * 80)
        
        return stats
    
    def alert_discord(self, webhook_url, stats):
        """Send alert to Discord webhook"""
        # Implementation if webhook provided
        pass
    
    def continuous_monitor(self, interval_minutes=30):
        """Run continuous monitoring"""
        print(f"Starting continuous monitoring (every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")
        print()
        
        while True:
            try:
                self.generate_dashboard()
                print(f"\nNext update in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    tracker = MetricsTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        tracker.continuous_monitor(interval_minutes=30)
    else:
        tracker.generate_dashboard()
