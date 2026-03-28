#!/usr/bin/env python3
"""
Usage tracking and limits for VerdictOS Scan
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class UsageTracker:
    def __init__(self):
        self.config_dir = Path.home() / '.verdictos'
        self.config_file = self.config_dir / 'usage.json'
        self.config_dir.mkdir(exist_ok=True)
        
        self.FREE_LIMIT = 10  # scans per month
        
    def load_usage(self):
        """Load usage data"""
        if not self.config_file.exists():
            return {
                'scans': [],
                'tier': 'free',
                'api_key': None
            }
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {'scans': [], 'tier': 'free', 'api_key': None}
    
    def save_usage(self, data):
        """Save usage data"""
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_monthly_scans(self, data):
        """Count scans in current month"""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_scans = [
            scan for scan in data.get('scans', [])
            if datetime.fromisoformat(scan) >= month_start
        ]
        
        return len(monthly_scans)
    
    def record_scan(self):
        """Record a scan and check limits"""
        data = self.load_usage()
        
        # Pro users have unlimited scans
        if data.get('tier') == 'pro' or data.get('api_key'):
            data['scans'].append(datetime.now().isoformat())
            self.save_usage(data)
            return True, None
        
        # Check free tier limits
        monthly_scans = self.get_monthly_scans(data)
        
        if monthly_scans >= self.FREE_LIMIT:
            remaining = 0
            message = f"""
╔══════════════════════════════════════════════════════════════╗
║  FREE TIER LIMIT REACHED                                     ║
╚══════════════════════════════════════════════════════════════╝

You've used {monthly_scans}/{self.FREE_LIMIT} free scans this month.

Upgrade to Pro for unlimited scans:
  • Unlimited private repo scans
  • GitHub Action integration
  • Priority support
  • Only $99/month

Learn more: https://verdictos.tech/pricing

Or reset next month: {(datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%B 1, %Y')}
"""
            return False, message
        
        # Record scan
        data['scans'].append(datetime.now().isoformat())
        self.save_usage(data)
        
        remaining = self.FREE_LIMIT - monthly_scans - 1
        
        if remaining <= 3:
            message = f"\n⚠️  {remaining} free scans remaining this month. Upgrade: https://verdictos.tech/pricing\n"
        else:
            message = None
        
        return True, message
    
    def set_pro_key(self, api_key):
        """Set Pro tier API key"""
        data = self.load_usage()
        data['api_key'] = api_key
        data['tier'] = 'pro'
        self.save_usage(data)
        print("✅ Pro tier activated!")
    
    def get_status(self):
        """Get usage status"""
        data = self.load_usage()
        monthly_scans = self.get_monthly_scans(data)
        
        if data.get('tier') == 'pro' or data.get('api_key'):
            return f"Pro tier: Unlimited scans ({monthly_scans} used this month)"
        else:
            remaining = self.FREE_LIMIT - monthly_scans
            return f"Free tier: {monthly_scans}/{self.FREE_LIMIT} scans used ({remaining} remaining)"

if __name__ == "__main__":
    tracker = UsageTracker()
    print(tracker.get_status())
