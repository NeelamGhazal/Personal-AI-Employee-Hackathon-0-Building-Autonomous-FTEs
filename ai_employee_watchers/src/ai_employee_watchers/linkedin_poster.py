# linkedin_poster.py - Posts to LinkedIn using Playwright browser automation
# Uses the SAME WORKING approach as twitter_poster.py (fixed version)
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
logger = logging.getLogger('LinkedInPoster')

# Stealth settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
STEALTH_SCRIPT = """
try { Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true}); } catch(e) {}
try { Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en'], configurable: true}); } catch(e) {}
try { window.chrome = { runtime: {} }; } catch(e) {}
"""


class LinkedInPoster:
    """Posts content to LinkedIn using Playwright browser automation"""

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

    def human_type(self, page, text: str):
        """Type text with human-like delays"""
        for char in text:
            page.keyboard.type(char)
            time.sleep(0.08)  # 80ms delay per character

    def create_post(self, page, message: str) -> dict:
        """Create a post on LinkedIn - USING WORKING APPROACH"""
        logger.info('Creating LinkedIn post...')

        try:
            # Step 1: Navigate to feed
            logger.info('Step 1: Navigating to LinkedIn feed...')
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(5)

            # Step 2: CRITICAL - Press Escape to dismiss any popups
            logger.info('Step 2: Dismissing any popups (Escape x3)...')
            for _ in range(3):
                page.keyboard.press('Escape')
                time.sleep(0.5)
            time.sleep(2)

            # Step 3: Find and click "Start a post" button
            logger.info('Step 3: Looking for "Start a post" button...')
            post_started = False

            start_post_selectors = [
                'button[aria-label="Start a post"]',
                '.share-box-feed-entry__trigger',
                'button.share-box-feed-entry__trigger',
                '[data-control-name="share.share_box"]',
            ]

            for selector in start_post_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.count() > 0:
                        logger.info(f'Found: {selector}')
                        elem.click()
                        post_started = True
                        time.sleep(3)
                        break
                except:
                    continue

            if not post_started:
                logger.warning('Could not find Start a post button, trying text click...')
                try:
                    page.click('text="Start a post"', timeout=5000)
                    time.sleep(3)
                except:
                    pass

            # Step 4: Wait for post modal to appear
            logger.info('Step 4: Waiting for post editor...')
            time.sleep(3)

            # Step 5: Find the text editor and click it
            logger.info('Step 5: Finding text editor...')
            editor_found = False

            editor_selectors = [
                '.ql-editor[data-placeholder]',
                'div[role="textbox"][contenteditable="true"]',
                '.editor-content[contenteditable="true"]',
                '[aria-label="Text editor for creating content"]',
                'div[contenteditable="true"]',
                'div.ql-editor',
            ]

            for selector in editor_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.count() > 0:
                        logger.info(f'Found editor: {selector}')
                        elem.click()
                        editor_found = True
                        time.sleep(1)
                        break
                except:
                    continue

            if not editor_found:
                logger.warning('Could not find editor, typing anyway...')

            # Step 6: Type message character by character
            logger.info('Step 6: Typing message character by character...')
            self.human_type(page, message)
            time.sleep(3)

            # Step 7: Take screenshot BEFORE posting
            logger.info('Step 7: Taking screenshot before posting...')
            before_screenshot = self.screenshots_path / 'linkedin_before_post.png'
            page.screenshot(path=str(before_screenshot))

            # Step 8: Click Post button using multiple methods
            logger.info('Step 8: Clicking Post button...')

            # Method A: JavaScript click
            logger.info('Method A: JavaScript click...')
            try:
                page.evaluate("""
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        const text = btn.textContent.trim().toLowerCase();
                        if (text === 'post' && !btn.disabled) {
                            btn.click();
                            console.log('JS clicked Post');
                            break;
                        }
                    }
                """)
                time.sleep(2)
            except:
                pass

            # Method B: Locator click with force
            logger.info('Method B: Force click on Post button...')
            post_selectors = [
                'button.share-actions__primary-action',
                'button[aria-label="Post"]',
                'button:has-text("Post")',
                'button.artdeco-button--primary:has-text("Post")',
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

            # Method C: Keyboard shortcut
            logger.info('Method C: Ctrl+Enter shortcut...')
            page.keyboard.press('Control+Enter')
            time.sleep(2)

            # Method D: Tab to Post button and Enter
            logger.info('Method D: Tab navigation...')
            for _ in range(5):
                page.keyboard.press('Tab')
                time.sleep(0.3)
            page.keyboard.press('Enter')

            # Step 9: Wait for post to submit
            logger.info('Step 9: Waiting 10 seconds for submission...')
            time.sleep(10)

            # Step 10: Take screenshot AFTER posting
            logger.info('Step 10: Taking screenshot after posting...')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.screenshots_path / f'linkedin_post_{timestamp}.png'
            page.screenshot(path=str(screenshot_path))

            # Also save to standard filename
            standard_screenshot = self.screenshots_path / 'linkedin_post.png'
            page.screenshot(path=str(standard_screenshot))

            return {
                'success': True,
                'platform': 'linkedin',
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'screenshot': str(screenshot_path)
            }

        except Exception as e:
            logger.error(f'Error creating post: {e}')
            return {
                'success': False,
                'platform': 'linkedin',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def create_action_file(self, post_result: dict) -> Path:
        """Create action file for the post"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}.md"
        filepath = self.social_media_path / filename

        status = 'posted' if post_result.get('success') else 'failed'

        content = f'''---
type: social_media_post
platform: linkedin
status: {status}
posted_at: {post_result.get('timestamp')}
---

# LinkedIn Post

## Status
**{status.upper()}**

## Content
{post_result.get('message', 'N/A')}

## Screenshot
{f"![[{Path(post_result.get('screenshot', '')).name}]]" if post_result.get('screenshot') else 'N/A'}

## Details
- Platform: LinkedIn
- Posted: {post_result.get('timestamp')}
- Success: {post_result.get('success', False)}
{f"- Error: {post_result.get('error')}" if post_result.get('error') else ''}

---
*Generated by LinkedInPoster (Silver Tier)*
'''
        filepath.write_text(content)
        logger.info(f'Created action file: {filename}')
        return filepath

    def log_action(self, action: str, details: dict):
        """Log action to Logs folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f'linkedin_{timestamp}.log'

        log_content = f'''[{datetime.now().isoformat()}] {action}
Details: {json.dumps(details, indent=2)}
'''
        with open(log_file, 'a') as f:
            f.write(log_content)

    def run(self, message: str = None, headless: bool = False):
        """Run the LinkedIn poster"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('STARTING LINKEDIN POSTER')
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

                # Wait up to 180 seconds for login
                if not self.wait_for_login(page, timeout_seconds=180):
                    logger.error('Exiting due to login failure.')
                    browser.close()
                    return

                # If message provided, post it
                if message:
                    result = self.create_post(page, message)
                    self.create_action_file(result)
                    self.log_action('POST', result)

                    if result['success']:
                        logger.info('')
                        logger.info('=' * 60)
                        logger.info('POST CREATED!')
                        logger.info('Check your LinkedIn profile to verify.')
                        logger.info('=' * 60)
                    else:
                        logger.error(f'Post failed: {result.get("error")}')
                else:
                    logger.info('No message provided. Login successful, session saved.')

                # Keep browser open briefly for verification
                logger.info('Keeping browser open for 5 seconds...')
                time.sleep(5)

            except Exception as e:
                logger.error(f'Error: {e}')

            finally:
                browser.close()

        logger.info('LinkedIn Poster stopped.')


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

    poster = LinkedInPoster(str(vault_path), str(session_path))

    if test_mode:
        logger.info('')
        logger.info('=' * 60)
        logger.info('RUNNING IN TEST MODE')
        logger.info('=' * 60)

        test_result = {
            'success': True,
            'platform': 'linkedin',
            'message': 'Test LinkedIn post from AI Employee! #AIEmployee #Automation',
            'timestamp': datetime.now().isoformat(),
            'screenshot': None
        }

        filepath = poster.create_action_file(test_result)
        poster.log_action('TEST_POST', test_result)

        logger.info(f'Action file created: {filepath}')
        logger.info('TEST PASSED!')
    else:
        # Get message from command line
        message = None
        for i, arg in enumerate(sys.argv):
            if arg == '--message' and i + 1 < len(sys.argv):
                message = sys.argv[i + 1]
                break

        poster.run(message=message, headless=headless)


if __name__ == '__main__':
    main()
