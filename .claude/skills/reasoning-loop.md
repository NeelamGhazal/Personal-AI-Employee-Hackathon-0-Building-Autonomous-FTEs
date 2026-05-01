# Skill: Reasoning Loop

## Description
Process all items in /Needs_Action folder, analyze them, and create structured Plan.md files with action steps.

## Trigger
Run this skill when there are unprocessed files in /Needs_Action or on a schedule (every 5 minutes via cron).

## Instructions

1. **Scan /Needs_Action folder**
   - Find all .md files not yet processed
   - Read each file's content and frontmatter

2. **Analyze each item**
   - Parse frontmatter for type, priority, source
   - Check content for priority keywords (urgent, asap, invoice, payment)
   - Determine action type (email_response, invoice_action, file_processing, scheduling)

3. **Generate action plan**
   For each item, create a Plan.md in /Plans/ with:
   - Source file reference
   - Priority level (high/normal)
   - Step-by-step action items
   - Approval requirements for sensitive actions

4. **Create approval files**
   If any step requires human approval:
   - Create APPROVAL_*.md in /Pending_Approval/
   - Include action details and instructions

5. **Log all actions**
   - Write to /Logs/YYYY-MM-DD.json

## Example Usage
```bash
# Run once
uv run python src/ai_employee_watchers/reasoning_loop.py --once

# Run continuously
uv run python src/ai_employee_watchers/reasoning_loop.py
```

## Output
- Plan.md files created in /Plans/
- Approval files in /Pending_Approval/ (if needed)
- Audit log entries

---
*AI Employee Silver Tier Skill*
