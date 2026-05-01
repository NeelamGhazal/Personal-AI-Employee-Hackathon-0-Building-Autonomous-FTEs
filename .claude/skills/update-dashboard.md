# Skill: Update Dashboard

## Description
Update the AI Employee Dashboard with current system status, folder counts, and recent activity.

## Trigger
Run this skill after any processing action or when requested.

## Instructions

1. **Gather current stats**
   - Count files in /Inbox
   - Count files in /Needs_Action
   - Count files in /Done (today only)
   - Count files in /Pending_Approval

2. **Update System Status table**
   - File Watcher: Check if watcher process is running
   - Claude Code: Always "Active" when this runs
   - Vault Sync: Check sync status

3. **Update Quick Stats section**
   - Pending Actions: Count of /Needs_Action items
   - Completed Today: Count of items moved to /Done today
   - Awaiting Approval: Count of /Pending_Approval items

4. **Add Recent Activity entries**
   - Add new entries at the top of the list
   - Include timestamp and action description
   - Keep last 10 entries only

5. **Update Folder Overview table**
   - Update item counts for each folder

6. **Set last_updated timestamp**
   - Update frontmatter with current ISO timestamp

## Example Usage
```
/update-dashboard
```

## Output
Confirmation that Dashboard.md has been updated with current stats.
