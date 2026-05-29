# linkedin_watcher.py - Monitors LinkedIn for notifications using Playwright
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
logger = logging.getLogger('LinkedInWatcher')

# Stealth settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
STEALTH_SCRIPT = """
try { Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true}); } catch(e) {}
try { Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en'], configurable: true}); } catch(e) {}
try { window.chrome = { runtime: {} }; } catch(e) {}
"""


class LinkedInWatcher:
    """Watcher for LinkedIn - monitors notifications using Playwright browser automation"""

    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.processed_ids_file = self.vault_path / '.linkedin_processed_ids.json'
        self.processed_ids = self._load_processed_ids()

        self.check_interval = 60  # Check every 60 seconds

        # Initialize domain classifier
        self.domain_classifier = DomainClassifier(str(self.vault_path))

        # Keywords indicating priority notifications
        self.priority_keywords = [
            'urgent', 'asap', 'opportunity', 'job',
            'interview', 'offer', 'contract', 'proposal',
            'meeting', 'call', 'deadline', 'immediate'
        ]

    def _load_processed_ids(self) -> set:
        """Load previously processed notification IDs"""
        if self.processed_ids_file.exists():
            try:
                with open(self.processed_ids_file) as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def _save_processed_ids(self):
        """Save processed notification IDs"""
        with open(self.processed_ids_file, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def wait_for_login(self, page, timeout_seconds: int = 180):
        """Wait for user to login to LinkedIn"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('WAITING FOR LINKEDIN LOGIN...')
        logger.info('=' * 60)

        # Step 1: Wait for page to load
        logger.info('Step 1: Waiting for page to load (10 seconds)...')
        time.sleep(10)

        # Step 2: Check if already logged in
        logger.info('Step 2: Checking if already logged in...')
        try:
            logged_in = page.query_selector('[data-alias="feed-tab"]') or \
                        page.query_selector('[data-test-global-nav-link="feed"]') or \
                        page.query_selector('button[aria-label="Start a post"]') or \
                        page.query_selector('.feed-identity-module') or \
                        page.query_selector('.share-box-feed-entry__trigger')

            if logged_in:
                logger.info('')
                logger.info('=' * 60)
                logger.info('SUCCESS: Already logged in to LinkedIn!')
                logger.info('Session was restored from previous login.')
                logger.info('=' * 60)
                return True
        except Exception as e:
            logger.debug(f'Login check error: {e}')

        # Step 3: Wait for manual login
        logger.info('Step 3: Not logged in. Please login manually...')
        logger.info('')
        logger.info('=' * 60)
        logger.info('>>> PLEASE LOGIN TO LINKEDIN IN THE BROWSER WINDOW <<<')
        logger.info(f'>>> You have {timeout_seconds} seconds to login <<<')
        logger.info('=' * 60)
        logger.info('')

        for i in range(timeout_seconds):
            try:
                logged_in = page.query_selector('[data-alias="feed-tab"]') or \
                            page.query_selector('button[aria-label="Start a post"]') or \
                            page.query_selector('.feed-identity-module') or \
                            page.query_selector('.share-box-feed-entry__trigger')

                if logged_in:
                    logger.info('')
                    logger.info('=' * 60)
                    logger.info('SUCCESS: Login detected!')
                    logger.info('Session saved for future use.')
                    logger.info('=' * 60)
                    return True
            except Exception:
                pass

            if i % 30 == 0:
                logger.info(f'  Waiting for login... ({i}/{timeout_seconds} seconds)')
            time.sleep(1)

        logger.error('Login timeout - please try again')
        return False

    def check_for_notifications(self, page) -> list:
        """Check for new LinkedIn notifications"""
        updates = []

        try:
            # Navigate to notifications page
            logger.info('Checking notifications...')
            page.goto('https://www.linkedin.com/notifications/', timeout=30000)
            time.sleep(3)

            # Press Escape to dismiss any popups
            for _ in range(2):
                page.keyboard.press('Escape')
                time.sleep(0.3)

            # Find notification items
            notification_selectors = [
                '.nt-card',
                '[data-view-name="notification-card"]',
                '.notification-card',
                'article.artdeco-card'
            ]

            notifications_found = []
            for selector in notification_selectors:
                try:
                    items = page.query_selector_all(selector)
                    if items:
                        notifications_found = items
                        logger.info(f'Found {len(items)} notifications using {selector}')
                        break
                except Exception:
                    continue

            # Process up to 5 most recent notifications
            for item in notifications_found[:5]:
                try:
                    # Extract notification info using JavaScript
                    notif_info = item.evaluate('''el => {
                        // Get notification text
                        const textEl = el.querySelector('.nt-card__text') ||
                                       el.querySelector('.notification-card__text') ||
                                       el.querySelector('span');
                        const text = textEl ? textEl.innerText : "";

                        // Get actor name
                        const actorEl = el.querySelector('.nt-card__actor-name') ||
                                       el.querySelector('strong');
                        const actor = actorEl ? actorEl.innerText : "LinkedIn";

                        // Get time
                        const timeEl = el.querySelector('.nt-card__time') ||
                                      el.querySelector('time');
                        const timeStr = timeEl ? timeEl.innerText : "";

                        return { text, actor, time: timeStr };
                    }''')

                    if notif_info and notif_info.get('text'):
                        text = notif_info.get('text', '')
                        actor = notif_info.get('actor', 'LinkedIn')
                        time_str = notif_info.get('time', '')

                        # Create unique ID
                        notif_id = f"linkedin_{hash(actor + text[:100] + str(datetime.now().date()))}"

                        if notif_id not in self.processed_ids:
                            # Determine notification type
                            notif_type = 'general'
                            if 'connect' in text.lower():
                                notif_type = 'connection_request'
                            elif 'message' in text.lower():
                                notif_type = 'message'
                            elif 'like' in text.lower() or 'react' in text.lower():
                                notif_type = 'reaction'
                            elif 'comment' in text.lower():
                                notif_type = 'comment'
                            elif 'mention' in text.lower():
                                notif_type = 'mention'
                            elif 'job' in text.lower():
                                notif_type = 'job_alert'

                            # Check priority
                            text_lower = text.lower()
                            is_priority = any(kw in text_lower for kw in self.priority_keywords)

                            updates.append({
                                'type': 'linkedin_notification',
                                'notification_type': notif_type,
                                'id': notif_id,
                                'actor': actor,
                                'text': text[:500],
                                'time': time_str,
                                'priority': 'high' if is_priority else 'normal',
                                'timestamp': datetime.now().isoformat()
                            })

                except Exception as e:
                    logger.debug(f'Error extracting notification: {e}')
                    continue

        except PlaywrightTimeout:
            logger.warning('Timeout loading notifications page')
        except Exception as e:
            logger.error(f'Error checking notifications: {e}')

        return updates

    def check_for_messages(self, page) -> list:
        """Check for new LinkedIn messages"""
        updates = []

        try:
            # Navigate to messaging
            logger.info('Checking messages...')
            page.goto('https://www.linkedin.com/messaging/', timeout=30000)
            time.sleep(3)

            # Press Escape to dismiss popups
            for _ in range(2):
                page.keyboard.press('Escape')
                time.sleep(0.3)

            # Find unread conversations (usually have a dot indicator)
            unread_selectors = [
                '.msg-conversation-card--unread',
                '[data-test-is-unread="true"]',
                '.msg-conversation-listitem--unread'
            ]

            unread_convos = []
            for selector in unread_selectors:
                try:
                    items = page.query_selector_all(selector)
                    if items:
                        unread_convos = items
                        logger.info(f'Found {len(items)} unread conversations')
                        break
                except Exception:
                    continue

            # Process unread messages
            for item in unread_convos[:5]:
                try:
                    msg_info = item.evaluate('''el => {
                        const nameEl = el.querySelector('.msg-conversation-card__participant-names') ||
                                      el.querySelector('.msg-conversation-listitem__participant-names');
                        const name = nameEl ? nameEl.innerText : "Unknown";

                        const previewEl = el.querySelector('.msg-conversation-card__message-snippet') ||
                                         el.querySelector('.msg-conversation-listitem__message-snippet');
                        const preview = previewEl ? previewEl.innerText : "";

                        const timeEl = el.querySelector('.msg-conversation-card__time-stamp') ||
                                      el.querySelector('time');
                        const time = timeEl ? timeEl.innerText : "";

                        return { name, preview, time };
                    }''')

                    if msg_info and msg_info.get('name'):
                        name = msg_info.get('name', 'Unknown')
                        preview = msg_info.get('preview', '')
                        time_str = msg_info.get('time', '')

                        # Create unique ID
                        msg_id = f"linkedin_msg_{hash(name + preview[:50] + str(datetime.now().date()))}"

                        if msg_id not in self.processed_ids:
                            # Check priority
                            preview_lower = preview.lower()
                            is_priority = any(kw in preview_lower for kw in self.priority_keywords)

                            updates.append({
                                'type': 'linkedin_message',
                                'notification_type': 'message',
                                'id': msg_id,
                                'actor': name,
                                'text': preview[:500],
                                'time': time_str,
                                'priority': 'high' if is_priority else 'normal',
                                'timestamp': datetime.now().isoformat()
                            })

                except Exception as e:
                    logger.debug(f'Error extracting message: {e}')
                    continue

        except PlaywrightTimeout:
            logger.warning('Timeout loading messages page')
        except Exception as e:
            logger.error(f'Error checking messages: {e}')

        return updates

    def create_action_file(self, notification: dict) -> Path:
        """Create action file for a LinkedIn notification with domain classification"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        notif_type = notification.get('notification_type', 'general').upper()

        # Classify domain (Personal or Business)
        domain, target_folder = self.domain_classifier.classify_and_route(
            content=notification['text'],
            sender=notification['actor'],
            source='linkedin'
        )

        filename = f"LINKEDIN_{notif_type}_{timestamp}.md"
        filepath = target_folder / filename

        content = f'''---
type: linkedin_notification
notification_type: {notification.get('notification_type', 'general')}
domain: {domain}
actor: {notification['actor']}
detected_at: {notification['timestamp']}
priority: {notification['priority']}
status: pending
---

# LinkedIn Notification

## Type
**{notif_type}** from {notification['actor']}

## Domain
**{domain.upper()}** - Routed to /{domain.capitalize()}/Needs_Action/

## Content
{notification['text']}

## Time
{notification.get('time', 'Recent')}

## Priority
**{notification['priority'].upper()}**

## Suggested Actions
- [ ] Open LinkedIn and review notification
- [ ] Respond if action required
- [ ] Accept/decline if connection request
- [ ] Archive after handling

## Quick Links
- [Open LinkedIn](https://www.linkedin.com)
- [View Notifications](https://www.linkedin.com/notifications/)
- [View Messages](https://www.linkedin.com/messaging/)

---
*Generated by LinkedInWatcher (Silver Tier)*
'''
        filepath.write_text(content)
        logger.info(f'Created action file: {filename} -> {domain.upper()} domain')
        return filepath

    def run(self, headless: bool = False):
        """Main run loop"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('STARTING LINKEDIN WATCHER')
        logger.info('=' * 60)
        logger.info(f'Vault path: {self.vault_path}')
        logger.info(f'Session path: {self.session_path}')
        logger.info(f'Headless mode: {headless}')
        logger.info('')

        with sync_playwright() as p:
            logger.info(f'Launching Chromium browser {"(headless)" if headless else "(visible window)"}...')

            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=headless,
                user_agent=USER_AGENT,
                viewport={'width': 1280, 'height': 800},
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]
            )

            page = browser.new_page()
            page.add_init_script(STEALTH_SCRIPT)

            try:
                logger.info('Navigating to https://www.linkedin.com ...')
                page.goto('https://www.linkedin.com', timeout=60000)

                # Wait for login
                if not self.wait_for_login(page, timeout_seconds=180):
                    logger.error('Exiting due to login failure.')
                    browser.close()
                    return

                logger.info(f'Check interval: {self.check_interval} seconds')
                logger.info('')
                logger.info('=' * 60)
                logger.info('WATCHER IS NOW RUNNING')
                logger.info('Monitoring for notifications and messages...')
                logger.info('Press Ctrl+C to stop.')
                logger.info('=' * 60)
                logger.info('')

                while True:
                    all_updates = []

                    # Check notifications
                    notif_updates = self.check_for_notifications(page)
                    all_updates.extend(notif_updates)

                    # Check messages
                    msg_updates = self.check_for_messages(page)
                    all_updates.extend(msg_updates)

                    for update in all_updates:
                        self.create_action_file(update)
                        self.processed_ids.add(update['id'])

                    if all_updates:
                        self._save_processed_ids()
                        logger.info(f'Processed {len(all_updates)} new notification(s)/message(s)')

                    time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info('')
                logger.info('Stopping LinkedIn Watcher...')
                self._save_processed_ids()

            except Exception as e:
                logger.error(f'Error: {e}')

            finally:
                browser.close()

        logger.info('LinkedIn Watcher stopped.')


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    default_session = Path(__file__).parent.parent.parent.parent / 'credentials' / 'linkedin_session'

    vault_path = default_vault
    session_path = default_session

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    headless = '--headless' in sys.argv
    test_mode = '--test' in sys.argv

    watcher = LinkedInWatcher(str(vault_path), str(session_path))

    if test_mode:
        logger.info('')
        logger.info('=' * 60)
        logger.info('RUNNING IN TEST MODE')
        logger.info('=' * 60)

        # Test: Business notification (connection request)
        logger.info('')
        logger.info('Test: Business LinkedIn Notification')
        logger.info('-' * 40)
        business_notif = {
            'type': 'linkedin_notification',
            'notification_type': 'connection_request',
            'id': f'test_linkedin_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'actor': 'John Smith, CEO at TechCorp',
            'text': 'John Smith wants to connect with you. He mentioned an exciting job opportunity and potential contract proposal.',
            'time': 'Just now',
            'priority': 'high',
            'timestamp': datetime.now().isoformat()
        }
        filepath = watcher.create_action_file(business_notif)
        logger.info(f'Created: {filepath}')

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
        logger.info('TEST PASSED!')
        logger.info('=' * 60)
    else:
        watcher.run(headless=headless)


if __name__ == '__main__':
    main()
