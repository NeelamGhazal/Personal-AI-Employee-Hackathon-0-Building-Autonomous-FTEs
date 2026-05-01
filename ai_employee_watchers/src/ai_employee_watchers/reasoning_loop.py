# reasoning_loop.py - Claude reasoning loop that processes Needs_Action and creates Plan.md files
import logging
import sys
import time
import json
import re
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ReasoningLoop')


class ReasoningLoop:
    """
    Claude's reasoning loop that:
    1. Monitors /Needs_Action for new items
    2. Analyzes each item
    3. Creates Plan.md files with action steps
    4. Creates approval files for sensitive actions
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        for folder in [self.plans, self.pending_approval, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # Load company handbook rules
        self.handbook = self._load_handbook()

        # Track processed files
        self.processed_file = self.vault_path / '.reasoning_processed.json'
        self.processed = self._load_processed()

        # Priority keywords from handbook
        self.priority_keywords = ['urgent', 'asap', 'emergency', 'invoice', 'payment', 'deadline']

        # Actions requiring approval
        self.approval_required = ['send_email', 'make_payment', 'delete_file', 'post_social']

    def _load_handbook(self) -> dict:
        """Load Company Handbook rules"""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        if handbook_path.exists():
            content = handbook_path.read_text()
            return {'content': content, 'loaded': True}
        return {'content': '', 'loaded': False}

    def _load_processed(self) -> set:
        """Load list of already processed files"""
        if self.processed_file.exists():
            try:
                with open(self.processed_file) as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def _save_processed(self):
        """Save processed files list"""
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed), f)

    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse YAML frontmatter from markdown file"""
        frontmatter = {}
        body = content

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm_text = parts[1].strip()
                body = parts[2].strip()

                for line in fm_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()

        return frontmatter, body

    def _determine_priority(self, content: str, frontmatter: dict) -> str:
        """Determine priority based on content and keywords"""
        content_lower = content.lower()

        # Check frontmatter priority
        if frontmatter.get('priority') == 'high':
            return 'high'

        # Check for priority keywords
        for keyword in self.priority_keywords:
            if keyword in content_lower:
                return 'high'

        return 'normal'

    def _determine_action_type(self, content: str, frontmatter: dict) -> str:
        """Determine what type of action is needed"""
        content_lower = content.lower()
        file_type = frontmatter.get('type', 'unknown')

        if file_type == 'email' or 'email' in content_lower:
            return 'email_response'
        elif 'invoice' in content_lower or 'payment' in content_lower:
            return 'invoice_action'
        elif file_type == 'file_drop':
            return 'file_processing'
        elif 'meeting' in content_lower or 'schedule' in content_lower:
            return 'scheduling'
        else:
            return 'general_task'

    def _generate_plan_steps(self, action_type: str, content: str, frontmatter: dict) -> list:
        """Generate action steps based on the task type"""
        steps = []

        if action_type == 'email_response':
            steps = [
                {'step': 'Read and understand the email content', 'auto': True},
                {'step': 'Identify sender and their request', 'auto': True},
                {'step': 'Draft appropriate response', 'auto': True},
                {'step': 'Send email response', 'auto': False, 'approval': 'send_email'},
                {'step': 'Log communication in CRM', 'auto': True},
                {'step': 'Archive original email', 'auto': True}
            ]
        elif action_type == 'invoice_action':
            steps = [
                {'step': 'Extract invoice details (client, amount, date)', 'auto': True},
                {'step': 'Verify client information', 'auto': True},
                {'step': 'Generate invoice document', 'auto': True},
                {'step': 'Send invoice to client', 'auto': False, 'approval': 'send_email'},
                {'step': 'Record in accounting system', 'auto': True},
                {'step': 'Set payment reminder', 'auto': True}
            ]
        elif action_type == 'file_processing':
            steps = [
                {'step': 'Analyze file content and type', 'auto': True},
                {'step': 'Categorize the file', 'auto': True},
                {'step': 'Extract relevant information', 'auto': True},
                {'step': 'Move to appropriate folder', 'auto': True},
                {'step': 'Update dashboard', 'auto': True}
            ]
        elif action_type == 'scheduling':
            steps = [
                {'step': 'Extract meeting details', 'auto': True},
                {'step': 'Check calendar availability', 'auto': True},
                {'step': 'Propose meeting times', 'auto': True},
                {'step': 'Send calendar invite', 'auto': False, 'approval': 'send_email'},
                {'step': 'Confirm with attendees', 'auto': True}
            ]
        else:
            steps = [
                {'step': 'Analyze the request', 'auto': True},
                {'step': 'Identify required actions', 'auto': True},
                {'step': 'Execute appropriate response', 'auto': True},
                {'step': 'Verify completion', 'auto': True},
                {'step': 'Archive task', 'auto': True}
            ]

        return steps

    def _create_plan(self, source_file: Path, content: str, frontmatter: dict) -> Path:
        """Create a Plan.md file for the given task"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        priority = self._determine_priority(content, frontmatter)
        action_type = self._determine_action_type(content, frontmatter)
        steps = self._generate_plan_steps(action_type, content, frontmatter)

        # Generate plan filename
        safe_name = source_file.stem[:30].replace(' ', '_')
        plan_filename = f"PLAN_{timestamp}_{safe_name}.md"
        plan_path = self.plans / plan_filename

        # Check if approval is needed
        needs_approval = any(s.get('approval') for s in steps)
        approval_actions = [s.get('approval') for s in steps if s.get('approval')]

        # Build steps markdown
        steps_md = ""
        for i, step in enumerate(steps, 1):
            checkbox = "[ ]"
            approval_note = f" *(REQUIRES APPROVAL: {step['approval']})*" if step.get('approval') else ""
            steps_md += f"{i}. {checkbox} {step['step']}{approval_note}\n"

        # Create plan content
        plan_content = f'''---
created: {datetime.now().isoformat()}
source_file: {source_file.name}
action_type: {action_type}
priority: {priority}
status: {'pending_approval' if needs_approval else 'ready'}
requires_approval: {needs_approval}
---

# Plan: {action_type.replace('_', ' ').title()}

## Source
- **File**: {source_file.name}
- **Type**: {frontmatter.get('type', 'unknown')}
- **Priority**: {priority}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis
This task has been analyzed and categorized as: **{action_type.replace('_', ' ').title()}**

## Action Steps
{steps_md}
## Approval Requirements
'''

        if needs_approval:
            plan_content += f'''The following actions require human approval before execution:
'''
            for action in approval_actions:
                plan_content += f"- {action.replace('_', ' ').title()}\n"
            plan_content += f'''
Approval file created at: `/Pending_Approval/APPROVAL_{safe_name}.md`
'''
        else:
            plan_content += "No approval required. All steps can be auto-executed.\n"

        plan_content += f'''
## Next Steps
1. Review this plan
2. {'Approve pending actions in /Pending_Approval/' if needs_approval else 'Execute the plan'}
3. Move to /Done when complete

---
*Generated by AI Employee Reasoning Loop*
'''

        plan_path.write_text(plan_content)
        logger.info(f'Created plan: {plan_filename}')

        # Create approval file if needed
        if needs_approval:
            self._create_approval_file(source_file, frontmatter, approval_actions, plan_filename)

        return plan_path

    def _create_approval_file(self, source_file: Path, frontmatter: dict, actions: list, plan_ref: str):
        """Create approval request file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = source_file.stem[:30].replace(' ', '_')
        approval_filename = f"APPROVAL_{timestamp}_{safe_name}.md"
        approval_path = self.pending_approval / approval_filename

        actions_md = "\n".join([f"- {a.replace('_', ' ').title()}" for a in actions])

        approval_content = f'''---
type: approval_request
source_file: {source_file.name}
plan_reference: {plan_ref}
actions_pending: {', '.join(actions)}
created: {datetime.now().isoformat()}
expires: {datetime.now().strftime('%Y-%m-%d')}T23:59:59Z
status: pending
---

# Approval Required

## Summary
The AI Employee requires human approval for the following actions.

## Actions Pending Approval
{actions_md}

## Source Details
- **Original File**: {source_file.name}
- **Plan File**: {plan_ref}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

---
*Generated by AI Employee Reasoning Loop*
'''

        approval_path.write_text(approval_content)
        logger.info(f'Created approval request: {approval_filename}')

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
            'actor': 'reasoning_loop',
            'target': target,
            'result': result,
            'details': details
        })

        with open(log_file, 'w') as f:
            json.dump(entries, f, indent=2)

    def process_item(self, item_path: Path) -> bool:
        """Process a single item from Needs_Action"""
        logger.info(f'Processing: {item_path.name}')

        try:
            content = item_path.read_text()
            frontmatter, body = self._parse_frontmatter(content)

            # Create plan
            plan_path = self._create_plan(item_path, content, frontmatter)

            # Log the action
            self._log_action(
                'create_plan',
                item_path.name,
                'success',
                f'Created plan: {plan_path.name}'
            )

            return True
        except Exception as e:
            logger.error(f'Error processing {item_path.name}: {e}')
            self._log_action('create_plan', item_path.name, 'failed', str(e))
            return False

    def run_once(self):
        """Run one iteration of the reasoning loop"""
        # Get all .md files in Needs_Action
        items = list(self.needs_action.glob('*.md'))

        new_items = [i for i in items if i.name not in self.processed]

        if not new_items:
            logger.info('No new items to process')
            return 0

        processed_count = 0
        for item in new_items:
            if self.process_item(item):
                self.processed.add(item.name)
                processed_count += 1

        self._save_processed()
        logger.info(f'Processed {processed_count} item(s)')
        return processed_count

    def run(self, interval: int = 30):
        """Run continuous reasoning loop"""
        logger.info(f'Starting Reasoning Loop')
        logger.info(f'Vault path: {self.vault_path}')
        logger.info(f'Watching: {self.needs_action}')
        logger.info(f'Plans folder: {self.plans}')
        logger.info(f'Check interval: {interval} seconds')
        logger.info('Press Ctrl+C to stop.')

        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info('Stopping Reasoning Loop...')
            self._save_processed()

        logger.info('Reasoning Loop stopped.')


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'

    # Parse arguments (skip flags starting with --)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    vault_path = Path(args[0]) if args else default_vault

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    loop = ReasoningLoop(str(vault_path))

    # If --once flag, run single iteration
    if '--once' in sys.argv:
        loop.run_once()
    else:
        loop.run()


if __name__ == '__main__':
    main()
