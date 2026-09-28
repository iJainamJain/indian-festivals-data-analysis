"""Task 1b - Source-ground each canonical festival: fetch its Wikipedia article (MediaWiki API),
extract the infobox 'Observed by', 'Type', 'Significance', 'Frequency' fields and the page URL.
Output: data/raw/festival_wikipedia_attribution.csv
"""
import os, time, csv, requests
from datetime import date
from bs4 import BeautifulSoup
from festival_catalog import CATALOG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://en.wikipedia.org/w/api.php"
H = {"User-Agent": "DAV-student-project/1.0 (academic; festival dataset)"}
rows = []

def api(params):
    """GET the MediaWiki API with retry/back-off (the API rate-limits bursts with empty bodies)."""
    for attempt in range(8):
        try:
            return requests.get(API, params={**params, "format": "json"}, headers=H, timeout=60).json()
        except ValueError:
            time.sleep(3 * (attempt + 1))
    return {}

for name, (_, trad, ftype, title) in CATALOG.items():
    r = api({"action": "parse", "page": title, "prop": "text", "redirects": 1})
    rec = {"festival": name, "wiki_title_requested": title, "wiki_title_resolved": "", "wiki_url": "",
           "wiki_observed_by": "", "wiki_type": "", "wiki_significance": "", "wiki_frequency": "",
           "wiki_duration": "", "retrieved_on": date.today().isoformat()}
    if "parse" not in r:  # title not found -> use the top Wikipedia search hit for the festival name
        hit = api({"action": "query", "list": "search", "srsearch": name.split(" (")[0] + " festival India",
                                         "srlimit": 1})
        hits = hit.get("query", {}).get("search", [])
        if hits:
            time.sleep(1)
            r = api({"action": "parse", "page": hits[0]["title"], "prop": "text", "redirects": 1})
    if "parse" in r:
        t = r["parse"]["title"]; rec["wiki_title_resolved"] = t
        rec["wiki_url"] = "https://en.wikipedia.org/wiki/" + t.replace(" ", "_")
        soup = BeautifulSoup(r["parse"]["text"]["*"], "html.parser")
        box = soup.find("table", class_="infobox")
        if box:
            for tr in box.find_all("tr"):
                th, td = tr.find("th"), tr.find("td")
                if not th or not td: continue
                k = th.get_text(" ", strip=True).replace(" ", " ").lower()
                for sup in td.find_all("sup"): sup.decompose()
                v = td.get_text(" ", strip=True).replace(" ", " ").replace(" ,", ",")[:200]
                for key in ["observed by", "type", "significance", "frequency", "duration"]:
                    if k.startswith(key): rec["wiki_" + key.replace("observed by", "observed_by")] = v
    rows.append(rec); print(name, "|", rec["wiki_title_resolved"], "|", rec["wiki_observed_by"], "|", rec["wiki_type"])
    time.sleep(1.0)
out = os.path.join(ROOT, "data", "raw", "festival_wikipedia_attribution.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("->", out)
