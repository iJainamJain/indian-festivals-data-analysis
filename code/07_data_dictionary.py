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
  "attribution": ("str", "unique = festival was the only item in RBI label; shared_date = co-listed with other festivals/civic days", DER),
  "n_items_on_date": ("int", "Festivals + civic items co-listed on that date", DER),
  "attribution_weight": ("float", "1 / n_items_on_date - fractional share of the closure attributed to this festival", DER)},
 "data/processed/festival_master.csv": {
  "festival, tradition, festival_type": ("str", "Identity & classification", WIKI),
  "years_observed": ("int", "Years (of 2024-26) with at least one observation", DER),
  "states_upper_per_year": ("float", "Upper bound: states whose office closed on a date whose label names the festival", DER),
  "states_confirmed_max / states_confirmed_any_year": ("int", "States observing it on dates where it was the ONLY label", DER),
  "reach_identifiable": ("bool", "False when the festival never appears alone in RBI labels (reach cannot be separated)", DER),
  "expected_states_per_year": ("float", "MAIN reach metric: sum over states of max attribution weight, averaged over years", DER),
  "national_reach_pct": ("float", "Expected states / 29 x 100", DER), "n_regions, regions, states": ("int/str", "Geographic footprint", DER),
  "modal_month, months_observed, modal_season_imd": ("int/str", "Timing", DER),
  "date_drift_days": ("float", "Range of first-observed day-of-year across 2024-26 (0-1 => fixed Gregorian date)", DER),
  "calendar_basis": ("str", "Gregorian (fixed) | Lunar/Lunisolar (moving) | Undetermined (1 year)", DER),
  "mean_holiday_days, max_holiday_days": ("float/int", "Duration: consecutive holiday days per office-year", DER),
  "total_office_holiday_days, weighted_holiday_days, share_shared_date": ("int/float", "Volume of observations", DER),
  "wiki_* , attribution_url, attribution_publisher": ("str", "Source grounding of the tradition label", WIKI),
  "primary_source_url, primary_source_publisher": ("str", "RBI", RBI),
  "latest_trade_inr_crore, latest_trade_year, trade_source_url": ("float/int/url", "Most recent trade/economy figure, if any", "economic_footfall_raw.csv")},
 "data/processed/state_profile.csv": {
  "state, region, n_rbi_offices": ("str/int", "State/UT (Punjab, Haryana & Chandigarh combined = RBI Chandigarh office)", DER),
  "hol_days_<tradition>": ("float", "Festival holiday-days per office per year attributed to each tradition (weighted)", DER),
  "hol_days_total_festival": ("float", "Total festival holiday-days per office per year", DER),
  "hol_share_<tradition>": ("float", "% of the state's festival holidays per tradition", DER),
  "holiday_diversity_shannon": ("float", "Shannon entropy of hol_share over traditions", DER),
  "n_distinct_festivals": ("int", "Distinct festivals observed 2024-26", DER),
  "census_pct_<religion>": ("float", "Religion share of population, Census 2011 (Telangana uses undivided AP)", CEN),
  "pop_total": ("int", "Census 2011 population", CEN), "population_diversity_shannon": ("float", "Shannon entropy of census shares", "code/05_eda_statistics.py"),
  "census_source_url": ("url", "Census table URL", CEN)},
}
rows = [{"table": t, "column": c, "type": v[0], "description": v[1], "source": v[2]} for t, cols in D.items() for c, v in cols.items()]
pd.DataFrame(rows).to_csv(os.path.join(ROOT, "data", "data_dictionary.csv"), index=False)
md = ["# Data Dictionary - Indian Festivals Socio-Economic & Demographic Dataset\n",
      "Zero synthetic records: every row traces to RBI, Census of India, Wikipedia/Govt. attribution pages or a cited news/industry URL.\n",
      "## Collection sources\n",
      "| Source | Publisher | Use |\n|---|---|---|",
      f"| {RBI} | Reserve Bank of India (Govt. of India) | Festival dates & state-wise observance, 2024-2026 |",
      f"| {CEN} | Office of the Registrar General & Census Commissioner | State religious demography |",
      "| MediaWiki API (en.wikipedia.org) + utsav.gov.in, soreng.nic.in, dtahills.mn.gov.in, megtourism.gov.in | Wikipedia / Govt. | Tradition ('Observed by') attribution |",
      "| cait.in, The Tribune, AIR (newsonair.gov.in), Business Today, Outlook Business, Onmanorama, Nagaland Tribune, OdishaBytes, The News Minute, Millennium Post, The Federal, Angel One, Inshorts, IBEF | CAIT & verified news | Consumer spending, sector split, footfall |",
      "| nrf.com, english.www.gov.cn, stats.gov.sa, muenchen.de, Redseer via Storyboard18 | Industry / governments | Global analogues & e-commerce |",
      "| DataMeet India state boundaries (CC BY 2.5 IN) | DataMeet | Choropleth geometry only |\n",
      "## Known limitations\n",
      "* RBI labels list every holiday on a date nationwide, not per office. Where several festivals share a date the closure is split equally (attribution_weight); 39 of 99 festivals never appear alone, so their reach is flagged not identifiable.",
      "* **Sundays are not listed.** The RBI matrix contains no Sunday dates (banks are closed anyway), so a festival that falls on a Sunday is absent for that year - e.g. Ram Navami 2025, Muharram 2025, Mahavir Jayanti 2024, Maha Shivaratri 2026. About one festival-day in seven is missing in any single year; all per-year averages divide by three years and are therefore conservative (national total 15.5 festival-days per office per year; about 17.4 if each festival is averaged only over the years it appears).",
      "* **Scope of 'holiday'.** Only holidays notified under the Negotiable Instruments Act are covered. Holidays for government offices or schools only, restricted (optional) holidays and district-level local holidays are not. Holidays declared later in the year ARE included when RBI adds them (33 such dates in the data: elections, heavy rain, state mourning); the 2026 list reflects what was published on the scrape date.",
      "* Bank holidays measure *official recognition*, not participation. Census 2011 is the latest published religion census.",
      "* Trade figures are industry-body estimates (mostly CAIT surveys), many are pre-event projections; comparable national figures are not published for most non-Hindu festivals - itself a finding on measurement bias.\n"]
for t, cols in D.items():
    md += [f"## `{t}`\n", "| Column | Type | Description | Source |", "|---|---|---|---|"]
    md += [f"| `{c}` | {v[0]} | {v[1]} | {v[2]} |" for c, v in cols.items()] + [""]
open(os.path.join(ROOT, "data", "data_dictionary.md"), "w", encoding="utf-8").write("\n".join(md))
print(len(rows), "dictionary rows")
