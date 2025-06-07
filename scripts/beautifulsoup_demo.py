#!/usr/bin/env python3
"""
bs_demo.py

A minimal BeautifulSoup + requests demo.  
Features:
- Fetch raw HTML with requests
- Parse with BeautifulSoup
- Extract the page title and all links
- Convert the full HTML body to Markdown via markdownify
- Save outputs into /scripts/out
"""

import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# 1. Configuration: target URL and output directory
URL = "https://www.restaurantbusinessonline.com/top-500-2024-ranking"
OUT_DIR = os.path.join(os.path.dirname(__file__), "out")

# 2. Ensure the output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# 3. Fetch the raw HTML
response = requests.get(URL)
response.raise_for_status()  # stop if we got a non-2xx response
html_content = response.text

# 4. Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# 4a. Extract the <title> text
page_title = soup.title.string if soup.title else "No title found"

# 4b. Extract all hyperlinks (<a href="...">)
links = []
for a in soup.find_all("a", href=True):
    text = a.get_text(strip=True) or "[no text]"
    href = a["href"]
    links.append((text, href))

# 5. Convert the main <body> to Markdown
body_tag = soup.body
body_md = md(str(body_tag)) if body_tag else "# No <body> tag found"

# 6. Write outputs to files

# 6a. Save page title and links as plain text
with open(os.path.join(OUT_DIR, "example_links.txt"), "w", encoding="utf-8") as f:
    f.write(f"Page Title: {page_title}\n\n")
    f.write("All Links:\n")
    for text, href in links:
        f.write(f"- [{text}]({href})\n")

# 6b. Save the body Markdown
with open(os.path.join(OUT_DIR, "example_body.md"), "w", encoding="utf-8") as f:
    f.write(body_md)

print("BeautifulSoup demo complete.")
print(f" • Links written to: {os.path.join(OUT_DIR, 'example_links.txt')}")
print(f" • Body Markdown written to: {os.path.join(OUT_DIR, 'example_body.md')}")
