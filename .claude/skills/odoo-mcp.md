# Skill: Odoo MCP Server

## Description
MCP server for Odoo 19 Community accounting integration. Provides tools for managing invoices, partners, products, and generating financial summaries.

## Prerequisites
```bash
# Start Odoo containers
cd /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/odoo
docker compose up -d

# Access Odoo at http://localhost:8069
# Database: ai_employee
# Credentials: admin / admin123
```

## Available Tools

### odoo_authenticate
Authenticate with Odoo server.
```json
{
  "database": "ai_employee",
  "username": "admin",
  "password": "admin123"
}
```

### odoo_list_invoices
List all invoices with optional filters.
```json
{
  "state": "posted",
  "limit": 10
}
```

### odoo_create_invoice
Create a new customer invoice.
```json
{
  "partner_name": "ABC Corp",
  "lines": [
    {"product": "Consulting", "quantity": 10, "price": 150}
  ]
}
```

### odoo_accounting_summary
Get financial summary for CEO briefing.
```json
{}
```
Returns: total_revenue, outstanding_invoices, recent_payments

### odoo_list_partners
List all partners (customers/vendors).
```json
{
  "customer": true
}
```

### odoo_list_products
List all products/services.
```json
{}
```

## Starting the Server
```bash
node mcp_servers/odoo_mcp_server.cjs
```

## Claude Code Configuration
Add to `~/.claude/mcp.json`:
```json
{
  "servers": [
    {
      "name": "odoo",
      "command": "node",
      "args": ["/path/to/mcp_servers/odoo_mcp_server.cjs"]
    }
  ]
}
```

## API Endpoint
- JSON-RPC: `http://localhost:8069/web/dataset/call_kw`
- Authentication: `http://localhost:8069/web/session/authenticate`

---
*AI Employee Gold Tier Skill*
