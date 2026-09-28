# What India's Bank-Holiday Calendar Reveals About How the Country Celebrates

*A data-driven look at 99 festivals, 29 states, three years of official holidays, and the economics of celebration*

**By Jainam Jain, Vrushan Patil, Dhanush Chowke, Aditya Tambe and Vivek Jaiswal** · B.E. (Electronics & Computer Science), Vidyalankar Institute of Technology · Data Analytics & Visualization project

---

Ask ten people "which festivals matter most in India?" and you'll get ten answers, usually shaped by where they grew up. We wanted to swap opinion for evidence. So we built a dataset where **every record traces to an official or verifiable source**, and asked three questions:

1. **When and where** does India officially pause to celebrate?
2. **Whose** festivals appear on the calendar, and how does that compare with who actually lives in each state?
3. **What is it worth**, economically, and how do we even measure that?

No festival is ranked as "better" here, and no community is singled out. The numbers are what they are, and every figure has a footnote.

## How the data was built

- **Festival dates and state coverage:** the Reserve Bank of India's official holiday matrix for all 34 RBI regional offices (29 states/UTs), covering **every holiday in 2024, 2025 and 2026**. That gives 2,705 festival-holiday observations for **99 distinct festivals**.[1]
- **Tradition of each festival:** taken from each festival's Wikipedia infobox ("Observed by"). Where no article exists, we used Government of India / State tourism portals.[2]
- **Demography:** Census of India 2011, Table C-01 (religion by state), the latest published religion census.[3]
- **Economics and footfall:** 78 figures, each opened and checked on its source page. Sources include CAIT trade surveys, state governments, All India Radio, and verified news outlets. Global comparisons come from NRF (US), China's Ministry of Culture & Tourism, Saudi GASTAT and the City of Munich.[4]

**One honest caveat up front:** RBI publishes one combined label per date (e.g. *"Ambedkar Jayanti / Vishu / Bihu / Baisakhi"*), not per state. When several festivals share a date, we split that day equally among them. Bank holidays measure **official recognition**, not how many people celebrate.

## 1. The calendar has two big peaks: March–April and October

![Festival holidays by month and tradition](images/F02_month_timeline_by_tradition.png)
*Fig. 1: Festival bank-holiday days per RBI office, by month and tradition, averaged over 2024–26.[1]*

Festival holidays are **not spread evenly** across the year. A chi-square goodness-of-fit test rejects uniformity decisively (χ² = 551, df = 11, p < 0.001).[5]

- **March** (2.7 days per office) and **April** (2.1) are the busiest months. Holi, Eid-ul-Fitr, Good Friday, Mahavir Jayanti and the spring New Year festivals (Ugadi, Gudi Padwa, Bihu, Vishu, Baisakhi, Cheiraoba) all fall here.
- **October** (2.5) belongs almost entirely to the Navratri–Durga Puja–Dussehra–Diwali season.
- **December** is Christmas; **November** is Guru Nanak Jayanti and Chhath; **May–June** carry Buddha Purnima and Eid-ul-Adha.
- **February and July** are the quietest months.

**Is a festival's season linked to its faith?** Not significantly. A chi-square test of tradition × IMD season gives a permutation p of 0.58 (Cramér's V = 0.16). Every tradition has festivals spread across the year.

## 2. The state-wise picture

![Festival holidays per year by state](images/F05_map_festival_holidays.png)
*Fig. 2: Festival bank holidays per year, by state.[1]*

- **Most festival holidays per year:** Sikkim (21.2), Uttar Pradesh (19.8), Jharkhand (19.1), West Bengal (18.0).
- **Fewest:** Goa (11.3), Arunachal Pradesh (11.6), Delhi (11.6), Nagaland (11.6).

Across the six regions, a Kruskal–Wallis test found **no significant difference** in holiday counts (p = 0.58). Big differences exist between individual states, not between North, South, East, West, Central and the North-East as blocks.

![State x month heatmap](images/F04_state_month_heatmap.png)
*Fig. 3: State-wise heatmap of festival bank-holiday days by month. Darker cells mark each state's festival season: Tamil Nadu in January (Pongal), West Bengal, Tripura and Sikkim in October, and Nagaland, Mizoram and Meghalaya in December.[1]*

## 3. Do holiday calendars mirror demography?

This was the question we cared about most.

![Holiday share vs population share](images/F07_holiday_vs_population_share.png)
*Fig. 4: Each dot is a state. The x-axis shows a faith's share of the population (Census 2011); the y-axis shows its share of that state's festival holidays.[1, 3]*

**Yes, for every faith tested.** The share of a state's festival holidays belonging to each tradition rises with that community's population share:

- **Buddhist:** ρ = 0.71 (p < 0.001)
- **Jain:** ρ = 0.64 (p < 0.001)
- **Hindu:** ρ = 0.58 (p = 0.001)
- **Sikh:** ρ = 0.54 (p = 0.003)
- **Christian:** ρ = 0.53 (p = 0.003)
- **Muslim:** ρ = 0.42 (p = 0.022)

(ρ is the Spearman rank correlation across 29 states/UTs; 1 would mean a perfect match.)

**But the calendar is flatter than the population.** Nationally, Hindus are 79.8% of the population (Census 2011)[3] but hold about **46%** of festival holidays. Muslim festivals hold about 17% of holidays (population 14.2%). Christian festivals hold about 14% (population 2.3%). Tribal and indigenous festivals hold about 7%.

The reason is structural. A handful of festivals (Christmas, Good Friday, the two Eids, Buddha Purnima, Mahavir Jayanti, Guru Nanak Jayanti) are **gazetted almost nationwide**, whatever the local population. Hindu festivals are more numerous (45 of 99) but more **regional**: their median reach is under two states. The shared national calendar gives minority traditions visibility beyond their numbers. The regional calendar reflects local majorities.

![Holiday diversity map](images/F06_map_holiday_diversity.png)
*Fig. 5: Diversity of each state's festival calendar (Shannon index across traditions).[1]*

Delhi, Mizoram and Arunachal Pradesh have the most diverse holiday calendars. Interestingly, a state's religious diversity in the Census does **not** significantly predict how diverse its holiday calendar is (ρ = 0.25, p = 0.19).

## 4. What machine learning adds

**Clustering states by their calendar.** K-Means on the Hindu, Muslim, Christian and Tribal/Indigenous holiday shares found four groups (silhouette = 0.41; bootstrap stability ARI = 0.61):

- **Christian-heavy calendars:** Arunachal Pradesh, Goa, Mizoram, Nagaland.
- **Muslim-heavy calendars:** Delhi, Jammu & Kashmir, Kerala, Chhattisgarh.
- **Tribal/indigenous-heavy calendars:** Manipur, Meghalaya, Tripura.
- **Hindu-heavy calendars:** the remaining 18 states.

These clusters barely overlap with geographic regions (ARI = 0.03). **Neighbouring states often celebrate differently**, and distant states can have similar calendars.

![State clusters map](images/M05_cluster_map.png)
*Fig. 6: States grouped by the mix of their festival calendar (K-Means, k = 4). Colours match the tradition colours used throughout.*

**Can a festival's date and footprint reveal its faith?** Only partly. A Random Forest reached macro-F1 = 0.40, against 0.16 for a majority-class baseline (repeated 5-fold cross-validation).

- The strongest signal is **North-East presence**, which separates tribal and indigenous festivals.
- The model often **confuses Diwali, Holi and Dussehra with the Eids and Christmas**, because nationwide festivals of every faith share the same kind of footprint.

In calendar terms, India's biggest festivals look more alike than different.

## 5. The economics of celebration

![Festive trade trend](images/F08_festive_trade_trend.png)
*Fig. 7: Festive trade estimates by year. Open markers are pre-event projections.[6]*

According to CAIT's national trader surveys:

- **Diwali 2025:** ₹6.05 lakh crore (about US$68.8 billion), made up of ₹5.40 lakh crore in goods and ₹65,000 crore in services. That is up from ₹1.25 lakh crore in 2021.[6]
- **Holi:** ₹60,000 crore in 2025, with ₹80,000 crore projected for 2026.[6]
- **Raksha Bandhan:** ₹17,000 crore projected for 2025, up from ₹3,000 crore in 2018.[6]
- **Karva Chauth 2025:** ₹28,000 crore.[6]

A pooled log-linear model with a separate term for each festival estimates **about 34% annual growth** in reported festive trade (95% CI 27–41%, p < 0.001). A version trained only on data up to 2025 predicted CAIT's 2026 Holi figure within 3% and its Raksha Bandhan figure within 23%.[5]

![Diwali sector split](images/F09_diwali_sector_split.png)
*Fig. 8: Where Diwali 2025 spending went. Grocery/FMCG (12%), jewellery (10%) and electronics (8%) lead.[6]*

**Crowds.** Maha Kumbh 2025 recorded 66.21 crore visits over 45 days, according to All India Radio / the Government of UP. That is about **1.47 crore visits a day**.[7] Telangana's Medaram Jatara, among India's largest tribal gatherings, drew about 1.5 crore people in four days in 2020.[7]

![Footfall density](images/F10_footfall_density.png)
*Fig. 9: Average visits per event-day, Indian festivals vs global analogues.[7]*

For scale:

- The US holiday season (Nov–Dec 2024) generated **US$994 billion** in retail sales.[8]
- China's 2025 Spring Festival generated **¥677 billion** (about US$94 billion) in tourism spending alone.[8]
- Oktoberfest drew about **6.5 million** visitors in 2025.[8]

## A measurement blind spot worth naming

While building the economic table, we found that **nationwide spending estimates are published regularly for Hindu festivals, but rarely for Eid, Christmas, Gurpurab, Buddha Purnima or tribal festivals.** For those, the verifiable numbers are mostly footfall or pilgrimage counts (Hajj, Hornbill, Medaram).

This is not evidence that other festivals matter less economically. **It shows what gets measured.** Anyone comparing "festival economies" in India should keep that gap in mind. It is also an open invitation to researchers and industry bodies to fill it.

## Key takeaways

1. India's official festival calendar peaks in **March–April and October**. Every tradition is spread across the year.
2. Holiday calendars **track demography** (ρ between 0.42 and 0.71 for every faith). They are also **more plural than the population**, because a set of minority festivals is recognised nationwide.
3. States cluster by **calendar culture**, not geography.
4. Reported festive trade is growing fast, about 34% a year. But these are survey estimates, often pre-event, and they cover some traditions far better than others.

**What would you add?** If you know a verified data source for festival spending on Eid, Christmas, Gurpurab or tribal festivals, please share it in the comments. We'll update the dataset and credit you.

*All code, the cleaned dataset and a full data dictionary are available on GitHub: https://github.com/iJainamJain/indian-festivals-data-analysis*

---

### Sources and footnotes

1. Reserve Bank of India, *Holidays under the Negotiable Instruments Act*, holiday matrix for all regional offices, 2024–2026. https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx (retrieved 28 Sep 2026). Shared-date holidays are split equally among co-listed items.
2. Wikipedia infobox "Observed by" field, fetched through the MediaWiki API for each festival. Where no article exists: Ministry of Tourism, utsav.gov.in (Pang Lhabsol, Nongkrem Dance); Govt. of Sikkim, soreng.nic.in/festivals (Drukpa Tshe-zi, Saga Dawa); Govt. of Manipur, dtahills.mn.gov.in/kut (Kut); Govt. of Meghalaya, megtourism.gov.in (Shad Suk Mynsiem).
3. Census of India 2011, Table C-01, *Population by religious community*. https://censusindia.gov.in/nada/index.php/catalog/11361. Telangana uses undivided Andhra Pradesh shares.
4. The full list of 78 records, each with its URL and verification date, is in `economic_footfall_raw.csv` in the repository.
5. Author's analysis. Tests are two-sided at α = 0.05. Full tables are in the Statistical Valuation & EDA report.
6. CAIT: Diwali 2025 — cait.in (10 Nov 2025) and IBEF (22 Oct 2025); Diwali 2021, 2023, 2024 — The Tribune (3 Oct 2025; Nov 2023); Holi — cait.in (8 Apr 2025) and All India Radio (22 Feb 2026); Raksha Bandhan — cait.in (14 Jul 2025), Inshorts (Aug 2024) and Outlook Business (25 Aug 2026); Karva Chauth — The Tribune (10 Oct 2025); Ganesh Chaturthi 2024 — cait.in (10 Sep 2024); Ganesh Chaturthi 2025 — Complete Circle Consultants via Business Today (6 Sep 2025).
7. Maha Kumbh — All India Radio, newsonair.gov.in (26 Feb 2025); Medaram — The News Minute (9 Feb 2020); Hornbill 2024 — Nagaland Tourism via Nagaland Tribune (11 Dec 2024); Hajj 2025 — GASTAT, stats.gov.sa (5 Jun 2025).
8. National Retail Federation (16 Jan 2025); Government of the PRC, english.www.gov.cn (5 Feb 2025); City of Munich, muenchen.de.
9. Project repository (code, data, data dictionary): https://github.com/iJainamJain/indian-festivals-data-analysis
