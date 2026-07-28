#!/usr/bin/env python3
"""Refresh Twitter session by logging in manually"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("E:/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/credentials/twitter_session")

print("=" * 60)
print("TWITTER SESSION REFRESH")
print("=" * 60)
print("Opening Twitter - please log in manually")
print("The session will be saved for future use")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(SESSION_PATH),
        headless=False,
        viewport={'width': 1280, 'height': 900},
        timeout=60000
    )

    page = browser.new_page()
    page.goto("https://twitter.com/login", timeout=30000)

    print("\n>>> LOG IN TO TWITTER IN THE BROWSER WINDOW <<<")
    print("\nWaiting for login... (checking every 10 seconds)")

    for i in range(30):  # Wait up to 5 minutes
        time.sleep(10)

        # Check if logged in
        try:
            logged_in = page.query_selector('[data-testid="SideNav_NewTweet_Button"]') or \
                       page.query_selector('[aria-label="Post"]') or \
                       page.query_selector('[data-testid="AppTabBar_Home_Link"]')

            if logged_in:
                print("\n" + "=" * 60)
                print("SUCCESS! Logged in to Twitter!")
                print("Session saved for future use.")
                print("=" * 60)
                time.sleep(3)
                browser.close()
                exit(0)
        except:
            pass

        print(f"  Still waiting... ({(i+1)*10}/300 seconds)")

    print("\nTimeout - please try again")
    browser.close()
