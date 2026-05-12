from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import csv

BASE_URL = "https://utdirect.utexas.edu/apps/campus/lis/drawings/"
PLAN_URL = "https://utdirect.utexas.edu/apps/campus/lis/drawings/{}/floorplan/"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "floorplans")
BUILDINGS_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "buildings.csv")

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.get(BASE_URL)

waiting_for_done = ""
while waiting_for_done != "DONE":
    waiting_for_done = input("Type DONE after logging in and the page has loaded: ")

try:
    _ = driver.current_url
except Exception:
    print("ERROR: Browser session was lost. Don't close the Chrome window.")
    exit(1)

# Read building abbreviations from buildings.csv
buildings = []
with open(BUILDINGS_CSV, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        abbr = row["building_abbreviation"]
        name = row["building_name"]
        if abbr and abbr not in [b[0] for b in buildings]:
            buildings.append((abbr, name))

print(f"Found {len(buildings)} unique buildings in buildings.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)
downloaded = 0
skipped = 0

for i, (abbr, name) in enumerate(buildings):
    url = PLAN_URL.format(abbr)
    print(f"[{i+1}/{len(buildings)}] {abbr} ({name})... ", end="", flush=True)

    driver.get(url)
    time.sleep(1)

    # Check if we got a PDF (the URL might redirect or show an error page)
    content_type = driver.execute_script(
        "return document.contentType || document.querySelector('embed')?.type || ''"
    )

    current_url = driver.current_url

    # If the browser is showing a PDF, download it via the current URL
    if "pdf" in content_type.lower() or current_url.lower().endswith(".pdf"):
        # Use selenium cookies to download
        cookies = driver.get_cookies()
        cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
        user_agent = driver.execute_script("return navigator.userAgent")

        import urllib.request
        req = urllib.request.Request(url)
        req.add_header("Cookie", cookie_str)
        req.add_header("User-Agent", user_agent)

        filepath = os.path.join(OUTPUT_DIR, f"{abbr}.pdf")
        try:
            resp = urllib.request.urlopen(req)
            data = resp.read()
            if data[:5] == b'%PDF-':
                with open(filepath, "wb") as f:
                    f.write(data)
                downloaded += 1
                print("OK")
            else:
                print("not a PDF")
                skipped += 1
        except Exception as e:
            print(f"download failed: {e}")
            skipped += 1
    else:
        # Not a PDF - probably no floor plan for this building
        print("no floor plan")
        skipped += 1

print(f"\nDone! Downloaded {downloaded}, skipped {skipped}")
print(f"PDFs saved to: {OUTPUT_DIR}")

driver.quit()
