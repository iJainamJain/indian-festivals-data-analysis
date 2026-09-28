"""Task 1c - Economic (consumer spending / trade) and footfall records for Indian festivals, plus
global analogue festivals for comparison.

ZERO SYNTHETIC DATA: every row below was transcribed from the cited URL.  Each page was opened
and the figure confirmed on 2026-09-28 (column `verified_on`).  Figures that could only be seen in a
search-engine snippet (e.g. Diwali 2022) were deliberately EXCLUDED.

`estimate_type`:  reported = post-event figure;  projection = pre-event / during-event estimate
by the publisher.  Keep the distinction in any modelling.
Output: data/raw/economic_footfall_raw.csv and .json
"""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = "2026-09-28"

CAIT_D25 = "https://cait.in/record-breaking-diwali-sales-of-%E2%82%B95-40-lakh-crore-in-goods-65-thousand-crores-in-services-reflect-indias-economic-strength-and-swadeshi-spirit/"
TRIB_D = "https://www.tribuneindia.com/news/bharatiya-diwali/record-rs-4-75-lakh-crore-of-sales-expected-during-festivals-driven-by-swadeshi-products-cait"
TRIB_D23 = "https://www.tribuneindia.com/news/business/diwali-sees-record-trade-of-rs-3-75-lakh-crore-cait-562159"
CAIT_RB25 = "https://cait.in/confluence-of-raksha-bandhan-and-quit-india-movement-on-august-9-traders-expect-business-worth-%E2%82%B917000-crore/"
INSH_RB24 = "https://inshorts.com/en/news/rakhi-business-set-to-grow-20--to--12-000-crore-this-year--cait-1723986512141"
OUT_RB26 = "https://www.outlookbusiness.com/industry/rakhi-trade-likely-to-exceed-over-30000-cr-caits-khandelwal"
CAIT_H25 = "https://cait.in/economic-impact-of-holi-festival-on-trade-business-expected-to-surpass-%E2%82%B960000-crore-this-year/"
AIR_H26 = "https://www.newsonair.gov.in/holi-trade-to-cross-%e2%82%b980000-crore-nationwide-cait"
TRIB_KC = "https://www.tribuneindia.com/news/business/karva-chauth-spurs-estimated-rs-28000-cr-business-nationwide-rs-8000-cr-in-delhi-alone-cait"
CAIT_G24 = "https://cait.in/ganesh-chaturthi-kickstarts-the-festive-season-sales-with-estimated-business-over-25000-crore-cait/"
BT_G25 = "https://www.businesstoday.in/india/story/indias-biggest-economic-influencer-powers-rs-45000-cr-economy-in-2025-expert-reveals-sector-wise-impact-492882-2025-09-06"
ANG_DH25 = "https://www.angelone.in/news/commodities/gold-silver-buying-on-dhanteras-2025-crosses-1-lakh-crore-rs-despite-price-surge"
CAIT_AT25 = "https://cait.in/gold-trade-across-india-estimated-at-%E2%82%B912000-crore-on-akshaya-tritiya-today/"
MP_DP = "https://www.millenniumpost.in/kolkata/durga-puja-generates-economy-of-rs-32377-cr-study-431963"
BC_DP = "https://www.britishcouncil.in/programmes/arts/Mapping-Creative-Economy-around-DurgaPuja"
FED_DP = "https://thefederal.com/category/states/east/west-bengal/durga-puja-festivities-economy-rebounds-up-to-by-fifteen-per-cent-209324"
AIR_KUMBH = "https://www.newsonair.gov.in/maha-kumbh-mela-2025-concludes-in-prayagraj-on-maha-shivratri"
TRIB_KUMBH = "https://www.tribuneindia.com/news/business/mahakumbh-2025-expected-to-boost-trade-by-rs-2-lakh-crore-says-confederation-of-all-india-traders"
ONM_SAB = "https://www.onmanorama.com/news/kerala/2025/01/21/sabarimala-hits-record-revenue-80-crore-increase.html"
NT_HB = "https://nagalandtribune.in/hornbill-festival-2024-records-204986-visitors/"
TRIB_AM = "https://www.tribuneindia.com/news/j-k/amarnath-yatra-set-for-new-record-as-pilgrim-count-crosses-4-lakh-in-18-days/"
OB_RY = "https://odishabytes.com/9-lakh-devotees-witness-puri-rath-yatra-amid-rain-key-rituals-conducted-smoothly-odisha-govt"
TNM_MED = "https://www.thenewsminute.com/telangana/medaram-jatara-one-world-s-largest-tribal-festivals-concludes-telangana-117817"
AIR_RAIL = "https://www.newsonair.gov.in/indian-railways-deploys-12-lakh-staff-runs-12000-special-trains-for-post-chhath-travel"
GASTAT = "https://www.stats.gov.sa/en/w/news/49"
RS_ECOM = "https://www.storyboard18.com/brand-marketing/e-commerce-recorded-14-billion-gmv-this-festive-season-reveals-redseers-report-47290.htm"
NRF = "https://nrf.com/media-center/press-releases/nrf-says-holiday-season-was-a-notable-success-as-consumers-came-out-to-spend-"
GOVCN = "https://english.www.gov.cn/archive/statistics/202502/05/content_WS67a34ea1c6d0868f4e8ef5ed.html"
MUC = "https://www.muenchen.de/en/events/oktoberfest/numbers-records"

# (festival, tradition, year, metric, value, unit, geography, sector, estimate_type, publisher, source_type, url, note)
R = [
    # ---- Diwali trade (CAIT national survey) ----
    ("Diwali (Deepavali)", "Hindu", 2021, "festive_trade", 125000, "INR crore", "India", "Retail (all)", "reported", "CAIT", "Industry body (via The Tribune)", TRIB_D, "Rs 1.25 lakh crore"),
    ("Diwali (Deepavali)", "Hindu", 2023, "festive_trade", 375000, "INR crore", "India", "Retail (all)", "reported", "CAIT", "Industry body (via The Tribune)", TRIB_D23, "Rs 3.75 lakh crore"),
    ("Diwali (Deepavali)", "Hindu", 2024, "festive_trade", 425000, "INR crore", "India", "Retail (all)", "reported", "CAIT", "Industry body (via The Tribune)", TRIB_D, "Rs 4.25 lakh crore"),
    ("Diwali (Deepavali)", "Hindu", 2025, "festive_trade", 605000, "INR crore", "India", "Retail (all)", "reported", "CAIT", "Industry body (primary)", CAIT_D25, "Rs 6.05 lakh crore = 5.40 goods + 0.65 services"),
    ("Diwali (Deepavali)", "Hindu", 2025, "festive_trade_goods", 540000, "INR crore", "India", "Goods", "reported", "CAIT", "Industry body (primary)", CAIT_D25, ""),
    ("Diwali (Deepavali)", "Hindu", 2025, "festive_trade_services", 65000, "INR crore", "India", "Services", "reported", "CAIT", "Industry body (primary)", CAIT_D25, ""),
    ("Diwali (Deepavali)", "Hindu", 2025, "dhanteras_trade", 100000, "INR crore", "India", "Retail (all)", "reported", "CAIT", "Industry body (via Angel One news)", ANG_DH25, "Dhanteras day"),
    ("Diwali (Deepavali)", "Hindu", 2025, "dhanteras_gold_silver", 60000, "INR crore", "India", "Jewellery / bullion", "reported", "CAIT", "Industry body (via Angel One news)", ANG_DH25, ""),
    ("Diwali (Deepavali)", "Hindu", 2025, "dhanteras_utensils", 15000, "INR crore", "India", "Household", "reported", "CAIT", "Industry body (via Angel One news)", ANG_DH25, ""),
    ("Diwali (Deepavali)", "Hindu", 2025, "dhanteras_electronics", 10000, "INR crore", "India", "Electronics", "reported", "CAIT", "Industry body (via Angel One news)", ANG_DH25, ""),
    # ---- Raksha Bandhan ----
    ("Raksha Bandhan", "Hindu", 2018, "festive_trade", 3000, "INR crore", "India", "Retail (rakhi & gifts)", "reported", "CAIT", "Industry body (via Inshorts)", INSH_RB24, ""),
    ("Raksha Bandhan", "Hindu", 2023, "festive_trade", 10000, "INR crore", "India", "Retail (rakhi & gifts)", "reported", "CAIT", "Industry body (via Inshorts)", INSH_RB24, ""),
    ("Raksha Bandhan", "Hindu", 2024, "festive_trade", 12000, "INR crore", "India", "Retail (rakhi & gifts)", "projection", "CAIT", "Industry body (via Inshorts)", INSH_RB24, "+20% YoY"),
    ("Raksha Bandhan", "Hindu", 2025, "festive_trade", 17000, "INR crore", "India", "Retail (rakhi & gifts)", "projection", "CAIT", "Industry body (primary)", CAIT_RB25, "+Rs 4,000 cr related products"),
    ("Raksha Bandhan", "Hindu", 2026, "festive_trade", 30000, "INR crore", "India", "Retail (rakhi & gifts)", "projection", "CAIT", "Industry body (via Outlook Business)", OUT_RB26, "rakhi ~25,000 + complementary"),
    # ---- Holi ----
    ("Holi", "Hindu", 2024, "festive_trade", 50000, "INR crore", "India", "Retail (all)", "reported", "CAIT", "Industry body (primary)", CAIT_H25, ""),
    ("Holi", "Hindu", 2025, "festive_trade", 60000, "INR crore", "India", "Retail (all)", "projection", "CAIT", "Industry body (primary)", CAIT_H25, "Delhi > Rs 8,000 cr"),
    ("Holi", "Hindu", 2026, "festive_trade", 80000, "INR crore", "India", "Retail (all)", "projection", "CAIT", "Public broadcaster (All India Radio)", AIR_H26, "Delhi > Rs 15,000 cr"),
    # ---- Karva Chauth ----
    ("Karva Chauth", "Hindu", 2023, "festive_trade", 15000, "INR crore", "India", "Retail (jewellery, apparel, cosmetics)", "reported", "CAIT", "Industry body (via The Tribune)", TRIB_KC, ""),
    ("Karva Chauth", "Hindu", 2024, "festive_trade", 22000, "INR crore", "India", "Retail (jewellery, apparel, cosmetics)", "reported", "CAIT", "Industry body (via The Tribune)", TRIB_KC, ""),
    ("Karva Chauth", "Hindu", 2025, "festive_trade", 28000, "INR crore", "India", "Retail (jewellery, apparel, cosmetics)", "reported", "CAIT", "Industry body (via The Tribune)", TRIB_KC, "Delhi ~ Rs 8,000 cr"),
    # ---- Ganesh Chaturthi ----
    ("Ganesh Chaturthi", "Hindu", 2024, "festive_trade", 25000, "INR crore", "India", "Retail + events", "projection", "CAIT", "Industry body (primary)", CAIT_G24, "20 lakh pandals; MH 7 lakh, KA 5 lakh"),
    ("Ganesh Chaturthi", "Hindu", 2025, "festive_trade", 45000, "INR crore", "India", "Retail + events", "projection", "Complete Circle Consultants (Gurmeet Chadha)", "Analyst (via Business Today)", BT_G25, "not CAIT"),
    # ---- Akshaya Tritiya ----
    ("Akshaya Tritiya", "Hindu", 2025, "gold_trade", 12000, "INR crore", "India", "Jewellery / bullion", "reported", "CAIT", "Industry body (primary)", CAIT_AT25, "silver Rs 4,000 cr extra"),
    ("Akshaya Tritiya", "Hindu", 2025, "silver_trade", 4000, "INR crore", "India", "Jewellery / bullion", "reported", "CAIT", "Industry body (primary)", CAIT_AT25, ""),
    # ---- Durga Puja ----
    ("Navratri / Durga Puja / Dussehra", "Hindu", 2019, "creative_economy", 32377, "INR crore", "West Bengal", "Creative industries", "reported", "British Council / QMUL / IIT Kharagpur", "Academic study (via Millennium Post)", MP_DP, "2.53% of state GDP; study page: " + BC_DP),
    ("Navratri / Durga Puja / Dussehra", "Hindu", 2024, "festive_economy", 42000, "INR crore", "West Bengal", "Retail + sponsorship", "reported", "Industry analysts (The Federal)", "Verified news", FED_DP, ""),
    ("Navratri / Durga Puja / Dussehra", "Hindu", 2025, "festive_economy", 48000, "INR crore", "West Bengal", "Retail + sponsorship", "projection", "Industry analysts (The Federal)", "Verified news", FED_DP, "range 46,000-50,000; midpoint stored"),
    # ---- Maha Kumbh ----
    ("Maha Kumbh Mela", "Hindu", 2025, "footfall", 662100000, "persons (visits)", "Uttar Pradesh", "Pilgrimage", "reported", "Govt. of UP via All India Radio", "Public broadcaster (All India Radio)", AIR_KUMBH, "66 crore 21 lakh over 45 days"),
    ("Maha Kumbh Mela", "Hindu", 2025, "festive_trade", 200000, "INR crore", "Uttar Pradesh", "Tourism, F&B, religious goods", "projection", "CAIT", "Industry body (via The Tribune)", TRIB_KUMBH, "accommodation 40k, F&B 20k, religious items 20k"),
    # ---- Sabarimala ----
    ("Sabarimala Mandala-Makaravilakku", "Hindu", 2024, "temple_revenue", 440, "INR crore", "Kerala", "Pilgrimage", "reported", "Kerala Devaswom Minister / TDB", "Verified news (Onmanorama)", ONM_SAB, "season 2024-25"),
    ("Sabarimala Mandala-Makaravilakku", "Hindu", 2023, "temple_revenue", 360, "INR crore", "Kerala", "Pilgrimage", "reported", "Kerala Devaswom Minister / TDB", "Verified news (Onmanorama)", ONM_SAB, "season 2023-24"),
    # ---- Amarnath ----
    ("Amarnath Yatra", "Hindu", 2011, "footfall", 630000, "persons", "Jammu & Kashmir", "Pilgrimage", "reported", "Shri Amarnathji Shrine Board (via The Tribune)", "Verified news", TRIB_AM, "all-time high"),
    ("Amarnath Yatra", "Hindu", 2024, "footfall", 512000, "persons", "Jammu & Kashmir", "Pilgrimage", "reported", "Shri Amarnathji Shrine Board (via The Tribune)", "Verified news", TRIB_AM, ""),
    ("Amarnath Yatra", "Hindu", 2025, "footfall", 414000, "persons", "Jammu & Kashmir", "Pilgrimage", "reported", "Shri Amarnathji Shrine Board (via The Tribune)", "Verified news", TRIB_AM, ""),
    # ---- Rath Yatra ----
    ("Rath Yatra", "Hindu", 2026, "footfall", 900000, "persons", "Odisha (Puri)", "Pilgrimage", "reported", "Govt. of Odisha (via OdishaBytes)", "Verified news", OB_RY, "single day"),
    # ---- Chhath / Diwali travel ----
    ("Chhath Puja", "Hindu", 2025, "special_trains", 12000, "trains", "India", "Travel (rail)", "reported", "Ministry of Railways via All India Radio", "Public broadcaster (All India Radio)", AIR_RAIL, "+12 lakh staff deployed"),
    # ---- Tribal / Indigenous ----
    ("Hornbill Festival", "Tribal/Indigenous", 2024, "footfall", 204986, "persons", "Nagaland", "Tourism", "reported", "Nagaland Tourism Dept (via Nagaland Tribune)", "Verified news", NT_HB, "foreign 2,527; domestic 54,306"),
    ("Hornbill Festival", "Tribal/Indigenous", 2023, "footfall", 150000, "persons", "Nagaland", "Tourism", "reported", "Nagaland Tourism Dept (via Nagaland Tribune)", "Verified news", NT_HB, "1.5 lakh"),
    ("Medaram Sammakka Saralamma Jatara", "Tribal/Indigenous", 2020, "footfall", 15000000, "persons", "Telangana", "Pilgrimage", "reported", "The News Minute", "Verified news", TNM_MED, "1.5 crore over 4 days"),
    # ---- Muslim (pilgrimage abroad; domestic trade figures not published by CAIT) ----
    ("Hajj (Eid-ul-Adha season)", "Muslim", 2025, "footfall", 1673230, "persons", "Saudi Arabia (global)", "Pilgrimage", "reported", "GASTAT (Saudi statistics authority)", "Government statistics", GASTAT, "1,506,576 from abroad"),
    # ---- Festive e-commerce ----
    ("Festive season (Onam-Diwali)", "Cultural (multi-faith)", 2024, "ecommerce_gmv", 14, "USD billion", "India", "E-commerce", "reported", "Redseer Strategy Consultants", "Consultancy (via Storyboard18)", RS_ECOM, "15 Sep-31 Oct 2024, +12% YoY"),
    # ---- Global analogues ----
    ("US winter holiday season (Thanksgiving-Christmas)", "Global analogue", 2024, "retail_sales", 994.1, "USD billion", "USA", "Retail (all)", "reported", "National Retail Federation", "Industry body (primary)", NRF, "1 Nov-31 Dec"),
    ("Chinese Spring Festival (Lunar New Year)", "Global analogue", 2025, "tourism_spending", 677, "CNY billion", "China", "Tourism", "reported", "Ministry of Culture and Tourism (gov.cn)", "Government", GOVCN, "8-day holiday; 501 mn trips"),
    ("Chinese Spring Festival (Lunar New Year)", "Global analogue", 2025, "footfall", 501000000, "trips", "China", "Tourism", "reported", "Ministry of Culture and Tourism (gov.cn)", "Government", GOVCN, ""),
    ("Oktoberfest", "Global analogue", 2025, "footfall", 6500000, "persons", "Germany (Munich)", "Tourism", "reported", "City of Munich", "Government", MUC, ""),
    ("Oktoberfest", "Global analogue", 2024, "footfall", 6700000, "persons", "Germany (Munich)", "Tourism", "reported", "City of Munich", "Government", MUC, ""),
]
# Diwali 2025 sector split (share of goods sales), CAIT primary report
for sector, pct in [("Grocery & FMCG", 12), ("Gold & Jewellery", 10), ("Electronics & Electricals", 8), ("Consumer Durables", 7),
                    ("Ready-made Garments", 7), ("Gift Items", 7), ("Home Decor", 5), ("Furnishing & Furniture", 5),
                    ("Sweets & Namkeen", 5), ("Textiles & Fabrics", 4), ("Pooja Articles", 3), ("Fruits & Dry Fruits", 3),
                    ("Bakery & Confectionery", 3), ("Footwear", 2), ("Other", 19)]:
    R.append(("Diwali (Deepavali)", "Hindu", 2025, "sector_share_of_goods_sales", pct, "percent", "India", sector,
              "reported", "CAIT", "Industry body (primary)", CAIT_D25, ""))
# Ganesh Chaturthi 2024 sector split, CAIT primary
for sector, v in [("Pandal setup", 10000), ("Event management", 5000), ("Catering & snacks", 3000), ("Retail merchandise", 3000),
                  ("Food & sweets", 2000), ("Tourism & transport", 2000), ("Idols", 500), ("Flowers & ritual items", 500)]:
    R.append(("Ganesh Chaturthi", "Hindu", 2024, "sector_trade", v, "INR crore", "India", sector, "projection", "CAIT",
              "Industry body (primary)", CAIT_G24, ""))
# Maha Kumbh 2025 sector split, CAIT via Tribune
for sector, v in [("Accommodation & tourism", 40000), ("Food & beverages", 20000), ("Religious items & offerings", 20000),
                  ("Entertainment & media", 10000), ("Transport & logistics", 10000), ("Tourism services", 10000),
                  ("Medical & wellness", 3000), ("Digital services", 1000)]:
    R.append(("Maha Kumbh Mela", "Hindu", 2025, "sector_trade", v, "INR crore", "Uttar Pradesh", sector, "projection", "CAIT",
              "Industry body (via The Tribune)", TRIB_KUMBH, ""))

cols = ["festival", "tradition", "year", "metric", "value", "unit", "geography", "sector", "estimate_type",
        "publisher", "source_type", "source_url", "note"]
rows = [dict(zip(cols, r)) for r in R]
for i, r in enumerate(rows, 1):
    r["record_id"] = f"ECO{i:03d}"; r["verified_on"] = V
out = os.path.join(ROOT, "data", "raw", "economic_footfall_raw")
fields = ["record_id"] + cols + ["verified_on"]
with open(out + ".csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
json.dump(rows, open(out + ".json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(rows), "records ->", out + ".csv/.json")
