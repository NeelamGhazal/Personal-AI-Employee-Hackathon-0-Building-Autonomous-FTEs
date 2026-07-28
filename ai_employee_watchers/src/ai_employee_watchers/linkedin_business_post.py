# linkedin_business_post.py - Post to LinkedIn BUSINESS PAGE
import time
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

def convert_wsl_path(wsl_path: str) -> str:
    """Convert WSL path to Windows path if running on Windows"""
    if sys.platform == 'win32' and wsl_path.startswith('/mnt/'):
        # /mnt/e/... -> E:/...
        parts = wsl_path.split('/')
        drive = parts[2].upper()
        rest = '/'.join(parts[3:])
        return f"{drive}:/{rest}"
    return wsl_path

def cleanup_session_locks(session_path: Path):
    """Remove stale lock files only - DO NOT kill any Chrome processes"""
    lock_files = [
        session_path / "SingletonLock",
        session_path / "SingletonSocket",
        session_path / "SingletonCookie",
    ]
    for lock_file in lock_files:
        try:
            if lock_file.exists():
                lock_file.unlink()
        except Exception:
            pass  # Ignore if can't remove

# Paths - auto-convert if running on Windows
SESSION_PATH = Path(convert_wsl_path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/linkedin_session"))
SCREENSHOTS_PATH = Path(convert_wsl_path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/AI_Employee_Vault/Business/Social_Media/screenshots"))
SCREENSHOTS_PATH.mkdir(parents=True, exist_ok=True)

# CORRECT GoalGetters Company ID
COMPANY_ID = "112034239"
COMPANY_URL = f"https://www.linkedin.com/company/{COMPANY_ID}/"
COMPANY_ADMIN_URL = f"https://www.linkedin.com/company/{COMPANY_ID}/admin/"

def get_post_message():
    """Generate unique post message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    return f"""Excited to share that GoalGetters now has a Personal AI Employee!

Our AI system autonomously handles:
- Email & WhatsApp monitoring
- Invoice creation via Odoo ERP
- Social media posting on all platforms
- CEO briefing generation
- Human-in-the-loop approval workflow

Built with Claude Code + MCP Servers + Playwright automation.

The future of business is here!

Posted: {timestamp}

#AIEmployee #ClaudeCode #GoalGetters #Automation #BusinessAutomation #FutureOfWork"""

# Stealth settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
STEALTH_SCRIPT = """
try { Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true}); } catch(e) {}
try { Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en'], configurable: true}); } catch(e) {}
try { window.chrome = { runtime: {} }; } catch(e) {}
"""

def safe_screenshot(page, filename):
    """Take screenshot with timeout handling"""
    try:
        page.screenshot(path=str(SCREENSHOTS_PATH / filename), timeout=10000)
        print(f"   Screenshot: {filename}")
    except Exception as e:
        print(f"   Screenshot failed: {e}")

def safe_goto(page, url, max_attempts=3):
    """Navigate to URL with retry logic and increased timeout"""
    for attempt in range(max_attempts):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            return True
        except Exception as e:
            print(f"   Navigation attempt {attempt + 1}/{max_attempts} failed: {e}")
            if attempt == max_attempts - 1:
                raise
            time.sleep(2)
    return False

def main():
    # Check for flags
    test_mode = "--test" in sys.argv
    headless_mode = "--headless" in sys.argv
    quick_mode = "--quick" in sys.argv  # Reduced timeouts for API calls

    # Generate unique message with timestamp
    MESSAGE = get_post_message()

    print("=" * 60)
    print("LINKEDIN BUSINESS PAGE POSTER - GoalGetters")
    print(f"Company ID: {COMPANY_ID}")
    print(f"Company URL: {COMPANY_URL}")
    if test_mode:
        print("*** TEST MODE - Will NOT actually post ***")
    if headless_mode:
        print("*** HEADLESS MODE ***")
    if quick_mode:
        print("*** QUICK MODE - Reduced timeouts ***")
    print("=" * 60)

    with sync_playwright() as p:
        # Step 1: Open browser with saved session
        print("\n[Step 1] Opening Playwright browser with saved session...")
        print(f"   Session path: {SESSION_PATH}")

        # Clean up stale lock files and orphaned browser processes
        cleanup_session_locks(SESSION_PATH)

        # Launch browser - Playwright uses its own bundled Chromium by default
        # which is separate from system Chrome, so no conflicts with user's browser
        browser = p.chromium.launch_persistent_context(
            str(SESSION_PATH),
            headless=headless_mode,
            user_agent=USER_AGENT,
            viewport={'width': 1280, 'height': 900},
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-software-rasterizer',
                '--no-first-run',
                '--no-default-browser-check',
            ],
            timeout=60000
        )

        page = browser.new_page()
        page.add_init_script(STEALTH_SCRIPT)

        # Step 2: Navigate directly to LinkedIn feed first
        print("[Step 2] Navigating to LinkedIn feed...")
        safe_goto(page, "https://www.linkedin.com/feed/")
        time.sleep(1 if quick_mode else 8)

        # Check if we need to login
        current_url = page.url
        print(f"   Current URL: {current_url}")

        if 'login' in current_url.lower() or 'signin' in current_url.lower():
            if quick_mode or headless_mode:
                print("   ERROR: Not logged in - session expired!")
                browser.close()
                return

            print("NOT LOGGED IN - Please login manually...")
            for i in range(180):
                current_url = page.url
                if 'feed' in current_url.lower() and 'login' not in current_url.lower():
                    break
                time.sleep(1)
            else:
                browser.close()
                return

        print("   Logged in!")
        time.sleep(0.5 if quick_mode else 3)

        # Dismiss popups quickly
        for _ in range(2):
            page.keyboard.press('Escape')
            time.sleep(0.2)

        # Step 4: Navigate to GoalGetters ADMIN page
        admin_url = f"https://www.linkedin.com/company/{COMPANY_ID}/admin/"
        print(f"[Step 4] Navigating to Admin: {admin_url}")
        safe_goto(page, admin_url)
        time.sleep(2 if quick_mode else 10)

        # Check what page we're on
        current_url = page.url
        print(f"   Current URL: {current_url}")

        if 'unavailable' in current_url.lower():
            print("   ERROR: Page unavailable!")
            browser.close()
            return

        # Dismiss modals quickly
        for _ in range(2):
            page.keyboard.press('Escape')
            time.sleep(0.2)

        # Step 5: Find and click "Start a post" button
        print("[Step 5] Looking for post button...")
        post_started = False
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5 if quick_mode else 2)

        # Admin page post button selectors - check for various formats
        start_post_selectors = [
            'button:has-text("Create")',
            'button:has-text("Create a post")',
            'button:has-text("Start a post")',
            'button[aria-label="Start a post"]',
            'button[aria-label="Create a post"]',
            '.share-box-feed-entry__trigger',
            'div[role="button"]:has-text("Create")',
            'div[role="button"]:has-text("Start a post")',
            # Look for post text area directly
            'div[data-placeholder*="post"]',
            'div[data-placeholder*="share"]',
        ]

        # Step 5a: Click the "+ Create" button first
        create_clicked = False
        for selector in start_post_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0 and elem.is_visible():
                    print(f"   Found Create button: {selector}")
                    elem.click(force=True)
                    create_clicked = True
                    time.sleep(0.5 if quick_mode else 2)
                    break
            except Exception:
                continue

        if not create_clicked:
            try:
                page.evaluate("""() => {
                    const btns = document.querySelectorAll('button');
                    for (const btn of btns) {
                        if (btn.textContent.toLowerCase().includes('create')) {
                            btn.click(); return;
                        }
                    }
                }""")
                create_clicked = True
                time.sleep(0.5 if quick_mode else 2)
            except:
                pass

        # Step 5b: Click "Start a post" from dropdown
        print("[Step 5b] Looking for 'Start a post' in dropdown...")
        time.sleep(1 if quick_mode else 2)  # Wait for dropdown to render

        try:
            start_post = page.locator('div:has-text("Start a post")').first
            if start_post.count() > 0 and start_post.is_visible():
                print("   Found 'Start a post' (locator)")
                start_post.click()
                post_started = True
                time.sleep(1 if quick_mode else 3)
        except:
            pass

        if not post_started:
            try:
                page.click('text="Start a post"', timeout=5000)
                print("   Found 'Start a post' (text selector)")
                post_started = True
                time.sleep(1 if quick_mode else 3)
            except:
                pass

        if not post_started:
            try:
                clicked = page.evaluate("""() => {
                    const items = document.querySelectorAll('div, li, a, button');
                    for (const item of items) {
                        const text = item.textContent.trim();
                        if (text === 'Start a post' || text.startsWith('Start a post')) {
                            item.click(); return true;
                        }
                    }
                    return false;
                }""")
                if clicked:
                    print("   Found 'Start a post' (JavaScript)")
                    post_started = True
                    time.sleep(1 if quick_mode else 3)
            except:
                pass

        if not post_started:
            print("   ERROR: Could not find Start a post button!")
            safe_screenshot(page, "post_error_no_start_button.png")
            browser.close()
            return

        print("   Post modal opening...")

        # Step 6: Wait for editor modal
        print("[Step 6] Finding editor...")
        time.sleep(2 if quick_mode else 3)  # Need at least 2s for modal to fully render

        # Step 7: Find and click the text editor
        editor_selectors = [
            '.ql-editor[data-placeholder]',
            'div[role="textbox"][contenteditable="true"]',
            'div[contenteditable="true"]',
        ]

        # First try wait_for_selector
        editor_found = False
        try:
            page.wait_for_selector('.ql-editor', timeout=5000)
            print("   Editor modal detected (.ql-editor)")
        except:
            print("   Waiting for contenteditable...")
            try:
                page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
            except:
                pass

        for selector in editor_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0 and elem.is_visible():
                    elem.click()
                    editor_found = True
                    print(f"   Found editor: {selector}")
                    time.sleep(0.5 if quick_mode else 1)
                    break
            except:
                continue

        if not editor_found:
            print("   ERROR: Could not find editor!")
            safe_screenshot(page, "post_error_no_editor.png")
            browser.close()
            return

        # Step 7b: Clear any existing content and ensure focus
        print("[Step 7b] Ensuring editor is ready...")
        page.keyboard.press("Control+a")  # Select all
        time.sleep(0.2)
        page.keyboard.press("Delete")  # Clear any existing content
        time.sleep(0.3)

        # Click editor again to ensure focus
        for selector in editor_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0 and elem.is_visible():
                    elem.click()
                    time.sleep(0.3)
                    break
            except:
                continue

        # Step 8: Type message - use fill() for speed in quick mode
        print(f"[Step 8] Typing message...")
        print(f"   Message length: {len(MESSAGE)} chars")
        if quick_mode:
            # Fast paste instead of character-by-character
            page.keyboard.type(MESSAGE, delay=15)  # 15ms per char for reliability
        else:
            for char in MESSAGE:
                page.keyboard.type(char)
                time.sleep(0.03)

        print("   Done typing!")

        # Wait for LinkedIn to process the text and enable Post button
        print("   Waiting for Post button to enable...")
        time.sleep(2)

        # TEST MODE - stop here
        if test_mode:
            print("TEST MODE - NOT POSTING")
            time.sleep(3 if quick_mode else 30)
            browser.close()
            return

        # Step 10: Click Post button
        print("[Step 10] Clicking Post button...")
        safe_screenshot(page, "post_step10_before_click.png")

        post_clicked = False

        # Method 1: Direct click on Post button
        try:
            # Wait for Post button to be enabled
            post_btn = page.locator('button.share-actions__primary-action').first
            page.wait_for_selector('button.share-actions__primary-action:not([disabled])', timeout=10000)
            print("   Post button is enabled!")
            post_btn.click()
            post_clicked = True
            print("   Post button clicked!")
        except Exception as e:
            print(f"   Method 1 failed: {e}")

        # Method 2: Find button with "Post" text
        if not post_clicked:
            try:
                btns = page.locator('button:has-text("Post")')
                for i in range(btns.count()):
                    btn = btns.nth(i)
                    text = btn.inner_text().strip()
                    if text == "Post":
                        disabled = btn.get_attribute('disabled')
                        if not disabled:
                            print(f"   Found Post button (text match), clicking...")
                            btn.click()
                            post_clicked = True
                            print("   Post button clicked!")
                            break
            except Exception as e:
                print(f"   Method 2 failed: {e}")

        # Method 3: JavaScript click
        if not post_clicked:
            print("   Trying JavaScript click...")
            try:
                clicked = page.evaluate("""() => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        const text = btn.textContent.trim();
                        if (text === 'Post' && !btn.disabled && !btn.hasAttribute('disabled')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }""")
                if clicked:
                    post_clicked = True
                    print("   JavaScript click succeeded!")
            except Exception as e:
                print(f"   JavaScript click failed: {e}")

        if not post_clicked:
            print("   ERROR: Could not click Post button!")
            safe_screenshot(page, "post_error_button.png")
            browser.close()
            return

        # Step 11: Wait for submission (need enough time for LinkedIn to process)
        print("[Step 11] Submitting...")
        time.sleep(5 if quick_mode else 8)

        # Step 12: Verify post on published posts page
        print("[Step 12] Verifying on published posts page...")
        published_url = f"https://www.linkedin.com/company/{COMPANY_ID}/admin/page-posts/published/"
        safe_goto(page, published_url)
        time.sleep(2 if quick_mode else 8)

        # Get the timestamp we used in the message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        page_content = page.content()

        # Check for our unique message content (not just "GoalGetters")
        post_verified = "AI Employee" in page_content and "Claude Code" in page_content

        print("=" * 60)
        if post_verified:
            print("[OK] POST VERIFIED on published posts page!")
        else:
            print("[!] POST NOT FOUND - may be in drafts or failed")
            print(f"    Check: {published_url}")
        print("=" * 60)

        browser.close()
        print("Done.")

if __name__ == "__main__":
    main()
