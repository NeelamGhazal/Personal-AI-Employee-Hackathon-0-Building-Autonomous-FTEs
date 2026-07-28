# Personal AI Employee - Demo Video Recording Script

**Total Duration:** 8-12 minutes
**Recording Date:** June 18, 2026
**Dashboard URL:** http://localhost:8000
**Odoo URL:** http://localhost:8069

---

## PRE-RECORDING CHECKLIST

Before starting, verify these are running:
```bash
# Terminal 1 - Check dashboard
curl http://localhost:8000/api/health
# Should show: "overall":"healthy", 8/8 components

# Terminal 2 - Check Odoo
curl http://localhost:8069 -s -o /dev/null -w "%{http_code}"
# Should show: 303 (redirect to login)

# Terminal 3 - Check Docker
docker.exe ps | grep odoo
# Should show: odoo and odoo-db containers running
```

---

## SECTION 1: INTRODUCTION (30 seconds)

### What to Say:
> "Assalam o Alaikum! Aaj main aapko dikhaunga apna Personal AI Employee project jo hackathon ke liye banaya hai. Ye ek fully autonomous AI employee hai jo business operations manage karta hai with human-in-the-loop approval."

### What to Show:
- Dashboard homepage at http://localhost:8000
- Scroll down slowly to show all sections

---

## SECTION 2: DASHBOARD HOME PAGE (1 minute)

### Page: Dashboard / Home Tab

#### Stats Cards (Top Section)
| Card | What It Shows | Backend | Working? |
|------|---------------|---------|----------|
| "Watchers Active" | Currently running watchers | `/api/stats` → `watchers_active` | ✅ YES |
| "Agent Skills" | Count of skills | `/api/stats` → `skills_count` | ✅ YES (shows 15) |
| "MCP Servers" | MCP server count | `/api/stats` → `mcp_servers` | ✅ YES (shows 4) |
| "Tiers Complete" | Bronze/Silver/Gold | `/api/stats` → `tiers_complete` | ✅ YES (shows 3) |

### What to Say:
> "Ye dashboard hai jahan aap dekh sakte hain - 15 Agent Skills loaded hain, 4 MCP servers connected hain, aur teeno tiers complete hain - Bronze, Silver, aur Gold."

### What to Show:
- Point to each card
- Hover over cards (they have hover effects)

---

## SECTION 3: HEALTH MONITOR (1 minute)

### Page: Health Monitor Tab (or bottom of home page)

#### Health Check Button
- **Button Name:** "Check Health" or auto-refreshing health panel
- **API Endpoint:** `GET /api/health`
- **Response Time:** ~500ms
- **What Happens:** Shows 8 component status

| Component | Expected Status | What It Checks |
|-----------|-----------------|----------------|
| API Server | ✅ healthy | Server running |
| Vault | ✅ healthy | AI_Employee_Vault folder exists |
| Watchers | ✅ healthy | Python scripts found |
| MCP Servers | ✅ healthy | 4 servers configured |
| Odoo | ✅ healthy | localhost:8069 responds |
| Social Sessions | ✅ healthy | 4/4 browser sessions exist |
| Gmail Credentials | ✅ healthy | token.json exists |
| Skills | ✅ healthy | 15 skill files found |

### What to Say:
> "Health monitor mein aap dekh sakte hain ke saare 8 components healthy hain. Odoo connected hai, social media sessions available hain, Gmail credentials configured hain."

### What to Show:
- Click refresh if available
- Point to each green checkmark
- Show "8/8 healthy" summary

---

## SECTION 4: VAULT BROWSER (2 minutes)

### Page: Vault / Files Tab

#### Folder Buttons
| Folder | Contents | API Endpoint |
|--------|----------|--------------|
| Inbox | Drop files here | `GET /api/vault/Inbox` |
| Needs_Action | Pending items | `GET /api/vault/Needs_Action` |
| Pending_Approval | Awaiting approval | `GET /api/vault/Pending_Approval` |
| Plans | AI-generated plans | `GET /api/vault/Plans` |
| Approved | Approved actions | `GET /api/vault/Approved` |
| Done | Completed tasks | `GET /api/vault/Done` |
| Briefings | CEO briefings | `GET /api/vault/Briefings` |

### What to Say:
> "Ye Obsidian-compatible vault hai. Files Inbox mein drop hoti hain, AI analyze karke Needs_Action mein move karta hai, phir Plan banata hai, aur approval ke baad execute hota hai. Ye human-in-the-loop workflow hai."

### What to Show:
1. Click "Inbox" - show files (21 items)
2. Click "Needs_Action" - show action files (50 items)
3. Click "Pending_Approval" - show 5 items waiting
4. Click "Plans" - show AI-generated plans
5. Click a file to see its content

### Demo Action: Click a Plan File
- **What Happens:** File content displayed
- **Time:** Instant

---

## SECTION 5: APPROVALS PAGE (1 minute)

### Page: Approvals Tab

#### View Pending Approvals
- **API Endpoint:** `GET /api/approval/pending`
- **What Happens:** Lists files in Pending_Approval folder

#### Approve Button
- **Button Name:** "Approve" (green button)
- **API Endpoint:** `POST /api/approval/action` with `{"action": "approve", "file": "filename.md"}`
- **What Happens:** Moves file from Pending_Approval to Approved folder
- **Time:** Instant

#### Reject Button
- **Button Name:** "Reject" (red button)
- **API Endpoint:** `POST /api/approval/action` with `{"action": "reject", "file": "filename.md"}`
- **What Happens:** Moves file to Rejected folder

### What to Say:
> "Ye sabse important feature hai - Human-in-the-Loop. AI kabhi bhi koi action directly execute nahi karta. Pehle yahan approval file banta hai, phir human review karta hai, approve ya reject karta hai, phir action execute hota hai."

### What to Show:
1. Show list of 5 pending items
2. Click on one to see details
3. **DO NOT approve during recording** (show workflow only)

---

## SECTION 6: RUN SCRIPTS - WATCHERS (2 minutes)

### Page: Watchers Tab or Quick Actions Panel

#### Gmail Watcher Button
- **Button Name:** "📧 Gmail Watcher" or "Run Gmail Watcher"
- **API Endpoint:** `POST /api/run/gmail-watcher`
- **Backend Script:** `gmail_watcher.py --once` (quick mode)
- **Time:** 5-10 seconds with --once flag
- **What Happens:** Checks Gmail for new emails, creates action files
- **Output:** Terminal shows OAuth check, email scan, completion time
- **Working?** ✅ YES (supports --once for fast single check)

#### WhatsApp Watcher Button
- **Button Name:** "💬 WhatsApp Watcher"
- **API Endpoint:** `POST /api/run/whatsapp-watcher`
- **Backend Script:** `whatsapp_watcher.py --test`
- **Time:** 5 seconds in test mode
- **What Happens:** Creates test action file
- **Output:** Shows WHATSAPP_*.md created
- **Working?** ✅ YES (test mode works)

#### LinkedIn Watcher Button
- **Button Name:** "💼 LinkedIn Watcher"
- **API Endpoint:** `POST /api/run/linkedin-watcher`
- **Backend Script:** `linkedin_watcher.py --test`
- **Time:** 5 seconds in test mode
- **Working?** ✅ YES (test mode)

#### Filesystem Watcher Button
- **Button Name:** "📁 Filesystem Watcher"
- **API Endpoint:** `POST /api/run/filesystem-watcher`
- **Backend Script:** `filesystem_watcher.py`
- **Time:** Runs continuously, timeout 10 seconds
- **Working?** ✅ YES

### What to Say:
> "Ye watchers hain jo continuously monitor karte hain. Gmail watcher inbox check karta hai, WhatsApp watcher messages dekhta hai, LinkedIn watcher connection requests monitor karta hai. Jab kuch naya aata hai, action file create hoti hai."

### What to Show:
1. Click "Gmail Watcher" - show terminal output
2. Wait for completion
3. Show that new file appeared in Needs_Action (if any)

### RECOMMENDED FOR DEMO:
- **RUN:** WhatsApp Watcher (test mode - fast, safe)
- **SKIP:** Gmail Watcher during recording (takes 30-60s)

---

## SECTION 7: SOCIAL MEDIA POSTING (2 minutes)

### Page: Social Media Tab

#### Facebook Post Button
- **Button Name:** "📘 Post to Facebook"
- **API Endpoint:** `POST /api/run/facebook-post`
- **Backend Script:** `facebook_poster.py`
- **Time:** 60-90 seconds
- **What Happens:** Opens Playwright browser, types message, posts
- **Output:** Screenshot saved, action file created
- **Working?** ✅ YES - VERIFIED WORKING

#### Twitter Post Button
- **Button Name:** "🐦 Post to Twitter"
- **API Endpoint:** `POST /api/run/twitter-post`
- **Backend Script:** `twitter_poster.py`
- **Time:** 90-120 seconds
- **Working?** ✅ YES - VERIFIED WORKING (takes ~2 min but works)

#### Instagram Post Button
- **Button Name:** "📸 Post to Instagram"
- **API Endpoint:** `POST /api/run/instagram-post`
- **Backend Script:** `instagram_poster.py`
- **Time:** 60-90 seconds
- **What Happens:** Creates image with PIL, uploads
- **Working?** ✅ YES - VERIFIED WORKING

#### LinkedIn Business Post Button (GoalGetters Page)
- **Button Name:** "🏢 LinkedIn Business"
- **API Endpoint:** `POST /api/run/linkedin-business-post`
- **Backend Script:** `linkedin_business_post.py`
- **Time:** 10-15 seconds
- **What Happens:** Posts to GoalGetters company page (ID: 112034239)
- **Working?** ✅ VERIFIED WORKING - Uses saved session, NO login needed
- **Hackathon Requirement:** Satisfies Silver Tier "Automatically Post on LinkedIn about business to generate sales"
- **Demo Command:** `uv run python src/ai_employee_watchers/linkedin_business_post.py`

### What to Say:
> "Social media posting Playwright browser automation se hoti hai. Facebook, Instagram, Twitter, LinkedIn - sab platforms pe post kar sakta hai. Dekho main Facebook pe post karta hoon..."

### RECOMMENDED FOR DEMO:
- **RUN:** LinkedIn Business (fastest - 10-15 seconds, satisfies hackathon requirement)
- **RUN:** Facebook Post (most reliable, 60-90 seconds)
- **OPTIONAL:** Twitter (works but takes ~2 min)

---

## SECTION 8: ODOO ERP (1.5 minutes)

### Page: Odoo Tab

#### Odoo Status
- **API Endpoint:** `GET /api/odoo/status`
- **What Shows:** Connected, version 19.0, database: ai_employee
- **Working?** ✅ YES

#### View Invoices Button
- **Button Name:** "View Invoices"
- **API Endpoint:** `GET /api/odoo/invoices`
- **What Happens:** Lists all invoices from Odoo
- **Working?** ✅ YES (shows INV/2026/00001)

#### Create Invoice Button
- **Button Name:** "Create Invoice"
- **API Endpoint:** `POST /api/odoo/invoice`
- **Parameters:** partner_name, invoice_lines
- **What Happens:** Creates invoice in Odoo via XML-RPC
- **Time:** 2-3 seconds
- **Working?** ✅ YES - VERIFIED

#### Accounting Summary
- **API Endpoint:** `GET /api/odoo/accounting`
- **What Shows:** Revenue, expenses, receivables
- **Working?** ✅ YES (shows $1,059.99 revenue)

### What to Say:
> "Odoo 19 ERP integration hai. Ye invoices create kar sakta hai, accounting summary dekh sakta hai. Dekho abhi ek invoice banate hain..."

### What to Show:
1. Show Odoo status (connected)
2. Click "View Invoices" - show INV/2026/00001
3. **OPTIONAL:** Create test invoice (takes 2-3 seconds)
4. Open http://localhost:8069 to show Odoo UI

### Odoo Login:
- **URL:** http://localhost:8069
- **Database:** ai_employee
- **Username:** admin
- **Password:** [SET_VIA_ENV_VAR]

---

## SECTION 9: CEO BRIEFING (1 minute)

### Page: Briefings Tab or Quick Actions

#### Generate CEO Briefing Button
- **Button Name:** "Generate CEO Briefing" or "📊 CEO Briefing"
- **API Endpoint:** `POST /api/run/ceo-briefing`
- **Backend Script:** `ceo_briefing.py`
- **Time:** 3-5 seconds
- **Output File:** `Briefings/CEO_BRIEFING_YYYYMMDD_HHMMSS.md`
- **Working?** ✅ YES - VERIFIED WORKING

### What It Generates:
- Financial overview from Odoo (revenue, expenses)
- Social media activity counts
- Pending communications
- Task pipeline status
- Action items

### What to Say:
> "CEO Briefing automatically generate hota hai. Ye Odoo se financial data leta hai, social media activity count karta hai, pending tasks dekhta hai. Ek click mein complete business summary mil jati hai."

### What to Show:
1. Click "Generate CEO Briefing"
2. Wait 3-5 seconds
3. Show the generated briefing content
4. Point out: Revenue ($1,059.99), Social posts (51), Pending items

---

## SECTION 10: AGENT SKILLS (30 seconds)

### Page: Skills Tab

#### Skills List
- **API Endpoint:** `GET /api/skills`
- **What Shows:** 15 skill files from .claude/skills/
- **Working?** ✅ YES

### Skills Available:
1. process-inbox.md
2. update-dashboard.md
3. create-plan.md
4. log-action.md
5. reasoning-loop.md
6. approval-orchestrator.md
7. vault-mcp.md
8. odoo-mcp.md
9. social-media-poster.md
10. ceo-briefing.md
11. comms-mcp.md
12. domain-classifier.md
13. error-handler.md
14. ralph-wiggum.md
15. audit-logger.md

### What to Say:
> "15 Agent Skills hain jo Claude Code ke saath kaam karti hain. Ye reusable workflows hain - inbox processing, plan creation, social posting, CEO briefing - sab skills ke through hota hai."

---

## SECTION 11: ARCHITECTURE DIAGRAM (30 seconds)

### Page: Architecture Tab

#### Architecture Button
- **API Endpoint:** `GET /api/demo/architecture`
- **What Shows:** ASCII architecture diagram
- **Working?** ✅ YES

### What to Say:
> "Architecture diagram mein dekh sakte hain - Watchers data collect karte hain, Vault mein store hota hai, Reasoning Loop analyze karta hai, Human approval ke baad Orchestrator execute karta hai. Full end-to-end autonomous workflow hai."

---

## SECTION 12: DEMO MODE (30 seconds)

### Page: Demo Mode Tab

#### Run Full Demo Sequence Button
- **Button Name:** "Run Full Demo Sequence"
- **API Endpoint:** `POST /api/demo/full`
- **Time:** ~10 seconds (fast!)
- **What Happens:** Runs test Gmail, WhatsApp, Invoice, Social, Briefing
- **Working?** ✅ YES - VERIFIED FAST (~10 seconds)

### What to Say:
> "Demo mode mein ek button se poora workflow chal sakta hai - test mode mein. Ye 10 seconds mein complete hota hai."

### RECOMMENDED:
- **RUN IT during recording** - It's fast and shows multiple features working

---

## SECTION 13: REASONING LOOP (1 minute)

### Quick Action or Separate Button

#### Run Reasoning Loop Button
- **Button Name:** "🧠 Reasoning Loop" or "Run Reasoning"
- **API Endpoint:** `POST /api/run/reasoning-loop`
- **Backend Script:** `reasoning_loop.py --once`
- **Time:** 2-5 seconds
- **What Happens:** Processes Needs_Action items, creates Plans
- **Output:** "Processing X items" or "No new items"
- **Working?** ✅ YES - VERIFIED

### What to Say:
> "Reasoning Loop AI ka brain hai. Ye Needs_Action folder se items utha kar analyze karta hai, Company Handbook aur Business Goals se context leta hai, aur Plan banata hai."

---

## SECTION 14: CLOSING (30 seconds)

### What to Say:
> "Toh ye tha mera Personal AI Employee project. Teen tiers complete hain - Bronze mein Vault structure, Silver mein Gmail/WhatsApp integration, Gold mein Social Media posting aur Odoo invoicing. Human-in-the-Loop approval workflow hai, MCP servers hain, 15 Agent Skills hain. Thank you for watching!"

### What to Show:
- Dashboard with all green health checks
- Scroll through quickly to show all features

---

## QUICK REFERENCE: WHAT TO DEMO (IN ORDER)

| # | Feature | Time | Status | Notes |
|---|---------|------|--------|-------|
| 1 | Dashboard overview | 30s | ✅ | Stats cards |
| 2 | Health Monitor | 30s | ✅ | 8/8 healthy |
| 3 | Vault folders | 1m | ✅ | Click through folders |
| 4 | Pending Approvals | 30s | ✅ | Show HITL workflow |
| 5 | WhatsApp Watcher | 15s | ✅ | Test mode - fast |
| 6 | Reasoning Loop | 10s | ✅ | Quick run |
| 7 | CEO Briefing | 10s | ✅ | Generate and show |
| 8 | **Full Demo Sequence** | 10s | ✅ | **NEW! Run this - fast!** |
| 9 | Facebook Post | 90s | ✅ | Real post - impressive |
| 10 | Gmail Watcher --once | 10s | ✅ | Quick single check |
| 11 | Odoo Status | 15s | ✅ | Show connected |
| 12 | Agent Skills | 15s | ✅ | Show list |
| 13 | Architecture | 15s | ✅ | Show diagram |

**Total Demo Time: ~7-10 minutes**

---

## THINGS TO DEMO (ALL WORKING!)

| Feature | Status | Notes |
|---------|--------|-------|
| LinkedIn Business | ✅ WORKING | Fastest social post - 10-15 seconds, satisfies hackathon requirement |
| Twitter Post | ✅ WORKING | Takes ~2 min - demo if time permits |
| Full Demo Sequence | ✅ WORKING | Fast ~10 seconds - great for demo! |
| Gmail Watcher | ✅ WORKING | Use --once flag for quick check (~5-10 sec) |

## NOT NEEDED FOR DEMO

| Feature | Reason |
|---------|--------|
| LinkedIn Personal | Not required - LinkedIn Business satisfies the hackathon requirement |

---

## TERMINAL COMMANDS FOR BACKUP

If dashboard buttons fail, run these directly:

```bash
# CEO Briefing
cd /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/ai_employee_watchers
uv run python src/ai_employee_watchers/ceo_briefing.py

# Reasoning Loop
uv run python src/ai_employee_watchers/reasoning_loop.py --once

# Gmail Watcher (quick mode - 5-10 seconds)
uv run python src/ai_employee_watchers/gmail_watcher.py --once

# Twitter Post (takes ~2 min but works)
uv run python src/ai_employee_watchers/twitter_poster.py --message "AI Employee demo post"

# Facebook Post (takes 90s)
uv run python src/ai_employee_watchers/facebook_poster.py --message "AI Employee demo post"

# LinkedIn Business (FASTEST - 10-15 seconds, satisfies hackathon requirement)
uv run python src/ai_employee_watchers/linkedin_business_post.py

# WhatsApp Test
uv run python src/ai_employee_watchers/whatsapp_watcher.py --test
```

---

## SCRIPT SUMMARY

**Opening:** Dashboard overview, stats cards, health monitor
**Middle:** Vault workflow, approvals, watchers, social posting, Odoo
**Closing:** Agent skills, architecture, summary

**Key Message:** "Autonomous AI Employee with Human-in-the-Loop approval"

**Hashtags for posting:** #PersonalAIEmployee #ClaudeCode #Hackathon #Automation #GoalGetters

---

*Last Updated: June 18, 2026 @ 17:15*
*All endpoints tested and verified working*
*Fixes applied: Twitter, Gmail --once, Full Demo Sequence*
