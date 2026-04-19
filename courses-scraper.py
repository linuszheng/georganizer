from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from lxml import etree
from types import SimpleNamespace
import time
import csv
import os

# Load catalog options from courses/catalog
# Format: "Label": "name", "url"
catalogs = []
with open("courses/catalog") as f:
    for line in f:
        line = line.strip().rstrip(",")
        if not line:
            continue
        # Split on first ":" to get label, then comma-split the rest
        label_part, _, rest = line.partition(":")
        parts = [p.strip().strip('"') for p in rest.split(",") if p.strip().strip('"')]
        label = label_part.strip().strip('"')
        if label and len(parts) >= 2:
            catalogs.append({"label": label, "name": parts[0], "url": parts[1]})

if not catalogs:
    print("No catalogs found in courses/catalog")
    exit(1)

print("Available catalogs:")
for i, c in enumerate(catalogs):
    print(f"  {i + 1}. {c['label']}")

choice = 0
while choice < 1 or choice > len(catalogs):
    try:
        choice = int(input(f"Choose a catalog (1-{len(catalogs)}): "))
    except ValueError:
        pass

selected = catalogs[choice - 1]
catalog_name = selected["name"]
url = selected["url"]
print(f"Scraping: {selected['label']} -> courses/{catalog_name}.csv")

driver = webdriver.Chrome()
driver.get(url)


waiting_for_done = ""
while waiting_for_done != "DONE":
    waiting_for_done = input("Type DONE after logging in: ")

time.sleep(2)

info_txts = []
dd1_len = driver.execute_script("return document.getElementById('fos_fl').length")
dd2_len = driver.execute_script("return document.getElementById('level').length")
for i in range(dd1_len):
    driver.execute_script("document.getElementById('fos_fl').selectedIndex=" + str(i))
    for j in range(dd2_len):
        driver.execute_script("document.getElementById('level').selectedIndex=" + str(j))
        driver.find_element(By.XPATH, "//*[@id='small_search']/form/input[2]").click()

        while True:
            time.sleep(.2)
            html = driver.page_source
            tree = etree.HTML(html)
            rows = tree.xpath("//table[contains(@class, 'results')]//tbody/tr")

            current_course = ""
            for row in rows:
                header = row.xpath("td[@class='course_header']/h2")
                if header:
                    current_course = header[0].text.strip()
                    continue

                cells = row.xpath("td")
                if len(cells) < 7:
                    continue

                info_txts.append({
                    "course": current_course,
                    "unique": cells[0].xpath(".//a/text()")[0].strip() if cells[0].xpath(".//a/text()") else "",
                    "days": " ".join(s.strip() for s in cells[1].xpath(".//span/text()")),
                    "hour": " ".join(s.strip() for s in cells[2].xpath(".//span/text()")),
                    "room": " ".join(s.strip() for s in cells[3].xpath(".//span/text()")),
                    "instruction_mode": (cells[4].text or "").strip(),
                    "instructor": " ".join(s.strip() for s in cells[5].xpath(".//span/text()")),
                    "status": (cells[6].text or "").strip(),
                    "level": "Lower" if j==0 else ("Upper" if j==1 else ("Graduate" if j==2 else "Unknown")),
                })

            # Click "Next page" if it exists, otherwise done with this search
            next_links = driver.find_elements(By.XPATH, "//*[@id='next_nav_link']")
            if next_links:
                next_links[0].click()
            else:
                break




with open("courses/{}.csv".format(catalog_name), "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["course", "unique", "days", "hour", "room", "instruction_mode", "instructor", "status", "level"])
    writer.writeheader()
    writer.writerows(info_txts)

driver.close()
