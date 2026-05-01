# Skill: Communications MCP Server

## Description
MCP server for Gmail and WhatsApp integration. Provides tools for checking messages, listing pending communications, and creating drafts.

## Available Tools

### comms_check_gmail
Check Gmail for new messages.
```json
{
  "max_results": 10,
  "unread_only": true
}
```
Returns: List of emails with sender, subject, snippet

### comms_check_whatsapp
Check WhatsApp for recent messages.
```json
{
  "max_results": 10
}
```
Returns: List of chats with sender, message, timestamp

### comms_get_pending
Get all pending communication items from vault.
```json
{
  "domain": "business"
}
```
Returns: Files in /Business/Needs_Action/ or /Personal/Needs_Action/

### comms_create_draft
Create a draft response in /Drafts/.
```json
{
  "type": "email",
  "to": "client@example.com",
  "subject": "Re: Invoice Request",
  "content": "Draft response content..."
}
```

## Starting the Server
```bash
node mcp_servers/comms_mcp_server.cjs
```

## Claude Code Configuration
Add to `~/.claude/mcp.json`:
```json
{
  "servers": [
    {
      "name": "comms",
      "command": "node",
      "args": ["/path/to/mcp_servers/comms_mcp_server.cjs"]
    }
  ]
}
```

## Integration with Watchers
The MCP server works with:
- `gmail_watcher.py` - Polls Gmail API
- `whatsapp_watcher.py` - Uses Playwright automation

## OAuth Setup (Gmail)
Gmail requires OAuth 2.0 credentials:
1. Create project in Google Cloud Console
2. Enable Gmail API
3. Download `credentials.json` to `/credentials/`
4. Run gmail_watcher.py to complete OAuth flow

## WhatsApp Session
WhatsApp uses Playwright with persistent session:
1. Run `whatsapp_watcher.py --test`
2. Scan QR code in browser
3. Session saved to `/credentials/whatsapp_session/`

---
*AI Employee Gold Tier Skill*
