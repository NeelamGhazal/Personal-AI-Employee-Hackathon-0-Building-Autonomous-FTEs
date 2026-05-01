# check_profile.py - Just check Twitter profile for tweets
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/twitter_session")
SCREENSHOTS_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/AI_Employee_Vault/Business/Social_Media/screenshots")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def main():
    print("Checking Twitter profile for tweets...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            str(SESSION_PATH),
            headless=False,
            user_agent=USER_AGENT,
            viewport={'width': 1280, 'height': 900},
            args=['--disable-blink-features=AutomationControlled']
        )

        page = browser.new_page()

        # Navigate directly to profile
        print("Navigating to profile...")
        page.goto("https://twitter.com/ShanayaKhan0907", timeout=60000)

        # Wait for page to fully load
        print("Waiting 8 seconds for full page load...")
        time.sleep(8)

        # Close any popups
        for _ in range(3):
            page.keyboard.press("Escape")
            time.sleep(0.3)

        time.sleep(1)

        # Dismiss verification banner if present
        try:
            close_btn = page.locator('button[aria-label="Close"]').first
            if close_btn.count() > 0:
                close_btn.click()
                time.sleep(1)
        except:
            pass

        # Scroll down to see tweets
        print("Scrolling down to see tweets...")
        page.evaluate("window.scrollBy(0, 400)")
        time.sleep(2)

        # Take screenshot showing the tweet
        screenshot_path = SCREENSHOTS_PATH / "profile_with_tweet.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}")

        # Try to get tweet text
        try:
            tweets = page.locator('[data-testid="tweetText"]').all()
            print(f"Found {len(tweets)} tweets on profile")
            for i, tweet in enumerate(tweets[:3]):
                text = tweet.text_content()
                print(f"Tweet {i+1}: {text[:100]}...")
        except Exception as e:
            print(f"Could not read tweets: {e}")

        # Keep open for viewing
        print("Keeping browser open for 10 seconds...")
        time.sleep(10)

        browser.close()

if __name__ == "__main__":
    main()
