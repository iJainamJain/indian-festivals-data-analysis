# Narration script

Voice: en-IN-PrabhatNeural (Indian English)

## Slide 1: What India's Holiday Calendar Reveals

Hello. We are Jainam Jain, Vrushan Patil, Dhanush Chowke, Aditya Tambe and Vivek Jaiswal. This video summarises our data analytics project on the socio-economic and demographic patterns of Indian festivals. We will cover the dataset, the statistics, the machine learning models, and our public blog.

## Slide 2: Festival comparisons usually rest on opinion, not data

India celebrates hundreds of festivals, but most information about them is scattered and anecdotal. That makes biased comparisons easy. Our goal was an evidence-only picture: when and where festivals are officially recognised, whose festivals they are, and what they are worth economically. We followed one strict rule. Zero synthetic data. Every record carries the link it came from.

## Slide 3: An official, source-linked festival dataset

The backbone is the Reserve Bank of India's official holiday list. We collected every bank holiday for all thirty-four regional offices, covering twenty-nine states, for 2024 to 2026. That gave 2,705 festival holiday records across 99 festivals. Each festival's tradition comes from its Wikipedia page or a government portal, and demography comes from Census 2011. We also added 78 spending and crowd figures, each one checked on its original page.

## Slide 4: How accurate is it? What the RBI list covers, and what it misses

How accurate is this data? The RBI list is the official record of bank holidays, and it is updated when holidays are declared later. Our data includes 33 such dates, for elections, heavy rain and state mourning. But it has limits. A holiday that falls on a Sunday is not listed, so roughly one festival day in seven is missing in any single year. Holidays meant only for government offices or schools, optional holidays, and district-level holidays are also not covered. So our numbers measure official bank holiday recognition, not every celebration. We average three years to reduce the Sunday effect.

## Slide 5: India's festival calendar peaks in March, April and October

First, timing. Festival holidays are strongly concentrated. A chi-square test rejects an even spread across months. March, October and April are the peaks. But a festival's season does not depend on its faith. Every tradition has festivals spread through the year.

## Slide 6: Holiday counts vary by state, not by region

Next, geography. Sikkim, Uttar Pradesh and Jharkhand have the most festival bank holidays. Goa, Arunachal Pradesh and Delhi have the fewest. The differences are between individual states, not between the six broad regions.

## Slide 7: Calendars follow demography, but are more plural than the population

Now, demography. For every faith we tested, a state's share of holidays for that faith rises with its share of the population. The correlations run from zero point four two to zero point seven one, and all are significant. But the calendar is flatter than the population. Hindu festivals are about forty-six percent of festival holidays, against a population share near eighty percent. That is because Christmas, both Eids, Buddha Purnima, Mahavir Jayanti and Guru Nanak Jayanti are recognised almost nationwide.

## Slide 8: Model 1: states group by calendar culture, not geography

For machine learning, we first clustered states by the mix of their festival calendar. K-Means selected 4 clusters, with a silhouette score of 0.41. Resampling shows the groups are reasonably stable. And they hardly match geographic regions. Neighbouring states often celebrate differently.

## Slide 9: Model 2: can a festival's date and footprint reveal its faith?

Second, we asked whether a festival's timing and geography reveal its tradition. A Random Forest reached a macro F one score of 0.40. That is well above the baseline of 0.16, but far from perfect. The strongest signal is presence in the North East. The model confuses Diwali and Holi with the Eids and Christmas, because India's big festivals share the same nationwide footprint.

## Slide 10: Model 3: reported festive trade is growing fast

Third, economics. A log-linear model estimates about 34 percent growth a year in reported festive trade. The traders' body C A I T reports Diwali 2025 trade of six point zero five lakh crore rupees. Trained only on data up to 2025, our model predicted the 2026 Holi estimate within 3 percent.

## Slide 11: Crowds are huge, and spending data has a blind spot

On crowds, Maha Kumbh 2025 recorded sixty-six crore visits in forty-five days. That is far denser than Oktoberfest or the Hajj. We also found a measurement blind spot. National spending estimates are published for Hindu festivals, but rarely for Eid, Christmas, Gurpurab or tribal festivals. That gap shows what gets measured, not what matters.

## Slide 12: The findings are published, with every figure cited

Our article is live on Medium, with every chart cited to its source. So far we have logged 0 external reactions and comments, against a target of forty, and we have replied to 0 comments. Only readers from outside our institution are counted, and each one is backed by a screenshot. The code and data are public on GitHub.

## Slide 13: Four things the data shows

To conclude. The official calendar peaks in spring and in October. It follows demography, yet it is more plural than the population. States group by calendar culture, not geography. And festive trade is growing quickly, but it is measured unevenly across traditions. All our code, data and sources are public. Thank you.
