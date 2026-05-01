# Skill: Vault MCP Server

## Description
MCP server providing file operations for the AI Employee Vault. Enables Claude to read, write, list, and move files within the vault structure.

## Available Tools

### vault_read
Read a file from the vault.
```json
{
  "folder": "Needs_Action",
  "filename": "task.md"
}
```

### vault_write
Write a file to the vault.
```json
{
  "folder": "Plans",
  "filename": "PLAN_task.md",
  "content": "# Plan content..."
}
```

### vault_list
List files in a vault folder.
```json
{
  "folder": "Pending_Approval"
}
```

### vault_move
Move a file between folders (for approval workflow).
```json
{
  "source_folder": "Pending_Approval",
  "dest_folder": "Approved",
  "filename": "APPROVAL_task.md"
}
```

## Allowed Folders
- Inbox
- Needs_Action
- Plans
- Pending_Approval
- Approved
- Rejected
- Done
- Logs
- Accounting
- Briefings

## Starting the Server
```bash
cd mcp_servers
node vault_mcp_server.js
```

## Claude Code Configuration
Add to `~/.claude/mcp.json`:
```json
{
  "servers": [
    {
      "name": "vault",
      "command": "node",
      "args": ["/path/to/mcp_servers/vault_mcp_server.js"],
      "env": {
        "VAULT_PATH": "/path/to/AI_Employee_Vault"
      }
    }
  ]
}
```

---
*AI Employee Silver Tier Skill*
