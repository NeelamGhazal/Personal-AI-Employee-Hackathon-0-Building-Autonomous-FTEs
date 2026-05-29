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
        """Create a post on Facebook - FIXED to actually post"""
        logger.info('Creating Facebook post...')

        try:
            # Step 1: Navigate to home/feed
            logger.info('Step 1: Navigating to Facebook home...')
            page.goto('https://www.facebook.com/', timeout=30000)
            time.sleep(5)

            # Step 2: CRITICAL - Press Escape to dismiss any popups/dialogs
            logger.info('Step 2: Dismissing any popups (Escape x3)...')
            for _ in range(3):
                page.keyboard.press('Escape')
                time.sleep(0.5)
            time.sleep(2)

            # Step 3: Click on "What's on your mind?" to open post composer
            logger.info('Step 3: Looking for and clicking post composer...')
            composer_clicked = False
            selectors = [
                '[aria-label="Create a post"]',
                '[aria-label*="What\'s on your mind"]',
                'div[role="button"]:has-text("What\'s on your mind")',
                'span:has-text("What\'s on your mind")',
            ]

            for selector in selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.count() > 0:
                        logger.info(f'Found composer: {selector}')
                        elem.click()
                        composer_clicked = True
                        time.sleep(3)
                        break
                except:
                    continue

            if not composer_clicked:
                logger.warning('Could not find composer with selectors, trying fallback...')
                try:
                    page.click('div[role="main"] >> text="What\'s on your mind"', timeout=5000)
                    time.sleep(3)
                except:
                    pass

            # Step 4: Wait for and find the text area
            logger.info('Step 4: Finding text input area...')
            time.sleep(2)

            text_area_found = False
            text_selectors = [
                '[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"][data-lexical-editor="true"]',
                'div[contenteditable="true"]',
            ]

            for selector in text_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.count() > 0:
                        logger.info(f'Found text area: {selector}')
                        elem.click()
                        text_area_found = True
                        time.sleep(1)
                        break
                except:
                    continue

            # Step 5: Type message character by character with delays
            logger.info('Step 5: Typing message character by character...')
            for char in message:
                page.keyboard.type(char)
                time.sleep(0.05)  # 50ms delay per character
            time.sleep(3)

            # Step 6: Find and click Post button with MULTIPLE methods
            logger.info('Step 6: Clicking Post button with multiple methods...')

            # Method A: Try JavaScript click first (most reliable)
            logger.info('Method A: JavaScript click on Post button...')
            try:
                page.evaluate("""
                    const buttons = document.querySelectorAll('[aria-label="Post"]');
                    for (const btn of buttons) {
                        if (btn.textContent.includes('Post') || btn.getAttribute('aria-label') === 'Post') {
                            btn.click();
                            console.log('JS clicked Post button');
                            break;
                        }
                    }
                """)
                time.sleep(2)
            except Exception as e:
                logger.debug(f'JS click failed: {e}')

            # Method B: Try locator click with force
            logger.info('Method B: Force click on Post button...')
            post_selectors = [
                '[aria-label="Post"]',
                'div[aria-label="Post"]',
                'span:text-is("Post")',
            ]

            for selector in post_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.count() > 0:
                        btn.click(force=True, timeout=3000)
                        logger.info(f'Clicked: {selector}')
                        time.sleep(2)
                        break
                except:
                    continue

            # Method C: Try Tab + Enter to navigate to Post and press
            logger.info('Method C: Tab + Enter navigation...')
            for _ in range(5):
                page.keyboard.press('Tab')
                time.sleep(0.3)
            page.keyboard.press('Enter')
            time.sleep(2)

            # Method D: Try Ctrl+Enter keyboard shortcut
            logger.info('Method D: Ctrl+Enter shortcut...')
            page.keyboard.press('Control+Enter')

            # Step 8: Wait for post to be submitted
            logger.info('Step 8: Waiting 10 seconds for post submission...')
            time.sleep(10)

            # Step 9: Take screenshot immediately after posting attempt
            logger.info('Step 9: Taking screenshot after post attempt...')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.screenshots_path / f'facebook_post_{timestamp}.png'
            page.screenshot(path=str(screenshot_path))

            # Step 10: VERIFY post by checking if dialog closed and message appears
            logger.info('Step 10: Verifying post was actually created...')
            post_verified = False
            post_url = None

            # Method 1: Check if the composer dialog is closed (indicates post submitted)
            try:
                dialog_closed = page.locator('[aria-label="Post"]').count() == 0
                if dialog_closed:
                    logger.info('  Post dialog closed - good sign')
            except:
                pass

            # Method 2: Navigate to profile/timeline and look for the message
            logger.info('  Navigating to profile to verify post...')
            try:
                page.goto('https://www.facebook.com/me', timeout=30000)
                time.sleep(5)

                # Take verification screenshot
                verification_screenshot = self.screenshots_path / f'facebook_verify_{timestamp}.png'
                page.screenshot(path=str(verification_screenshot))
                logger.info(f'  Verification screenshot: {verification_screenshot}')

                # Check if our message text appears on the page
                page_content = page.content()
                # Check for first 50 chars of message (handles truncation)
                search_text = message[:50] if len(message) > 50 else message
                if search_text in page_content:
                    post_verified = True
                    logger.info('  SUCCESS: Message found on profile page!')

                    # Try to find post URL
                    try:
                        post_links = page.locator('a[href*="/posts/"]').all()
                        if post_links:
                            post_url = post_links[0].get_attribute('href')
                            logger.info(f'  Post URL: {post_url}')
                    except:
                        pass
                else:
                    logger.warning('  Message NOT found on profile page')
                    logger.warning(f'  Searched for: "{search_text[:30]}..."')

            except Exception as e:
                logger.error(f'  Verification error: {e}')

            # Step 11: Final screenshot
            standard_screenshot = self.screenshots_path / 'facebook_post.png'
            page.screenshot(path=str(standard_screenshot))

            # Return result with ACTUAL verification status
            result = {
                'success': post_verified,
                'platform': 'facebook',
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'screenshot': str(screenshot_path),
                'verified': post_verified,
                'post_url': post_url
            }

            if post_verified:
                logger.info('')
                logger.info('=' * 60)
                logger.info('POST VERIFIED SUCCESSFULLY!')
                if post_url:
                    logger.info(f'Post URL: {post_url}')
                logger.info('=' * 60)
            else:
                logger.warning('')
                logger.warning('=' * 60)
                logger.warning('POST NOT VERIFIED - Check screenshots manually')
                logger.warning(f'Screenshot: {screenshot_path}')
                logger.warning('=' * 60)

            return result

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

                    if result.get('verified'):
                        post_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        self.posted_ids.append(post_id)
                        self._save_posted_ids()
                        logger.info('')
                        logger.info('=' * 60)
                        logger.info('FACEBOOK POST VERIFIED!')
                        logger.info(f'Message: {message[:50]}...')
                        if result.get('post_url'):
                            logger.info(f'URL: {result["post_url"]}')
                        logger.info('=' * 60)
                    elif result['success']:
                        logger.warning('Post submitted but NOT VERIFIED on profile')
                        logger.warning('Check screenshots to confirm manually')
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
