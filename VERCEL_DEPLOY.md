# Vercel Deployment Guide - VerdictOS Scan

**Status:** Ready to deploy
**Files:** ✅ All configured

---

## PRE-DEPLOYMENT CHECKLIST

### Files Ready:
- ✅ `landing.html` (14KB) - Main landing page
- ✅ `install.sh` (4.3KB) - One-line installer
- ✅ `vercel.json` (285B) - Vercel configuration

### Vercel Config:
- ✅ Routes configured (/ → landing.html)
- ✅ Static build setup
- ✅ install.sh accessible at /install.sh

---

## DEPLOYMENT STEPS

### Option 1: Vercel CLI (Recommended)

```bash
cd /data/.openclaw/workspace/verdictos-scan

# Install Vercel CLI (if needed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Expected output:
# ✅ Production: https://verdictos-scan-xxx.vercel.app
# 🔗 Inspect: https://vercel.com/...
```

### Option 2: GitHub Integration

1. Go to https://vercel.com/new
2. Import from GitHub: `VerdictOS/scan`
3. Configure:
   - Framework Preset: Other
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: `./`
4. Click "Deploy"

### Option 3: Drag & Drop

1. Go to https://vercel.com/new
2. Drag the `verdictos-scan` folder
3. Click "Deploy"

---

## POST-DEPLOYMENT

### 1. Verify Deployment

**Check these URLs work:**
```
https://your-deployment.vercel.app/
https://your-deployment.vercel.app/install.sh
```

**Test install script:**
```bash
curl -fsSL https://your-deployment.vercel.app/install.sh | head -20
```

Should show the installer script.

### 2. Add Custom Domain

**In Vercel dashboard:**
1. Go to project settings
2. Click "Domains"
3. Add `verdictos.tech`
4. Add `www.verdictos.tech`
5. Vercel will show DNS instructions

**DNS Configuration:**
```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### 3. Configure Environment (Optional)

**Not needed for static site, but for future:**
```bash
vercel env add NEXT_PUBLIC_APP_URL production
# Value: https://verdictos.tech
```

---

## TROUBLESHOOTING

### Issue: "vercel command not found"

**Fix:**
```bash
npm install -g vercel
```

### Issue: "Authentication required"

**Fix:**
```bash
vercel login
# Opens browser for login
```

### Issue: "Build failed"

**Check:**
- vercel.json is valid JSON
- All referenced files exist
- No syntax errors in HTML

**Our setup:** Static files only, should never fail

### Issue: "Domain not working"

**Check:**
1. DNS propagation (can take 24-48 hours)
2. Check with: `dig verdictos.tech`
3. Vercel domain settings show "Valid Configuration"

**Quick test:**
```bash
curl -I https://your-deployment.vercel.app
# Should return 200 OK
```

---

## EXPECTED RESULTS

### After Deployment:

**URLs that will work:**
- `https://verdictos.tech` → Landing page
- `https://verdictos.tech/install.sh` → Installer
- `https://www.verdictos.tech` → Landing page (www redirect)

**Install command will work:**
```bash
curl -fsSL https://verdictos.tech/install.sh | sh
```

**Analytics:**
- Vercel provides built-in analytics
- View at: https://vercel.com/[your-project]/analytics

---

## VERIFICATION SCRIPT

**Run after deployment:**

```bash
#!/bin/bash
echo "Testing VerdictOS Scan deployment..."

DOMAIN="your-deployment.vercel.app"

echo "1. Testing landing page..."
curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/
echo ""

echo "2. Testing install script..."
curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/install.sh
echo ""

echo "3. Testing install script content..."
curl -s https://$DOMAIN/install.sh | head -5
echo ""

echo "4. Testing DNS (if custom domain set)..."
dig verdictos.tech +short
echo ""

echo "✅ Verification complete!"
```

---

## QUICK COMMANDS

**Deploy:**
```bash
cd /data/.openclaw/workspace/verdictos-scan
vercel --prod
```

**Update:**
```bash
cd /data/.openclaw/workspace/verdictos-scan
# Make changes to landing.html
vercel --prod
```

**View logs:**
```bash
vercel logs
```

**Check status:**
```bash
vercel ls
```

---

## WHAT'S DEPLOYED

### Static Files:
- `landing.html` (main page)
- `install.sh` (installer script)

### Routes:
- `/` → `landing.html`
- `/install.sh` → `install.sh`

### Features:
- ✅ One-line install command
- ✅ Professional landing page
- ✅ Mobile responsive
- ✅ Fast CDN delivery (Vercel Edge)
- ✅ HTTPS by default
- ✅ Auto-scaling
- ✅ Built-in analytics

---

## READY TO DEPLOY!

**Just run:**
```bash
cd /data/.openclaw/workspace/verdictos-scan
vercel --prod
```

**That's it! 🚀**
