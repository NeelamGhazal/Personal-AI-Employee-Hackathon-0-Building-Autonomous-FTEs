from playwright.sync_api import sync_playwright
print("Playwright imported OK")
with sync_playwright() as p:
    print("Context started")
    browser = p.chromium.launch(headless=True, timeout=15000)
    print("Browser launched!")
    browser.close()
    print("SUCCESS!")
