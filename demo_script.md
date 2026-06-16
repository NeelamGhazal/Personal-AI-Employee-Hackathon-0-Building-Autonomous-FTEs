# AI Employee Demo Script
## Full-Time Equivalent Hackathon 0 - Judge Presentation

**Duration:** 5-10 minutes
**Dashboard URL:** http://localhost:8000

---

## Pre-Demo Checklist

```bash
# 1. Start Odoo (if not running)
cd odoo && docker compose up -d

# 2. Start API Server
python3 api_server.py

# 3. Open Dashboard
# Navigate to http://localhost:8000
```

---

## Demo Flow (5-10 Minutes)

### Opening (30 seconds)
> "This is the Personal AI Employee - an autonomous business management system that handles communications, scheduling, social media, and accounting with human-in-the-loop safety."

**Action:** Show the dashboard overview with live stats.

---

### Section 1: System Overview (1 minute)

**Navigate to:** Dashboard tab

**Key Points:**
- "All three tiers are complete: Bronze, Silver, and Gold"
- "15 agent skills powering autonomous workflows"
- "4 MCP servers for Claude integration"
- "Real-time statistics from the Obsidian vault"

**Action:** Click through the stats to show they're interactive.

---

### Section 2: Demo Mode - Guided Demo (2 minutes)

**Navigate to:** Demo Mode tab (🎬)

**Script:**
> "Let me show you how the AI Employee processes a task autonomously."

**Action:** Click "Run Guided Demo"

**As it runs, explain:**
1. **Incoming Trigger** - "A message arrives via Gmail, WhatsApp, or filesystem"
2. **AI Reasoning** - "Claude analyzes content and creates a structured plan"
3. **Human Approval** - "The plan waits for human review - no autonomous execution"
4. **Action Execute** - "Upon approval, the AI executes via MCP servers"
5. **Result & Log** - "Everything is logged for compliance and audit"

---

### Section 3: Live Workflow Demos (3 minutes)

**Gmail Workflow:**
> "Let's create a real email processing workflow."

**Action:** Click "Execute Gmail Flow"

**Point out:**
- ✓ File created in Needs_Action
- ✓ Plan generated automatically
- ✓ Awaiting human approval

**Odoo Invoice:**
> "Now let's create a real invoice in Odoo ERP."

**Action:** Click "Create Invoice"

**Point out:**
- ✓ Connected to Odoo 19
- ✓ Partner created
- ✓ Invoice ID generated with amount

**Social Media:**
> "The system can also post to Twitter, Facebook, Instagram, and LinkedIn."

**Action:** Click "Create Post" (test mode)

---

### Section 4: Health Monitor (30 seconds)

**Navigate to:** Health Monitor tab (💚)

**Script:**
> "The system continuously monitors all 8 components. Any issues are flagged with suggested fixes."

**Point out:** All green status indicators.

---

### Section 5: Architecture (30 seconds)

**Navigate to:** Architecture tab (📐)

**Script:**
> "The system uses a local-first architecture with no cloud dependencies. All data stays on-premise."

**Action:** Show the ASCII architecture diagram.

---

### Section 6: Full Demo Sequence (1 minute)

**Navigate back to:** Demo Mode tab

**Script:**
> "Let's run the complete demo sequence to show all workflows working together."

**Action:** Click "Run Full Demo Sequence"

**Watch for:** Confetti animation on completion!

---

### Closing (30 seconds)

**Key Differentiators:**
1. **HITL Safety** - "No autonomous execution without human approval"
2. **Local-First** - "100% on-premise, no cloud dependencies"
3. **MCP Native** - "Built specifically for Claude Code integration"
4. **Enterprise-Ready** - "Odoo ERP, audit logging, CEO briefings"

> "This is a production-ready AI Employee that can be deployed today."

---

## Troubleshooting

### Odoo Offline
```bash
cd odoo && docker compose up -d
# Wait 30 seconds for startup
```

### API Server Not Responding
```bash
# Kill existing process
pkill -f "python.*api_server"
# Restart
python3 api_server.py
```

### Social Media Session Expired
- Demo will still work in test mode
- Proof panel will show "Session needed" warning

---

## Q&A Preparation

**Q: How does HITL work?**
> Files are placed in Pending_Approval folder. Human moves to Approved or Rejected. Only approved actions execute.

**Q: Is this secure?**
> Yes - local-first architecture, no cloud dependencies, comprehensive audit logging, and HITL for all actions.

**Q: How does it integrate with existing tools?**
> MCP servers provide Claude-native integration. Odoo for ERP, Gmail API for email, Playwright for WhatsApp/LinkedIn.

**Q: Can it scale?**
> The file-based architecture (Obsidian vault) can handle thousands of items. Odoo handles enterprise-scale accounting.

---

## Demo Video Tips

1. **Use Full Screen** - Hide browser tabs
2. **Zoom Dashboard** - 110-120% for recording
3. **Pause on Proof Panels** - Let viewers see the real data
4. **Highlight Confetti** - It's the wow moment!
5. **Show Health Monitor** - Proves everything is working

---

*Good luck with the demo!*
