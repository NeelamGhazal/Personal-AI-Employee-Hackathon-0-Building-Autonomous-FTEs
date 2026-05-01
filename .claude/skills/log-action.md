# Skill: Log Action

## Description
Log all AI Employee actions to the audit log for compliance and review.

## Trigger
Run automatically after every action taken by the AI Employee.

## Arguments
- `action_type`: Type of action (e.g., file_read, file_write, email_draft, plan_created)
- `target`: The target of the action (file path, email address, etc.)
- `result`: success | failed | pending_approval
- `details`: Additional context about the action

## Instructions

1. **Determine log file**
   - Use format: `/Logs/YYYY-MM-DD.json`
   - Create file if it doesn't exist

2. **Create log entry**
   ```json
   {
     "timestamp": "<ISO timestamp>",
     "action_type": "<action_type>",
     "actor": "claude_code",
     "target": "<target>",
     "parameters": {},
     "approval_status": "auto | approved | pending",
     "approved_by": "system | human",
     "result": "<result>",
     "details": "<details>"
   }
   ```

3. **Append to log file**
   - Read existing entries if file exists
   - Append new entry
   - Write back to file

4. **Retention policy**
   - Logs retained for minimum 90 days
   - Older logs can be archived to /Logs/archive/

## Example Usage
```
/log-action file_write AI_Employee_Vault/Dashboard.md success "Updated dashboard stats"
```

## Output
Confirmation that action has been logged.
