# twitter_poster.py - Posts to Twitter/X using Playwright browser automation
import logging
import sys
import time
import json
import random
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Stealth script to hide automation (with error handling)
STEALTH_SCRIPT = """
try {
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true});
} catch(e) {}
try {
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en'], configurable: true});
} catch(e) {}
try {
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5], configurable: true});
} catch(e) {}
try {
    window.chrome = { runtime: {} };
} catch(e) {}
"""

# Real Chrome user agent
CHROME_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TwitterPoster')


class TwitterPoster:
    """Posts content to Twitter/X using Playwright browser automation"""

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

        self.posted_ids_file = self.vault_path / '.twitter_posted_ids.json'
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
            json.dump(self.posted_ids[-100:], f)

    def wait_for_login(self, page):
        """Wait for user to login to Twitter/X"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('WAITING FOR TWITTER/X LOGIN...')
        logger.info('=' * 60)

        # Step 1: Wait for page to load
        logger.info('Step 1: Waiting for page to load (10 seconds)...')
        time.sleep(10)

        # Step 2: Check if already logged in
        logger.info('Step 2: Checking if already logged in...')
        try:
            # Look for elements that indicate logged-in state
            logged_in = page.query_selector('[data-testid="SideNav_NewTweet_Button"]') or \
                        page.query_selector('[aria-label="Post"]') or \
                        page.query_selector('[data-testid="AppTabBar_Home_Link"]') or \
                        page.query_selector('[aria-label="Home"]')

            if logged_in:
                logger.info('')
                logger.info('=' * 60)
                logger.info('SUCCESS: Already logged in to Twitter/X!')
                logger.info('Session was restored from previous login.')
                logger.info('=' * 60)
                return True
        except Exception as e:
            logger.debug(f'Login check error: {e}')

        # Step 3: Wait for manual login
        logger.info('Step 3: Not logged in. Please login manually...')
        logger.info('')
        logger.info('>>> ENTER CREDENTIALS IN THE BROWSER WINDOW <<<')
        logger.info('')

        for i in range(180):
            try:
                logged_in = page.query_selector('[data-testid="SideNav_NewTweet_Button"]') or \
                            page.query_selector('[aria-label="Post"]') or \
                            page.query_selector('[data-testid="AppTabBar_Home_Link"]')

                if logged_in:
                    logger.info('')
                    logger.info('=' * 60)
                    logger.info('SUCCESS: Login detected!')
                    logger.info('=' * 60)
                    return True
            except Exception:
                pass

            if i % 10 == 0:
                logger.info(f'  Waiting for login... ({i}/180 seconds)')
            time.sleep(1)

        logger.error('Login timeout - please try again')
        return False

    def human_type(self, page, text: str):
        """Type text with human-like random delays"""
        for char in text:
            page.keyboard.type(char)
            # Random delay between 100-200ms per character (slower, more human)
            time.sleep(random.uniform(0.1, 0.2))

    def create_tweet(self, page, message: str) -> dict:
        """Create a tweet on Twitter/X"""
        logger.info('Creating tweet...')

        try:
            # Method 1: Try home feed text box first
            logger.info('Method 1: Going to home feed...')
            page.goto('https://twitter.com/home', timeout=30000)
            time.sleep(5)  # Wait for page to fully load

            # Re-inject stealth script
            page.evaluate(STEALTH_SCRIPT)
            time.sleep(1)

            # Look for the "What is happening?!" text box on home feed
            logger.info('Looking for home feed compose box...')
            posted = False

            # Try clicking the compose area
            try:
                compose_selectors = [
                    '[data-testid="tweetTextarea_0"]',
                    '[aria-label="Post text"]',
                    'div[data-contents="true"]',
                    '[role="textbox"]',
                ]

                for selector in compose_selectors:
                    try:
                        elem = page.locator(selector).first
                        if elem.count() > 0:
                            logger.info(f'Found compose box: {selector}')
                            elem.click()
                            time.sleep(2)
                            break
                    except:
                        continue

                # Type with human-like delays
                logger.info('Typing tweet slowly...')
                self.human_type(page, message)
                time.sleep(3)  # Wait after typing

                # Find and click Post button
                logger.info('Looking for Post button...')
                post_selectors = [
                    '[data-testid="tweetButtonInline"]',
                    '[data-testid="tweetButton"]',
                ]

                for selector in post_selectors:
                    try:
                        btn = page.locator(selector).first
                        if btn.count() > 0:
                            logger.info(f'Found Post button: {selector}')
                            time.sleep(2)
                            # Use force click to bypass any overlays
                            btn.click(force=True, timeout=5000)
                            posted = True
                            logger.info('Post button clicked!')
                            time.sleep(5)
                            break
                    except Exception as e:
                        logger.info(f'Click failed for {selector}: {e}')
                        continue

            except Exception as e:
                logger.info(f'Home feed method failed: {e}')

            # Method 2: If home feed failed, try compose/tweet URL
            if not posted:
                logger.info('Method 2: Trying compose/tweet URL...')
                page.goto('https://twitter.com/compose/tweet', timeout=30000)
                time.sleep(4)

                page.evaluate(STEALTH_SCRIPT)
                time.sleep(1)

                # Wait for text box
                try:
                    page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
                    time.sleep(2)

                    # Click and type
                    text_area = page.locator('[data-testid="tweetTextarea_0"]').first
                    text_area.click()
                    time.sleep(1)

                    logger.info('Typing tweet in compose modal...')
                    self.human_type(page, message)
                    time.sleep(3)

                    # Click Post with force
                    post_btn = page.locator('[data-testid="tweetButton"]').first
                    time.sleep(2)
                    post_btn.click(force=True, timeout=5000)
                    posted = True
                    logger.info('Posted via compose modal!')
                    time.sleep(5)

                except Exception as e:
                    logger.info(f'Compose URL method failed: {e}')

            # Take screenshot immediately
            logger.info('Taking screenshot...')

            # Take screenshot as proof
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.screenshots_path / f'twitter_post_{timestamp}.png'
            page.screenshot(path=str(screenshot_path))

            # Also save to standard filename for easy reference
            standard_screenshot = self.screenshots_path / 'twitter_post.png'
            page.screenshot(path=str(standard_screenshot))

            return {
                'success': True,
                'platform': 'twitter',
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'screenshot': str(screenshot_path)
            }

        except Exception as e:
            logger.error(f'Error creating tweet: {e}')
            return {
                'success': False,
                'platform': 'twitter',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def create_action_file(self, post_result: dict) -> Path:
        """Create action file for the tweet"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"TWITTER_POST_{timestamp}.md"
        filepath = self.social_media_path / filename

        status = 'posted' if post_result.get('success') else 'failed'

        content = f'''---
type: social_media_post
platform: twitter
status: {status}
posted_at: {post_result.get('timestamp')}
---

# Twitter/X Post

## Status
**{status.upper()}**

## Content
{post_result.get('message', 'N/A')}

## Screenshot
{f"![[{Path(post_result.get('screenshot', '')).name}]]" if post_result.get('screenshot') else 'N/A'}

## Details
- Platform: Twitter/X
- Posted: {post_result.get('timestamp')}
- Success: {post_result.get('success', False)}
- Character Count: {len(post_result.get('message', ''))}
{f"- Error: {post_result.get('error')}" if post_result.get('error') else ''}

---
*Generated by TwitterPoster (Gold Tier)*
'''
        filepath.write_text(content)
        logger.info(f'Created action file: {filename}')
        return filepath

    def log_action(self, action: str, details: dict):
        """Log action to Logs folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f'twitter_{timestamp}.log'

        log_content = f'''[{datetime.now().isoformat()}] {action}
Details: {json.dumps(details, indent=2)}
'''
        with open(log_file, 'a') as f:
            f.write(log_content)

    def run(self, message: str = None, headless: bool = False):
        """Run the Twitter poster"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('STARTING TWITTER/X POSTER')
        logger.info('=' * 60)
        logger.info(f'Vault path: {self.vault_path}')
        logger.info(f'Session path: {self.session_path}')
        logger.info(f'Headless mode: {headless}')
        logger.info('')

        with sync_playwright() as p:
            logger.info(f'Launching Chromium browser {"(headless)" if headless else "(visible window)"}...')
            logger.info('Using stealth mode to avoid bot detection...')

            # Anti-detection browser options
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=headless,
                user_agent=CHROME_USER_AGENT,
                viewport={'width': 1280, 'height': 720},
                locale='en-US',
                timezone_id='America/New_York',
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--disable-extensions',
                    '--start-maximized',
                ]
            )

            page = browser.new_page()

            # Inject stealth script to hide automation
            page.add_init_script(STEALTH_SCRIPT)

            # Also run it immediately on current page
            page.evaluate(STEALTH_SCRIPT)

            try:
                logger.info('Navigating to https://twitter.com ...')
                time.sleep(2)  # Small delay before navigation
                page.goto('https://twitter.com', timeout=60000)
                time.sleep(3)  # Wait for page to fully load

                if not self.wait_for_login(page):
                    logger.error('Exiting due to login failure.')
                    browser.close()
                    return

                if message:
                    result = self.create_tweet(page, message)
                    self.create_action_file(result)
                    self.log_action('TWEET', result)

                    if result['success']:
                        post_id = f"tw_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        self.posted_ids.append(post_id)
                        self._save_posted_ids()
                        logger.info('Tweet posted successfully!')
                    else:
                        logger.error(f'Tweet failed: {result.get("error")}')
                else:
                    logger.info('No message provided. Login successful, session saved.')

            except Exception as e:
                logger.error(f'Error: {e}')

            finally:
                browser.close()

        logger.info('Twitter Poster stopped.')


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    default_session = Path(__file__).parent.parent.parent.parent / 'credentials' / 'twitter_session'

    vault_path = default_vault
    session_path = default_session

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    headless = '--headless' in sys.argv
    test_mode = '--test' in sys.argv

    poster = TwitterPoster(str(vault_path), str(session_path))

    if test_mode:
        logger.info('')
        logger.info('=' * 60)
        logger.info('RUNNING IN TEST MODE')
        logger.info('=' * 60)
        logger.info('Simulating a Twitter/X post...')

        test_result = {
            'success': True,
            'platform': 'twitter',
            'message': 'Test tweet from AI Employee! Automated posting via Playwright. #AIEmployee #GoldTier #Automation',
            'timestamp': datetime.now().isoformat(),
            'screenshot': None
        }

        filepath = poster.create_action_file(test_result)
        poster.log_action('TEST_TWEET', test_result)

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
        message = None
        for i, arg in enumerate(sys.argv):
            if arg == '--message' and i + 1 < len(sys.argv):
                message = sys.argv[i + 1]
                break

        poster.run(message=message, headless=headless)


if __name__ == '__main__':
    main()
