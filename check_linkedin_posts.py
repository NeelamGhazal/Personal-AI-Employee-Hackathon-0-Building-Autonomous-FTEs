#!/usr/bin/env python3
"""Check LinkedIn published posts page"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("E:/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/linkedin_session")
SCREENSHOT_PATH = Path("E:/linkedin_posts_check.png")

print("Opening browser with saved session...")
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(SESSION_PATH),
        headless=False,
        viewport={'width': 1280, 'height': 900},
        timeout=60000
    )

    page = browser.new_page()

    print("Navigating to published posts page...")
    page.goto("https://www.linkedin.com/company/112034239/admin/page-posts/published/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    # Take screenshot (skip waiting for fonts)
    page.screenshot(path=str(SCREENSHOT_PATH), timeout=60000)
    print(f"Screenshot saved: {SCREENSHOT_PATH}")

    # Get page content to check
    content = page.content()

    # Check for our posts
    if "AI Employee" in content:
        print("[OK] Found 'AI Employee' in page content!")
    else:
        print("[!] 'AI Employee' NOT found in page content")

    if "Claude Code" in content:
        print("[OK] Found 'Claude Code' in page content!")
    else:
        print("[!] 'Claude Code' NOT found in page content")

    # Look for post elements
    posts = page.locator('div[data-test-id="page-post"]').count()
    print(f"Found {posts} post elements on page")

    browser.close()
    print("Done.")
