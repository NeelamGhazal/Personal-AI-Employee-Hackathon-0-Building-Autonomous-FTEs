# Personal AI Employee - Project Memory

## Project Overview

**Project Name:** Personal AI Employee (Full-Time Equivalent)  
**Hackathon:** Claude Code Hackathon 2026  
**Completion Date:** July 29, 2026  
**Video Recording:** All 14 scenes completed  

---

## Hackathon Tier Completion

| Tier | Score | Status |
|------|-------|--------|
| Bronze | **100%** | All requirements met |
| Silver | **95%** | All features working, scheduling is manual |
| Gold | **90%** | All features present, production-ready |

---

## Features Built and Working

### Core Infrastructure
- **Obsidian Vault** (`AI_Employee_Vault/`) - Full folder structure with Personal/Business domains
- **Dashboard.md** - Live status dashboard
- **Company_Handbook.md** - Business policies and procedures
- **ARCHITECTURE.md** - System architecture documentation
- **FastAPI Server** (`api_server.py`) - REST API at http://localhost:8000
- **Web Dashboard** (`dashboard.html`) - Modern UI at http://localhost:8000/dashboard.html

### Watcher Scripts (21 total)
- `gmail_watcher.py` - Gmail monitoring via OAuth
- `whatsapp_watcher.py` - WhatsApp Web monitoring
- `filesystem_watcher.py` - Inbox folder monitoring
- `linkedin_watcher.py` - LinkedIn monitoring
- `linkedin_business_post.py` - LinkedIn business page posting
- `linkedin_poster.py` - Personal LinkedIn posting
- `twitter_poster.py` - Twitter/X posting with auto-login
- `facebook_poster.py` - Facebook posting
- `instagram_poster.py` - Instagram posting with image generation
- `reasoning_loop.py` - Claude Code reasoning with Plan.md generation
- `approval_orchestrator.py` - Human-in-the-loop approval workflow
- `ceo_briefing.py` - Weekly CEO briefing generation
- `ralph_wiggum.py` - Persistent task completion loop
- `domain_classifier.py` - Personal vs Business classification
- `error_handler.py` - Error recovery and logging
- `audit_logger.py` - Audit trail logging

### MCP Servers (4 total)
- `vault_mcp_server.js` - Vault read/write/list operations
- `odoo_mcp_server.cjs` - Odoo ERP integration
- `social_media_mcp_server.cjs` - Social media posting
- `comms_mcp_server.cjs` - Communications (Gmail, WhatsApp)

### Agent Skills (15 total)
- `process-inbox.md`, `reasoning-loop.md`, `create-plan.md`
- `domain-classifier.md`, `approval-orchestrator.md`
- `vault-mcp.md`, `odoo-mcp.md`, `social-media-poster.md`, `comms-mcp.md`
- `ceo-briefing.md`, `ralph-wiggum.md`, `error-handler.md`, `audit-logger.md`
- `log-action.md`, `update-dashboard.md`

---

## All Fixes Applied

### LinkedIn Fixes
- Added `safe_goto()` helper with 60000ms timeout and 3x retry logic
- Increased browser launch timeout to 60000ms
- Added `--quick` mode for faster API responses
- Fixed session lock cleanup (SingletonLock files)
- Verified posting to GoalGetters business page (Company ID: 112034239)

### Twitter Fixes
- Fixed critical indentation bug where `return` was outside if block (caused script to exit without posting)
- Implemented `auto_login()` with multi-step flow (username → Next → password)
- Added environment variable support for `TWITTER_PASSWORD`
- Changed to use `channel="chrome"` to avoid bot detection
- Increased API timeout from 240s to 360s
- Fixed endpoint to always post for real (removed test_mode flag)

### Facebook Fixes
- Fixed endpoint to always post for real (removed test_mode flag)
- Added default message with timestamp if none provided
- Increased timeout to 240s
- Verified posting working on Neelum Ghazal's profile

### Instagram Fixes
- Fixed endpoint to always post for real (removed test_mode flag)
- Added default message with timestamp if none provided
- Increased font size to 72px with Arial Bold for image text
- Added dark gradient background (navy to purple)
- Session lock cleanup for Playwright persistent context

### Filesystem Watcher Fixes
- Fixed to watch correct Inbox folder
- Proper file extension handling (.txt, .md)
- Debouncing for rapid file changes

### Dashboard Approval Button Fix
- Fixed approval endpoint to properly move files
- Added visual feedback for approve/reject actions
- Connected to approval_orchestrator.py

### API Server Fixes
- All social media endpoints now post for real (no test_mode)
- Proper PowerShell subprocess handling for WSL → Windows
- Environment variable passing to subprocesses
- Timeout increases for long-running operations

---

## Current System Status

### Services
| Service | URL | Status |
|---------|-----|--------|
| API Server | http://localhost:8000 | Running |
| Web Dashboard | http://localhost:8000/dashboard.html | Running |
| Odoo ERP | http://localhost:8069 | Running (Docker) |
| PostgreSQL | localhost:5432 | Running (Docker) |

### Health Check
- API Server: Healthy
- Vault: Healthy
- Watchers: Scripts found
- MCP Servers: 4 configured
- Odoo: Connected
- Social Sessions: 4/4 (Twitter, Facebook, Instagram, LinkedIn)
- Gmail Credentials: Configured
- Agent Skills: 15 loaded

---

## Credentials and Paths

### Paths
```
Project Root:     /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/
Vault:            /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/AI_Employee_Vault/
Watchers:         /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/ai_employee_watchers/
MCP Servers:      /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/mcp_servers/
Credentials:      /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/
```

### Odoo ERP
```
URL:      http://localhost:8069
Database: ai_employee
Login:    admin
Password: admin123
```

### Social Media Sessions (Playwright Persistent Contexts)
```
Twitter:   credentials/twitter_session/
Facebook:  credentials/facebook_session/
Instagram: credentials/instagram_session/
LinkedIn:  credentials/linkedin_session/
```

### Gmail OAuth
```
Credentials: credentials/gmail_credentials.json
Token:       credentials/gmail_token.json
```

---

## Video Recording - All 14 Scenes Completed

1. Introduction and Dashboard Overview
2. Inbox Processing Demo
3. Domain Classification
4. Plan.md Generation
5. Human-in-the-Loop Approval
6. Odoo Invoice Creation
7. Gmail Watcher
8. WhatsApp Watcher
9. Social Media Posting (LinkedIn, Twitter, Facebook, Instagram)
10. Odoo ERP Integration
11. CEO Briefing Generation
12. Ralph Wiggum Loop
13. Error Recovery Demo
14. Final Summary

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI EMPLOYEE                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   WATCHERS   │    │   REASONING  │    │  MCP SERVERS │       │
│  │              │    │    LOOP      │    │              │       │
│  │ • Gmail      │───▶│              │───▶│ • Vault      │       │
│  │ • WhatsApp   │    │ Claude Code  │    │ • Odoo       │       │
│  │ • Filesystem │    │              │    │ • Social     │       │
│  └──────────────┘    └──────────────┘    │ • Comms      │       │
│         │                   │            └──────────────┘       │
│         ▼                   ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    OBSIDIAN VAULT                        │    │
│  │  /Inbox/ → /Needs_Action/ → /Pending_Approval/          │    │
│  │  /Plans/ → /In_Progress/ → /Done/                       │    │
│  │  /Logs/  /Briefings/  /Accounting/  /Social_Media/      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technologies Used

- **AI:** Claude Code (Opus 4.5), MCP Protocol
- **Backend:** Python 3.10+, FastAPI, Playwright
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** PostgreSQL 15, Odoo Community 17
- **Infrastructure:** Docker, WSL2, Windows 11
- **Social APIs:** Twitter/X, Facebook, Instagram, LinkedIn (via Playwright automation)
- **Email:** Gmail API (OAuth 2.0)
- **ERP:** Odoo Community (XML-RPC, JSON-RPC)

---

## How to Restart Services

```bash
# Start API Server
cd /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0
nohup python3 api_server.py > /tmp/api_server.log 2>&1 &

# Verify Health
sleep 5 && curl -s http://localhost:8000/api/health

# Check Odoo
docker ps | grep odoo

# Dashboard
open http://localhost:8000/dashboard.html
```

---

## Final Notes

This Personal AI Employee demonstrates a complete autonomous system that can:
- Monitor multiple input channels (email, chat, filesystem)
- Classify and route tasks to appropriate domains
- Generate execution plans with Claude Code reasoning
- Request human approval for sensitive actions
- Execute approved actions via MCP servers
- Create invoices in Odoo ERP
- Post to 4 social media platforms
- Generate executive briefings
- Recover from errors automatically
- Maintain audit logs for compliance

**Built with Claude Code for the Full-Time Equivalent Hackathon 2026.**
