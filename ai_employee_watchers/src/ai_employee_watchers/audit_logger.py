# audit_logger.py - Comprehensive audit logging for AI Employee
import logging
import json
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AuditLogger')


class AuditAction(Enum):
    # File operations
    FILE_READ = 'file_read'
    FILE_WRITE = 'file_write'
    FILE_MOVE = 'file_move'
    FILE_DELETE = 'file_delete'

    # Communication actions
    EMAIL_RECEIVED = 'email_received'
    EMAIL_SENT = 'email_sent'
    WHATSAPP_RECEIVED = 'whatsapp_received'
    WHATSAPP_SENT = 'whatsapp_sent'

    # Social media actions
    SOCIAL_POST_CREATED = 'social_post_created'
    SOCIAL_POST_PUBLISHED = 'social_post_published'

    # Accounting actions
    INVOICE_CREATED = 'invoice_created'
    INVOICE_SENT = 'invoice_sent'
    PAYMENT_RECEIVED = 'payment_received'
    PAYMENT_SENT = 'payment_sent'

    # Workflow actions
    TASK_CREATED = 'task_created'
    TASK_APPROVED = 'task_approved'
    TASK_REJECTED = 'task_rejected'
    TASK_COMPLETED = 'task_completed'

    # System actions
    SYSTEM_START = 'system_start'
    SYSTEM_STOP = 'system_stop'
    ERROR_OCCURRED = 'error_occurred'
    AUTHENTICATION = 'authentication'

    # AI actions
    AI_DECISION = 'ai_decision'
    AI_PLAN_CREATED = 'ai_plan_created'
    CEO_BRIEFING = 'ceo_briefing'


class AuditLogger:
    """Comprehensive audit logging system"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / 'Logs'
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Session ID for tracking
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Daily audit file - direct in Logs/ folder with YYYY-MM-DD.jsonl format
        self.daily_file = self.logs_path / f'{datetime.now().strftime("%Y-%m-%d")}.jsonl'

    def log(self, action: AuditAction, details: Dict[str, Any],
            user: str = 'ai_employee', success: bool = True,
            metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log an audit entry"""

        entry_id = f"AUD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(details)}"

        # Simple JSON format for .jsonl file
        simple_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'action_type': action.value,
            'actor': user,
            'result': 'success' if success else 'failure'
        }

        # Write to daily file in simple format
        with open(self.daily_file, 'a') as f:
            f.write(json.dumps(simple_entry) + '\n')

        # Also log to standard logger
        status = '✓' if success else '✗'
        logger.info(f'[AUDIT] {status} {action.value}: {json.dumps(details)[:100]}')

        return entry_id

    def log_file_operation(self, operation: str, file_path: str,
                          success: bool = True, error: str = None):
        """Log file operation"""
        action_map = {
            'read': AuditAction.FILE_READ,
            'write': AuditAction.FILE_WRITE,
            'move': AuditAction.FILE_MOVE,
            'delete': AuditAction.FILE_DELETE
        }
        action = action_map.get(operation, AuditAction.FILE_READ)

        return self.log(action, {
            'operation': operation,
            'file_path': str(file_path),
            'error': error
        }, success=success)

    def log_communication(self, comm_type: str, direction: str,
                         contact: str, subject: str = None,
                         success: bool = True):
        """Log communication action"""
        if comm_type == 'email':
            action = AuditAction.EMAIL_SENT if direction == 'sent' else AuditAction.EMAIL_RECEIVED
        else:
            action = AuditAction.WHATSAPP_SENT if direction == 'sent' else AuditAction.WHATSAPP_RECEIVED

        return self.log(action, {
            'type': comm_type,
            'direction': direction,
            'contact': contact,
            'subject': subject
        }, success=success)

    def log_social_media(self, platform: str, action_type: str,
                        content: str = None, success: bool = True):
        """Log social media action"""
        action = AuditAction.SOCIAL_POST_PUBLISHED if action_type == 'published' else AuditAction.SOCIAL_POST_CREATED

        return self.log(action, {
            'platform': platform,
            'action_type': action_type,
            'content_preview': content[:100] if content else None
        }, success=success)

    def log_accounting(self, action_type: str, amount: float = None,
                      partner: str = None, reference: str = None,
                      success: bool = True):
        """Log accounting action"""
        action_map = {
            'invoice_created': AuditAction.INVOICE_CREATED,
            'invoice_sent': AuditAction.INVOICE_SENT,
            'payment_received': AuditAction.PAYMENT_RECEIVED,
            'payment_sent': AuditAction.PAYMENT_SENT
        }
        action = action_map.get(action_type, AuditAction.INVOICE_CREATED)

        return self.log(action, {
            'action_type': action_type,
            'amount': amount,
            'partner': partner,
            'reference': reference
        }, success=success)

    def log_workflow(self, action_type: str, task_id: str,
                    task_type: str = None, success: bool = True):
        """Log workflow action"""
        action_map = {
            'created': AuditAction.TASK_CREATED,
            'approved': AuditAction.TASK_APPROVED,
            'rejected': AuditAction.TASK_REJECTED,
            'completed': AuditAction.TASK_COMPLETED
        }
        action = action_map.get(action_type, AuditAction.TASK_CREATED)

        return self.log(action, {
            'action_type': action_type,
            'task_id': task_id,
            'task_type': task_type
        }, success=success)

    def log_ai_action(self, action_type: str, decision: str = None,
                     context: str = None, success: bool = True):
        """Log AI decision or action"""
        action_map = {
            'decision': AuditAction.AI_DECISION,
            'plan': AuditAction.AI_PLAN_CREATED,
            'briefing': AuditAction.CEO_BRIEFING
        }
        action = action_map.get(action_type, AuditAction.AI_DECISION)

        return self.log(action, {
            'action_type': action_type,
            'decision': decision,
            'context': context
        }, success=success)

    def log_error(self, error: Exception, context: str):
        """Log error occurrence"""
        return self.log(AuditAction.ERROR_OCCURRED, {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }, success=False)

    def get_session_logs(self) -> list:
        """Get all logs from current day"""
        return self.get_daily_logs()

    def get_daily_logs(self, date: str = None) -> list:
        """Get all logs for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        daily_file = self.logs_path / f'{date}.jsonl'
        logs = []

        if daily_file.exists():
            with open(daily_file) as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
        return logs

    def generate_audit_report(self) -> Path:
        """Generate audit report for current day"""
        logs = self.get_daily_logs()

        # Analyze logs
        action_counts = {}
        success_count = 0
        failure_count = 0

        for log in logs:
            action = log.get('action_type', 'unknown')
            action_counts[action] = action_counts.get(action, 0) + 1

            if log.get('result') == 'success':
                success_count += 1
            else:
                failure_count += 1

        # Generate report
        timestamp = datetime.now()
        filename = f"AUDIT_REPORT_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.logs_path / filename

        content = f'''---
type: audit_report
generated_at: {timestamp.isoformat()}
date: {timestamp.strftime('%Y-%m-%d')}
---

# Audit Report

**Generated:** {timestamp.strftime('%B %d, %Y at %H:%M')}
**Total Entries:** {len(logs)}

## Summary

| Metric | Count |
|--------|-------|
| Total Actions | {len(logs)} |
| Successful | {success_count} |
| Failed | {failure_count} |
| Success Rate | {(success_count/len(logs)*100) if logs else 0:.1f}% |

## Actions by Type

| Action | Count |
|--------|-------|
'''
        for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
            content += f'| {action} | {count} |\n'

        content += f'''

## Recent Entries (Last 10)

'''
        for log in logs[-10:]:
            status = '✓' if log.get('result') == 'success' else '✗'
            content += f"- [{log.get('timestamp', '')}] {status} {log.get('action_type', '')} by {log.get('actor', '')}\n"

        content += '''

---
*Generated by AuditLogger*
'''
        filepath.write_text(content)
        return filepath


# Decorator for automatic audit logging
def audit_logged(action: AuditAction, get_details=None):
    """Decorator to automatically log function calls"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find vault_path
            vault_path = kwargs.get('vault_path')
            if vault_path is None and args and hasattr(args[0], 'vault_path'):
                vault_path = str(args[0].vault_path)

            if vault_path is None:
                vault_path = '/tmp/audit'

            audit = AuditLogger(vault_path)

            try:
                result = func(*args, **kwargs)

                # Get details
                details = {}
                if get_details:
                    details = get_details(result, *args, **kwargs)
                else:
                    details = {'function': func.__name__, 'result_type': type(result).__name__}

                audit.log(action, details, success=True)
                return result

            except Exception as e:
                audit.log(action, {
                    'function': func.__name__,
                    'error': str(e)
                }, success=False)
                raise

        return wrapper
    return decorator


def main():
    """Test audit logging"""
    import sys

    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    audit = AuditLogger(str(default_vault))

    print("=" * 60)
    print("AUDIT LOGGER TEST")
    print("=" * 60)

    # Log various actions with different actors
    audit.log(AuditAction.SYSTEM_START, {'component': 'audit_logger'}, user='system')
    audit.log(AuditAction.EMAIL_RECEIVED, {'from': 'client@example.com'}, user='gmail_watcher')
    audit.log(AuditAction.WHATSAPP_RECEIVED, {'from': '+1234567890'}, user='whatsapp_watcher')
    audit.log(AuditAction.FILE_WRITE, {'path': '/Inbox/task.md'}, user='filesystem_watcher')
    audit.log(AuditAction.AI_DECISION, {'decision': 'approve'}, user='reasoning_loop')
    audit.log(AuditAction.TASK_APPROVED, {'task': 'TASK_001'}, user='approval_orchestrator')
    audit.log(AuditAction.SOCIAL_POST_PUBLISHED, {'platform': 'twitter'}, user='twitter_poster')

    print(f"✓ Logged {7} actions to: {audit.daily_file}")

    # Generate report
    report_path = audit.generate_audit_report()
    print(f"✓ Generated report: {report_path}")

    print("")
    print("Daily logs:")
    print("-" * 40)
    for log in audit.get_daily_logs()[-7:]:
        print(f"  {log}")

    print("=" * 60)
    print("AUDIT LOGGER TEST COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
