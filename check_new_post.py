#!/usr/bin/env python3
"""Check for new LinkedIn post format"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("E:/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/linkedin_session")

print("Opening browser...")
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(SESSION_PATH),
        headless=False,
        viewport={'width': 1280, 'height': 900},
        timeout=60000
    )

    page = browser.new_page()
    page.goto("https://www.linkedin.com/company/112034239/admin/page-posts/published/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    content = page.content()

    # Check for new format
    print("\n--- Checking for post content ---")
    if "Excited to share" in content:
        print("[OK] Found 'Excited to share' - NEW FORMAT!")
    else:
        print("[!] 'Excited to share' NOT found")

    if "Email" in content and "WhatsApp" in content:
        print("[OK] Found 'Email' and 'WhatsApp'")
    else:
        print("[!] 'Email' or 'WhatsApp' NOT found")

    if "Odoo ERP" in content:
        print("[OK] Found 'Odoo ERP'")
    else:
        print("[!] 'Odoo ERP' NOT found")

    if "Future of Work" in content or "FutureOfWork" in content:
        print("[OK] Found 'FutureOfWork' hashtag")
    else:
        print("[!] 'FutureOfWork' hashtag NOT found")

    # Get first post text
    try:
        first_post = page.locator('article').first
        if first_post.count() > 0:
            text = first_post.inner_text()[:500]
            print(f"\n--- First post preview ---\n{text}")
    except:
        pass

    browser.close()
