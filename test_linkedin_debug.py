#!/usr/bin/env python3
"""Debug test for LinkedIn browser launch"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

print("=" * 60)
print("DEBUG: LinkedIn Browser Launch Test")
print("=" * 60)

SESSION_PATH = Path("E:/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/linkedin_session")
print(f"Session path: {SESSION_PATH}")
print(f"Session exists: {SESSION_PATH.exists()}")

# Check for lock files
lock_files = ["SingletonLock", "SingletonSocket", "SingletonCookie"]
for lock in lock_files:
    lock_path = SESSION_PATH / lock
    print(f"Lock file {lock}: exists={lock_path.exists()}")

print("\nStarting Playwright...")
start = time.time()

with sync_playwright() as p:
    print(f"Playwright started in {time.time()-start:.2f}s")
    print("Launching browser...")
    start = time.time()

    try:
        browser = p.chromium.launch_persistent_context(
            str(SESSION_PATH),
            headless=False,  # Try with visible browser to see what happens
            viewport={'width': 1280, 'height': 900},
            args=['--no-sandbox', '--disable-gpu'],
            timeout=30000  # 30 second timeout
        )
        print(f"Browser launched in {time.time()-start:.2f}s")

        print("Creating new page...")
        page = browser.new_page()
        print("Page created")

        print("Closing browser...")
        browser.close()
        print("Browser closed")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

print("\nSUCCESS!")
