#!/usr/bin/env python3
"""
playwright_demo.py

A minimal Playwright demo (sync API).  
Features:
- Launch headless Chromium
- Navigate to https://example.com
- Wait for DOM load / network idle
- Extract <h1> text
- Take a screenshot of the <h1> element
- Take a full-page screenshot
- Save all outputs into /scripts/out
"""

import os
from playwright.sync_api import sync_playwright

# 1. Configuration: target URL and output directory
URL = "https://www.restaurantbusinessonline.com/top-500-2024-ranking"
OUT_DIR = os.path.join(os.path.dirname(__file__), "out")

# 2. Ensure the output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# 3. Launch Playwright and navigate
with sync_playwright() as pw:
    # 3a. Launch a headless Chromium browser
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()

    # 3b. Go to the target URL and wait until network is idle
    page.goto(URL, wait_until="networkidle")

    # 4. Extract the text of the first <h1> (if present)
    try:
        h1_locator = page.locator("h1")
        h1_text = h1_locator.inner_text().strip()
    except Exception:
        h1_text = "No <h1> found"

    # 5. Write the <h1> text to a file
    with open(os.path.join(OUT_DIR, "example_h1.txt"), "w", encoding="utf-8") as f:
        f.write(f"H1 Text:\n{h1_text}\n")

    # 6. Screenshot the <h1> element (if it exists)
    if h1_text != "No <h1> found":
        try:
            # Make sure the element is visible before screenshot
            h1_locator.wait_for(state="visible", timeout=5000)
            h1_locator.screenshot(path=os.path.join(OUT_DIR, "example_h1.png"))
        except Exception:
            print("Failed to screenshot <h1> element.")
    else:
        print("No <h1> to screenshot.")

    # 7. Take a full-page screenshot
    page.screenshot(path=os.path.join(OUT_DIR, "example_full.png"), full_page=True)

    # 8. Close browser
    browser.close()

print("Playwright demo complete.")
print(f" • H1 text written to: {os.path.join(OUT_DIR, 'example_h1.txt')}")
print(f" • H1 screenshot (if any) at: {os.path.join(OUT_DIR, 'example_h1.png')}")
print(f" • Full-page screenshot at: {os.path.join(OUT_DIR, 'example_full.png')}")
