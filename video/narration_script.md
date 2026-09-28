# Narration script

## Slide 1: What India's Holiday Calendar Reveals

Hello. We are Jainam Jain, Vrushan Patil, Dhanush Chowke, Aditya Tambe and Vivek Jaiswal. This video summarises our data analytics project on the socio-economic and demographic patterns of Indian festivals. It covers the dataset, the statistics, the machine learning models, and the public blog.

## Slide 2: 1. Motivation

India celebrates hundreds of festivals, but most information about them is scattered and anecdotal, which makes biased comparisons easy. My goal was an evidence-only picture: when and where festivals are officially recognised, whose festivals they are, and what they are worth economically. The strict rule was zero synthetic data. Every record carries its source link.

## Slide 3: 1. Dataset curation and source integrity

The backbone is the Reserve Bank of India's official holiday matrix. We scraped every holiday for all thirty-four regional offices, covering twenty-nine states, for 2024 to 2026. That gave 2,705 festival observations across 99 festivals. Each festival's tradition comes from its Wikipedia infobox, or a government tourism portal. Demography comes from Census 2011. We also added 78 economic and crowd figures, every one checked on its original page. Where RBI lists several festivals on one date, the day is split equally, and we flag festivals whose reach cannot be separated.

## Slide 4: 2. When India celebrates

First, timing. Festival holidays are strongly concentrated. A chi-square test rejects a uniform spread across months. March, October and April are the peak months. But a festival's season does not depend on its faith: every tradition has festivals spread through the year.

## Slide 5: 2. Do calendars mirror demography?

Next, demography. For every faith we tested, a state's share of holidays for that faith rises with its population share. The correlations run from 0.42 to 0.71, all significant. But the calendar is flatter than the population. Hindu festivals are about forty-six percent of festival holidays, against a population share near eighty percent, because Christmas, both Eids, Buddha Purnima, Mahavir Jayanti and Guru Nanak Jayanti are recognised almost nationwide.

## Slide 6: 2. Where India celebrates

Geographically, Sikkim, Uttar Pradesh and Jharkhand have the most festival bank holidays, while Goa, Arunachal Pradesh, Delhi and Nagaland have the fewest. Differences exist between individual states, not between the six broad regions.

## Slide 7: 3. Machine learning: state clusters

For machine learning, we first clustered states by the mix of their festival calendar. K-Means selected 4 clusters with a silhouette of 0.41, and bootstrap resampling shows they are reasonably stable. The clusters hardly overlap with geographic regions, so neighbouring states often celebrate differently.

## Slide 8: 3. Machine learning: classification and forecasting

Second, we asked whether a festival's timing and geography reveal its tradition. A Random Forest reached a macro F1 of 0.40, well above the 0.16 baseline but far from perfect. The model confuses Diwali and Holi with the Eids and Christmas, because India's big festivals share the same nationwide footprint. Third, a log-linear trade model estimates about 34.0 percent growth a year in reported festive trade. Trained only on data up to 2025, it predicted the 2026 Holi estimate within 3 percent.

## Slide 9: Economics and crowds

On economics, CAIT reports Diwali 2025 trade of six point zero five lakh crore rupees. Maha Kumbh recorded sixty-six crore visits in forty-five days, far denser than Oktoberfest or the Hajj. One important finding is a measurement blind spot: national spending estimates are published for Hindu festivals, but rarely for Eid, Christmas, Gurpurab or tribal festivals. That gap reflects what gets measured, not what matters.

## Slide 10: 4. Public blog and reception

The article is live on Medium, published on 28 September 2026. It has 0 external reactions and comments, working towards the target of 40, and we replied to 0 comments.

## Slide 11: Key takeaways

To conclude: the official calendar peaks in spring and October. It tracks demography, yet it is more plural than the population. States cluster by calendar culture rather than geography. And festive trade is growing quickly, but it is measured unevenly across traditions. All code, data and sources are in the project repository. Thank you.
