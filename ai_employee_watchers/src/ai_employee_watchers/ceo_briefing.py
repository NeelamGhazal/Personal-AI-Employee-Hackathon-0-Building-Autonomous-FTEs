# ceo_briefing.py - Generates weekly CEO briefing with business and accounting audit
import logging
import sys
import json
import http.client
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CEOBriefing')

# Odoo config
ODOO_CONFIG = {
    'host': 'localhost',
    'port': 8069,
    'database': 'ai_employee',
    'username': 'admin',
    'password': 'admin123'
}


class CEOBriefing:
    """Generates weekly CEO briefing with business and accounting audit"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_path = self.vault_path / 'Briefings'
        self.briefings_path.mkdir(parents=True, exist_ok=True)

        self.social_media_path = self.vault_path / 'Business' / 'Social_Media'
        self.logs_path = self.vault_path / 'Logs'
        self.personal_path = self.vault_path / 'Personal'
        self.business_path = self.vault_path / 'Business'

        self.session_id = None

    def odoo_authenticate(self):
        """Authenticate with Odoo"""
        try:
            conn = http.client.HTTPConnection(ODOO_CONFIG['host'], ODOO_CONFIG['port'])
            payload = json.dumps({
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'db': ODOO_CONFIG['database'],
                    'login': ODOO_CONFIG['username'],
                    'password': ODOO_CONFIG['password']
                },
                'id': 1
            })
            headers = {'Content-Type': 'application/json'}
            conn.request('POST', '/web/session/authenticate', payload, headers)
            response = conn.getresponse()
            data = json.loads(response.read())

            if 'result' in data and data['result'].get('uid'):
                # Extract session cookie
                for header in response.getheaders():
                    if header[0] == 'Set-Cookie':
                        match = header[1].split('session_id=')
                        if len(match) > 1:
                            self.session_id = match[1].split(';')[0]
                return True
            return False
        except Exception as e:
            logger.warning(f'Odoo connection failed: {e}')
            return False

    def odoo_call(self, model, method, args=None, kwargs=None):
        """Call Odoo model method"""
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        try:
            conn = http.client.HTTPConnection(ODOO_CONFIG['host'], ODOO_CONFIG['port'])
            payload = json.dumps({
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'model': model,
                    'method': method,
                    'args': args,
                    'kwargs': kwargs
                },
                'id': 1
            })
            headers = {
                'Content-Type': 'application/json',
                'Cookie': f'session_id={self.session_id}'
            }
            conn.request('POST', '/web/dataset/call_kw', payload, headers)
            response = conn.getresponse()
            data = json.loads(response.read())
            return data.get('result', [])
        except Exception as e:
            logger.warning(f'Odoo call failed: {e}')
            return []

    def get_accounting_summary(self):
        """Get accounting summary from Odoo"""
        if not self.odoo_authenticate():
            return {
                'status': 'disconnected',
                'revenue': 0,
                'expenses': 0,
                'receivable': 0,
                'payable': 0,
                'invoice_count': 0,
                'bill_count': 0
            }

        try:
            # Get invoices
            invoices = self.odoo_call('account.move', 'search_read', [], {
                'domain': [['move_type', '=', 'out_invoice'], ['state', '=', 'posted']],
                'fields': ['amount_total', 'amount_residual']
            })

            # Get bills
            bills = self.odoo_call('account.move', 'search_read', [], {
                'domain': [['move_type', '=', 'in_invoice'], ['state', '=', 'posted']],
                'fields': ['amount_total', 'amount_residual']
            })

            total_revenue = sum(inv.get('amount_total', 0) for inv in invoices)
            total_receivable = sum(inv.get('amount_residual', 0) for inv in invoices)
            total_expenses = sum(bill.get('amount_total', 0) for bill in bills)
            total_payable = sum(bill.get('amount_residual', 0) for bill in bills)

            return {
                'status': 'connected',
                'revenue': total_revenue,
                'expenses': total_expenses,
                'receivable': total_receivable,
                'payable': total_payable,
                'invoice_count': len(invoices),
                'bill_count': len(bills),
                'net_position': total_revenue - total_expenses
            }
        except Exception as e:
            logger.warning(f'Accounting summary failed: {e}')
            return {'status': 'error', 'error': str(e)}

    def get_social_media_summary(self):
        """Get social media activity summary"""
        summary = {'facebook': 0, 'instagram': 0, 'twitter': 0}

        if self.social_media_path.exists():
            for file in self.social_media_path.glob('*.md'):
                name = file.name.upper()
                if name.startswith('FACEBOOK'):
                    summary['facebook'] += 1
                elif name.startswith('INSTAGRAM'):
                    summary['instagram'] += 1
                elif name.startswith('TWITTER'):
                    summary['twitter'] += 1

        summary['total'] = sum(summary.values())
        return summary

    def get_communications_summary(self):
        """Get communications summary"""
        summary = {
            'personal': {'emails': 0, 'whatsapp': 0},
            'business': {'emails': 0, 'whatsapp': 0}
        }

        for domain, path in [('personal', self.personal_path), ('business', self.business_path)]:
            needs_action = path / 'Needs_Action'
            if needs_action.exists():
                for file in needs_action.glob('*.md'):
                    name = file.name.upper()
                    if name.startswith('EMAIL'):
                        summary[domain]['emails'] += 1
                    elif name.startswith('WHATSAPP'):
                        summary[domain]['whatsapp'] += 1

        summary['total'] = (
            summary['personal']['emails'] + summary['personal']['whatsapp'] +
            summary['business']['emails'] + summary['business']['whatsapp']
        )
        return summary

    def get_task_summary(self):
        """Get task completion summary"""
        summary = {'pending': 0, 'approved': 0, 'done': 0, 'rejected': 0}

        folders = {
            'pending': self.vault_path / 'Pending_Approval',
            'approved': self.vault_path / 'Approved',
            'done': self.vault_path / 'Done',
            'rejected': self.vault_path / 'Rejected'
        }

        for status, path in folders.items():
            if path.exists():
                summary[status] = len(list(path.glob('*.md')))

        return summary

    def generate_briefing(self) -> Path:
        """Generate the CEO briefing document"""
        logger.info('Generating CEO Briefing...')

        # Gather all data
        accounting = self.get_accounting_summary()
        social_media = self.get_social_media_summary()
        communications = self.get_communications_summary()
        tasks = self.get_task_summary()

        # Generate briefing
        timestamp = datetime.now()
        week_start = timestamp - timedelta(days=timestamp.weekday())
        week_end = week_start + timedelta(days=6)

        filename = f"CEO_BRIEFING_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.briefings_path / filename

        content = f'''---
type: ceo_briefing
generated_at: {timestamp.isoformat()}
week_start: {week_start.strftime('%Y-%m-%d')}
week_end: {week_end.strftime('%Y-%m-%d')}
---

# CEO Weekly Briefing

**Generated:** {timestamp.strftime('%B %d, %Y at %H:%M')}
**Report Period:** {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}

---

## Executive Summary

This briefing provides a comprehensive overview of your business operations, financial status, and communication activities for the current week.

---

## Financial Overview (Odoo)

| Metric | Value |
|--------|-------|
| Odoo Status | {accounting.get('status', 'unknown').upper()} |
| Total Revenue | ${accounting.get('revenue', 0):,.2f} |
| Total Expenses | ${accounting.get('expenses', 0):,.2f} |
| **Net Position** | **${accounting.get('net_position', 0):,.2f}** |
| Outstanding Receivables | ${accounting.get('receivable', 0):,.2f} |
| Outstanding Payables | ${accounting.get('payable', 0):,.2f} |
| Total Invoices | {accounting.get('invoice_count', 0)} |
| Total Bills | {accounting.get('bill_count', 0)} |

### Financial Health
{'🟢 Healthy - Net positive position' if accounting.get('net_position', 0) > 0 else '🔴 Attention Needed - Net negative position'}

---

## Social Media Activity

| Platform | Posts |
|----------|-------|
| Facebook | {social_media.get('facebook', 0)} |
| Instagram | {social_media.get('instagram', 0)} |
| Twitter/X | {social_media.get('twitter', 0)} |
| **Total** | **{social_media.get('total', 0)}** |

### Social Media Health
{'🟢 Active presence' if social_media.get('total', 0) > 0 else '🟡 No recent activity'}

---

## Communications Overview

### Personal Domain
| Type | Pending |
|------|---------|
| Emails | {communications['personal']['emails']} |
| WhatsApp | {communications['personal']['whatsapp']} |

### Business Domain
| Type | Pending |
|------|---------|
| Emails | {communications['business']['emails']} |
| WhatsApp | {communications['business']['whatsapp']} |

**Total Pending:** {communications.get('total', 0)}

### Communication Health
{'🟢 All caught up' if communications.get('total', 0) == 0 else '🟡 ' + str(communications.get('total', 0)) + ' items need attention'}

---

## Task Pipeline

| Status | Count |
|--------|-------|
| Pending Approval | {tasks['pending']} |
| Approved | {tasks['approved']} |
| Completed | {tasks['done']} |
| Rejected | {tasks['rejected']} |

### Workflow Health
{'🟢 Pipeline clear' if tasks['pending'] == 0 else '🟡 ' + str(tasks['pending']) + ' items awaiting approval'}

---

## Action Items

1. {'Review ' + str(communications.get('total', 0)) + ' pending communications' if communications.get('total', 0) > 0 else '✓ Communications up to date'}
2. {'Approve ' + str(tasks['pending']) + ' pending tasks' if tasks['pending'] > 0 else '✓ No pending approvals'}
3. {'Follow up on $' + f"{accounting.get('receivable', 0):,.2f}" + ' receivables' if accounting.get('receivable', 0) > 0 else '✓ No outstanding receivables'}
4. {'Post social media updates' if social_media.get('total', 0) == 0 else '✓ Social media active'}

---

## Next Week Focus

Based on current metrics, recommended focus areas:
- {'**Financial:** Collect outstanding receivables' if accounting.get('receivable', 0) > 0 else '**Financial:** Maintain current position'}
- {'**Communications:** Clear pending messages' if communications.get('total', 0) > 0 else '**Communications:** Proactive outreach'}
- {'**Social Media:** Increase posting frequency' if social_media.get('total', 0) < 3 else '**Social Media:** Maintain engagement'}

---

*This briefing was automatically generated by AI Employee*
*Gold Tier - CEO Briefing Module*
'''
        filepath.write_text(content)
        logger.info(f'Briefing generated: {filename}')

        # Also log this generation
        log_file = self.logs_path / f'ceo_briefing_{timestamp.strftime("%Y%m%d_%H%M%S")}.log'
        log_file.write_text(f'''[{timestamp.isoformat()}] CEO Briefing Generated
Accounting: {json.dumps(accounting, indent=2)}
Social Media: {json.dumps(social_media, indent=2)}
Communications: {json.dumps(communications, indent=2)}
Tasks: {json.dumps(tasks, indent=2)}
Output: {filepath}
''')

        return filepath


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'

    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    vault_path = Path(args[0]) if len(args) > 0 else default_vault

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    briefing = CEOBriefing(str(vault_path))

    logger.info('')
    logger.info('=' * 60)
    logger.info('CEO BRIEFING GENERATOR')
    logger.info('=' * 60)
    logger.info(f'Vault: {vault_path}')
    logger.info('')

    filepath = briefing.generate_briefing()

    logger.info('')
    logger.info('=' * 60)
    logger.info('BRIEFING COMPLETE')
    logger.info('=' * 60)
    logger.info(f'File: {filepath}')
    logger.info('')
    logger.info('Contents:')
    logger.info('-' * 40)
    print(filepath.read_text())


if __name__ == '__main__':
    main()
