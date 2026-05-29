# linkedin_diagnose.py - Find correct GoalGetters URL
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/linkedin_session")
SCREENSHOTS_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/AI_Employee_Vault/Business/Social_Media/screenshots")
SCREENSHOTS_PATH.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def main():
    print("=" * 60)
    print("LINKEDIN DIAGNOSTIC - Finding GoalGetters URL")
    print("=" * 60)

    with sync_playwright() as p:
        print("\n[1] Opening browser with saved session...")
        browser = p.chromium.launch_persistent_context(
            str(SESSION_PATH),
            headless=False,
            user_agent=USER_AGENT,
            viewport={'width': 1280, 'height': 900},
            args=['--disable-blink-features=AutomationControlled']
        )

        page = browser.new_page()

        # Step 1: Go to feed
        print("\n[2] Going to LinkedIn feed...")
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        time.sleep(5)

        current_url = page.url
        print(f"   URL: {current_url}")

        # Check login status
        if 'login' in current_url.lower() or 'signin' in current_url.lower():
            print("\n   NOT LOGGED IN - waiting 180s for manual login...")
            for i in range(180):
                if 'feed' in page.url.lower():
                    print("   Login detected!")
                    break
                if i % 30 == 0:
                    print(f"   Waiting {i}/180s...")
                time.sleep(1)
            time.sleep(3)

        # Screenshot of feed
        screenshot1 = SCREENSHOTS_PATH / "diag_1_feed.png"
        page.screenshot(path=str(screenshot1))
        print(f"   Screenshot: {screenshot1}")

        # Step 2: Try /company/goalgetters/
        print("\n[3] Going to /company/goalgetters/...")
        page.goto("https://www.linkedin.com/company/goalgetters/", timeout=60000)
        time.sleep(5)
        current_url = page.url
        print(f"   URL landed: {current_url}")

        screenshot2 = SCREENSHOTS_PATH / "diag_2_goalgetters.png"
        page.screenshot(path=str(screenshot2))
        print(f"   Screenshot: {screenshot2}")

        # Step 3: Try admin page
        print("\n[4] Going to /company/goalgetters/admin/...")
        page.goto("https://www.linkedin.com/company/goalgetters/admin/", timeout=60000)
        time.sleep(5)
        current_url = page.url
        print(f"   URL landed: {current_url}")

        screenshot3 = SCREENSHOTS_PATH / "diag_3_admin.png"
        page.screenshot(path=str(screenshot3))
        print(f"   Screenshot: {screenshot3}")

        # Step 4: Search for GoalGetters in company search
        print("\n[5] Searching for 'GoalGetters' company...")
        page.goto("https://www.linkedin.com/search/results/companies/?keywords=goalgetters", timeout=60000)
        time.sleep(5)

        screenshot4 = SCREENSHOTS_PATH / "diag_4_search.png"
        page.screenshot(path=str(screenshot4))
        print(f"   Screenshot: {screenshot4}")

        # Step 5: Go to profile page to see managed pages
        print("\n[6] Going to your pages...")
        page.goto("https://www.linkedin.com/company/setup/new/", timeout=60000)
        time.sleep(5)
        current_url = page.url
        print(f"   URL: {current_url}")

        screenshot5 = SCREENSHOTS_PATH / "diag_5_pages.png"
        page.screenshot(path=str(screenshot5))
        print(f"   Screenshot: {screenshot5}")

        # Step 6: Try to find pages from profile
        print("\n[7] Checking 'My pages' dropdown...")
        # Click on "For Business" or similar
        try:
            page.goto("https://www.linkedin.com/feed/", timeout=60000)
            time.sleep(3)
            # Look for "Me" icon and dropdown
            page.click('text="For Business"', timeout=5000)
            time.sleep(2)
            screenshot6 = SCREENSHOTS_PATH / "diag_6_business_dropdown.png"
            page.screenshot(path=str(screenshot6))
            print(f"   Screenshot: {screenshot6}")
        except:
            print("   Could not find For Business dropdown")

        print("\n" + "=" * 60)
        print("DIAGNOSTIC COMPLETE")
        print("Check screenshots in:")
        print(f"  {SCREENSHOTS_PATH}")
        print("\nKeeping browser open 30s for manual investigation...")
        print("=" * 60)
        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    main()
