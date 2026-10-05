"""Task 1e - Data dictionary: every column of every raw & processed table, with type, description and source.
Output: data/data_dictionary.md and data/data_dictionary.csv"""
import os, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RBI = "RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx"
CEN = "Census of India 2011, Table C-01 - https://censusindia.gov.in/nada/index.php/catalog/11361"
WIKI = "Wikipedia infobox (MediaWiki API) or Govt. page in attribution_url"
DER = "Derived (code/04_build_clean_dataset.py)"
D = {
 "data/raw/rbi_holiday_matrix_raw.csv": {
  "year": ("int", "Calendar year of the holiday", RBI), "month": ("int", "Month 1-12", RBI), "day": ("int", "Day of month", RBI),
  "date": ("date", "ISO date", RBI), "rbi_regional_office": ("str", "RBI regional office (34) whose jurisdiction observes the holiday", RBI),
  "rbi_holiday_description": ("str", "RBI's label for all holidays on that date across India ('|' joins multiple labels)", RBI),
  "holiday_type": ("str", "Always 'NI Act holiday' (Negotiable Instruments Act); account-closing days excluded", RBI),
  "source_url": ("str", "Exact page + POST parameters used", RBI), "source_publisher": ("str", "Reserve Bank of India", RBI),
  "retrieved_on": ("date", "Scrape date", "code/01_scrape_rbi_holidays.py")},
 "data/raw/festival_wikipedia_attribution.csv": {
  "festival": ("str", "Canonical festival name (code/festival_catalog.py)", DER),
  "wiki_title_requested / wiki_title_resolved": ("str", "Article requested / article actually returned", WIKI),
  "wiki_url": ("url", "Article URL", WIKI), "wiki_observed_by": ("str", "Infobox 'Observed by' text", WIKI),
  "wiki_type / wiki_significance / wiki_frequency / wiki_duration": ("str", "Infobox fields", WIKI)},
 "data/raw/economic_footfall_raw.csv (.json)": {
  "record_id": ("str", "ECO001..", DER), "festival": ("str", "Festival / event", "per-row source_url"),
  "tradition": ("str", "Tradition of the festival, or 'Global analogue'", "per-row source_url"),
  "year": ("int", "Year the figure refers to", "per-row source_url"),
  "metric": ("str", "festive_trade | creative_economy | festive_economy | footfall | temple_revenue | special_trains | sector_share_of_goods_sales | sector_trade | gold_trade | silver_trade | dhanteras_* | ecommerce_gmv | retail_sales | tourism_spending", DER),
  "value / unit": ("float/str", "Figure exactly as published (INR crore, persons, percent, USD/CNY billion, trains)", "per-row source_url"),
  "geography": ("str", "Area the figure covers", "per-row source_url"), "sector": ("str", "Market sector (retail, jewellery, travel, FMCG...)", "per-row source_url"),
  "estimate_type": ("str", "reported (post-event) or projection (pre-event estimate)", "per-row source_url"),
  "publisher / source_type / source_url": ("str", "Who produced the number, kind of source, exact URL", "-"),
  "note": ("str", "Extra context quoted from the source", "per-row source_url"), "verified_on": ("date", "Date the page was opened and the figure confirmed", "-")},
 "data/processed/festival_observations.csv": {
  "year, date, month, day, day_of_year": ("int/date", "Calendar fields", RBI), "season_imd": ("str", "IMD season: Winter (Jan-Feb), Pre-monsoon (Mar-May), Monsoon (Jun-Sep), Post-monsoon (Oct-Dec)", "India Meteorological Department definition"),
  "rbi_regional_office, state, region": ("str", "Office, mapped State/UT (jurisdiction) and 6-way region", DER),
  "festival": ("str", "Canonical festival resolved from description by regex", DER), "tradition": ("str", "Hindu | Muslim | Christian | Sikh | Buddhist | Jain | Parsi | Tribal/Indigenous | Cultural (multi-faith)", WIKI),
  "festival_type": ("str", "Religious | Harvest | New Year | Seasonal | Commemoration | Cultural", DER),
  "attribution": ("str", "unique = festival was the only item in the RBI label; shared_resolved = shared date but recognition >= 0.9; shared_split = shared date, evidence ambiguous", DER),
  "n_items_on_date": ("int", "Festivals + civic items co-listed on that date", DER),
  "equal_split_weight": ("float", "1 / n_items_on_date - the naive equal split, kept for comparison", DER),
  "attribution_weight": ("float", "Share of the closure credited to this festival by the evidence score (sums to 1 per closed office-date)", DER),
  "recognition_weight": ("float", "HEADLINE measure: 1.0 where the office is confirmed to observe the festival (even on a shared date), otherwise the attribution_weight", DER),
  "years_listable": ("int", "Years of the study period in which the festival could be listed (study years minus presumed-Sunday years)", DER),
  "sunday_affected_year": ("bool", "True if this row belongs to a year in which the festival's main day fell on a Sunday; excluded from per-year averages", DER),
  "annual_weight": ("float", "recognition_weight / years_listable (0 in Sunday-affected years): summing it gives recognised festival holidays per year", DER)},
 "data/processed/festival_master.csv": {
  "festival, tradition, festival_type": ("str", "Identity & classification", WIKI),
  "years_observed": ("int", "Study years with at least one observation", DER),
  "years_presumed_sunday": ("int", "Years excluded from averages because the festival's main day fell on a Sunday (checked by calendar for fixed dates; inferred for moving dates)", DER),
  "years_listable": ("int", "Study years minus years_presumed_sunday", DER),
  "expected_states_per_year": ("float", "MAIN reach metric: sum over states of the highest recognition weight in a year, averaged over listable years", DER),
  "states_confirmed_any_year": ("int", "States with recognition >= 0.9 in at least one year", DER),
  "states_upper_any_year": ("int", "Upper bound: states with any credited observation", DER),
  "attribution_certainty": ("float", "Share of the festival's recognition coming from unique or confirmed observations", DER),
  "reach_identifiable": ("bool", "True when attribution_certainty >= 0.5", DER),
  "national_reach_pct": ("float", "Expected states / 29 x 100", DER), "n_regions, regions, states": ("int/str", "Geographic footprint", DER),
  "modal_month, months_observed, modal_season_imd": ("int/str", "Timing", DER),
  "date_drift_days": ("float", "Range of the first-observed calendar day across the study years (0-1 => fixed Gregorian date)", DER),
  "calendar_basis": ("str", "Gregorian (fixed) | Lunar/Lunisolar (moving) | Undetermined (1 year)", DER),
  "mean_holiday_days, max_holiday_days": ("float/int", "Duration: consecutive holiday days per office-year", DER),
  "total_office_holiday_days, weighted_holiday_days, share_shared_date": ("int/float", "Volume of observations", DER),
  "holiday_days_per_office_per_year": ("float", "Recognised holiday-days per RBI office per year (Sunday-corrected)", DER),
  "wiki_* , attribution_url, attribution_publisher": ("str", "Source grounding of the tradition label", WIKI),
  "primary_source_url, primary_source_publisher": ("str", "RBI", RBI),
  "latest_trade_inr_crore, latest_trade_year, trade_source_url": ("float/int/url", "Most recent trade/economy figure, if any", "economic_footfall_raw.csv")},
 "data/processed/state_profile.csv": {
  "state, region, n_rbi_offices": ("str/int", "State/UT (Punjab, Haryana & Chandigarh combined = RBI Chandigarh office)", DER),
  "hol_days_<tradition>": ("float", "Recognised festival holiday-days per office per year for each tradition (sum of annual_weight)", DER),
  "hol_days_total_festival": ("float", "Total festival holiday-days per office per year", DER),
  "hol_share_<tradition>": ("float", "% of the state's festival holidays per tradition", DER),
  "holiday_diversity_shannon": ("float", "Shannon entropy of hol_share over traditions", DER),
  "n_distinct_festivals": ("int", "Distinct festivals with recognition > 0.5 in at least two years", DER),
  "census_pct_<religion>": ("float", "Religion share of population, Census 2011 (Telangana = 10 districts coded 532-541 of the AP table; Andhra Pradesh = the other 13)", CEN),
  "pop_total": ("int", "Census 2011 population", CEN), "population_diversity_shannon": ("float", "Shannon entropy of census shares", DER),
  "census_source_url": ("url", "Census table URL", CEN)},
}
rows = [{"table": t, "column": c, "type": v[0], "description": v[1], "source": v[2]} for t, cols in D.items() for c, v in cols.items()]
pd.DataFrame(rows).to_csv(os.path.join(ROOT, "data", "data_dictionary.csv"), index=False)
md = ["# Data Dictionary - Indian Festivals Socio-Economic & Demographic Dataset\n",
      "Zero synthetic records: every row traces to RBI, Census of India, Wikipedia/Govt. attribution pages or a cited news/industry URL.\n",
      "## Collection sources\n",
      "| Source | Publisher | Use |\n|---|---|---|",
      f"| {RBI} | Reserve Bank of India (Govt. of India) | Festival dates & state-wise observance, 2022-2026 (all offices x months) |",
      "| DoPT O.M. F.No.12/2/2023-JCA, 3 July 2025 (holidays in Central Government offices, 2026) | Dept. of Personnel & Training, Govt. of India | List of 14 compulsory holidays, used as second-source confirmation |",
      f"| {CEN} | Office of the Registrar General & Census Commissioner | State religious demography |",
      "| MediaWiki API (en.wikipedia.org) + utsav.gov.in, soreng.nic.in, dtahills.mn.gov.in, megtourism.gov.in | Wikipedia / Govt. | Tradition ('Observed by') attribution |",
      "| cait.in, The Tribune, AIR (newsonair.gov.in), Business Today, Outlook Business, Onmanorama, Nagaland Tribune, OdishaBytes, The News Minute, Millennium Post, The Federal, Angel One, Inshorts, IBEF | CAIT & verified news | Consumer spending, sector split, footfall |",
      "| nrf.com, english.www.gov.cn, stats.gov.sa, muenchen.de, Redseer via Storyboard18 | Industry / governments | Global analogues & e-commerce |",
      "| DataMeet India state boundaries (CC BY 2.5 IN) | DataMeet | Choropleth geometry only |\n",
      "## How under-counting is avoided\n",
      "* **Sunday correction.** The RBI matrix contains no Sunday dates (banks are closed anyway), so a festival that falls on a Sunday is absent for that year - e.g. Christmas 2022, Ram Navami 2025, Muharram 2025. Fixed-date festivals are checked against the calendar; for moving-date festivals a missing year, or a year in which the festival reached under half of its usual states, is presumed to be a Sunday year (at most 2 of 5). Each festival is averaged only over its listable years. Check: about 1 festival-year in 7 should be a Sunday (72 of 505); the method flags 63.",
      "* **Shared dates.** RBI prints one combined label per date for the whole country. An office-festival pair is *confirmed* when (a) the office closed on a date where the festival stood alone, (b) the festival is one of the 14 compulsory Central Government holidays (DoPT) and the office closed in every year it was listed, or (c) the office belongs to the festival's home community according to the Wikipedia 'Observed by' field (data/raw/home_region_prior.csv). A confirmed festival counts in full (recognition_weight = 1) even on a shared date. Unconfirmed co-listings are discounted by an evidence score, more heavily if the office stayed open on the festival's dates in some year. The audit trail is data/processed/attribution_propensity.csv.",
      "* **Telangana** did not exist in 2011; it and residual Andhra Pradesh are rebuilt from the district rows of the Census table.\n",
      "## Known limitations\n",
      "* **What the data cannot see.** Only holidays notified under the Negotiable Instruments Act are covered. Festivals with no bank holiday, holidays for government offices or schools only, restricted (optional) holidays and district-level local holidays are not. Union territories without an RBI regional office are not covered; Punjab, Haryana and Chandigarh share one office.",
      "* **Residual ambiguity.** Festivals that always share their date and have no confirming evidence remain uncertain; they are split by evidence score and flagged (reach_identifiable = False).",
      "* Holidays declared later in the year ARE included when RBI adds them (elections, heavy rain, state mourning); the 2026 list reflects what RBI had published on the retrieval date.",
      "* Bank holidays measure *official recognition*, not participation. Census 2011 is the latest published religion census.",
      "* Trade figures are industry-body estimates (mostly CAIT surveys), many are pre-event projections; comparable national figures are not published for most non-Hindu festivals - itself a finding on measurement bias.\n"]
for t, cols in D.items():
    md += [f"## `{t}`\n", "| Column | Type | Description | Source |", "|---|---|---|---|"]
    md += [f"| `{c}` | {v[0]} | {v[1]} | {v[2]} |" for c, v in cols.items()] + [""]
open(os.path.join(ROOT, "data", "data_dictionary.md"), "w", encoding="utf-8").write("\n".join(md))
print(len(rows), "dictionary rows")
