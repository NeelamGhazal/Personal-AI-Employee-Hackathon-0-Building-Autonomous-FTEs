# Skill: Process Inbox

## Description
Process all files in the /Needs_Action folder, categorize them, create appropriate action plans, and update the Dashboard.

## Trigger
Run this skill when there are unprocessed files in /Needs_Action folder.

## Instructions

1. **Read all files in /Needs_Action**
   - List all .md files in `AI_Employee_Vault/Needs_Action/`
   - For each file, read its contents and frontmatter

2. **Categorize each item**
   Based on the file type and content, categorize as:
   - `email` - Email-related actions
   - `file_drop` - Files dropped for processing
   - `invoice` - Invoice requests or payments
   - `communication` - Messages requiring response
   - `task` - General tasks

3. **Determine priority**
   Check for keywords in Company_Handbook.md:
   - `urgent`, `asap`, `emergency` → High priority
   - `invoice`, `payment` → High priority
   - Default → Normal priority

4. **Create action plan**
   For each item, decide:
   - Can be auto-processed → Process immediately
   - Requires human approval → Move to /Pending_Approval
   - Needs more info → Flag for review

5. **Update Dashboard**
   After processing, update `Dashboard.md` with:
   - New activity entries
   - Updated folder counts
   - Current timestamp

6. **Move completed items**
   - Processed items → /Done
   - Pending approval → /Pending_Approval
   - Keep unresolved in /Needs_Action

## Example Usage
```
/process-inbox
```

## Output
Report of actions taken and items processed.
