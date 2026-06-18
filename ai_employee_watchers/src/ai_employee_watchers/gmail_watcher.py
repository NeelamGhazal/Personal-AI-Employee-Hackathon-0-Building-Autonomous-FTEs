# gmail_watcher.py - Monitors Gmail for important/unread emails
import logging
import sys
import time
import os
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime
from email.utils import parsedate_to_datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GmailWatcher')

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher:
    """Watcher for Gmail - monitors for important/unread emails"""

    def __init__(self, vault_path: str, credentials_path: str, token_path: str = None):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path) if token_path else self.credentials_path.parent / 'token.json'
        self.processed_ids_file = self.vault_path / '.gmail_processed_ids.json'
        self.processed_ids = self._load_processed_ids()

        self.service = None
        self.check_interval = 120  # Check every 2 minutes

        # Keywords that indicate high priority
        self.priority_keywords = ['urgent', 'asap', 'important', 'invoice', 'payment', 'deadline']

    def _load_processed_ids(self) -> set:
        """Load previously processed message IDs"""
        if self.processed_ids_file.exists():
            try:
                with open(self.processed_ids_file) as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def _save_processed_ids(self):
        """Save processed message IDs"""
        with open(self.processed_ids_file, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info('Refreshing expired credentials...')
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    logger.error(f'Credentials file not found: {self.credentials_path}')
                    logger.error('Please download OAuth credentials from Google Cloud Console')
                    logger.error('and save as credentials.json')
                    return False

                logger.info('Starting OAuth flow...')
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )

                # Manual OAuth flow for WSL/headless environments
                flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                auth_url, _ = flow.authorization_url(prompt='consent')

                print("\n" + "="*60)
                print("GMAIL AUTHENTICATION REQUIRED")
                print("="*60)
                print("\nStep 1: Copy this URL and open in your Windows browser:")
                print(f"\n{auth_url}\n")
                print("Step 2: Login with your Google account")
                print("Step 3: Click 'Allow' to grant access")
                print("Step 4: Copy the authorization code shown")
                print("="*60)

                auth_code = input("\nPaste the authorization code here: ").strip()
                flow.fetch_token(code=auth_code)
                creds = flow.credentials

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            logger.info(f'Credentials saved to {self.token_path}')

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info('Gmail API authenticated successfully')
        return True

    def check_for_updates(self) -> list:
        """Check for new unread/important emails"""
        try:
            # Query for unread emails, prioritizing important ones
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            new_messages = []

            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)

            return new_messages
        except Exception as e:
            logger.error(f'Error checking Gmail: {e}')
            return []

    def get_message_details(self, message_id: str) -> dict:
        """Get full message details"""
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {}
            for header in msg['payload'].get('headers', []):
                headers[header['name'].lower()] = header['value']

            # Get snippet/body
            snippet = msg.get('snippet', '')

            # Determine priority based on keywords and labels
            labels = msg.get('labelIds', [])
            is_important = 'IMPORTANT' in labels

            subject_lower = headers.get('subject', '').lower()
            snippet_lower = snippet.lower()
            has_priority_keyword = any(
                kw in subject_lower or kw in snippet_lower
                for kw in self.priority_keywords
            )

            priority = 'high' if (is_important or has_priority_keyword) else 'normal'

            return {
                'id': message_id,
                'from': headers.get('from', 'Unknown'),
                'to': headers.get('to', ''),
                'subject': headers.get('subject', 'No Subject'),
                'date': headers.get('date', ''),
                'snippet': snippet,
                'labels': labels,
                'priority': priority
            }
        except Exception as e:
            logger.error(f'Error getting message {message_id}: {e}')
            return None

    def create_action_file(self, message: dict) -> Path:
        """Create action file for an email"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = ''.join(c if c.isalnum() or c in ' -_' else '' for c in message['subject'])[:30]
        safe_subject = safe_subject.replace(' ', '_')

        filename = f"EMAIL_{timestamp}_{safe_subject}.md"
        filepath = self.needs_action / filename

        content = f'''---
type: email
message_id: {message['id']}
from: {message['from']}
to: {message['to']}
subject: {message['subject']}
received: {message['date']}
detected_at: {datetime.now().isoformat()}
priority: {message['priority']}
status: pending
labels: {', '.join(message['labels'])}
---

# Email: {message['subject']}

## From
{message['from']}

## Preview
{message['snippet']}

## Suggested Actions
- [ ] Read full email
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

---
*Generated by GmailWatcher*
'''
        filepath.write_text(content)
        logger.info(f'Created action file: {filename}')
        return filepath

    def run(self):
        """Main run loop"""
        if not self.authenticate():
            logger.error('Authentication failed. Exiting.')
            return

        logger.info(f'Starting Gmail Watcher')
        logger.info(f'Vault path: {self.vault_path}')
        logger.info(f'Check interval: {self.check_interval} seconds')
        logger.info('Watcher is now running. Press Ctrl+C to stop.')

        try:
            while True:
                messages = self.check_for_updates()

                for msg in messages:
                    details = self.get_message_details(msg['id'])
                    if details:
                        self.create_action_file(details)
                        self.processed_ids.add(msg['id'])

                if messages:
                    self._save_processed_ids()
                    logger.info(f'Processed {len(messages)} new email(s)')

                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info('Stopping Gmail Watcher...')
            self._save_processed_ids()

        logger.info('Gmail Watcher stopped.')

    def run_once(self):
        """Single check mode - check once and exit immediately"""
        start_time = time.time()

        if not self.authenticate():
            logger.error('Authentication failed.')
            return False

        logger.info('Running Gmail check (once mode)...')
        messages = self.check_for_updates()

        if messages:
            for msg in messages:
                details = self.get_message_details(msg['id'])
                if details:
                    self.create_action_file(details)
                    self.processed_ids.add(msg['id'])
            self._save_processed_ids()
            logger.info(f'Processed {len(messages)} new email(s)')
        else:
            logger.info('No new unread emails found')

        elapsed = time.time() - start_time
        logger.info(f'Gmail check completed in {elapsed:.2f} seconds')
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Gmail Watcher - Monitor for important emails')
    parser.add_argument('--once', action='store_true', help='Check once and exit immediately')
    parser.add_argument('--vault', type=str, help='Path to AI Employee Vault')
    parser.add_argument('--credentials', type=str, help='Path to Gmail credentials JSON')
    args = parser.parse_args()

    # Default paths
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    default_creds = Path(__file__).parent.parent.parent.parent / 'credentials' / 'gmail_credentials.json'

    vault_path = Path(args.vault) if args.vault else default_vault
    creds_path = Path(args.credentials) if args.credentials else default_creds

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    watcher = GmailWatcher(str(vault_path), str(creds_path))

    if args.once:
        # Single check mode - fast execution for demos
        success = watcher.run_once()
        sys.exit(0 if success else 1)
    else:
        # Continuous monitoring mode
        watcher.run()


if __name__ == '__main__':
    main()
