import urllib.request
from html.parser import HTMLParser

URL = "https://utdirect.utexas.edu/apps/campus/buildings/information/nlogon/maps/"

campuses_abbreviations = ["utm", "prc", "mrc", "aus", "bfl", "jwc", "mcd", "msi", "smv", "whc"]

campuses_full = ["Main Campus",
"Pickle Research Campus",
"Montopolis Research Center",
"Austin, TX",
"Brackenridge Field Lab",
"Johnson Wildflower Center",
"McDonald Observatory",
"Marine Science Institute",
"Stengl Lost Pines",
"Winedale Historical Center"
]

class BuildingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buildings = []
        self.in_row = False
        self.in_cell = False
        self.cells = []
        self.current_text = ""
        self.has_building_link = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.in_row = True
            self.cells = []
            self.has_building_link = False
        elif tag in ("td", "th") and self.in_row:
            self.in_cell = True
            self.current_text = ""
        elif tag == "a" and self.in_cell:
            href = dict(attrs).get("href", "")
            if "/maps/" in href and not href.rstrip("/").endswith(tuple(campuses_abbreviations)):
                self.has_building_link = True

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_cell:
            self.in_cell = False
            self.cells.append(self.current_text.strip())
        elif tag == "tr" and self.in_row:
            self.in_row = False
            if self.has_building_link and len(self.cells) >= 2:
                self.buildings.append((self.cells[0], self.cells[1]))

    def handle_data(self, data):
        if self.in_cell:
            self.current_text += data


all_buildings = []

for campus_abbr, campus_name in zip(campuses_abbreviations, campuses_full):
    campus_url = URL + campus_abbr + "/"
    print(f"Scraping {campus_name} ({campus_abbr})...")
    response = urllib.request.urlopen(campus_url)
    html = response.read().decode("utf-8")

    parser = BuildingParser()
    parser.feed(html)

    for abbr, name in parser.buildings:
        all_buildings.append((campus_abbr, campus_name, abbr, name))

with open("buildings.csv", "w") as f:
    f.write("campus_abbreviation,campus_name,building_abbreviation,building_name\n")
    for campus_abbr, campus_name, abbr, name in all_buildings:
        # Quote fields that may contain commas
        campus_name_q = f'"{campus_name}"' if "," in campus_name else campus_name
        name_q = f'"{name}"' if "," in name else name
        f.write(f"{campus_abbr},{campus_name_q},{abbr},{name_q}\n")

print(f"Wrote {len(all_buildings)} buildings to buildings.csv")
