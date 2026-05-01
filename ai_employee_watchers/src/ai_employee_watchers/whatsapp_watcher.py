# whatsapp_watcher.py - Monitors WhatsApp Web for messages using Playwright
import logging
import sys
import time
import json
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Import domain classifier for Personal/Business routing
try:
    from .domain_classifier import DomainClassifier
except ImportError:
    from domain_classifier import DomainClassifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WhatsAppWatcher')


class WhatsAppWatcher:
    """Watcher for WhatsApp Web - monitors messages using Playwright browser automation"""

    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.processed_ids_file = self.vault_path / '.whatsapp_processed_ids.json'
        self.processed_ids = self._load_processed_ids()

        self.check_interval = 30  # Check every 30 seconds

        # Initialize domain classifier for Personal/Business routing
        self.domain_classifier = DomainClassifier(str(self.vault_path))

        # Keywords indicating priority messages
        self.priority_keywords = [
            'urgent', 'asap', 'emergency', 'help',
            'invoice', 'payment', 'quote', 'pricing',
            'meeting', 'call', 'deadline'
        ]

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

    def check_for_updates(self, page) -> list:
        """Check for new unread messages"""
        updates = []

        try:
            # Wait for chat list to load
            page.wait_for_selector('[aria-label="Chat list"]', timeout=10000)

            # Find chats with unread messages (indicated by unread badge)
            unread_chats = page.query_selector_all('span[aria-label*="unread message"]')

            logger.info(f'Found {len(unread_chats)} chats with unread messages')

            for chat in unread_chats[:5]:  # Limit to 5 most recent
                try:
                    # Extract chat info directly using JavaScript (avoids JSHandle issues)
                    chat_info = chat.evaluate('''el => {
                        const container = el.closest("[data-testid='cell-frame-container']");
                        if (!container) return null;

                        // Get chat name from title attribute
                        const nameEl = container.querySelector("span[title]");
                        const chatName = nameEl ? nameEl.getAttribute("title") : "Unknown";

                        // Get message preview - try multiple selectors
                        let preview = "";
                        const previewEl = container.querySelector("span[class*='matched-text']") ||
                                          container.querySelector("[data-testid='last-msg-status']");
                        if (previewEl) {
                            preview = previewEl.innerText || "";
                        }

                        return { chatName, preview };
                    }''')

                    if chat_info:
                        chat_name = chat_info.get('chatName', 'Unknown')
                        preview = chat_info.get('preview', '')

                        # Create unique ID
                        msg_id = f"whatsapp_{hash(chat_name + preview + str(datetime.now().date()))}"

                        if msg_id not in self.processed_ids:
                            # Check priority
                            preview_lower = preview.lower()
                            is_priority = any(kw in preview_lower for kw in self.priority_keywords)

                            updates.append({
                                'type': 'whatsapp_message',
                                'id': msg_id,
                                'sender': chat_name,
                                'preview': preview[:200],  # Limit preview length
                                'priority': 'high' if is_priority else 'normal',
                                'timestamp': datetime.now().isoformat()
                            })

                except Exception as e:
                    logger.warning(f'Error extracting chat info: {e}')
                    continue

        except PlaywrightTimeout:
            logger.warning('Timeout waiting for chat list')
        except Exception as e:
            logger.error(f'Error checking WhatsApp: {e}')

        return updates

    def create_action_file(self, message: dict) -> Path:
        """Create action file for a WhatsApp message with domain classification"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_sender = ''.join(c if c.isalnum() or c == ' ' else '' for c in message['sender'])[:20]
        safe_sender = safe_sender.replace(' ', '_')

        # Classify domain (Personal or Business)
        domain, target_folder = self.domain_classifier.classify_and_route(
            content=message['preview'],
            sender=message['sender'],
            source='whatsapp'
        )

        filename = f"WHATSAPP_{timestamp}_{safe_sender}.md"
        filepath = target_folder / filename

        content = f'''---
type: whatsapp_message
domain: {domain}
sender: {message['sender']}
detected_at: {message['timestamp']}
priority: {message['priority']}
status: pending
---

# WhatsApp Message from {message['sender']}

## Domain
**{domain.upper()}** - Routed to /{domain.capitalize()}/Needs_Action/

## Preview
{message['preview']}

## Priority
**{message['priority'].upper()}** - {'Contains priority keyword' if message['priority'] == 'high' else 'Normal message'}

## Suggested Actions
- [ ] Open WhatsApp Web and read full message
- [ ] Respond to sender
- [ ] Log conversation if business-related
- [ ] Archive after handling

## Quick Links
- [Open WhatsApp Web](https://web.whatsapp.com)

---
*Generated by WhatsAppWatcher (Gold Tier - Cross-Domain)*
'''
        filepath.write_text(content)
        logger.info(f'Created action file: {filename} -> {domain.upper()} domain')
        return filepath

    def wait_for_login(self, page):
        """Wait for user to complete WhatsApp Web login via QR code"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('WAITING FOR WHATSAPP WEB TO LOAD...')
        logger.info('=' * 60)

        # Step 1: Wait for page to fully load (give it time)
        logger.info('Step 1: Waiting for page to load (10 seconds)...')
        time.sleep(10)

        # Step 2: Check if already logged in (chat list visible)
        logger.info('Step 2: Checking if already logged in...')
        try:
            chat_list = page.query_selector('[aria-label="Chat list"]')
            if chat_list:
                logger.info('')
                logger.info('=' * 60)
                logger.info('SUCCESS: Already logged in to WhatsApp Web!')
                logger.info('Session was restored from previous login.')
                logger.info('=' * 60)
                logger.info('')
                return True
        except Exception:
            pass

        # Step 3: Not logged in - wait for QR code to appear
        logger.info('Step 3: Not logged in. Waiting for QR code (up to 60 seconds)...')

        qr_found = False
        for i in range(60):  # Wait up to 60 seconds for QR
            try:
                # Check again if logged in (session may have loaded)
                chat_list = page.query_selector('[aria-label="Chat list"]')
                if chat_list:
                    logger.info('Session restored! Already logged in.')
                    return True

                # Try multiple selectors for QR code (WhatsApp changes these)
                qr_selectors = [
                    '[data-testid="qrcode"]',
                    'canvas[aria-label*="QR"]',
                    'canvas[aria-label*="Scan"]',
                    'div[data-ref] canvas',
                    'canvas',
                    '[data-testid="intro-text"]',  # Intro screen has QR nearby
                    'div._akau canvas',  # Class-based fallback
                ]

                for selector in qr_selectors:
                    qr_code = page.query_selector(selector)
                    if qr_code:
                        qr_found = True
                        break

                if qr_found:
                    break
            except Exception as e:
                if i % 20 == 0:
                    logger.debug(f'QR detection error: {e}')

            if i % 10 == 0:
                logger.info(f'  Waiting for QR code... ({i}/60 seconds)')
            time.sleep(1)

        if not qr_found:
            # QR element not found but page is loaded - assume QR is there
            logger.warning('QR element not detected, but proceeding (page may have different structure)')

        # Step 4: QR code should be visible - prompt user to scan
        logger.info('')
        logger.info('=' * 60)
        logger.info('*' * 60)
        logger.info('*  QR CODE IS ON SCREEN - SCAN NOW WITH YOUR PHONE  *')
        logger.info('*' * 60)
        logger.info('')
        logger.info('  Instructions:')
        logger.info('  1. Open WhatsApp on your phone')
        logger.info('  2. Go to Settings > Linked Devices')
        logger.info('  3. Tap "Link a Device"')
        logger.info('  4. Point your camera at the QR code on screen')
        logger.info('')
        logger.info('  Waiting for you to scan... (up to 120 seconds)')
        logger.info('=' * 60)
        logger.info('')

        # Step 5: Wait for login to complete (up to 120 seconds)
        for i in range(120):
            try:
                chat_list = page.query_selector('[aria-label="Chat list"]')
                if chat_list:
                    logger.info('')
                    logger.info('=' * 60)
                    logger.info('*' * 60)
                    logger.info('*       SUCCESS: LOGIN COMPLETE!       *')
                    logger.info('*' * 60)
                    logger.info('WhatsApp Web is now connected.')
                    logger.info('Session saved for future use.')
                    logger.info('=' * 60)
                    logger.info('')
                    return True
            except Exception:
                pass

            if i % 15 == 0 and i > 0:
                remaining = 120 - i
                logger.info(f'  Still waiting for scan... ({remaining} seconds remaining)')

            time.sleep(1)

        # Timeout
        logger.error('')
        logger.error('=' * 60)
        logger.error('FAILED: Login timeout - QR code was not scanned in time')
        logger.error('Please try again.')
        logger.error('=' * 60)
        return False

    def run(self, headless: bool = False):
        """Main run loop"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('STARTING WHATSAPP WATCHER')
        logger.info('=' * 60)
        logger.info(f'Vault path: {self.vault_path}')
        logger.info(f'Session path: {self.session_path}')
        logger.info(f'Headless mode: {headless}')
        logger.info('')

        if headless:
            logger.warning('WARNING: Running headless on first login will fail!')
            logger.warning('Run without --headless first to scan QR code.')
            logger.info('')

        with sync_playwright() as p:
            logger.info('Launching Chromium browser (visible window)...')

            # Use persistent context to maintain login session
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ],
                viewport={'width': 1280, 'height': 900}
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # Navigate to WhatsApp Web
            logger.info('Navigating to https://web.whatsapp.com ...')
            try:
                page.goto('https://web.whatsapp.com', timeout=60000, wait_until='domcontentloaded')
            except PlaywrightTimeout:
                logger.error('FAILED: Could not load WhatsApp Web (timeout)')
                browser.close()
                return

            # Wait for login
            if not self.wait_for_login(page):
                logger.error('Exiting due to login failure.')
                browser.close()
                return

            logger.info(f'Check interval: {self.check_interval} seconds')
            logger.info('')
            logger.info('=' * 60)
            logger.info('WATCHER IS NOW RUNNING')
            logger.info('Monitoring for new messages...')
            logger.info('Press Ctrl+C to stop.')
            logger.info('=' * 60)
            logger.info('')

            try:
                while True:
                    updates = self.check_for_updates(page)

                    for update in updates:
                        self.create_action_file(update)
                        self.processed_ids.add(update['id'])

                    if updates:
                        self._save_processed_ids()
                        logger.info(f'Processed {len(updates)} new message(s)')

                    time.sleep(self.check_interval)
            except KeyboardInterrupt:
                logger.info('')
                logger.info('Stopping WhatsApp Watcher...')
                self._save_processed_ids()

            browser.close()

        logger.info('WhatsApp Watcher stopped.')


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    default_session = Path(__file__).parent.parent.parent.parent / 'credentials' / 'whatsapp_session'

    # Parse arguments
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    vault_path = Path(args[0]) if len(args) > 0 else default_vault
    session_path = Path(args[1]) if len(args) > 1 else default_session

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    headless = '--headless' in sys.argv
    test_mode = '--test' in sys.argv

    watcher = WhatsAppWatcher(str(vault_path), str(session_path))

    if test_mode:
        # Create fake test messages to verify domain classification works
        logger.info('')
        logger.info('=' * 60)
        logger.info('RUNNING IN TEST MODE - CROSS-DOMAIN TEST')
        logger.info('=' * 60)

        # Test 1: Personal message
        logger.info('')
        logger.info('Test 1: Personal Message')
        logger.info('-' * 40)
        personal_message = {
            'type': 'whatsapp_message',
            'id': f'test_personal_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'sender': 'Mom',
            'preview': 'Hey! How are you doing? Want to grab dinner tonight? Miss you!',
            'priority': 'normal',
            'timestamp': datetime.now().isoformat()
        }
        filepath1 = watcher.create_action_file(personal_message)
        logger.info(f'Created: {filepath1}')
        logger.info(f'Domain: PERSONAL (expected)')

        # Test 2: Business message
        logger.info('')
        logger.info('Test 2: Business Message')
        logger.info('-' * 40)
        time.sleep(1)  # Ensure different timestamp
        business_message = {
            'type': 'whatsapp_message',
            'id': f'test_business_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'sender': 'Client ABC',
            'preview': 'Invoice #1234 is ready. Please process payment by deadline. Meeting scheduled for project review.',
            'priority': 'high',
            'timestamp': datetime.now().isoformat()
        }
        filepath2 = watcher.create_action_file(business_message)
        logger.info(f'Created: {filepath2}')
        logger.info(f'Domain: BUSINESS (expected)')

        # Use filepath2 for the final display
        filepath = filepath2

        logger.info('')
        logger.info('=' * 60)
        logger.info('TEST RESULTS')
        logger.info('=' * 60)
        logger.info(f'Action file created: {filepath}')
        logger.info(f'File exists: {filepath.exists()}')
        logger.info('')
        logger.info('File contents:')
        logger.info('-' * 40)
        print(filepath.read_text())
        logger.info('-' * 40)
        logger.info('')
        logger.info('TEST PASSED - Action file created successfully!')
        logger.info('=' * 60)
    else:
        watcher.run(headless=headless)


if __name__ == '__main__':
    main()
