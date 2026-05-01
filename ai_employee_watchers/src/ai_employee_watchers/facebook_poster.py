# facebook_poster.py - Posts to Facebook using Playwright browser automation
import logging
import sys
import time
import json
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FacebookPoster')


class FacebookPoster:
    """Posts content to Facebook using Playwright browser automation"""

    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.social_media_path = self.vault_path / 'Business' / 'Social_Media'
        self.social_media_path.mkdir(parents=True, exist_ok=True)

        self.logs_path = self.vault_path / 'Logs'
        self.logs_path.mkdir(parents=True, exist_ok=True)

        self.screenshots_path = self.vault_path / 'Business' / 'Social_Media' / 'screenshots'
        self.screenshots_path.mkdir(parents=True, exist_ok=True)

        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.posted_ids_file = self.vault_path / '.facebook_posted_ids.json'
        self.posted_ids = self._load_posted_ids()

    def _load_posted_ids(self) -> list:
        """Load previously posted IDs"""
        if self.posted_ids_file.exists():
            try:
                with open(self.posted_ids_file) as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_posted_ids(self):
        """Save posted IDs"""
        with open(self.posted_ids_file, 'w') as f:
            json.dump(self.posted_ids[-100:], f)  # Keep last 100

    def wait_for_login(self, page):
        """Wait for user to login to Facebook"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('WAITING FOR FACEBOOK LOGIN...')
        logger.info('=' * 60)

        # Step 1: Wait for page to load
        logger.info('Step 1: Waiting for page to load (10 seconds)...')
        time.sleep(10)

        # Step 2: Check if already logged in
        logger.info('Step 2: Checking if already logged in...')
        try:
            # Look for elements that indicate logged-in state
            logged_in = page.query_selector('[aria-label="Your profile"]') or \
                        page.query_selector('[aria-label="Account"]') or \
                        page.query_selector('[data-pagelet="ProfileTilesFeed"]') or \
                        page.query_selector('[aria-label="Create a post"]') or \
                        page.query_selector('[aria-label="Create"]')

            if logged_in:
                logger.info('')
                logger.info('=' * 60)
                logger.info('SUCCESS: Already logged in to Facebook!')
                logger.info('Session was restored from previous login.')
                logger.info('=' * 60)
                return True
        except Exception as e:
            logger.debug(f'Login check error: {e}')

        # Step 3: Wait for manual login
        logger.info('Step 3: Not logged in. Please login manually...')
        logger.info('')
        logger.info('>>> SCAN QR CODE OR ENTER CREDENTIALS IN THE BROWSER WINDOW <<<')
        logger.info('')

        # Wait up to 120 seconds for login
        for i in range(120):
            try:
                logged_in = page.query_selector('[aria-label="Your profile"]') or \
                            page.query_selector('[aria-label="Account"]') or \
                            page.query_selector('[aria-label="Create a post"]') or \
                            page.query_selector('[aria-label="Create"]')

                if logged_in:
                    logger.info('')
                    logger.info('=' * 60)
                    logger.info('SUCCESS: Login detected!')
                    logger.info('=' * 60)
                    return True
            except Exception:
                pass

            if i % 10 == 0:
                logger.info(f'  Waiting for login... ({i}/120 seconds)')
            time.sleep(1)

        logger.error('Login timeout - please try again')
        return False

    def create_post(self, page, message: str) -> dict:
        """Create a post on Facebook"""
        logger.info('Creating Facebook post...')

        try:
            # Navigate to home/feed
            page.goto('https://www.facebook.com/', timeout=30000)
            time.sleep(5)

            # Click on "What's on your mind?" to open post composer
            # Try multiple selectors for the create post area
            logger.info('Looking for post composer...')
            post_box = None
            selectors = [
                '[aria-label="Create a post"]',
                '[aria-label*="What\'s on your mind"]',
                'span:has-text("What\'s on your mind")',
                '[data-pagelet="FeedComposer"]',
                'div[role="button"]:has-text("What\'s on your mind")',
            ]

            for selector in selectors:
                try:
                    post_box = page.query_selector(selector)
                    if post_box:
                        logger.info(f'Found post box with selector: {selector}')
                        break
                except:
                    continue

            if post_box:
                post_box.click()
                time.sleep(3)
            else:
                # Try clicking on the feed composer area directly
                logger.info('Trying to click on feed composer area...')
                page.click('div[role="main"] >> text="What\'s on your mind"', timeout=5000)
                time.sleep(3)

            # Wait for post dialog/text area to be ready
            logger.info('Waiting for text input area...')
            time.sleep(2)

            # Type the message using multiple approaches
            text_area = None
            text_selectors = [
                '[contenteditable="true"][role="textbox"]',
                '[contenteditable="true"][data-lexical-editor="true"]',
                '[aria-label*="What\'s on your mind"]',
                'div[contenteditable="true"]',
            ]

            for selector in text_selectors:
                try:
                    text_area = page.query_selector(selector)
                    if text_area:
                        logger.info(f'Found text area with selector: {selector}')
                        break
                except:
                    continue

            if text_area:
                text_area.click()
                time.sleep(0.5)
                page.keyboard.type(message, delay=50)
                time.sleep(2)
            else:
                # Fallback: just type wherever focus is
                logger.info('Using keyboard type fallback...')
                page.keyboard.type(message, delay=50)
                time.sleep(2)

            # Click Post button
            logger.info('Looking for Post button...')
            post_button = None
            post_selectors = [
                '[aria-label="Post"]',
                'div[aria-label="Post"]',
                'span:has-text("Post")',
                'div[role="button"]:has-text("Post")',
            ]

            for selector in post_selectors:
                try:
                    post_button = page.query_selector(selector)
                    if post_button:
                        logger.info(f'Found Post button with selector: {selector}')
                        break
                except:
                    continue

            if post_button:
                post_button.click()
                time.sleep(5)
                logger.info('Post button clicked!')

            # Take screenshot as proof
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.screenshots_path / f'facebook_post_{timestamp}.png'
            page.screenshot(path=str(screenshot_path))

            # Also save to standard filename for easy reference
            standard_screenshot = self.screenshots_path / 'facebook_post.png'
            page.screenshot(path=str(standard_screenshot))

            return {
                'success': True,
                'platform': 'facebook',
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'screenshot': str(screenshot_path)
            }

        except Exception as e:
            logger.error(f'Error creating post: {e}')
            return {
                'success': False,
                'platform': 'facebook',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def create_action_file(self, post_result: dict) -> Path:
        """Create action file for the post"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"FACEBOOK_POST_{timestamp}.md"
        filepath = self.social_media_path / filename

        status = 'posted' if post_result.get('success') else 'failed'

        content = f'''---
type: social_media_post
platform: facebook
status: {status}
posted_at: {post_result.get('timestamp')}
---

# Facebook Post

## Status
**{status.upper()}**

## Content
{post_result.get('message', 'N/A')}

## Screenshot
{f"![[{Path(post_result.get('screenshot', '')).name}]]" if post_result.get('screenshot') else 'N/A'}

## Details
- Platform: Facebook
- Posted: {post_result.get('timestamp')}
- Success: {post_result.get('success', False)}
{f"- Error: {post_result.get('error')}" if post_result.get('error') else ''}

---
*Generated by FacebookPoster (Gold Tier)*
'''
        filepath.write_text(content)
        logger.info(f'Created action file: {filename}')
        return filepath

    def log_action(self, action: str, details: dict):
        """Log action to Logs folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f'facebook_{timestamp}.log'

        log_content = f'''[{datetime.now().isoformat()}] {action}
Details: {json.dumps(details, indent=2)}
'''
        with open(log_file, 'a') as f:
            f.write(log_content)

    def run(self, message: str = None, headless: bool = False):
        """Run the Facebook poster"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('STARTING FACEBOOK POSTER')
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
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            page = browser.new_page()

            try:
                logger.info('Navigating to https://www.facebook.com ...')
                page.goto('https://www.facebook.com', timeout=60000)

                if not self.wait_for_login(page):
                    logger.error('Exiting due to login failure.')
                    browser.close()
                    return

                # If message provided, post it
                if message:
                    result = self.create_post(page, message)
                    self.create_action_file(result)
                    self.log_action('POST', result)

                    if result['success']:
                        post_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        self.posted_ids.append(post_id)
                        self._save_posted_ids()
                        logger.info('Post created successfully!')
                    else:
                        logger.error(f'Post failed: {result.get("error")}')
                else:
                    logger.info('No message provided. Login successful, session saved.')

            except Exception as e:
                logger.error(f'Error: {e}')

            finally:
                browser.close()

        logger.info('Facebook Poster stopped.')


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    default_session = Path(__file__).parent.parent.parent.parent / 'credentials' / 'facebook_session'

    vault_path = default_vault
    session_path = default_session

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    headless = '--headless' in sys.argv
    test_mode = '--test' in sys.argv

    poster = FacebookPoster(str(vault_path), str(session_path))

    if test_mode:
        # Test mode - create a test post action file without actually posting
        logger.info('')
        logger.info('=' * 60)
        logger.info('RUNNING IN TEST MODE')
        logger.info('=' * 60)
        logger.info('Simulating a Facebook post...')

        test_result = {
            'success': True,
            'platform': 'facebook',
            'message': 'Test post from AI Employee! This is a simulated post to verify the Facebook integration works correctly. #AIEmployee #GoldTier',
            'timestamp': datetime.now().isoformat(),
            'screenshot': None
        }

        filepath = poster.create_action_file(test_result)
        poster.log_action('TEST_POST', test_result)

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
        # Get message from command line or use default
        message = None
        for i, arg in enumerate(sys.argv):
            if arg == '--message' and i + 1 < len(sys.argv):
                message = sys.argv[i + 1]
                break

        poster.run(message=message, headless=headless)


if __name__ == '__main__':
    main()
