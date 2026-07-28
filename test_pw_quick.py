#!/usr/bin/env python3
"""Quick Playwright test - just check if browser can launch"""
import sys
print("Test started")
print(f"Python: {sys.executable}")

from playwright.sync_api import sync_playwright
print("Playwright imported")

with sync_playwright() as p:
    print("Starting browser...")
    browser = p.chromium.launch(headless=True, timeout=30000)
    print("Browser launched!")
    browser.close()
    print("Browser closed!")

print("SUCCESS!")
