# Skill: Approval Orchestrator

## Description
Monitor /Approved folder and execute actions when files are moved there by human approval.

## Trigger
Run continuously or on schedule to process approved actions.

## Instructions

1. **Watch /Approved folder**
   - Scan for new .md files
   - Skip already-processed files

2. **Parse approval file**
   - Extract frontmatter (action type, recipient, amount, etc.)
   - Identify actions to execute

3. **Execute approved actions**
   Based on action type:
   - `send_email`: Send email via MCP server
   - `send_invoice`: Generate and send invoice
   - `make_payment`: Process payment (requires additional verification)

4. **Handle dry-run mode**
   - If DRY_RUN=true, log what would happen without executing
   - Useful for testing

5. **Complete workflow**
   - Move processed file to /Done
   - Update Dashboard.md with completion
   - Log action with approval_status: "approved", approved_by: "human"

## Example Usage
```bash
# Run once
uv run python src/ai_employee_watchers/approval_orchestrator.py --once

# Run continuously
uv run python src/ai_employee_watchers/approval_orchestrator.py

# Live mode (execute real actions)
DRY_RUN=false uv run python src/ai_employee_watchers/approval_orchestrator.py
```

## Human-in-the-Loop Flow
1. AI creates APPROVAL_*.md in /Pending_Approval/
2. Human reviews and moves to /Approved/
3. Orchestrator detects and executes
4. File moves to /Done/

---
*AI Employee Silver Tier Skill*
