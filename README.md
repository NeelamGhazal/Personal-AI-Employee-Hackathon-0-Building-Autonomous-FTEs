# Personal AI Employee — Hackathon 0

A fully autonomous AI-powered digital employee that monitors communications, reasons about tasks, executes actions with human approval, and manages business operations across multiple platforms.

## What is this project?

The **Digital Full-Time Equivalent (FTE)** concept reimagines how AI can function as a complete employee rather than just a tool. This project implements an AI system that:

- **Monitors** incoming communications (email, WhatsApp, file drops)
- **Reasons** about what actions to take based on business context
- **Plans** multi-step workflows with human oversight
- **Executes** approved actions across platforms (social media, accounting, communications)
- **Audits** all activities for compliance and review

Unlike traditional automation, this AI Employee operates with understanding, adapting to context from a Company Handbook and Business Goals, just like a human employee would.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PERSONAL AI EMPLOYEE SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Gmail     │  │  WhatsApp   │  │  Filesystem │  │   Manual    │        │
│  │  Watcher    │  │  Watcher    │  │  Watcher    │  │   Input     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┴────────────────┴────────────────┘               │
│                                   │                                         │
│                                   ▼                                         │
│                    ┌──────────────────────────────┐                        │
│                    │         AI_Employee_Vault    │                        │
│                    │  ┌────────┐  ┌────────────┐  │                        │
│                    │  │ Inbox/ │  │ Dashboard  │  │                        │
│                    │  └───┬────┘  └────────────┘  │                        │
│                    │      │                       │                        │
│                    │      ▼                       │                        │
│                    │  ┌─────────────────────┐    │                        │
│                    │  │   Reasoning Loop    │◄───┼── Company_Handbook.md  │
│                    │  │   (Claude AI)       │◄───┼── Business_Goals.md    │
│                    │  └──────────┬──────────┘    │                        │
│                    │             │               │                        │
│                    │             ▼               │                        │
│                    │  ┌──────────────────┐       │                        │
│                    │  │ Pending_Approval │       │                        │
│                    │  └────────┬─────────┘       │                        │
│                    │           │                 │                        │
│                    │     [Human Review]          │                        │
│                    │           │                 │                        │
│                    │           ▼                 │                        │
│                    │  ┌──────────────────┐       │                        │
│                    │  │    Approved/     │       │                        │
│                    │  └────────┬─────────┘       │                        │
│                    │           │                 │                        │
│                    └───────────┼─────────────────┘                        │
│                                │                                           │
│                                ▼                                           │
│         ┌──────────────────────────────────────────────────┐              │
│         │            Approval Orchestrator                  │              │
│         └──────────────────────┬───────────────────────────┘              │
│                                │                                           │
│         ┌──────────┬───────────┼───────────┬───────────┐                  │
│         ▼          ▼           ▼           ▼           ▼                  │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│    │ Twitter │ │Facebook │ │Instagram│ │  Odoo   │ │  Email  │           │
│    │ Poster  │ │ Poster  │ │ Poster  │ │Invoices │ │ Sender  │           │
│    └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                                            │
│    ┌───────────────────────────────────────────────────────────┐          │
│    │                    Audit Logger                            │          │
│    │              (YYYY-MM-DD.jsonl → Logs/)                   │          │
│    └───────────────────────────────────────────────────────────┘          │
│                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Bronze Tier — Foundation

The foundation layer establishes the AI Employee's workspace, monitoring capabilities, and knowledge base.

### What it does
- Creates the Vault folder structure for organizing work
- Monitors an Inbox folder for new files/tasks
- Provides context through Company Handbook and Business Goals
- Defines Agent Skills for repeatable workflows

### Files Created

```
AI_Employee_Vault/
├── Inbox/              # Drop files here for processing
├── Needs_Action/       # Items requiring attention
├── Done/               # Completed items
├── Plans/              # AI-generated action plans
├── Pending_Approval/   # Plans awaiting human review
├── Approved/           # Human-approved actions
├── Logs/               # Audit logs (YYYY-MM-DD.jsonl)
├── Drafts/             # Work in progress
├── Business/
│   └── Social_Media/
│       └── screenshots/
├── Dashboard.md        # Daily status overview
├── Company_Handbook.md # Company policies & procedures
├── Business_Goals.md   # Current objectives & KPIs
└── memory.md           # Project state & history
```

### Agent Skills (in .claude/skills/)
- `process-inbox.md` - Handle incoming items
- `update-dashboard.md` - Refresh daily status
- `create-plan.md` - Generate action plans
- `log-action.md` - Record activities
- `reasoning-loop.md` - Main decision loop
- `approval-orchestrator.md` - Execute approved actions
- `vault-mcp.md` - MCP server operations

### How to Run

```bash
# Navigate to project
cd /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/ai_employee_watchers

# Run filesystem watcher (monitors Inbox for new files)
uv run python src/ai_employee_watchers/filesystem_watcher.py

# The watcher will:
# 1. Detect new files in Inbox/
# 2. Create action files in Needs_Action/
# 3. Log activities to Logs/
```

---

## Silver Tier — Functional Assistant

The functional layer adds real-world integrations, reasoning capabilities, and an approval workflow.

### What it does
- Connects to Gmail API for email monitoring
- Monitors WhatsApp via browser automation
- Runs reasoning loop to analyze tasks and create plans
- Implements human-in-the-loop approval workflow
- Provides MCP server for Claude Desktop integration

### Files Created

```
ai_employee_watchers/src/ai_employee_watchers/
├── gmail_watcher.py          # Gmail API integration
├── whatsapp_watcher.py       # WhatsApp browser automation
├── reasoning_loop.py         # AI reasoning engine
├── approval_orchestrator.py  # Action executor

ai_employee_watchers/mcp_servers/
└── vault_mcp_server.js       # MCP server for Claude Desktop

credentials/
├── gmail_credentials.json    # Gmail OAuth credentials
├── token.json               # Gmail access token (auto-refresh)
└── whatsapp_session/        # WhatsApp browser session
```

### How to Run

#### Gmail Watcher
```bash
# First time: Will open browser for OAuth consent
uv run python src/ai_employee_watchers/gmail_watcher.py

# Subsequent runs: Uses saved token.json
# Monitors inbox for new emails, creates action files
```

#### WhatsApp Watcher
```bash
# Opens browser window for QR code scan
uv run python src/ai_employee_watchers/whatsapp_watcher.py

# Test mode (creates fake action file)
uv run python src/ai_employee_watchers/whatsapp_watcher.py --test

# Session is saved after first login
```

#### Reasoning Loop
```bash
# Run once (process current items)
uv run python src/ai_employee_watchers/reasoning_loop.py --once

# Run continuously
uv run python src/ai_employee_watchers/reasoning_loop.py

# Creates Plan.md files in Plans/ folder
```

#### Approval Orchestrator
```bash
# Run once
uv run python src/ai_employee_watchers/approval_orchestrator.py --once

# Run continuously
uv run python src/ai_employee_watchers/approval_orchestrator.py

# Watches Approved/ folder, executes actions, moves to Done/
```

#### MCP Server
```bash
# Start the MCP server
node mcp_servers/vault_mcp_server.js

# Add to Claude Desktop config (~/.config/claude/claude_desktop_config.json):
{
  "mcpServers": {
    "vault": {
      "command": "node",
      "args": ["/path/to/mcp_servers/vault_mcp_server.js"]
    }
  }
}
```

#### Cron Job Setup
```bash
# Edit crontab
crontab -e

# Add this line (runs every 5 minutes)
*/5 * * * * /path/to/run_ai_employee.sh
```

---

## Gold Tier — Autonomous Employee

The autonomous layer adds cross-platform execution, accounting integration, and comprehensive auditing.

### What it does
- Posts to Twitter/X, Facebook, and Instagram
- Creates invoices in Odoo accounting system
- Generates weekly CEO briefings
- Implements "Ralph Wiggum" creative loop
- Provides comprehensive error recovery
- Maintains detailed audit logs in JSONL format

### Files Created

```
ai_employee_watchers/src/ai_employee_watchers/
├── twitter_poster.py         # Twitter/X posting with stealth mode
├── twitter_manual_post.py    # Manual assisted Twitter posting
├── facebook_poster.py        # Facebook timeline posting
├── instagram_poster.py       # Instagram posting with PIL images
├── audit_logger.py           # JSONL audit logging
├── check_profile.py          # Twitter profile verification
└── [ceo_briefing.py]         # Weekly briefing generator
└── [ralph_wiggum.py]         # Creative content generator
└── [error_handler.py]        # Error recovery system

odoo/
├── docker-compose.yml        # Odoo container config
└── addons/                   # Custom Odoo modules

credentials/
├── twitter_session/          # Twitter browser session
├── facebook_session/         # Facebook browser session
└── instagram_session/        # Instagram browser session
```

### How to Run

#### Odoo Setup (Docker)
```bash
# Navigate to Odoo directory
cd /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/odoo

# Start Odoo containers
docker compose up -d

# Access Odoo at http://localhost:8069
# Database: ai_employee
# Username: admin
# Password: [SET_VIA_ENV_VAR]

# Create invoice via JSON-RPC (see odoo_invoice.py)
```

#### Twitter/X Posting
```bash
# Standard posting (uses stealth mode)
uv run python src/ai_employee_watchers/twitter_poster.py --message "Your tweet here"

# Manual assisted posting (recommended for new accounts)
uv run python src/ai_employee_watchers/twitter_manual_post.py

# Key steps for Twitter success:
# 1. Press Escape 3x to dismiss popups
# 2. Click compose box to focus
# 3. Type character-by-character (150ms delay)
# 4. Verify Post button is enabled
# 5. Use Ctrl+Enter to submit
```

#### Facebook Posting
```bash
# Opens browser, posts to timeline
uv run python src/ai_employee_watchers/facebook_poster.py --message "Your post here"

# First run: Manual login required
# Subsequent runs: Uses saved session
```

#### Instagram Posting
```bash
# Automatically creates 1080x1080 gradient image with text
uv run python src/ai_employee_watchers/instagram_poster.py --message "Your post here"

# Uses PIL/Pillow to generate images
# Handles file upload and caption
```

#### Audit Logger
```bash
# Test the audit logger
uv run python src/ai_employee_watchers/audit_logger.py

# Logs are written to:
# AI_Employee_Vault/Logs/YYYY-MM-DD.jsonl

# Format:
# {"timestamp":"2026-05-01T12:00:00","action_type":"TASK_CREATED","actor":"system","result":"success"}
```

#### Clear Browser Session Locks
```bash
# If browser crashed, clear lock files
rm -f /path/to/credentials/twitter_session/SingletonLock
rm -f /path/to/credentials/facebook_session/SingletonLock
rm -f /path/to/credentials/whatsapp_session/SingletonLock
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop (for Odoo)
- uv (Python package manager)
- Playwright browsers

### Step 1: Clone and Setup Environment
```bash
# Navigate to project
cd /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0

# Install Python dependencies
cd ai_employee_watchers
uv sync

# Install Playwright browsers
uv run playwright install chromium
```

### Step 2: Create Vault Structure
```bash
# The filesystem_watcher will create folders automatically
# Or manually create:
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Done,Plans,Pending_Approval,Approved,Logs,Drafts}
mkdir -p AI_Employee_Vault/Business/Social_Media/screenshots
```

### Step 3: Setup Gmail (Silver Tier)
```bash
# 1. Go to Google Cloud Console
# 2. Create OAuth 2.0 credentials
# 3. Download as gmail_credentials.json
# 4. Place in credentials/ folder
# 5. Run gmail_watcher.py to complete OAuth flow
```

### Step 4: Setup WhatsApp (Silver Tier)
```bash
# Run WhatsApp watcher
uv run python src/ai_employee_watchers/whatsapp_watcher.py

# Scan QR code with WhatsApp mobile app
# Session is saved for future runs
```

### Step 5: Setup Odoo (Gold Tier)
```bash
# Start Docker Desktop first
cd odoo
docker compose up -d

# Wait for Odoo to initialize (~2 minutes)
# Access http://localhost:8069
# Create database: ai_employee
# Set admin password: [SET_VIA_ENV_VAR]
```

### Step 6: Setup Social Media (Gold Tier)
```bash
# For each platform, run the poster once to login:
uv run python src/ai_employee_watchers/twitter_poster.py
uv run python src/ai_employee_watchers/facebook_poster.py
uv run python src/ai_employee_watchers/instagram_poster.py

# Login manually in the browser window
# Sessions are saved for future runs
```

---

## Credentials Required

| Service | File Location | How to Obtain |
|---------|--------------|---------------|
| Gmail OAuth | `credentials/gmail_credentials.json` | Google Cloud Console → APIs → OAuth 2.0 |
| Gmail Token | `credentials/token.json` | Auto-generated on first OAuth flow |
| WhatsApp | `credentials/whatsapp_session/` | QR code scan in browser |
| Twitter/X | `credentials/twitter_session/` | Manual login in Playwright browser |
| Facebook | `credentials/facebook_session/` | Manual login in Playwright browser |
| Instagram | `credentials/instagram_session/` | Manual login in Playwright browser |
| Odoo | Docker container | `admin` / `[SET_VIA_ENV_VAR]` |

---

## Security

### Credential Handling
- All credentials stored locally in `credentials/` folder
- OAuth tokens auto-refresh (Gmail)
- Browser sessions persist in user data directories
- No credentials committed to version control

### Best Practices
- Add `credentials/` to `.gitignore`
- Use environment variables for sensitive data in production
- Regularly rotate OAuth tokens
- Review audit logs for unauthorized access

### Audit Trail
- All actions logged to `Logs/YYYY-MM-DD.jsonl`
- Human approval required before execution
- Screenshots captured for social media posts

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.11 |
| Package Manager | uv |
| Browser Automation | Playwright |
| Image Processing | PIL/Pillow |
| Email | Gmail API (google-auth, google-api-python-client) |
| Accounting | Odoo Community (Docker) |
| MCP Server | Node.js |
| AI/LLM | Claude (Anthropic) |
| Containerization | Docker Compose |
| Scheduling | Cron |

### Key Python Packages
```
playwright
google-auth
google-auth-oauthlib
google-api-python-client
Pillow
watchdog
requests
```

---

## Verified Working Features

| Feature | Status | Evidence |
|---------|--------|----------|
| Filesystem Watcher | WORKING | Creates action files from Inbox |
| Gmail Integration | WORKING | OAuth connected, token saved |
| WhatsApp Monitoring | WORKING | QR scanned, session persisted |
| Reasoning Loop | WORKING | Creates Plan.md files |
| Approval Orchestrator | WORKING | Executes from Approved/ |
| Audit Logging | WORKING | YYYY-MM-DD.jsonl format |
| Twitter Posting | VERIFIED | @ShanayaKhan0907 shows 1 post |
| Facebook Posting | VERIFIED | Posted to timeline |
| Instagram Posting | VERIFIED | Posted with PIL-generated image |
| Odoo Invoicing | VERIFIED | Invoice INV/2026/00001 created |
| MCP Server | WORKING | Node.js server running |

---

## Project Structure

```
Full-Time-Equivalent-0/
├── AI_Employee_Vault/          # Main workspace
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Done/
│   ├── Plans/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Logs/
│   ├── Drafts/
│   ├── Business/Social_Media/screenshots/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   └── memory.md
├── ai_employee_watchers/       # Python package
│   ├── src/ai_employee_watchers/
│   │   ├── filesystem_watcher.py
│   │   ├── gmail_watcher.py
│   │   ├── whatsapp_watcher.py
│   │   ├── reasoning_loop.py
│   │   ├── approval_orchestrator.py
│   │   ├── twitter_poster.py
│   │   ├── facebook_poster.py
│   │   ├── instagram_poster.py
│   │   └── audit_logger.py
│   ├── mcp_servers/
│   │   └── vault_mcp_server.js
│   └── pyproject.toml
├── credentials/                # OAuth & session data
│   ├── gmail_credentials.json
│   ├── token.json
│   ├── whatsapp_session/
│   ├── twitter_session/
│   ├── facebook_session/
│   └── instagram_session/
├── odoo/                       # Odoo Docker setup
│   └── docker-compose.yml
├── .claude/skills/             # Agent skill definitions
└── README.md                   # This file
```

---

## License

This project was created for the Personal AI Employee Hackathon.

---

*Last updated: 2026-05-01*
