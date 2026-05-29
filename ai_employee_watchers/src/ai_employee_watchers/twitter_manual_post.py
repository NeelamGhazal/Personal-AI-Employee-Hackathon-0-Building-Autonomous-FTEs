# twitter_manual_post.py - Simple manual assisted Twitter posting
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Paths
SESSION_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/twitter_session")
SCREENSHOTS_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/AI_Employee_Vault/Business/Social_Media/screenshots")
SCREENSHOTS_PATH.mkdir(parents=True, exist_ok=True)

# Message to post
MESSAGE = "AI Employee May 5 test! #AIEmployee #ClaudeCode"

# Stealth settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
STEALTH_SCRIPT = """
try { Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true}); } catch(e) {}
try { Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en'], configurable: true}); } catch(e) {}
try { window.chrome = { runtime: {} }; } catch(e) {}
"""

def main():
    print("=" * 60)
    print("TWITTER MANUAL ASSISTED POSTING - ATTEMPT 3")
    print("=" * 60)

    with sync_playwright() as p:
        # Step 1: Open browser with saved session
        print("\n[Step 1] Opening Playwright browser with saved session...")
        browser = p.chromium.launch_persistent_context(
            str(SESSION_PATH),
            headless=False,
            user_agent=USER_AGENT,
            viewport={'width': 1280, 'height': 720},
            args=['--disable-blink-features=AutomationControlled']
        )

        page = browser.new_page()
        page.add_init_script(STEALTH_SCRIPT)

        # Step 2: Session should auto-login
        print("[Step 2] Session is saved - should auto login...")

        # Step 3: Navigate to home
        print("\n[Step 3] Navigating to https://twitter.com/home ...")
        page.goto("https://twitter.com/home", timeout=60000)

        # Step 4: Wait 5 seconds
        print("[Step 4] Waiting 5 seconds for page to load...")
        time.sleep(5)

        # IMPORTANT: Close any dialogs/popups first
        print("\n[Step 4.5] Closing any popups/dialogs...")
        for _ in range(3):
            page.keyboard.press("Escape")
            time.sleep(0.5)
        time.sleep(2)

        # Take a screenshot to see current state
        print("   Taking screenshot of current state...")
        page.screenshot(path=str(SCREENSHOTS_PATH / "step4_state.png"))

        # Step 5 & 6: Find and click the text box MULTIPLE times to ensure focus
        print("\n[Step 5] Finding the 'What is happening?!' text box...")
        print("[Step 6] Clicking on it MULTIPLE times to ensure focus...")

        # First, scroll to top to make sure compose box is visible
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        # Try to click the compose box area
        compose_clicked = False

        # Method 1: Click by test ID
        try:
            elem = page.locator('[data-testid="tweetTextarea_0"]').first
            if elem.count() > 0:
                print("   Found tweetTextarea_0, clicking...")
                elem.click()
                time.sleep(1)
                elem.click()  # Click again to ensure focus
                compose_clicked = True
        except Exception as e:
            print(f"   tweetTextarea_0 failed: {e}")

        # Method 2: Click the placeholder text
        if not compose_clicked:
            try:
                elem = page.locator('div[data-text="true"]').first
                if elem.count() > 0:
                    print("   Found data-text div, clicking...")
                    elem.click()
                    time.sleep(1)
                    compose_clicked = True
            except Exception as e:
                print(f"   data-text failed: {e}")

        # Method 3: Click the editor wrapper
        if not compose_clicked:
            try:
                elem = page.locator('.DraftEditor-editorContainer').first
                if elem.count() > 0:
                    print("   Found DraftEditor, clicking...")
                    elem.click()
                    time.sleep(1)
                    compose_clicked = True
            except Exception as e:
                print(f"   DraftEditor failed: {e}")

        # Take screenshot before typing
        print("   Taking screenshot before typing...")
        page.screenshot(path=str(SCREENSHOTS_PATH / "step6_before_type.png"))

        # Step 7: Type message character by character with 150ms delay
        print(f"\n[Step 7] Typing message character by character (150ms delay)...")
        print(f"   Message: {MESSAGE}")

        for i, char in enumerate(MESSAGE):
            page.keyboard.type(char)
            time.sleep(0.15)  # 150ms delay
            if (i + 1) % 20 == 0:
                print(f"   Typed {i + 1}/{len(MESSAGE)} characters...")

        print(f"   Typed all {len(MESSAGE)} characters!")

        # Step 8: Wait 3 seconds
        print("\n[Step 8] Waiting 3 seconds...")
        time.sleep(3)

        # Step 9: Screenshot BEFORE clicking post
        print("\n[Step 9] Taking screenshot BEFORE clicking post...")
        before_path = SCREENSHOTS_PATH / "before_post.png"
        page.screenshot(path=str(before_path))
        print(f"   Saved: {before_path}")

        # Check if Post button is NOW enabled (should be if text was entered correctly)
        print("\n   Checking Post button state...")
        try:
            btn = page.locator('[data-testid="tweetButtonInline"]').first
            aria_disabled = btn.get_attribute("aria-disabled")
            print(f"   Post button aria-disabled: {aria_disabled}")

            if aria_disabled == "true":
                print("   WARNING: Post button is still disabled!")
                print("   Text may not have been entered into the compose box.")
            else:
                print("   Post button is ENABLED!")
        except Exception as e:
            print(f"   Could not check button state: {e}")

        # Step 10: Click the Post button
        print("\n[Step 10] Clicking the Post button...")

        try:
            # First try Ctrl+Enter
            print("   Trying Ctrl+Enter...")
            page.keyboard.press("Control+Enter")
            time.sleep(3)
        except:
            pass

        try:
            btn = page.locator('[data-testid="tweetButtonInline"]').first
            if btn.count() > 0:
                print("   Clicking Post button with force...")
                btn.click(force=True)
                time.sleep(3)
        except Exception as e:
            print(f"   Click failed: {e}")

        # Step 11: Wait 5 seconds
        print("\n[Step 11] Waiting 5 seconds after posting attempts...")
        time.sleep(5)

        # Step 12: Screenshot AFTER posting
        print("\n[Step 12] Taking screenshot AFTER posting...")
        after_path = SCREENSHOTS_PATH / "after_post.png"
        page.screenshot(path=str(after_path))
        print(f"   Saved: {after_path}")

        # Step 13: Navigate to profile
        print("\n[Step 13] Navigating to https://twitter.com/ShanayaKhan0907 ...")
        page.goto("https://twitter.com/ShanayaKhan0907", timeout=60000)
        time.sleep(5)

        # Step 14: Screenshot of profile
        print("\n[Step 14] Taking screenshot of profile...")
        profile_path = SCREENSHOTS_PATH / "profile_with_tweet.png"
        page.screenshot(path=str(profile_path))
        print(f"   Saved: {profile_path}")

        print("\n" + "=" * 60)
        print("DONE! Screenshots saved:")
        print(f"  1. {before_path}")
        print(f"  2. {after_path}")
        print(f"  3. {profile_path}")
        print("=" * 60)

        # Keep browser open for 10 seconds for user to verify
        print("\nKeeping browser open for 10 seconds for verification...")
        time.sleep(10)

        browser.close()
        print("\nBrowser closed.")

if __name__ == "__main__":
    main()
