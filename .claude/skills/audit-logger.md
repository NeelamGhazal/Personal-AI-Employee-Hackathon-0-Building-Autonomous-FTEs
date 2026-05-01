# Skill: Audit Logger

## Description
Comprehensive audit logging for all AI Employee actions. Tracks file operations, communications, social media, accounting, and AI decisions.

## Action Types

### File Operations
- `FILE_READ` - File was read
- `FILE_WRITE` - File was written
- `FILE_MOVE` - File was moved
- `FILE_DELETE` - File was deleted

### Communications
- `EMAIL_RECEIVED` - Email received
- `EMAIL_SENT` - Email sent
- `WHATSAPP_RECEIVED` - WhatsApp message received
- `WHATSAPP_SENT` - WhatsApp message sent

### Social Media
- `SOCIAL_POST_CREATED` - Post drafted
- `SOCIAL_POST_PUBLISHED` - Post published

### Accounting
- `INVOICE_CREATED` - Invoice created in Odoo
- `INVOICE_SENT` - Invoice sent to customer
- `PAYMENT_RECEIVED` - Payment recorded
- `PAYMENT_SENT` - Payment made

### Workflow
- `TASK_CREATED` - New task created
- `TASK_APPROVED` - Task approved by human
- `TASK_REJECTED` - Task rejected
- `TASK_COMPLETED` - Task finished

### AI Actions
- `AI_DECISION` - AI made a decision
- `AI_PLAN_CREATED` - AI created a plan
- `CEO_BRIEFING` - CEO briefing generated

## Usage
```python
from audit_logger import AuditLogger, AuditAction

audit = AuditLogger("/path/to/vault")
audit.log(AuditAction.FILE_WRITE, {'file': 'test.md'})
audit.log_communication('email', 'received', 'client@example.com')
audit.log_social_media('twitter', 'published', 'Tweet content')
audit.log_accounting('invoice_created', 500.00, 'ABC Corp', 'INV-001')
```

## Log Locations
- Session logs: `/Logs/audit/audit_session_*.jsonl`
- Daily logs: `/Logs/audit/audit_YYYYMMDD.jsonl`

## Generate Report
```bash
uv run python src/ai_employee_watchers/audit_logger.py
# Creates: /Logs/AUDIT_REPORT_*.md
```

---
*AI Employee Gold Tier Skill*
