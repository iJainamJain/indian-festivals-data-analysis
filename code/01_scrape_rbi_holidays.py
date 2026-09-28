"""Task 1a - Scrape the Reserve Bank of India holiday matrix (Negotiable Instruments Act holidays)
for every RBI regional office (state/UT proxy), every month, 2024-2026.
Source: https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx  (official Government of India / RBI portal)
Output: data/raw/rbi_holiday_matrix_raw.csv  (one row per office x date x holiday)
"""
import csv, os, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
YEARS = ["2024", "2025", "2026"]

S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (academic research; DAV project)"

def form_state():
    s = BeautifulSoup(S.get(URL, timeout=60).text, "html.parser")
    return {i["name"]: i.get("value", "") for i in s.find("form").find_all("input") if i.get("type") == "hidden"}

rows = []
for yr in YEARS:
    for m in range(1, 13):
        d = form_state(); d.update({"drRegionalOffice": "0", "drMonth": str(m), "drYear": yr, "btnGo": "GO"})
        html = S.post(URL, data=d, timeout=60).text
        open(os.path.join(RAW, "rbi_html", f"rbi_{yr}_{m:02d}.html"), "w", encoding="utf-8").write(html)
        b = BeautifulSoup(html, "html.parser")
        tables = b.find_all("table")
        matrix = next((t for t in tables if t.find("tr") and "20" in t.find("tr").get_text() and len(t.find_all("tr")) > 20), None)
        desc = next((t for t in tables if "Holiday Description" in t.get_text()), None)
        if matrix is None or desc is None:
            print(yr, m, "no holidays"); continue
        day2desc = {}
        for tr in desc.find_all("tr")[1:]:
            c = [x.get_text(" ", strip=True) for x in tr.find_all("td")]
            if len(c) == 2: day2desc.setdefault(int(c[1]), []).append(c[0])
        trs = matrix.find_all("tr")
        days = [int(x.get_text(strip=True)) for x in trs[0].find_all(["td", "th"])[1:]]
        for tr in trs[1:]:
            cells = tr.find_all(["td", "th"]); office = cells[0].get_text(strip=True)
            for day, c in zip(days, cells[1:]):
                t = c.get_text(" ", strip=True)
                if "Negotiable" in t:
                    rows.append({"year": int(yr), "month": m, "day": day,
                                 "date": datetime(int(yr), m, day).strftime("%Y-%m-%d"),
                                 "rbi_regional_office": office,
                                 "rbi_holiday_description": " | ".join(day2desc.get(day, [])),
                                 "holiday_type": "NI Act holiday",
                                 "source_url": URL + f"?drRegionalOffice=0&drMonth={m}&drYear={yr} (POST form)",
                                 "source_publisher": "Reserve Bank of India",
                                 "retrieved_on": datetime.now().strftime("%Y-%m-%d")})
        print(yr, m, len(days), "dates")
        time.sleep(0.5)

out = os.path.join(RAW, "rbi_holiday_matrix_raw.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("rows:", len(rows), "->", out)
