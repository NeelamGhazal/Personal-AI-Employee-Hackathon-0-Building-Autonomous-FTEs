# AI Employee Architecture Documentation

## Overview

The AI Employee is an autonomous system that manages personal and business tasks using:
- **Obsidian Vault** as the knowledge base and dashboard
- **Claude Code** as the reasoning engine
- **Watchers** for monitoring inputs (Gmail, WhatsApp, Filesystem)
- **MCP Servers** for executing actions
- **Ralph Wiggum Loop** for persistent task completion

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI EMPLOYEE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   WATCHERS   │    │   REASONING  │    │  MCP SERVERS │       │
│  │              │    │    LOOP      │    │              │       │
│  │ • Gmail      │───▶│              │───▶│ • Vault      │       │
│  │ • WhatsApp   │    │ Claude Code  │    │ • Odoo       │       │
│  │ • Filesystem │    │              │    │ • Social     │       │
│  └──────────────┘    └──────────────┘    │ • Comms      │       │
│         │                   │            └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    OBSIDIAN VAULT                        │    │
│  │                                                          │    │
│  │  /Personal/              /Business/                      │    │
│  │    Inbox/                  Inbox/                        │    │
│  │    Needs_Action/           Needs_Action/                 │    │
│  │    Done/                   Accounting/                   │    │
│  │                            Social_Media/                 │    │
│  │                                                          │    │
│  │  /Plans/  /Pending_Approval/  /Approved/  /Done/        │    │
│  │  /Logs/   /Briefings/         /Drafts/                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Watchers (Perception Layer)

| Watcher | File | Purpose |
|---------|------|---------|
| Filesystem | `filesystem_watcher.py` | Monitors vault folders for changes |
| Gmail | `gmail_watcher.py` | Fetches new emails via Gmail API |
| WhatsApp | `whatsapp_watcher.py` | Monitors WhatsApp Web via Playwright |

**Key Features:**
- Use `PollingObserver` for WSL2 compatibility
- Session persistence for WhatsApp
- OAuth 2.0 manual flow for Gmail (WSL-compatible)
- Domain classification (Personal vs Business)

### 2. Reasoning Loop

| Component | File | Purpose |
|-----------|------|---------|
| Reasoning Loop | `reasoning_loop.py` | Creates plans from Needs_Action items |
| Approval Orchestrator | `approval_orchestrator.py` | Executes approved plans |
| Domain Classifier | `domain_classifier.py` | Routes items to Personal/Business |
| Ralph Wiggum | `ralph_wiggum.py` | Keeps working until task complete |

### 3. MCP Servers (Action Layer)

| Server | File | Tools |
|--------|------|-------|
| Vault | `vault_mcp_server.js` | vault_read, vault_write, vault_list, vault_move |
| Odoo | `odoo_mcp_server.cjs` | odoo_authenticate, odoo_list_invoices, odoo_create_invoice |
| Social Media | `social_media_mcp_server.cjs` | social_post_facebook, social_post_instagram, social_post_twitter |
| Communications | `comms_mcp_server.cjs` | comms_check_gmail, comms_check_whatsapp, comms_create_draft |

### 4. Social Media Posters

| Platform | File | Features |
|----------|------|----------|
| Facebook | `facebook_poster.py` | Session persistence, screenshot proof |
| Instagram | `instagram_poster.py` | Session persistence, action files |
| Twitter/X | `twitter_poster.py` | Character count validation |

### 5. Business Intelligence

| Component | File | Purpose |
|-----------|------|---------|
| CEO Briefing | `ceo_briefing.py` | Weekly audit with financial summary |
| Audit Logger | `audit_logger.py` | Comprehensive action logging |
| Error Handler | `error_handler.py` | Graceful degradation and recovery |

---

## Workflow

### HITL (Human-in-the-Loop) Approval Flow

```
1. Watcher detects input (email/message/file)
         │
         ▼
2. Creates action file in /Needs_Action/
         │
         ▼
3. Reasoning Loop reads and creates Plan.md
         │
         ▼
4. Plan moves to /Pending_Approval/
         │
         ▼
5. Human reviews and moves to /Approved/ or /Rejected/
         │
         ▼
6. Approval Orchestrator executes approved plans
         │
         ▼
7. Task moves to /Done/
```

### Ralph Wiggum Pattern

```
1. Task created in /Needs_Action/
         │
         ▼
2. Ralph Wiggum loop starts
         │
         ▼
3. Execute step → Check if in /Done/
         │            │
         NO           YES
         │            │
         ▼            ▼
    Continue      Stop loop
    iterating
```

---

## Domain Classification

The system classifies incoming items as Personal or Business:

**Business Keywords:**
- Financial: invoice, payment, billing, revenue
- Operations: client, project, deadline, meeting
- Marketing: campaign, social media, promotion

**Personal Keywords:**
- Life: family, friend, birthday, vacation
- Health: doctor, appointment, medication
- Personal finance: bank statement, rent, subscription

---

## Odoo Integration

### Setup
```bash
# Docker Compose
docker compose up -d

# Creates:
# - PostgreSQL database (odoo-db)
# - Odoo 19 server (localhost:8069)
```

### API Access
- JSON-RPC endpoint: `http://localhost:8069/web/dataset/call_kw`
- Authentication: `http://localhost:8069/web/session/authenticate`
- Database: `ai_employee`
- Credentials: admin / [SET_VIA_ENV_VAR]

---

## Folder Structure

```
/AI_Employee_Vault/
├── Personal/
│   ├── Inbox/
│   ├── Needs_Action/
│   └── Done/
├── Business/
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Done/
│   ├── Accounting/
│   ├── Social_Media/
│   │   └── screenshots/
│   └── Projects/
├── Plans/
├── Pending_Approval/
├── Approved/
├── Done/
├── Rejected/
├── Logs/
│   ├── audit/
│   └── errors/
├── Briefings/
├── Drafts/
├── Dashboard.md
├── Company_Handbook.md
└── ARCHITECTURE.md
```

---

## Lessons Learned

### 1. WSL2 Compatibility
- **Problem:** inotify doesn't work reliably in WSL2
- **Solution:** Use `PollingObserver` instead of standard `Observer`

### 2. OAuth in Headless Environments
- **Problem:** `webbrowser.open()` fails in WSL
- **Solution:** Manual OAuth flow with `urn:ietf:wg:oauth:2.0:oob` redirect

### 3. Playwright Session Persistence
- **Problem:** WhatsApp requires re-login each time
- **Solution:** Use `launch_persistent_context()` with dedicated session folder

### 4. JSHandle vs ElementHandle
- **Problem:** `evaluate_handle()` returns JSHandle, can't call DOM methods
- **Solution:** Use `evaluate()` to extract data directly in JavaScript

### 5. Browser Lock Files
- **Problem:** Stale lock files prevent browser launch
- **Solution:** Clean up `SingletonLock` files before launching

### 6. ES Modules vs CommonJS
- **Problem:** Node.js ES modules don't support `require()`
- **Solution:** Use `.cjs` extension for CommonJS files

### 7. Domain Classification
- **Problem:** All messages going to same folder
- **Solution:** Implement keyword-based classifier with domain routing

### 8. Error Recovery
- **Problem:** Failures cascade and stop the system
- **Solution:** Circuit breaker pattern and fallback values

---

## Commands Reference

```bash
# Navigate to project
cd /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/ai_employee_watchers

# Run watchers
uv run python src/ai_employee_watchers/filesystem_watcher.py
uv run python src/ai_employee_watchers/gmail_watcher.py
uv run python src/ai_employee_watchers/whatsapp_watcher.py

# Test modes
uv run python src/ai_employee_watchers/whatsapp_watcher.py --test
uv run python src/ai_employee_watchers/facebook_poster.py --test
uv run python src/ai_employee_watchers/twitter_poster.py --test

# Generate CEO briefing
uv run python src/ai_employee_watchers/ceo_briefing.py

# Run MCP servers
node mcp_servers/vault_mcp_server.js
node mcp_servers/odoo_mcp_server.cjs
node mcp_servers/social_media_mcp_server.cjs
node mcp_servers/comms_mcp_server.cjs

# Docker (Odoo)
docker compose up -d
docker ps
```

---

## Security Considerations

1. **Credentials** stored in `/credentials/` (gitignored)
2. **Session files** not synced to cloud
3. **OAuth tokens** auto-refresh
4. **Secrets** never in vault markdown files
5. **HITL approval** for sensitive actions

---

*AI Employee v0.3 - Gold Tier*
*Generated: 2026-04-28*
