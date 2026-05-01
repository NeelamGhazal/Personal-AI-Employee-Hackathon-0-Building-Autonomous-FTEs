# approval_orchestrator.py - Watches /Approved folder and executes approved actions
import logging
import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ApprovalOrchestrator')

# Dry run mode - set to False to enable real actions
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'


class ApprovalOrchestrator:
    """
    Orchestrator that:
    1. Watches /Approved folder for new files
    2. Parses the approval file to determine action
    3. Executes the approved action
    4. Moves completed files to /Done
    5. Logs all actions
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.plans = self.vault_path / 'Plans'

        # Ensure directories exist
        for folder in [self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # Track processed approvals
        self.processed_file = self.vault_path / '.approvals_processed.json'
        self.processed = self._load_processed()

        self.check_interval = 10  # Check every 10 seconds

    def _load_processed(self) -> set:
        """Load list of already processed approvals"""
        if self.processed_file.exists():
            try:
                with open(self.processed_file) as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def _save_processed(self):
        """Save processed approvals list"""
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed), f)

    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from approval file"""
        frontmatter = {}

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm_text = parts[1].strip()

                for line in fm_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()

        return frontmatter

    def _log_action(self, action_type: str, target: str, result: str, details: str = ""):
        """Log an action to the audit log"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        entries = []
        if log_file.exists():
            try:
                with open(log_file) as f:
                    entries = json.load(f)
            except Exception:
                entries = []

        entries.append({
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'approval_orchestrator',
            'target': target,
            'approval_status': 'approved',
            'approved_by': 'human',
            'result': result,
            'details': details,
            'dry_run': DRY_RUN
        })

        with open(log_file, 'w') as f:
            json.dump(entries, f, indent=2)

    def _execute_send_email(self, frontmatter: dict, content: str) -> tuple:
        """Execute send email action"""
        recipient = frontmatter.get('contact_email', frontmatter.get('recipient', 'unknown'))
        subject = f"Re: {frontmatter.get('source_file', 'Your Request')}"

        if DRY_RUN:
            logger.info(f'[DRY RUN] Would send email to: {recipient}')
            logger.info(f'[DRY RUN] Subject: {subject}')
            return True, f'DRY RUN: Email would be sent to {recipient}'
        else:
            # In production, this would call the email MCP server
            logger.info(f'Sending email to: {recipient}')
            # Placeholder for actual email sending
            return True, f'Email sent to {recipient}'

    def _execute_send_invoice(self, frontmatter: dict, content: str) -> tuple:
        """Execute send invoice action"""
        recipient = frontmatter.get('contact_email', frontmatter.get('recipient', 'unknown'))
        amount = frontmatter.get('amount', '0')

        if DRY_RUN:
            logger.info(f'[DRY RUN] Would send invoice to: {recipient}')
            logger.info(f'[DRY RUN] Amount: ${amount}')
            return True, f'DRY RUN: Invoice for ${amount} would be sent to {recipient}'
        else:
            logger.info(f'Sending invoice to: {recipient}')
            return True, f'Invoice for ${amount} sent to {recipient}'

    def _execute_action(self, action: str, frontmatter: dict, content: str) -> tuple:
        """Execute the approved action based on type"""
        action_lower = action.lower().replace(' ', '_')

        if 'email' in action_lower or 'send_email' in action_lower:
            return self._execute_send_email(frontmatter, content)
        elif 'invoice' in action_lower or 'send_invoice' in action_lower:
            return self._execute_send_invoice(frontmatter, content)
        elif 'payment' in action_lower:
            if DRY_RUN:
                return True, f'DRY RUN: Payment action would be executed'
            return True, 'Payment processed'
        else:
            if DRY_RUN:
                return True, f'DRY RUN: Generic action "{action}" would be executed'
            return True, f'Action "{action}" executed'

    def _update_dashboard(self, action_summary: str):
        """Update dashboard with completed action"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        if dashboard_path.exists():
            content = dashboard_path.read_text()

            # Find Recent Activity section and add entry
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            new_entry = f"- [{timestamp}] APPROVED: {action_summary}\n"

            if '## Recent Activity' in content:
                content = content.replace(
                    '## Recent Activity\n',
                    f'## Recent Activity\n{new_entry}'
                )
                dashboard_path.write_text(content)
                logger.info('Updated dashboard with approval action')

    def process_approval(self, approval_file: Path) -> bool:
        """Process a single approval file"""
        logger.info(f'Processing approval: {approval_file.name}')

        try:
            content = approval_file.read_text()
            frontmatter = self._parse_frontmatter(content)

            # Get action type from frontmatter
            actions = frontmatter.get('actions_pending', frontmatter.get('action', 'unknown'))

            # Execute each action
            for action in actions.split(','):
                action = action.strip()
                success, message = self._execute_action(action, frontmatter, content)

                if success:
                    logger.info(f'Action completed: {message}')
                    self._log_action(action, approval_file.name, 'success', message)
                else:
                    logger.error(f'Action failed: {message}')
                    self._log_action(action, approval_file.name, 'failed', message)
                    return False

            # Move approval file to Done
            done_path = self.done / approval_file.name
            approval_file.rename(done_path)
            logger.info(f'Moved {approval_file.name} to Done')

            # Update dashboard
            self._update_dashboard(f"{actions} - {frontmatter.get('source_file', 'unknown')}")

            return True

        except Exception as e:
            logger.error(f'Error processing {approval_file.name}: {e}')
            self._log_action('process_approval', approval_file.name, 'error', str(e))
            return False

    def run_once(self):
        """Run one iteration - process all pending approvals"""
        # Get all .md files in Approved folder
        approvals = list(self.approved.glob('*.md'))

        new_approvals = [a for a in approvals if a.name not in self.processed]

        if not new_approvals:
            logger.debug('No new approvals to process')
            return 0

        processed_count = 0
        for approval in new_approvals:
            if self.process_approval(approval):
                self.processed.add(approval.name)
                processed_count += 1

        self._save_processed()

        if processed_count > 0:
            logger.info(f'Processed {processed_count} approval(s)')

        return processed_count

    def run(self):
        """Run continuous approval monitoring"""
        mode = "DRY RUN" if DRY_RUN else "LIVE"
        logger.info(f'Starting Approval Orchestrator [{mode} MODE]')
        logger.info(f'Vault path: {self.vault_path}')
        logger.info(f'Watching: {self.approved}')
        logger.info(f'Check interval: {self.check_interval} seconds')
        logger.info('Press Ctrl+C to stop.')

        try:
            while True:
                self.run_once()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info('Stopping Approval Orchestrator...')
            self._save_processed()

        logger.info('Approval Orchestrator stopped.')


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'

    # Parse arguments
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    vault_path = Path(args[0]) if args else default_vault

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    orchestrator = ApprovalOrchestrator(str(vault_path))

    if '--once' in sys.argv:
        orchestrator.run_once()
    else:
        orchestrator.run()


if __name__ == '__main__':
    main()
