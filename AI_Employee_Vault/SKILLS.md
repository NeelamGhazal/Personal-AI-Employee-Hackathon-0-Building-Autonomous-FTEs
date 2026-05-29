# AI Employee Skills Registry

---
version: 2.0
last_updated: 2026-04-22
tier: Silver
---

## Available Skills

### Bronze Tier Skills
| Skill | Description | Location |
|-------|-------------|----------|
| process-inbox | Process files in /Needs_Action | `.claude/skills/process-inbox.md` |
| update-dashboard | Update Dashboard.md stats | `.claude/skills/update-dashboard.md` |
| create-plan | Create task plan | `.claude/skills/create-plan.md` |
| log-action | Log actions to audit trail | `.claude/skills/log-action.md` |

### Silver Tier Skills
| Skill | Description | Location |
|-------|-------------|----------|
| reasoning-loop | Automated reasoning and plan creation | `.claude/skills/reasoning-loop.md` |
| approval-orchestrator | HITL approval workflow execution | `.claude/skills/approval-orchestrator.md` |
| vault-mcp | MCP server for vault operations | `.claude/skills/vault-mcp.md` |

## Skill Capabilities

### Automation Level
| Skill | Auto-Run | Scheduled | Manual |
|-------|----------|-----------|--------|
| reasoning-loop | Yes | Every 5 min | Yes |
| approval-orchestrator | Yes | Every 5 min | Yes |
| vault-mcp | Always on | - | - |

### Approval Requirements
| Skill | Creates Approvals | Processes Approvals |
|-------|-------------------|---------------------|
| reasoning-loop | Yes | No |
| approval-orchestrator | No | Yes |

## Running Skills

### Via Cron (Scheduled)
```bash
# Every 5 minutes via crontab
*/5 * * * * /path/to/scripts/run_ai_employee.sh
```

### Manual Execution
```bash
# Reasoning loop
uv run python src/ai_employee_watchers/reasoning_loop.py --once

# Approval orchestrator
uv run python src/ai_employee_watchers/approval_orchestrator.py --once

# MCP server
node mcp_servers/vault_mcp_server.js
```

## Adding New Skills

1. Create skill file in `.claude/skills/`
2. Follow the skill template structure
3. Add entry to this registry
4. Test the skill
5. Add to cron schedule if automated

---
*AI Employee Skills System - Silver Tier*
