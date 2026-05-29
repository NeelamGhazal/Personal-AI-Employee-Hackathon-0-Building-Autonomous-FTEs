# linkedin_find_page.py - Find correct GoalGetters URL by clicking sidebar
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/linkedin_session")
SCREENSHOTS_PATH = Path("/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/AI_Employee_Vault/Business/Social_Media/screenshots")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def main():
    print("=" * 60)
    print("FINDING GOALGETTERS URL")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            str(SESSION_PATH),
            headless=False,
            user_agent=USER_AGENT,
            viewport={'width': 1280, 'height': 900},
            args=['--disable-blink-features=AutomationControlled']
        )

        page = browser.new_page()

        # Go to feed with domcontentloaded wait
        print("\n[1] Going to LinkedIn feed...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(8)

        current_url = page.url
        print(f"   URL: {current_url}")
        page.screenshot(path=str(SCREENSHOTS_PATH / "step1_feed.png"))

        # Find all href containing /company/
        print("\n[2] Scanning page for company links...")
        try:
            links = page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="/company/"]'));
                    return links.map(a => ({href: a.href, text: a.textContent.trim().slice(0,50)}));
                }
            """)
            for link in links[:20]:
                print(f"   {link['href']} - {link['text']}")
        except Exception as e:
            print(f"   Error: {e}")

        # Click on GoalGetters in sidebar
        print("\n[3] Clicking GoalGetters in sidebar...")
        try:
            # Look for the specific sidebar link
            sidebar = page.locator('aside').first
            goalgetters_link = sidebar.locator('a:has-text("GoalGetters")').first
            if goalgetters_link.count() > 0:
                href = goalgetters_link.get_attribute('href')
                print(f"   Found sidebar link: {href}")
                goalgetters_link.click()
                time.sleep(5)
                current_url = page.url
                print(f"   Landed: {current_url}")
                page.screenshot(path=str(SCREENSHOTS_PATH / "goalgetters_from_sidebar.png"))
        except Exception as e:
            print(f"   Sidebar click failed: {e}")

        # Try the search and click Tech company
        print("\n[4] Going to search results...")
        page.goto("https://www.linkedin.com/search/results/companies/?keywords=goalgetters",
                  wait_until="domcontentloaded", timeout=30000)
        time.sleep(8)

        # Extract all company hrefs
        print("\n[5] Extracting company URLs from search...")
        try:
            links = page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="/company/"]'));
                    return links.map(a => a.href).filter((v, i, a) => a.indexOf(v) === i);
                }
            """)
            for link in links[:15]:
                if 'goalgetters' in link.lower() or 'goal' in link.lower():
                    print(f"   {link}")
        except Exception as e:
            print(f"   Error: {e}")

        # Click the Technology one
        print("\n[6] Clicking Technology, Information and Internet company...")
        try:
            # Find anchor with that text
            tech_parent = page.locator('span:has-text("Technology, Information and Internet")').first
            if tech_parent.count() > 0:
                # Find parent link
                parent_link = tech_parent.locator('xpath=ancestor::a').first
                if parent_link.count() > 0:
                    href = parent_link.get_attribute('href')
                    print(f"   Link found: {href}")
                    parent_link.click()
                    time.sleep(5)
                    current_url = page.url
                    print(f"   Landed: {current_url}")
                    page.screenshot(path=str(SCREENSHOTS_PATH / "goalgetters_tech_clicked.png"))
        except Exception as e:
            print(f"   Error: {e}")

        print("\n" + "=" * 60)
        print(f"FINAL URL: {page.url}")
        print("KEEPING BROWSER OPEN 45s")
        print("=" * 60)
        time.sleep(45)

        browser.close()

if __name__ == "__main__":
    main()
