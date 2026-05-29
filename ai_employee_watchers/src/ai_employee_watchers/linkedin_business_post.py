# linkedin_business_post.py - Post to LinkedIn BUSINESS PAGE
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Paths
SESSION_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/linkedin_session")
SCREENSHOTS_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/AI_Employee_Vault/Business/Social_Media/screenshots")
SCREENSHOTS_PATH.mkdir(parents=True, exist_ok=True)

# CORRECT GoalGetters Company ID
COMPANY_ID = "112034239"
COMPANY_URL = f"https://www.linkedin.com/company/{COMPANY_ID}/"
COMPANY_ADMIN_URL = f"https://www.linkedin.com/company/{COMPANY_ID}/admin/"

# Message to post on GoalGetters business page
MESSAGE = "🤖 AI Employee is now managing GoalGetters! Automated posting, client management, and business operations via Claude Code. The future of business automation is here! #AIEmployee #ClaudeCode #GoalGetters #Automation #BusinessAutomation"

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

def main():
    # Check for --test flag
    test_mode = "--test" in sys.argv

    print("=" * 60)
    print("LINKEDIN BUSINESS PAGE POSTER - GoalGetters")
    print(f"Company ID: {COMPANY_ID}")
    print(f"Company URL: {COMPANY_URL}")
    if test_mode:
        print("*** TEST MODE - Will NOT actually post ***")
    print("=" * 60)

    with sync_playwright() as p:
        # Step 1: Open browser with saved session
        print("\n[Step 1] Opening Playwright browser with saved session...")
        browser = p.chromium.launch_persistent_context(
            str(SESSION_PATH),
            headless=False,
            user_agent=USER_AGENT,
            viewport={'width': 1280, 'height': 900},
            args=['--disable-blink-features=AutomationControlled']
        )

        page = browser.new_page()
        page.add_init_script(STEALTH_SCRIPT)

        # Step 2: Navigate directly to LinkedIn feed first
        print("[Step 2] Navigating to LinkedIn feed...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(8)

        # Check if we need to login
        current_url = page.url
        print(f"   Current URL: {current_url}")

        if 'login' in current_url.lower() or 'signin' in current_url.lower():
            print("\n" + "=" * 60)
            print("NOT LOGGED IN - Please login manually in the browser!")
            print("Waiting 3 minutes for login...")
            print("=" * 60 + "\n")

            for i in range(180):
                current_url = page.url
                if 'feed' in current_url.lower() and 'login' not in current_url.lower():
                    print("   Login successful!")
                    break
                if i % 30 == 0:
                    print(f"   Waiting... ({i}/180 seconds)")
                time.sleep(1)
            else:
                print("   Login timeout!")
                browser.close()
                return

        print("   Logged in to LinkedIn!")
        safe_screenshot(page, "post_step2_feed.png")
        time.sleep(3)

        # Press Escape to dismiss any popups
        print("\n[Step 3] Dismissing popups...")
        for _ in range(3):
            page.keyboard.press('Escape')
            time.sleep(0.5)
        time.sleep(2)

        # Step 4: Navigate to GoalGetters ADMIN page (where posting works)
        admin_url = f"https://www.linkedin.com/company/{COMPANY_ID}/admin/"
        print(f"\n[Step 4] Navigating to GoalGetters Admin: {admin_url}")
        page.goto(admin_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)

        # Check what page we're on
        current_url = page.url
        print(f"   Current URL: {current_url}")

        # Verify we're on the right page
        if 'unavailable' in current_url.lower():
            print("   ERROR: Page unavailable! Check company ID")
            safe_screenshot(page, "post_error_unavailable.png")
            browser.close()
            return

        # Take screenshot of the page
        safe_screenshot(page, "post_step4_admin_page.png")

        # Press Escape to dismiss any modals
        for _ in range(3):
            page.keyboard.press('Escape')
            time.sleep(0.5)
        time.sleep(2)

        # Step 5: Find and click "Start a post" or "Create post" button
        print("\n[Step 5] Looking for post button on admin page...")
        post_started = False

        # First scroll to top
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

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
                    time.sleep(2)
                    break
            except Exception as e:
                continue

        if not create_clicked:
            print("   Trying JavaScript to click Create...")
            try:
                page.evaluate("""
                    () => {
                        const btns = document.querySelectorAll('button');
                        for (const btn of btns) {
                            if (btn.textContent.toLowerCase().includes('create')) {
                                btn.click();
                                return;
                            }
                        }
                    }
                """)
                create_clicked = True
                time.sleep(2)
            except:
                pass

        # Step 5b: Now click "Start a post" from the dropdown menu
        print("   Looking for 'Start a post' in dropdown menu...")
        time.sleep(2)
        safe_screenshot(page, "post_step5b_create_menu.png")

        try:
            # Click "Start a post" option in the menu
            start_post = page.locator('div:has-text("Start a post")').first
            if start_post.count() > 0 and start_post.is_visible():
                print("   Found 'Start a post' option, clicking...")
                start_post.click()
                post_started = True
                time.sleep(3)
        except:
            pass

        if not post_started:
            # Try other selectors for "Start a post"
            try:
                page.click('text="Start a post"', timeout=5000)
                post_started = True
                time.sleep(3)
            except:
                pass

        if not post_started:
            print("   Trying JavaScript to click 'Start a post'...")
            try:
                clicked = page.evaluate("""
                    () => {
                        // Find menu items
                        const items = document.querySelectorAll('div, li, a, button');
                        for (const item of items) {
                            const text = item.textContent.trim();
                            if (text === 'Start a post' || text.startsWith('Start a post')) {
                                item.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                if clicked:
                    post_started = True
                    time.sleep(3)
            except:
                pass

        # If still not found, let's try the company feed page
        if not post_started:
            print("   Not found on admin, trying company posts page...")
            page.goto(f"https://www.linkedin.com/company/{COMPANY_ID}/posts/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(8)
            safe_screenshot(page, "post_step5_posts_page.png")

            # Try to find post button again
            try:
                clicked = page.evaluate("""
                    () => {
                        const btns = document.querySelectorAll('button, div[role="button"]');
                        for (const btn of btns) {
                            const text = btn.textContent.toLowerCase();
                            if (text.includes('start a post') || text.includes('create')) {
                                btn.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                if clicked:
                    post_started = True
                    time.sleep(3)
            except:
                pass

        if not post_started:
            print("   ERROR: Could not find Start a post button!")
            safe_screenshot(page, "post_error_no_button.png")
            print("   Keeping browser open 60s for manual inspection...")
            print("   Please note which page/button works for posting")
            time.sleep(60)
            browser.close()
            return

        # Step 6: Wait for editor modal
        print("\n[Step 6] Waiting for post editor...")
        safe_screenshot(page, "post_step6_after_click.png")
        time.sleep(3)

        # Step 7: Find and click the text editor
        print("[Step 7] Finding text editor...")
        editor_selectors = [
            '.ql-editor[data-placeholder]',
            'div[role="textbox"][contenteditable="true"]',
            '.editor-content[contenteditable="true"]',
            '[aria-label="Text editor for creating content"]',
            'div[contenteditable="true"]',
            'div.ql-editor',
        ]

        editor_found = False
        for selector in editor_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0 and elem.is_visible():
                    print(f"   Found editor: {selector}")
                    elem.click()
                    editor_found = True
                    time.sleep(1)
                    break
            except:
                continue

        if not editor_found:
            print("   Using JavaScript to find and focus editor...")
            try:
                page.evaluate("""
                    () => {
                        const editor = document.querySelector('[contenteditable="true"]');
                        if (editor) editor.focus();
                    }
                """)
            except:
                pass

        # Step 8: Type message character by character
        print(f"\n[Step 8] Typing message...")
        print(f"   Message: {MESSAGE[:60]}...")

        for char in MESSAGE:
            page.keyboard.type(char)
            time.sleep(0.03)  # 30ms delay - faster

        print("   Done typing!")
        time.sleep(2)

        # Take screenshot before posting
        print("\n[Step 9] Taking screenshot before posting...")
        safe_screenshot(page, "post_step9_before_submit.png")

        # TEST MODE - stop here
        if test_mode:
            print("\n" + "=" * 60)
            print("TEST MODE - NOT POSTING")
            print("Message typed successfully. Check screenshot.")
            print("Keeping browser open 30s for verification...")
            print("=" * 60)
            time.sleep(30)
            browser.close()
            return

        # Step 10: Click Post button with multiple methods
        print("\n[Step 10] Clicking Post button...")
        post_clicked = False

        # Method A: Find Post button directly
        post_selectors = [
            'button.share-actions__primary-action',
            'button[aria-label="Post"]',
            'button:has-text("Post"):not(:has-text("Start"))',
        ]

        for selector in post_selectors:
            try:
                btn = page.locator(selector).first
                if btn.count() > 0 and btn.is_visible():
                    print(f"   Found Post button: {selector}")
                    btn.click(force=True)
                    post_clicked = True
                    time.sleep(3)
                    break
            except:
                continue

        if not post_clicked:
            # Method B: JavaScript click
            print("   Method B: JavaScript click...")
            try:
                clicked = page.evaluate("""
                    () => {
                        const buttons = document.querySelectorAll('button');
                        for (const btn of buttons) {
                            const text = btn.textContent.trim().toLowerCase();
                            if (text === 'post' && !btn.disabled) {
                                btn.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                if clicked:
                    post_clicked = True
                    time.sleep(3)
            except:
                pass

        if not post_clicked:
            # Method C: Ctrl+Enter
            print("   Method C: Ctrl+Enter...")
            page.keyboard.press('Control+Enter')
            time.sleep(3)

        # Step 11: Wait for submission and verify
        print("\n[Step 11] Waiting for submission...")
        time.sleep(8)

        # Take screenshot immediately after submit
        safe_screenshot(page, "post_step11_after_submit.png")

        # Step 12: Navigate back to company page to verify post
        print("\n[Step 12] Verifying post on company page...")
        page.goto(COMPANY_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(8)

        # Scroll to see posts
        page.evaluate("window.scrollTo(0, 300)")
        time.sleep(2)

        # Take verification screenshot
        safe_screenshot(page, "post_step12_verification.png")

        # Check if our message appears on the page
        page_content = page.content()
        post_verified = MESSAGE[:30] in page_content or "AI Employee" in page_content

        print("\n" + "=" * 60)
        if post_verified:
            print("✓ POST VERIFIED - Message found on company page!")
        else:
            print("⚠ POST NOT VERIFIED - Message not found on page")
            print("  Check screenshots manually to confirm")
        print("=" * 60)

        # Keep browser open for verification
        print("\nKeeping browser open 20 seconds for manual verification...")
        time.sleep(20)

        browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    main()
