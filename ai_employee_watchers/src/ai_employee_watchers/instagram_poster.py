# instagram_poster.py - Posts to Instagram using Playwright browser automation
import logging
import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('InstagramPoster')


class InstagramPoster:
    """Posts content to Instagram using Playwright browser automation"""

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

        self.posted_ids_file = self.vault_path / '.instagram_posted_ids.json'
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
        """Wait for user to login to Instagram"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('WAITING FOR INSTAGRAM LOGIN...')
        logger.info('=' * 60)

        # Step 1: Wait for page to load
        logger.info('Step 1: Waiting for page to load (10 seconds)...')
        time.sleep(10)

        # Step 2: Check if already logged in
        logger.info('Step 2: Checking if already logged in...')
        try:
            logged_in = page.query_selector('[aria-label="Home"]') or \
                        page.query_selector('[aria-label="New post"]') or \
                        page.query_selector('svg[aria-label="Home"]') or \
                        page.query_selector('[href="/direct/inbox/"]')

            if logged_in:
                logger.info('')
                logger.info('=' * 60)
                logger.info('SUCCESS: Already logged in to Instagram!')
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

        for i in range(120):
            try:
                logged_in = page.query_selector('[aria-label="Home"]') or \
                            page.query_selector('[aria-label="New post"]') or \
                            page.query_selector('svg[aria-label="Home"]')

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

    def create_image_with_text(self, message: str) -> str:
        """Create an image with text for Instagram post - LARGE BOLD TEXT"""
        logger.info('Creating image with text (large bold)...')

        # Create a 1080x1080 image (Instagram square format)
        width, height = 1080, 1080

        # Dark gradient background (dark blue to purple)
        img = Image.new('RGB', (width, height), color=(20, 20, 40))

        draw = ImageDraw.Draw(img)

        # Add dark gradient effect
        for i in range(height):
            r = int(20 + (i / height) * 30)
            g = int(20 + (i / height) * 20)
            b = int(40 + (i / height) * 60)
            draw.line([(0, i), (width, i)], fill=(r, g, b))

        # LARGE BOLD font - try multiple paths for Windows/Linux
        font_size = 72  # Larger font
        small_font_size = 48
        font = None
        small_font = None

        # Font paths to try (Windows first, then Linux)
        bold_font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold (Windows)
            "C:/Windows/Fonts/calibrib.ttf",     # Calibri Bold (Windows)
            "C:/Windows/Fonts/segoeui.ttf",      # Segoe UI (Windows)
            "C:/Windows/Fonts/impact.ttf",       # Impact (Windows) - very bold
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
        ]

        for font_path in bold_font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                small_font = ImageFont.truetype(font_path, small_font_size)
                logger.info(f'Using font: {font_path}')
                break
            except:
                continue

        if font is None:
            logger.warning('No TrueType font found, using default')
            font = ImageFont.load_default()
            small_font = font

        # Wrap text to fit with wider margins
        max_width = width - 150  # More margin
        words = message.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Calculate total text height with more spacing
        line_height = font_size + 30  # More line spacing
        total_height = len(lines) * line_height
        start_y = (height - total_height) // 2 - 40  # Shift up a bit

        # Draw text with stronger shadow effect
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + i * line_height

            # Stronger shadow (multiple layers for bold effect)
            for offset in [(4, 4), (3, 3), (2, 2)]:
                draw.text((x + offset[0], y + offset[1]), line, font=font, fill=(0, 0, 0))
            # Main text - bright white
            draw.text((x, y), line, font=font, fill=(255, 255, 255))

        # Add branding at bottom
        branding = "GoalGetters AI Employee"
        bbox = draw.textbbox((0, 0), branding, font=small_font)
        brand_x = (width - (bbox[2] - bbox[0])) // 2
        # Shadow for branding
        draw.text((brand_x + 2, height - 100 + 2), branding, font=small_font, fill=(0, 0, 0))
        draw.text((brand_x, height - 100), branding, font=small_font, fill=(255, 255, 255))

        # Save to temp file
        temp_path = self.screenshots_path / 'temp_instagram_image.png'
        img.save(str(temp_path), 'PNG')
        logger.info(f'Created image: {temp_path}')

        return str(temp_path)

    def create_post(self, page, message: str, image_path: str = None) -> dict:
        """Create a post on Instagram (requires image)"""
        logger.info('Creating Instagram post...')

        temp_image = None
        try:
            # Create image with message text
            temp_image = self.create_image_with_text(message)
            logger.info(f'Using image: {temp_image}')

            # Navigate to Instagram home
            page.goto('https://www.instagram.com/', timeout=30000)
            time.sleep(3)

            # Step 1: Click Create/New Post button to open modal
            logger.info('Step 1: Opening create modal...')
            try:
                page.click('[aria-label="New post"]', timeout=5000)
            except:
                try:
                    page.click('text="Create"', timeout=5000)
                except:
                    page.click('svg[aria-label="New post"]', force=True, timeout=5000)

            # Wait for modal to appear
            logger.info('Waiting for modal...')
            time.sleep(3)

            # Step 2: Look for "Select from computer" button inside modal and click it
            logger.info('Step 2: Looking for Select button in modal...')
            uploaded = False

            # Try to find and click "Select from computer" with file chooser
            try:
                with page.expect_file_chooser(timeout=15000) as fc_info:
                    # Try clicking various selectors for the select button
                    try:
                        page.click('button:has-text("Select from computer")', timeout=3000)
                    except:
                        try:
                            page.click('button:has-text("Select From Computer")', timeout=3000)
                        except:
                            try:
                                page.click('text="Select from computer"', timeout=3000)
                            except:
                                # Click on the media icon in the modal
                                page.click('svg[aria-label="Post"]', timeout=3000)

                file_chooser = fc_info.value
                file_chooser.set_files(temp_image)
                logger.info('Image uploaded!')
                uploaded = True
            except Exception as e:
                logger.info(f'Select button method failed: {e}')

            # Alternative: try direct file input approach
            if not uploaded:
                try:
                    logger.info('Trying direct file input...')
                    # Instagram might have added a file input to the page
                    page.locator('input[type="file"]').set_input_files(temp_image, timeout=5000)
                    logger.info('Image uploaded via file input!')
                    uploaded = True
                except Exception as e:
                    logger.info(f'Direct input failed: {e}')

            if not uploaded:
                page.screenshot(path=str(self.screenshots_path / 'debug_modal.png'))
                raise Exception('Could not upload image')

            time.sleep(5)

            # Click Next button (first time - crop screen)
            logger.info('Looking for Next button...')
            time.sleep(2)
            try:
                page.click('div[role="button"]:has-text("Next")', timeout=5000)
                logger.info('Clicked Next (crop)')
            except:
                try:
                    page.click('text="Next"', timeout=3000)
                    logger.info('Clicked Next via text')
                except:
                    logger.info('No Next button found (crop)')
            time.sleep(2)

            # Click Next again (filters screen)
            try:
                page.click('div[role="button"]:has-text("Next")', timeout=5000)
                logger.info('Clicked Next (filters)')
            except:
                try:
                    page.click('text="Next"', timeout=3000)
                    logger.info('Clicked Next via text')
                except:
                    logger.info('No Next button found (filters)')
            time.sleep(2)

            # Add caption if there's a caption field
            logger.info('Adding caption...')
            try:
                caption_area = page.locator('[aria-label="Write a caption..."]').first
                if caption_area.count() > 0:
                    caption_area.click()
                    time.sleep(0.5)
                    page.keyboard.type(message, delay=30)
                    time.sleep(1)
                    logger.info('Caption added')
            except Exception as e:
                logger.info(f'Could not add caption: {e}')

            # Click Share button - use specific selector
            logger.info('Looking for Share button...')
            share_clicked = False
            try:
                # The Share button is usually in the header of the modal
                page.locator('div[role="dialog"] >> div[role="button"]:has-text("Share")').click(timeout=5000)
                logger.info('Clicked Share in dialog!')
                share_clicked = True
            except:
                pass

            if not share_clicked:
                try:
                    # Try clicking a visible Share span/div
                    page.locator('div:has-text("Share"):visible').last.click(timeout=5000)
                    logger.info('Clicked Share via visible div!')
                    share_clicked = True
                except:
                    pass

            if not share_clicked:
                try:
                    # Use keyboard shortcut if available
                    page.keyboard.press('Enter')
                    logger.info('Pressed Enter as Share fallback')
                    share_clicked = True
                except:
                    pass

            if share_clicked:
                logger.info('Share action completed!')
            else:
                logger.info('Could not click Share button')

            time.sleep(8)  # Wait for post to upload

            # Take screenshot as proof
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.screenshots_path / f'instagram_post_{timestamp}.png'
            page.screenshot(path=str(screenshot_path))

            # Also save standard filename
            standard_screenshot = self.screenshots_path / 'instagram_post.png'
            page.screenshot(path=str(standard_screenshot))

            return {
                'success': True,
                'platform': 'instagram',
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'screenshot': str(screenshot_path),
                'note': 'Image created and uploaded successfully'
            }

        except Exception as e:
            logger.error(f'Error creating post: {e}')
            return {
                'success': False,
                'platform': 'instagram',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        finally:
            # Clean up temp image
            if temp_image and os.path.exists(temp_image):
                try:
                    os.remove(temp_image)
                    logger.info('Cleaned up temp image')
                except:
                    pass

    def create_action_file(self, post_result: dict) -> Path:
        """Create action file for the post"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"INSTAGRAM_POST_{timestamp}.md"
        filepath = self.social_media_path / filename

        status = 'posted' if post_result.get('success') else 'failed'

        content = f'''---
type: social_media_post
platform: instagram
status: {status}
posted_at: {post_result.get('timestamp')}
---

# Instagram Post

## Status
**{status.upper()}**

## Content
{post_result.get('message', 'N/A')}

## Screenshot
{f"![[{Path(post_result.get('screenshot', '')).name}]]" if post_result.get('screenshot') else 'N/A'}

## Details
- Platform: Instagram
- Posted: {post_result.get('timestamp')}
- Success: {post_result.get('success', False)}
{f"- Note: {post_result.get('note')}" if post_result.get('note') else ''}
{f"- Error: {post_result.get('error')}" if post_result.get('error') else ''}

---
*Generated by InstagramPoster (Gold Tier)*
'''
        filepath.write_text(content)
        logger.info(f'Created action file: {filename}')
        return filepath

    def log_action(self, action: str, details: dict):
        """Log action to Logs folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f'instagram_{timestamp}.log'

        log_content = f'''[{datetime.now().isoformat()}] {action}
Details: {json.dumps(details, indent=2)}
'''
        with open(log_file, 'a') as f:
            f.write(log_content)

    def run(self, message: str = None, headless: bool = False):
        """Run the Instagram poster"""
        logger.info('')
        logger.info('=' * 60)
        logger.info('STARTING INSTAGRAM POSTER')
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
                logger.info('Navigating to https://www.instagram.com ...')
                page.goto('https://www.instagram.com', timeout=60000)

                if not self.wait_for_login(page):
                    logger.error('Exiting due to login failure.')
                    browser.close()
                    return

                if message:
                    result = self.create_post(page, message)
                    self.create_action_file(result)
                    self.log_action('POST', result)

                    if result['success']:
                        post_id = f"ig_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        self.posted_ids.append(post_id)
                        self._save_posted_ids()
                        logger.info('Post action completed!')
                    else:
                        logger.error(f'Post failed: {result.get("error")}')
                else:
                    logger.info('No message provided. Login successful, session saved.')

            except Exception as e:
                logger.error(f'Error: {e}')

            finally:
                browser.close()

        logger.info('Instagram Poster stopped.')


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    default_session = Path(__file__).parent.parent.parent.parent / 'credentials' / 'instagram_session'

    vault_path = default_vault
    session_path = default_session

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    headless = '--headless' in sys.argv
    test_mode = '--test' in sys.argv

    poster = InstagramPoster(str(vault_path), str(session_path))

    if test_mode:
        logger.info('')
        logger.info('=' * 60)
        logger.info('RUNNING IN TEST MODE')
        logger.info('=' * 60)
        logger.info('Simulating an Instagram post...')

        test_result = {
            'success': True,
            'platform': 'instagram',
            'message': 'Test post from AI Employee! This is a simulated Instagram post. #AIEmployee #GoldTier #Automation',
            'timestamp': datetime.now().isoformat(),
            'screenshot': None,
            'note': 'Test mode - no actual posting'
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
        message = None
        for i, arg in enumerate(sys.argv):
            if arg == '--message' and i + 1 < len(sys.argv):
                message = sys.argv[i + 1]
                break

        poster.run(message=message, headless=headless)


if __name__ == '__main__':
    main()
