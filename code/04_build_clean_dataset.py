"""Task 1d - Clean / preprocess / integrate all raw sources into analysis-ready tables.

Inputs  (data/raw):  rbi_holiday_matrix_raw.csv, festival_wikipedia_attribution.csv,
                      census/C01_India_2011.xls, census/C01_AndhraPradesh_2011.xls, economic_footfall_raw.csv
Outputs (data/processed):
  festival_observations.csv  one row = one festival observed as a bank holiday at one RBI office on one date
  festival_master.csv        one row = one canonical festival (features for EDA / ML)
  state_profile.csv          one row = one state/UT (holiday mix by tradition + Census 2011 religion shares)
  economic_footfall_clean.csv
  attribution_propensity.csv office x item evidence status and score used to credit shared dates (audit trail)

Accuracy measures built into this step (see data_dictionary.md):
  A. Evidence-based handling of shared dates.  RBI prints ONE combined label per date for the whole country.
     Step 4 scores each office-item pair from the matrix itself (closed on a date where the item stood alone =
     confirmed; open on all of an item's dates in some year = evidence against).
       attribution_weight  splits each closure among its items in proportion to the evidence (sums to 1 per closure).
       recognition_weight  HEADLINE MEASURE: a festival the office is confirmed to observe counts in full even when
                           it shares the date with another holiday, so no tradition is under-counted because of a
                           calendar coincidence; only unconfirmed co-listings are discounted (flagged shared_split).
  B. Sunday correction.  RBI lists no Sunday dates, so a festival falling on a Sunday is missing for that year.
     Per-year averages therefore divide by the years a festival could be listed (annual_weight), not by all years.
  C. Telangana and residual Andhra Pradesh religion shares are computed from Census 2011 district tables.
"""
import os, re, datetime
import numpy as np, pandas as pd
from festival_catalog import CATALOG, NON_FESTIVAL
from project_config import YEARS, N_YEARS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, OUT = os.path.join(ROOT, "data", "raw"), os.path.join(ROOT, "data", "processed")
os.makedirs(OUT, exist_ok=True)
RBI_URL = "https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx"
CENSUS_URL = "https://censusindia.gov.in/nada/index.php/catalog/11361"

# 1. RBI regional office -> State/UT (RBI office jurisdictions) and region --------------------
OFFICE_STATE = {
    "Agartala": "Tripura", "Ahmedabad": "Gujarat", "Aizawl": "Mizoram", "Belapur": "Maharashtra",
    "Bengaluru": "Karnataka", "Bhopal": "Madhya Pradesh", "Bhubaneswar": "Odisha", "Chandigarh": "Punjab-Haryana-Chandigarh",
    "Chennai": "Tamil Nadu", "Dehradun": "Uttarakhand", "Gangtok": "Sikkim", "Guwahati": "Assam", "Hyderabad": "Telangana",
    "Imphal": "Manipur", "Itanagar": "Arunachal Pradesh", "Jaipur": "Rajasthan", "Jammu": "Jammu & Kashmir",
    "Kanpur": "Uttar Pradesh", "Kochi": "Kerala", "Kohima": "Nagaland", "Kolkata": "West Bengal", "Lucknow": "Uttar Pradesh",
    "Mumbai": "Maharashtra", "Nagpur": "Maharashtra", "New Delhi": "Delhi", "Panaji": "Goa", "Patna": "Bihar",
    "Raipur": "Chhattisgarh", "Ranchi": "Jharkhand", "Shillong": "Meghalaya", "Shimla": "Himachal Pradesh",
    "Srinagar": "Jammu & Kashmir", "Thiruvananthapuram": "Kerala", "Vijayawada": "Andhra Pradesh"}
REGION = {
    "Jammu & Kashmir": "North", "Himachal Pradesh": "North", "Punjab-Haryana-Chandigarh": "North", "Uttarakhand": "North",
    "Delhi": "North", "Rajasthan": "North", "Uttar Pradesh": "North",
    "Bihar": "East", "West Bengal": "East", "Odisha": "East", "Jharkhand": "East",
    "Madhya Pradesh": "Central", "Chhattisgarh": "Central",
    "Gujarat": "West", "Maharashtra": "West", "Goa": "West",
    "Karnataka": "South", "Kerala": "South", "Tamil Nadu": "South", "Telangana": "South", "Andhra Pradesh": "South",
    "Assam": "North-East", "Arunachal Pradesh": "North-East", "Manipur": "North-East", "Meghalaya": "North-East",
    "Mizoram": "North-East", "Nagaland": "North-East", "Tripura": "North-East", "Sikkim": "North-East"}
def imd_season(m):  # India Meteorological Department season definitions
    return {1: "Winter", 2: "Winter", 3: "Pre-monsoon", 4: "Pre-monsoon", 5: "Pre-monsoon", 6: "Monsoon", 7: "Monsoon",
            8: "Monsoon", 9: "Monsoon", 10: "Post-monsoon", 11: "Post-monsoon", 12: "Post-monsoon"}[m]

# 2. Load raw RBI rows, normalise whitespace, drop exact duplicates ---------------------------
raw = pd.read_csv(os.path.join(RAW, "rbi_holiday_matrix_raw.csv"))
raw = raw[raw.year.isin(YEARS)]
raw["rbi_holiday_description"] = raw["rbi_holiday_description"].fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
n0 = len(raw); raw = raw.drop_duplicates(["date", "rbi_regional_office"]); print("dup office-dates dropped:", n0 - len(raw))
raw["state"] = raw["rbi_regional_office"].map(OFFICE_STATE)
assert raw["state"].notna().all(), raw.loc[raw.state.isna(), "rbi_regional_office"].unique()
raw["region"] = raw["state"].map(REGION)
OFFICES = sorted(OFFICE_STATE)

# 3. Resolve each date label into ITEMS: canonical festivals + canonical civic items ----------
compiled = {k: re.compile(v[0]) for k, v in CATALOG.items()}
nonfest = re.compile(NON_FESTIVAL, re.I)
CIVIC = [("Republic Day", r"Republic Day"), ("Independence Day", r"Independence Day"), ("Gandhi Jayanti", r"Gandhi Jayanti"),
         ("Ambedkar Jayanti", r"Ambedkar"), ("May Day / Maharashtra Day", r"May Day|Maharashtra Di|Maharashtra Day"),
         ("Election day", r"Election|Poll day"), ("New Year (Gregorian)", r"New Year.?s (Day|Eve|Celebration)|New Year Celebration"),
         ("Netaji Jayanti", r"Netaji"), ("State formation day", r"State ?Day|State +Day|Statehood|State Formation|State Inauguration"),
         ("Weather closure", r"rains|Cyclone"), ("Bank account closing", r"close their yearly accounts")]
CIVIC = [(k, re.compile(p, re.I)) for k, p in CIVIC]
def civic_key(tok):
    for k, rx in CIVIC:
        if rx.search(tok): return "CIVIC: " + k
    return "CIVIC: " + re.sub(r"[^a-z]+", " ", tok.lower()).strip()[:40]
def resolve(desc):
    parts = [p.strip() for p in re.split(r"/| \| ", desc) if p.strip()]
    fests = [k for k, rx in compiled.items() if rx.search(desc)]
    civ = sorted({civic_key(p) for p in parts if nonfest.search(p) and not any(compiled[f].search(p) for f in fests)})
    return fests, civ
dates = raw.drop_duplicates("date")[["date", "rbi_holiday_description"]].set_index("date")["rbi_holiday_description"]
ITEMS = {d: resolve(s) for d, s in dates.items()}
unmatched = [s for d, s in dates.items() if not ITEMS[d][0] and not ITEMS[d][1]]
print("labels with neither festival nor civic match:", unmatched)

# 4. Evidence-based attribution of shared dates (deterministic, auditable) ----------------------
#    Every closed office-date is credited to the items in its RBI label in proportion to an evidence score:
#      score 1.0  national statutory holidays; state-named civic days in their own state; festivals on the Central
#                 Government compulsory list (DoPT) where the office closed every year; regional festivals at the
#                 offices of their home community (Wikipedia 'Observed by').
#      score 1.0  confirmed: the office was closed on a date where this item was the ONLY one listed.
#      score 0.6  never absent: in every year the item was listed, the office closed on at least one of its dates.
#      score 0.15 x presence rate   the office stayed open on all of the item's dates in at least one year.
#    The score is multiplied by the date-level closure rate (share of the item's dates on which the office closed).
#    Credits below 0.10 are dropped and the rest renormalised.  attribution_propensity.csv is the audit trail.
closed = {(d, o) for d, o in zip(raw.date, raw.rbi_regional_office)}
all_items = sorted({f for fs, cs in ITEMS.values() for f in fs + cs})
dates_f, years_f = {}, {}
for d, (fs, cs) in ITEMS.items():
    for f in fs + cs: dates_f.setdefault(f, []).append(d); years_f.setdefault(f, set()).add(int(d[:4]))
NATIONAL = {"CIVIC: Republic Day", "CIVIC: Independence Day", "CIVIC: Gandhi Jayanti"}
STATE_CIVIC = {"CIVIC: himachal day": ["Shimla"], "CIVIC: bihar divas": ["Patna"], "CIVIC: bihar diwas": ["Patna"],
               "CIVIC: May Day / Maharashtra Day": None, "CIVIC: kannada rajyothsava": ["Bengaluru"], "CIVIC: kannada rajyotsava": ["Bengaluru"],
               "CIVIC: goa liberation day": ["Panaji"]}
unique_conf = {(o, (ITEMS[d][0] + ITEMS[d][1])[0]) for (d, o) in closed if len(ITEMS[d][0] + ITEMS[d][1]) == 1}
# Second official source: festivals that are COMPULSORY holidays for Central Government offices
# (DoPT O.M. F.No.12/2/2023-JCA dated 3 July 2025, para 2).  Where an RBI office closed in every year such a festival was
# listed, the festival is treated as confirmed there even if it always shares its date with another holiday.
DOPT_URL = "https://www.staffnews.in/2025/07/list-of-holidays-2026-dopt-order-reg-closed-and-restricted-holidays.html"
CENTRAL_GAZETTED = {"Buddha Purnima", "Christmas", "Navratri / Durga Puja / Dussehra", "Diwali (Deepavali)", "Good Friday",
                    "Guru Nanak Jayanti (Gurpurab)", "Eid-ul-Fitr", "Eid-ul-Adha (Bakrid)", "Mahavir Jayanti", "Muharram / Ashura", "Milad-un-Nabi"}
# Home-community prior for regional festivals, taken from each festival's Wikipedia 'Observed by' field
# (data/raw/festival_wikipedia_attribution.csv).  It only confirms a festival at an office that actually closed on its dates.
HOME = {"Tamil New Year (Puthandu)": ["Chennai"], "Pongal": ["Chennai"], "Vishu": ["Kochi", "Thiruvananthapuram"],
        "Onam": ["Kochi", "Thiruvananthapuram"], "Bengali New Year (Pohela Boishakh)": ["Kolkata", "Agartala"],
        "Bohag Bihu": ["Guwahati"], "Magh Bihu": ["Guwahati"], "Kati Bihu": ["Guwahati"],
        "Gudi Padwa / Ugadi": ["Mumbai", "Nagpur", "Belapur", "Hyderabad", "Vijayawada", "Bengaluru"],
        "Maha Vishuva Sankranti (Odia New Year)": ["Bhubaneswar"], "Raja Sankranti": ["Bhubaneswar"], "Nuakhai": ["Bhubaneswar"],
        "Baisakhi (Vaisakhi)": ["Chandigarh"], "Vikram Samvat New Year": ["Ahmedabad"], "Basava Jayanti": ["Bengaluru"],
        "Cheiraoba (Meitei New Year)": ["Imphal"], "Yaosang": ["Imphal"], "Ningol Chakkouba": ["Imphal"], "Mera Chaoren Houba": ["Imphal"],
        "Imoinu Iratpa": ["Imphal"], "Kut (Chin-Kuki-Mizo)": ["Imphal"], "Biju / Buisu": ["Agartala", "Aizawl"]}
_w = pd.read_csv(os.path.join(RAW, "festival_wikipedia_attribution.csv")).set_index("festival")
pd.DataFrame([{"festival": f, "home_rbi_offices": ";".join(v), "wikipedia_observed_by": _w["wiki_observed_by"].get(f, ""),
               "wikipedia_url": _w["wiki_url"].get(f, "")} for f, v in HOME.items()]).to_csv(os.path.join(RAW, "home_region_prior.csv"), index=False)
score, certain, aud = {}, set(), []
for f in all_items:
    for o in OFFICES:
        cl = [d for d in dates_f[f] if (d, o) in closed]
        if not cl: continue
        present = {int(d[:4]) for d in cl}; rate = len(cl) / len(dates_f[f])
        own = STATE_CIVIC.get(f, "na")
        if f in NATIONAL or (own not in ("na", None) and o in own):
            certain.add((o, f)); sc, status = 1.0, "confirmed (statutory / own-state day)"
        elif own not in ("na", None):
            sc, status = 0.0, "other-state civic day"
        elif (o, f) in unique_conf: sc, status = 1.0 * rate, "confirmed"
        elif f in CENTRAL_GAZETTED and len(present) == len(years_f[f]):
            certain.add((o, f)); sc, status = 1.0 * rate, "confirmed (central gazetted holiday, never absent)"
        elif o in HOME.get(f, []):
            certain.add((o, f)); sc, status = 1.0 * rate, "confirmed (home community)"
        elif len(present) == len(years_f[f]): sc, status = 0.6 * rate, "never absent"
        else: sc, status = 0.15 * len(present) / len(years_f[f]) * rate, "absent in some years"
        score[(o, f)] = sc
        aud.append({"rbi_regional_office": o, "item": f, "status": status, "years_listed": len(years_f[f]), "years_closed": len(present),
                    "date_closure_rate": round(rate, 3), "evidence_score": round(sc, 4)})
pd.DataFrame(aud).to_csv(os.path.join(OUT, "attribution_propensity.csv"), index=False)
print("attribution evidence:", pd.DataFrame(aud).status.value_counts().to_dict())

confirmed_pairs = unique_conf | certain
rows = []
for r in raw.itertuples():
    fs, cs = ITEMS[r.date]; its = fs + cs; o = r.rbi_regional_office
    sc = {f: score.get((o, f), 0) for f in its}; tot = sum(sc.values())
    w = {f: v / tot for f, v in sc.items()} if tot > 0 else {f: 1 / len(its) for f in its}
    w = {f: v for f, v in w.items() if v >= 0.10}; t2 = sum(w.values()); w = {f: v / t2 for f, v in w.items()}
    for f in fs:
        if f in w:
            # recognition: a festival the office is CONFIRMED to observe counts in full even on a shared date,
            # so no festival is under-counted merely because it coincides with another holiday
            rec = 1.0 if (o, f) in confirmed_pairs else w[f]
            rows.append((r.year, r.date, r.month, r.day, o, r.state, r.region, f, len(its), 1 / len(its), w[f], rec,
                         r.rbi_holiday_description, r.source_url, r.source_publisher, r.retrieved_on))
obs = pd.DataFrame(rows, columns=["year", "date", "month", "day", "rbi_regional_office", "state", "region", "festival", "n_items_on_date",
                                  "equal_split_weight", "attribution_weight", "recognition_weight", "rbi_holiday_description", "source_url", "source_publisher", "retrieved_on"])
obs["attribution"] = np.where(obs.n_items_on_date == 1, "unique", np.where(obs.recognition_weight >= 0.9, "shared_resolved", "shared_split"))
obs["tradition"] = obs["festival"].map(lambda f: CATALOG[f][1]); obs["festival_type"] = obs["festival"].map(lambda f: CATALOG[f][2])
obs["season_imd"] = obs["month"].map(imd_season); obs["day_of_year"] = pd.to_datetime(obs["date"]).dt.dayofyear

# 5. Sunday correction: how many years could each festival have been listed? ------------------
first = obs.groupby(["festival", "year"]).agg(month=("month", "first"), day=("day", "first"), date=("date", "min")).reset_index()
first["md"] = pd.to_datetime(first.date).map(lambda t: datetime.date(2023, t.month, t.day).timetuple().tm_yday)  # non-leap reference
eff_years, cal_basis, drift, sunday_years, skip_years = {}, {}, {}, {}, {}
_pres = obs.groupby(["festival", "year", "state"])["recognition_weight"].max().groupby(["festival", "year"]).sum()
for f, g in first.groupby("festival"):
    listed = sorted(set(g.year)); missing = [y for y in YEARS if y not in listed]
    dr = int(g.md.max() - g.md.min()); drift[f] = dr
    fixed = len(g) >= 2 and dr <= 1
    cal_basis[f] = "Gregorian (fixed date)" if fixed else ("Lunar/Lunisolar (moving date)" if len(g) >= 2 else "Undetermined (1 year)")
    pres = _pres[f]; med = pres.median()
    if fixed:   # the date is known, so every year can be checked against the calendar
        mo, da = (int(x) for x in g.date.str[5:].mode().iloc[0].split("-"))
        sun = [y for y in YEARS if datetime.date(y, mo, da).weekday() == 6]
    else:
        # moving date: a year in which the festival reached under half of its usual number of states is a year whose main
        # day fell on a Sunday (only side-days were listed); missing years are presumed Sundays too.  At most 2 years in total
        # are excluded (P(more than 2 Sundays in 5 years) = 2%), and only for festivals listed in at least 3 years.
        weak = [y for y in listed if pres[y] < 0.5 * med] if len(listed) >= 3 else []
        sun = (missing + weak)[:2] if len(listed) >= 3 else []
    sunday_years[f] = len(sun); skip_years[f] = set(sun); eff_years[f] = N_YEARS - len(sun)
obs["years_listable"] = obs.festival.map(eff_years)
_skip = np.array([y in skip_years[f] for f, y in zip(obs.festival, obs.year)])
obs["sunday_affected_year"] = _skip          # rows kept for transparency but excluded from per-year averages
obs["annual_weight"] = np.where(_skip, 0.0, obs.recognition_weight / obs.years_listable)
obs = obs[["year", "date", "month", "day", "day_of_year", "season_imd", "rbi_regional_office", "state", "region", "festival", "tradition",
           "festival_type", "attribution", "n_items_on_date", "equal_split_weight", "attribution_weight", "recognition_weight", "years_listable", "sunday_affected_year", "annual_weight",
           "rbi_holiday_description", "source_url", "source_publisher", "retrieved_on"]].sort_values(["date", "rbi_regional_office", "festival"])
obs.round(5).to_csv(os.path.join(OUT, "festival_observations.csv"), index=False)
print("festival observations:", len(obs), "| festivals:", obs.festival.nunique(), "| states:", obs.state.nunique(),
      "| attribution:", obs.attribution.value_counts().to_dict())

# 6. Festival-level feature table --------------------------------------------------------------
wiki = pd.read_csv(os.path.join(RAW, "festival_wikipedia_attribution.csv"))
OVERRIDE = {  # festivals with no/incorrect Wikipedia article -> official Government of India / State sources
    "Drukpa Tshe-zi": ("https://soreng.nic.in/festivals/", "Soreng District, Govt. of Sikkim", "Buddhists of Sikkim"),
    "Saga Dawa": ("https://soreng.nic.in/festivals/", "Soreng District, Govt. of Sikkim", "Buddhists of Sikkim"),
    "Pang Lhabsol": ("https://utsav.gov.in/view-event/pang-lhabsol-1", "Ministry of Tourism (Utsav portal)", "Bhutia, Lepcha and Nepali communities of Sikkim"),
    "Kut (Chin-Kuki-Mizo)": ("https://dtahills.mn.gov.in/kut/", "Dept. of Tribal Affairs & Hills, Govt. of Manipur", "Kuki-Chin-Mizo tribes"),
    "Nongkrem Dance": ("https://utsav.gov.in/view-event/nongkrem-dance", "Ministry of Tourism (Utsav portal)", "Khasi people"),
    "Shad Suk Mynsiem": ("http://megtourism.gov.in/festival.html", "Dept. of Tourism, Govt. of Meghalaya", "Khasi people"),
}
wiki["attribution_url"] = wiki["wiki_url"]; wiki["attribution_publisher"] = "Wikipedia (infobox)"
for f, (u, p, ob) in OVERRIDE.items():
    m = wiki.festival == f
    wiki.loc[m, ["attribution_url", "attribution_publisher", "wiki_observed_by"]] = [u, p, ob]
    wiki.loc[m, ["wiki_title_resolved", "wiki_url"]] = ["", ""]

def run_lengths(g):
    d = pd.to_datetime(g["date"]).sort_values().drop_duplicates()
    return d.groupby((d.diff().dt.days != 1).cumsum()).size().tolist()

rows = []
for f, g in obs.groupby("festival"):
    strong = g[g.recognition_weight >= 0.5]
    runs = sum((run_lengths(x) for _, x in strong.groupby(["rbi_regional_office", "year"])), []) or [1]
    pres = g.groupby(["year", "state"])["recognition_weight"].max()          # presence of f in a state-year (0..1)
    months = g.groupby("month")["recognition_weight"].sum()
    certain = g.loc[(g.attribution == "unique") | (g.recognition_weight >= 0.9), "recognition_weight"].sum() / g.recognition_weight.sum()
    reg_w = g.groupby("region")["recognition_weight"].sum()
    rows.append({
        "festival": f, "tradition": CATALOG[f][1], "festival_type": CATALOG[f][2],
        "years_observed": g["year"].nunique(), "years_presumed_sunday": sunday_years[f], "years_listable": eff_years[f],
        "expected_states_per_year": pres[[y not in skip_years[f] for y in pres.index.get_level_values("year")]].groupby("year").sum().sum() / eff_years[f],
        "states_confirmed_any_year": strong.loc[strong.recognition_weight >= 0.9, "state"].nunique(),
        "states_upper_any_year": g["state"].nunique(),
        "attribution_certainty": certain, "reach_identifiable": bool(certain >= 0.5),
        "national_reach_pct": 100 * pres.groupby("year").sum().max() / len(REGION),
        "n_regions": int((reg_w / reg_w.sum() >= 0.05).sum()),
        "regions": ";".join(sorted(reg_w[reg_w / reg_w.sum() >= 0.05].index)),
        "states": ";".join(sorted(st for st, n in g[g.recognition_weight > 0.5].groupby("state")["year"].nunique().items() if n >= min(2, eff_years[f]))),
        "modal_month": int(months.idxmax()), "months_observed": ";".join(map(str, sorted(g["month"].unique()))),
        "modal_season_imd": imd_season(int(months.idxmax())),
        "date_drift_days": float(drift[f]), "calendar_basis": cal_basis[f],
        "mean_holiday_days": float(np.mean(runs)), "max_holiday_days": int(np.max(runs)),
        "total_office_holiday_days": len(g), "weighted_holiday_days": g["recognition_weight"].sum(),
        "holiday_days_per_office_per_year": g["annual_weight"].sum() / len(OFFICES),
        "share_shared_date": (g["attribution"] != "unique").mean(),
    })
master = pd.DataFrame(rows).merge(
    wiki[["festival", "wiki_title_resolved", "wiki_observed_by", "wiki_type", "wiki_duration", "attribution_url",
          "attribution_publisher"]], on="festival", how="left")
master["primary_source_url"] = RBI_URL; master["primary_source_publisher"] = "Reserve Bank of India"

eco = pd.read_csv(os.path.join(RAW, "economic_footfall_raw.csv"))
eco["value_inr_crore"] = np.where(eco["unit"] == "INR crore", eco["value"], np.nan)
trade = eco[eco.metric.isin(["festive_trade", "creative_economy", "festive_economy", "gold_trade"])].sort_values("year")
latest = trade.groupby("festival").tail(1).set_index("festival")
master["latest_trade_inr_crore"] = master.festival.map(latest["value"])
master["latest_trade_year"] = master.festival.map(latest["year"])
master["trade_source_url"] = master.festival.map(latest["source_url"])
master = master.sort_values(["tradition", "festival"])
master.round(4).to_csv(os.path.join(OUT, "festival_master.csv"), index=False)
print("festival master:", master.shape, master.tradition.value_counts().to_dict(), "| identifiable:", int(master.reach_identifiable.sum()))

# 7. Census 2011 religion shares by state (primary Census table C-01) ------------------------
CC = ["area", "pop_total", "pop_hindu", "pop_muslim", "pop_christian", "pop_sikh", "pop_buddhist", "pop_jain", "pop_other", "pop_not_stated"]
c = pd.read_excel(os.path.join(RAW, "census", "C01_India_2011.xls"), header=None, skiprows=6)
c = c[c[6].astype(str).str.strip() == "Total"][[5, 7, 10, 13, 16, 19, 22, 25, 28, 31]]; c.columns = CC
c["area"] = c["area"].str.replace("State - ", "").str.strip().str.title()
CENSUS_MAP = {"Jammu & Kashmir": "Jammu & Kashmir", "Himachal Pradesh": "Himachal Pradesh", "Punjab": "Punjab-Haryana-Chandigarh",
              "Chandigarh": "Punjab-Haryana-Chandigarh", "Haryana": "Punjab-Haryana-Chandigarh", "Uttarakhand": "Uttarakhand",
              "Nct Of Delhi": "Delhi", "Rajasthan": "Rajasthan", "Uttar Pradesh": "Uttar Pradesh", "Bihar": "Bihar",
              "Sikkim": "Sikkim", "Arunachal Pradesh": "Arunachal Pradesh", "Nagaland": "Nagaland", "Manipur": "Manipur",
              "Mizoram": "Mizoram", "Tripura": "Tripura", "Meghalaya": "Meghalaya", "Assam": "Assam", "West Bengal": "West Bengal",
              "Jharkhand": "Jharkhand", "Odisha": "Odisha", "Chhattisgarh": "Chhattisgarh", "Madhya Pradesh": "Madhya Pradesh",
              "Gujarat": "Gujarat", "Maharashtra": "Maharashtra", "Karnataka": "Karnataka", "Goa": "Goa", "Kerala": "Kerala", "Tamil Nadu": "Tamil Nadu"}
c["state"] = c["area"].map(CENSUS_MAP)
cs = c.dropna(subset=["state"]).groupby("state").sum(numeric_only=True)
# Telangana was carved out of Andhra Pradesh in 2014: rebuild both from the 2011 district rows (district codes 532-541 = Telangana)
ap = pd.read_excel(os.path.join(RAW, "census", "C01_AndhraPradesh_2011.xls"), header=None, skiprows=6)
ap = ap[(ap[6].astype(str).str.strip() == "Total") & (ap[3].astype(float) == 0) & (ap[2].astype(float) > 0)]
apd = ap[[2, 7, 10, 13, 16, 19, 22, 25, 28, 31]].copy(); apd.columns = ["dist"] + CC[1:]
tel = apd[apd.dist.between(532, 541)]; rest = apd[~apd.dist.between(532, 541)]
assert len(tel) == 10 and len(rest) == 13
cs.loc["Telangana"] = tel[CC[1:]].sum(); cs.loc["Andhra Pradesh"] = rest[CC[1:]].sum()
for col in ["hindu", "muslim", "christian", "sikh", "buddhist", "jain", "other"]:
    cs[f"census_pct_{col}"] = 100 * cs[f"pop_{col}"] / cs["pop_total"]
cs["census_source_url"] = CENSUS_URL

# 8. State profile: festival-holiday days per office per year (Sunday-corrected) by tradition --
TR = ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Parsi", "Tribal/Indigenous", "Cultural (multi-faith)"]
n_off = raw.groupby("state")["rbi_regional_office"].nunique()
sp = obs.groupby(["state", "tradition"])["annual_weight"].sum().unstack(fill_value=0).div(n_off, axis=0)
sp = sp.reindex(columns=TR, fill_value=0)
sp.columns = ["hol_days_" + t.lower().replace("/", "_").replace(" (multi-faith)", "_multifaith").replace(" ", "_") for t in TR]
sp["hol_days_total_festival"] = sp.sum(axis=1)
for col in [c_ for c_ in sp.columns if c_.startswith("hol_days_") and c_ != "hol_days_total_festival"]:
    sp[col.replace("hol_days_", "hol_share_")] = 100 * sp[col] / sp["hol_days_total_festival"]
shares = sp[[c_ for c_ in sp.columns if c_.startswith("hol_share_")]] / 100
sp["holiday_diversity_shannon"] = -(shares.where(shares > 0).apply(np.log) * shares).sum(axis=1)
_sy = obs[obs.recognition_weight > 0.5].groupby(["state", "festival"])["year"].nunique()
sp["n_distinct_festivals"] = _sy[_sy >= 2].groupby("state").size()
sp["n_rbi_offices"] = n_off
sp["region"] = sp.index.map(REGION)
sp = sp.join(cs[[c_ for c_ in cs.columns if c_.startswith("census_pct_")] + ["pop_total", "census_source_url"]])
pc = sp[[c_ for c_ in sp.columns if c_.startswith("census_pct_")]] / 100
sp["population_diversity_shannon"] = -(pc.where(pc > 0).apply(np.log) * pc).sum(axis=1)
sp.index.name = "state"
sp.round(4).to_csv(os.path.join(OUT, "state_profile.csv"))
print("state profile:", sp.shape)

# 9. Economic table ---------------------------------------------------------------------------
eco["is_indian_festival"] = ~eco["tradition"].eq("Global analogue")
eco.to_csv(os.path.join(OUT, "economic_footfall_clean.csv"), index=False)
print("economic records:", len(eco))
