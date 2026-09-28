# Data Dictionary - Indian Festivals Socio-Economic & Demographic Dataset

Zero synthetic records: every row traces to RBI, Census of India, Wikipedia/Govt. attribution pages or a cited news/industry URL.

## Collection sources

| Source | Publisher | Use |
|---|---|---|
| RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx | Reserve Bank of India (Govt. of India) | Festival dates & state-wise observance, 2024-2026 |
| Census of India 2011, Table C-01 - https://censusindia.gov.in/nada/index.php/catalog/11361 | Office of the Registrar General & Census Commissioner | State religious demography |
| MediaWiki API (en.wikipedia.org) + utsav.gov.in, soreng.nic.in, dtahills.mn.gov.in, megtourism.gov.in | Wikipedia / Govt. | Tradition ('Observed by') attribution |
| cait.in, The Tribune, AIR (newsonair.gov.in), Business Today, Outlook Business, Onmanorama, Nagaland Tribune, OdishaBytes, The News Minute, Millennium Post, The Federal, Angel One, Inshorts, IBEF | CAIT & verified news | Consumer spending, sector split, footfall |
| nrf.com, english.www.gov.cn, stats.gov.sa, muenchen.de, Redseer via Storyboard18 | Industry / governments | Global analogues & e-commerce |
| DataMeet India state boundaries (CC BY 2.5 IN) | DataMeet | Choropleth geometry only |

## Known limitations

* RBI labels list every holiday on a date nationwide, not per office. Where several festivals share a date the closure is split equally (attribution_weight); 39 of 99 festivals never appear alone, so their reach is flagged not identifiable.
* Bank holidays measure *official recognition*, not participation. Census 2011 is the latest published religion census.
* Trade figures are industry-body estimates (mostly CAIT surveys), many are pre-event projections; comparable national figures are not published for most non-Hindu festivals - itself a finding on measurement bias.

## `data/raw/rbi_holiday_matrix_raw.csv`

| Column | Type | Description | Source |
|---|---|---|---|
| `year` | int | Calendar year of the holiday | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `month` | int | Month 1-12 | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `day` | int | Day of month | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `date` | date | ISO date | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `rbi_regional_office` | str | RBI regional office (34) whose jurisdiction observes the holiday | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `rbi_holiday_description` | str | RBI's label for all holidays on that date across India ('|' joins multiple labels) | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `holiday_type` | str | Always 'NI Act holiday' (Negotiable Instruments Act); account-closing days excluded | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `source_url` | str | Exact page + POST parameters used | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `source_publisher` | str | Reserve Bank of India | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `retrieved_on` | date | Scrape date | code/01_scrape_rbi_holidays.py |

## `data/raw/festival_wikipedia_attribution.csv`

| Column | Type | Description | Source |
|---|---|---|---|
| `festival` | str | Canonical festival name (code/festival_catalog.py) | Derived (code/04_build_clean_dataset.py) |
| `wiki_title_requested / wiki_title_resolved` | str | Article requested / article actually returned | Wikipedia infobox (MediaWiki API) or Govt. page in attribution_url |
| `wiki_url` | url | Article URL | Wikipedia infobox (MediaWiki API) or Govt. page in attribution_url |
| `wiki_observed_by` | str | Infobox 'Observed by' text | Wikipedia infobox (MediaWiki API) or Govt. page in attribution_url |
| `wiki_type / wiki_significance / wiki_frequency / wiki_duration` | str | Infobox fields | Wikipedia infobox (MediaWiki API) or Govt. page in attribution_url |

## `data/raw/economic_footfall_raw.csv (.json)`

| Column | Type | Description | Source |
|---|---|---|---|
| `record_id` | str | ECO001.. | Derived (code/04_build_clean_dataset.py) |
| `festival` | str | Festival / event | per-row source_url |
| `tradition` | str | Tradition of the festival, or 'Global analogue' | per-row source_url |
| `year` | int | Year the figure refers to | per-row source_url |
| `metric` | str | festive_trade | creative_economy | festive_economy | footfall | temple_revenue | special_trains | sector_share_of_goods_sales | sector_trade | gold_trade | silver_trade | dhanteras_* | ecommerce_gmv | retail_sales | tourism_spending | Derived (code/04_build_clean_dataset.py) |
| `value / unit` | float/str | Figure exactly as published (INR crore, persons, percent, USD/CNY billion, trains) | per-row source_url |
| `geography` | str | Area the figure covers | per-row source_url |
| `sector` | str | Market sector (retail, jewellery, travel, FMCG...) | per-row source_url |
| `estimate_type` | str | reported (post-event) or projection (pre-event estimate) | per-row source_url |
| `publisher / source_type / source_url` | str | Who produced the number, kind of source, exact URL | - |
| `note` | str | Extra context quoted from the source | per-row source_url |
| `verified_on` | date | Date the page was opened and the figure confirmed | - |

## `data/processed/festival_observations.csv`

| Column | Type | Description | Source |
|---|---|---|---|
| `year, date, month, day, day_of_year` | int/date | Calendar fields | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `season_imd` | str | IMD season: Winter (Jan-Feb), Pre-monsoon (Mar-May), Monsoon (Jun-Sep), Post-monsoon (Oct-Dec) | India Meteorological Department definition |
| `rbi_regional_office, state, region` | str | Office, mapped State/UT (jurisdiction) and 6-way region | Derived (code/04_build_clean_dataset.py) |
| `festival` | str | Canonical festival resolved from description by regex | Derived (code/04_build_clean_dataset.py) |
| `tradition` | str | Hindu | Muslim | Christian | Sikh | Buddhist | Jain | Parsi | Tribal/Indigenous | Cultural (multi-faith) | Wikipedia infobox (MediaWiki API) or Govt. page in attribution_url |
| `festival_type` | str | Religious | Harvest | New Year | Seasonal | Commemoration | Cultural | Derived (code/04_build_clean_dataset.py) |
| `attribution` | str | unique = festival was the only item in RBI label; shared_date = co-listed with other festivals/civic days | Derived (code/04_build_clean_dataset.py) |
| `n_items_on_date` | int | Festivals + civic items co-listed on that date | Derived (code/04_build_clean_dataset.py) |
| `attribution_weight` | float | 1 / n_items_on_date - fractional share of the closure attributed to this festival | Derived (code/04_build_clean_dataset.py) |

## `data/processed/festival_master.csv`

| Column | Type | Description | Source |
|---|---|---|---|
| `festival, tradition, festival_type` | str | Identity & classification | Wikipedia infobox (MediaWiki API) or Govt. page in attribution_url |
| `years_observed` | int | Years (of 2024-26) with at least one observation | Derived (code/04_build_clean_dataset.py) |
| `states_upper_per_year` | float | Upper bound: states whose office closed on a date whose label names the festival | Derived (code/04_build_clean_dataset.py) |
| `states_confirmed_max / states_confirmed_any_year` | int | States observing it on dates where it was the ONLY label | Derived (code/04_build_clean_dataset.py) |
| `reach_identifiable` | bool | False when the festival never appears alone in RBI labels (reach cannot be separated) | Derived (code/04_build_clean_dataset.py) |
| `expected_states_per_year` | float | MAIN reach metric: sum over states of max attribution weight, averaged over years | Derived (code/04_build_clean_dataset.py) |
| `national_reach_pct` | float | Expected states / 29 x 100 | Derived (code/04_build_clean_dataset.py) |
| `n_regions, regions, states` | int/str | Geographic footprint | Derived (code/04_build_clean_dataset.py) |
| `modal_month, months_observed, modal_season_imd` | int/str | Timing | Derived (code/04_build_clean_dataset.py) |
| `date_drift_days` | float | Range of first-observed day-of-year across 2024-26 (0-1 => fixed Gregorian date) | Derived (code/04_build_clean_dataset.py) |
| `calendar_basis` | str | Gregorian (fixed) | Lunar/Lunisolar (moving) | Undetermined (1 year) | Derived (code/04_build_clean_dataset.py) |
| `mean_holiday_days, max_holiday_days` | float/int | Duration: consecutive holiday days per office-year | Derived (code/04_build_clean_dataset.py) |
| `total_office_holiday_days, weighted_holiday_days, share_shared_date` | int/float | Volume of observations | Derived (code/04_build_clean_dataset.py) |
| `wiki_* , attribution_url, attribution_publisher` | str | Source grounding of the tradition label | Wikipedia infobox (MediaWiki API) or Govt. page in attribution_url |
| `primary_source_url, primary_source_publisher` | str | RBI | RBI Holiday Matrix - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx |
| `latest_trade_inr_crore, latest_trade_year, trade_source_url` | float/int/url | Most recent trade/economy figure, if any | economic_footfall_raw.csv |

## `data/processed/state_profile.csv`

| Column | Type | Description | Source |
|---|---|---|---|
| `state, region, n_rbi_offices` | str/int | State/UT (Punjab, Haryana & Chandigarh combined = RBI Chandigarh office) | Derived (code/04_build_clean_dataset.py) |
| `hol_days_<tradition>` | float | Festival holiday-days per office per year attributed to each tradition (weighted) | Derived (code/04_build_clean_dataset.py) |
| `hol_days_total_festival` | float | Total festival holiday-days per office per year | Derived (code/04_build_clean_dataset.py) |
| `hol_share_<tradition>` | float | % of the state's festival holidays per tradition | Derived (code/04_build_clean_dataset.py) |
| `holiday_diversity_shannon` | float | Shannon entropy of hol_share over traditions | Derived (code/04_build_clean_dataset.py) |
| `n_distinct_festivals` | int | Distinct festivals observed 2024-26 | Derived (code/04_build_clean_dataset.py) |
| `census_pct_<religion>` | float | Religion share of population, Census 2011 (Telangana uses undivided AP) | Census of India 2011, Table C-01 - https://censusindia.gov.in/nada/index.php/catalog/11361 |
| `pop_total` | int | Census 2011 population | Census of India 2011, Table C-01 - https://censusindia.gov.in/nada/index.php/catalog/11361 |
| `population_diversity_shannon` | float | Shannon entropy of census shares | code/05_eda_statistics.py |
| `census_source_url` | url | Census table URL | Census of India 2011, Table C-01 - https://censusindia.gov.in/nada/index.php/catalog/11361 |
