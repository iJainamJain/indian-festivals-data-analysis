"""Task 1d - Clean / preprocess / integrate all raw sources into analysis-ready tables.

Inputs  (data/raw):  rbi_holiday_matrix_raw.csv, festival_wikipedia_attribution.csv,
                      census/C01_India_2011.xls, economic_footfall_raw.csv
Outputs (data/processed):
  festival_observations.csv  one row = one festival observed as a bank holiday at one RBI office on one date
  festival_master.csv        one row = one canonical festival (features for EDA / ML)
  state_profile.csv          one row = one state/UT (holiday mix by tradition + Census 2011 religion shares)
  economic_footfall_clean.csv
Preprocessing steps are numbered in comments; see data_dictionary.md for every column.
"""
import os, re
import numpy as np, pandas as pd
from festival_catalog import CATALOG, NON_FESTIVAL

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
# IMD season definitions (India Meteorological Department)
def imd_season(m):
    return {1: "Winter", 2: "Winter", 3: "Pre-monsoon", 4: "Pre-monsoon", 5: "Pre-monsoon", 6: "Monsoon", 7: "Monsoon",
            8: "Monsoon", 9: "Monsoon", 10: "Post-monsoon", 11: "Post-monsoon", 12: "Post-monsoon"}[m]

# 2. Load raw RBI rows, normalise whitespace, drop exact duplicates ---------------------------
raw = pd.read_csv(os.path.join(RAW, "rbi_holiday_matrix_raw.csv"))
raw["rbi_holiday_description"] = raw["rbi_holiday_description"].fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
n0 = len(raw); raw = raw.drop_duplicates(["date", "rbi_regional_office"]); print("dup office-dates dropped:", n0 - len(raw))
raw["state"] = raw["rbi_regional_office"].map(OFFICE_STATE)
assert raw["state"].notna().all(), raw.loc[raw.state.isna(), "rbi_regional_office"].unique()
raw["region"] = raw["state"].map(REGION)

# 3. Resolve each description to canonical festivals (regex catalog) + count civic items ------
compiled = {k: re.compile(v[0]) for k, v in CATALOG.items()}
nonfest = re.compile(NON_FESTIVAL, re.I)
def resolve(desc):
    parts = [p.strip() for p in re.split(r"/| \| ", desc) if p.strip()]
    fests = [k for k, rx in compiled.items() if rx.search(desc)]
    civic = [p for p in parts if nonfest.search(p) and not any(compiled[f].search(p) for f in fests)]
    return fests, len(civic)
res = raw["rbi_holiday_description"].map(resolve)
raw["festivals"] = res.map(lambda x: x[0]); raw["n_civic_items"] = res.map(lambda x: x[1])
unmatched = raw[(raw.festivals.str.len() == 0) & (raw.n_civic_items == 0)]["rbi_holiday_description"].unique()
print("descriptions with neither festival nor civic match:", list(unmatched))

# 4. Explode to one row per festival; fractional attribution weight = 1 / items sharing the date
obs = raw[raw.festivals.str.len() > 0].explode("festivals").rename(columns={"festivals": "festival"})
obs["n_items_on_date"] = obs.groupby(["date", "rbi_regional_office"])["festival"].transform("size") + obs["n_civic_items"]
obs["attribution_weight"] = 1 / obs["n_items_on_date"]
obs["attribution"] = np.where(obs["n_items_on_date"] == 1, "unique", "shared_date")
obs["tradition"] = obs["festival"].map(lambda f: CATALOG[f][1])
obs["festival_type"] = obs["festival"].map(lambda f: CATALOG[f][2])
obs["season_imd"] = obs["month"].map(imd_season)
obs["day_of_year"] = pd.to_datetime(obs["date"]).dt.dayofyear
obs = obs[["year", "date", "month", "day", "day_of_year", "season_imd", "rbi_regional_office", "state", "region", "festival",
           "tradition", "festival_type", "attribution", "n_items_on_date", "attribution_weight", "rbi_holiday_description",
           "source_url", "source_publisher", "retrieved_on"]].sort_values(["date", "rbi_regional_office", "festival"])
obs.to_csv(os.path.join(OUT, "festival_observations.csv"), index=False)
print("festival observations:", len(obs), "| festivals:", obs.festival.nunique(), "| states:", obs.state.nunique())

# 5. Festival-level feature table --------------------------------------------------------------
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
    """Consecutive-day holiday blocks per office-year (festival duration as a bank holiday)."""
    d = pd.to_datetime(g["date"]).sort_values().drop_duplicates()
    blocks = (d.diff().dt.days != 1).cumsum()
    return d.groupby(blocks).size().tolist()

rows = []
for f, g in obs.groupby("festival"):
    per_year_states = g.groupby("year")["state"].nunique()
    runs = sum((run_lengths(x) for _, x in g.groupby(["rbi_regional_office", "year"])), [])
    doy_by_year = g.groupby("year")["day_of_year"].min()
    months = g["month"].value_counts()
    rows.append({
        "festival": f, "tradition": CATALOG[f][1], "festival_type": CATALOG[f][2],
        "years_observed": g["year"].nunique(),
        # upper bound: every state whose office closed on a date whose RBI label mentions the festival
        "states_upper_per_year": per_year_states.reindex([2024, 2025, 2026]).fillna(0).mean(),
        # confirmed: only dates where the festival was the ONLY item in the RBI label
        "states_confirmed_max": g[g.attribution == "unique"].groupby("year")["state"].nunique().max() if (g.attribution == "unique").any() else 0,
        "states_confirmed_any_year": g.loc[g.attribution == "unique", "state"].nunique(),
        "reach_identifiable": bool((g.attribution == "unique").any()),
        # expected reach (main metric): sum over states of the max attribution weight, averaged over years
        "expected_states_per_year": g.groupby(["year", "state"])["attribution_weight"].max().groupby("year").sum()
                                     .reindex([2024, 2025, 2026]).fillna(0).mean(),
        "national_reach_pct": 100 * g.groupby(["year", "state"])["attribution_weight"].max().groupby("year").sum().max() / len(REGION),
        "n_regions": g["region"].nunique(),
        "regions": ";".join(sorted(g["region"].unique())),
        "states": ";".join(sorted(g["state"].unique())),
        "modal_month": int(months.idxmax()), "months_observed": ";".join(map(str, sorted(g["month"].unique()))),
        "modal_season_imd": imd_season(int(months.idxmax())),
        "date_drift_days": float(doy_by_year.max() - doy_by_year.min()) if len(doy_by_year) > 1 else 0.0,
        "calendar_basis": "Gregorian (fixed date)" if (len(doy_by_year) > 1 and doy_by_year.max() - doy_by_year.min() <= 1)
                          else ("Lunar/Lunisolar (moving date)" if len(doy_by_year) > 1 else "Undetermined (1 year)"),
        "mean_holiday_days": float(np.mean(runs)), "max_holiday_days": int(np.max(runs)),
        "total_office_holiday_days": len(g), "weighted_holiday_days": g["attribution_weight"].sum(),
        "share_shared_date": (g["attribution"] == "shared_date").mean(),
    })
master = pd.DataFrame(rows).merge(
    wiki[["festival", "wiki_title_resolved", "wiki_observed_by", "wiki_type", "wiki_duration", "attribution_url",
          "attribution_publisher"]], on="festival", how="left")
master["primary_source_url"] = RBI_URL; master["primary_source_publisher"] = "Reserve Bank of India"

# 6. Attach economic / footfall indicators (latest reported/projection value per festival) -----
eco = pd.read_csv(os.path.join(RAW, "economic_footfall_raw.csv"))
eco["value_inr_crore"] = np.where(eco["unit"] == "INR crore", eco["value"], np.nan)
trade = eco[eco.metric.isin(["festive_trade", "creative_economy", "festive_economy", "gold_trade"])].sort_values("year")
latest = trade.groupby("festival").tail(1).set_index("festival")
master["latest_trade_inr_crore"] = master.festival.map(latest["value"])
master["latest_trade_year"] = master.festival.map(latest["year"])
master["trade_source_url"] = master.festival.map(latest["source_url"])
master = master.sort_values(["tradition", "festival"])
master.to_csv(os.path.join(OUT, "festival_master.csv"), index=False)
print("festival master:", master.shape, master.tradition.value_counts().to_dict())

# 7. Census 2011 religion shares by state (primary Census table C-01) ------------------------
c = pd.read_excel(os.path.join(RAW, "census", "C01_India_2011.xls"), header=None, skiprows=6)
c = c[c[6].astype(str).str.strip() == "Total"]
c = c[[5, 7, 10, 13, 16, 19, 22, 25, 28, 31]]
c.columns = ["area", "pop_total", "pop_hindu", "pop_muslim", "pop_christian", "pop_sikh", "pop_buddhist", "pop_jain",
             "pop_other", "pop_not_stated"]
c["area"] = c["area"].str.replace("State - ", "").str.strip().str.title()
CENSUS_MAP = {"Jammu & Kashmir": "Jammu & Kashmir", "Himachal Pradesh": "Himachal Pradesh", "Punjab": "Punjab-Haryana-Chandigarh",
              "Chandigarh": "Punjab-Haryana-Chandigarh", "Haryana": "Punjab-Haryana-Chandigarh", "Uttarakhand": "Uttarakhand",
              "Nct Of Delhi": "Delhi", "Rajasthan": "Rajasthan", "Uttar Pradesh": "Uttar Pradesh", "Bihar": "Bihar",
              "Sikkim": "Sikkim", "Arunachal Pradesh": "Arunachal Pradesh", "Nagaland": "Nagaland", "Manipur": "Manipur",
              "Mizoram": "Mizoram", "Tripura": "Tripura", "Meghalaya": "Meghalaya", "Assam": "Assam", "West Bengal": "West Bengal",
              "Jharkhand": "Jharkhand", "Odisha": "Odisha", "Chhattisgarh": "Chhattisgarh", "Madhya Pradesh": "Madhya Pradesh",
              "Gujarat": "Gujarat", "Maharashtra": "Maharashtra", "Andhra Pradesh": "Andhra Pradesh", "Karnataka": "Karnataka",
              "Goa": "Goa", "Kerala": "Kerala", "Tamil Nadu": "Tamil Nadu"}
# NB: Census 2011 predates Telangana (2014); undivided Andhra Pradesh shares are used for both AP and Telangana.
c["state"] = c["area"].map(CENSUS_MAP)
cs = c.dropna(subset=["state"]).groupby("state").sum(numeric_only=True)
cs.loc["Telangana"] = cs.loc["Andhra Pradesh"]
for col in ["hindu", "muslim", "christian", "sikh", "buddhist", "jain", "other"]:
    cs[f"census_pct_{col}"] = 100 * cs[f"pop_{col}"] / cs["pop_total"]
cs["census_source_url"] = CENSUS_URL

# 8. State profile: mean weighted festival-holiday days per year by tradition -----------------
TR = ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Parsi", "Tribal/Indigenous", "Cultural (multi-faith)"]
# a state with 2+ offices: average across its offices so states are comparable
n_off = raw.groupby("state")["rbi_regional_office"].nunique()
w = obs.groupby(["state", "tradition"])["attribution_weight"].sum()
sp = w.unstack(fill_value=0).div(n_off, axis=0) / 3.0  # per office, per year (3 years: 2024-26)
sp = sp.reindex(columns=TR, fill_value=0)
sp.columns = ["hol_days_" + t.lower().replace("/", "_").replace(" (multi-faith)", "_multifaith").replace(" ", "_") for t in TR]
sp["hol_days_total_festival"] = sp.sum(axis=1)
for col in [c_ for c_ in sp.columns if c_.startswith("hol_days_") and c_ != "hol_days_total_festival"]:
    sp[col.replace("hol_days_", "hol_share_")] = 100 * sp[col] / sp["hol_days_total_festival"]
shares = sp[[c_ for c_ in sp.columns if c_.startswith("hol_share_")]] / 100
sp["holiday_diversity_shannon"] = -(shares.where(shares > 0).apply(np.log) * shares).sum(axis=1)
sp["n_distinct_festivals"] = obs.groupby("state")["festival"].nunique()
sp["n_rbi_offices"] = obs.groupby("state")["rbi_regional_office"].nunique()
sp["region"] = sp.index.map(REGION)
sp = sp.join(cs[[c_ for c_ in cs.columns if c_.startswith("census_pct_")] + ["pop_total", "census_source_url"]])
sp.index.name = "state"
sp.round(4).to_csv(os.path.join(OUT, "state_profile.csv"))
print("state profile:", sp.shape)

# 9. Economic table: normalise units, INR->USD not applied (currencies kept native) ------------
eco["is_indian_festival"] = ~eco["tradition"].eq("Global analogue")
eco.to_csv(os.path.join(OUT, "economic_footfall_clean.csv"), index=False)
print("economic records:", len(eco))
