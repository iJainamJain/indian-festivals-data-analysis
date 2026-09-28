# Statistical Valuation & EDA Report

All tests two-sided, alpha = 0.05. Data: RBI holiday matrix 2024-26 (34 offices, 29 states/UTs), Census 2011 C-01, and 78 verified economic/footfall records.

## 1. Descriptive statistics

|                                              |   n |      mean |   median |       std |     min |       q1 |        q3 |       max |      iqr |   cv_pct |   skewness |   kurtosis |
|:---------------------------------------------|----:|----------:|---------:|----------:|--------:|---------:|----------:|----------:|---------:|---------:|-----------:|-----------:|
| festival_expected_states_per_year            |  99 |      4.11 |     1.27 |      6.32 |    0.33 |     0.92 |      4.08 |     29    |     3.16 |   153.85 |       2.44 |       5.21 |
| festival_mean_holiday_days (duration)        |  99 |      1.03 |     1    |      0.09 |    1    |     1    |      1    |      1.63 |     0    |     8.5  |       4.44 |      23.22 |
| festival_date_drift_days (moving festivals)  |  64 |     23.19 |    19    |     43.7  |    6    |    16.75 |     22    |    365    |     5.25 |   188.44 |       7.65 |      57.38 |
| state_festival_holidays_per_year (frequency) |  29 |     15.39 |    15.32 |      2.49 |   11.27 |    14.15 |     16.63 |     21.23 |     2.47 |    16.16 |       0.27 |      -0.27 |
| state_holiday_diversity_shannon              |  29 |      1.54 |     1.52 |      0.14 |    1.28 |     1.44 |      1.65 |      1.88 |     0.21 |     9.15 |       0.46 |      -0.21 |
| state_distinct_festivals_2024_26             |  29 |     34.97 |    35    |      5.68 |   19    |    31    |     39    |     45    |     8    |    16.24 |      -0.52 |       0.4  |
| festive_trade_INR_crore (spending)           |  18 | 118167    | 37500    | 173145    | 3000    | 18250    | 113750    | 605000    | 95500    |   146.53 |       1.77 |       1.88 |


### By tradition

| tradition              |   festivals |   mean_expected_states |   median_expected_states |   mean_duration_days |   pct_lunar |   holiday_days_per_office_per_year |   share_of_all_festival_holidays_pct |
|:-----------------------|------------:|-----------------------:|-------------------------:|---------------------:|------------:|-----------------------------------:|-------------------------------------:|
| Hindu                  |          45 |                   3.98 |                     1.74 |                 1.04 |       68.89 |                               7.22 |                                 46.5 |
| Tribal/Indigenous      |          22 |                   1.53 |                     1    |                 1    |       63.64 |                               1.13 |                                  7.3 |
| Muslim                 |           7 |                  10.15 |                     8    |                 1.01 |      100    |                               2.69 |                                 17.3 |
| Christian              |           7 |                   8.38 |                     1    |                 1.01 |       14.29 |                               2.1  |                                 13.5 |
| Buddhist               |           6 |                   2.74 |                     1    |                 1.05 |       83.33 |                               0.63 |                                  4   |
| Sikh                   |           5 |                   2.35 |                     0.67 |                 1    |       60    |                               0.43 |                                  2.8 |
| Cultural (multi-faith) |           4 |                   3.28 |                     3.19 |                 1.07 |       25    |                               0.51 |                                  3.3 |
| Jain                   |           2 |                   5.06 |                     5.06 |                 1    |      100    |                               0.37 |                                  2.4 |
| Parsi                  |           1 |                  12.89 |                    12.89 |                 1    |        0    |                               0.44 |                                  2.9 |


## 2. Hypothesis tests

| id           | question                                                                                | test                                                         |   statistic |   df |   p_value |   effect_size | result            | interpretation                                                                                                                                            |
|:-------------|:----------------------------------------------------------------------------------------|:-------------------------------------------------------------|------------:|-----:|----------:|--------------:|:------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------|
| H1           | Festival holiday-days uniformly distributed across months?                              | Chi-square goodness-of-fit (12 months, weighted office-days) |    551.155  |   11 |   0       |      nan      | Reject H0         | Peak months: Mar, Oct, Apr                                                                                                                                |
| H2           | Is a festival's season independent of its tradition?                                    | Chi-square test of independence (+5,000-permutation p)       |      7.719  |    9 |   0.57788 |        0.1612 | Fail to reject H0 | Cramer's V = 0.16; asymptotic p = 0.563; 7 cells expected<5 -> permutation p reported                                                                     |
| H3-Hindu     | State holiday share for Hindu festivals correlates with Hindu population share?         | Spearman rank correlation (n=29 states/UTs)                  |      0.5752 |   27 |   0.0011  |        0.5752 | Reject H0         | slope 0.26 holiday-pp per population-pp                                                                                                                   |
| H3-Muslim    | State holiday share for Muslim festivals correlates with Muslim population share?       | Spearman rank correlation (n=29 states/UTs)                  |      0.4225 |   27 |   0.02243 |        0.4225 | Reject H0         | slope 0.27 holiday-pp per population-pp                                                                                                                   |
| H3-Christian | State holiday share for Christian festivals correlates with Christian population share? | Spearman rank correlation (n=29 states/UTs)                  |      0.5316 |   27 |   0.003   |        0.5316 | Reject H0         | slope 0.24 holiday-pp per population-pp                                                                                                                   |
| H3-Sikh      | State holiday share for Sikh festivals correlates with Sikh population share?           | Spearman rank correlation (n=29 states/UTs)                  |      0.5365 |   27 |   0.0027  |        0.5365 | Reject H0         | slope 0.28 holiday-pp per population-pp                                                                                                                   |
| H3-Buddhist  | State holiday share for Buddhist festivals correlates with Buddhist population share?   | Spearman rank correlation (n=29 states/UTs)                  |      0.7094 |   27 |   2e-05   |        0.7094 | Reject H0         | slope 0.66 holiday-pp per population-pp                                                                                                                   |
| H3-Jain      | State holiday share for Jain festivals correlates with Jain population share?           | Spearman rank correlation (n=29 states/UTs)                  |      0.6395 |   27 |   0.00019 |        0.6395 | Reject H0         | slope 4.66 holiday-pp per population-pp                                                                                                                   |
| H4           | Does festival geographic reach differ across tradition groups?                          | Kruskal-Wallis H (identifiable-reach festivals)              |      7.251  |    3 |   0.06431 |        0.0759 | Fail to reject H0 | epsilon^2 effect size; medians: Abrahamic (Muslim, Christian)=2.2; Hindu=1.8; Other (Sikh, Buddhist, Jain, Parsi, multi-faith)=1.6; Tribal/Indigenous=1.0 |
| H5           | Do lunar/moving-date festivals reach more states than fixed-date ones?                  | Mann-Whitney U                                               |    885.5    |  nan |   0.2703  |       -0.153  | Fail to reject H0 | median lunar 1.78 (n=64) vs fixed 1.37 (n=24); effect = rank-biserial                                                                                     |
| H6-hol_days  | Does festival holidays/yr differ across the 6 regions?                                  | Kruskal-Wallis H                                             |      3.788  |    5 |   0.58032 |       -0.0527 | Fail to reject H0 | Central=14.95; East=17.65; North=14.66; North-East=15.56; South=15.32; West=14.45                                                                         |
| H6-holiday_  | Does holiday diversity (Shannon) differ across the 6 regions?                           | Kruskal-Wallis H                                             |      4.5872 |    5 |   0.4683  |       -0.0179 | Fail to reject H0 | Central=1.69; East=1.50; North=1.47; North-East=1.53; South=1.51; West=1.52                                                                               |
| H7           | Are religiously more diverse states (Census) also more diverse in festival holidays?    | Spearman rank correlation                                    |      0.2483 |   27 |   0.19401 |        0.2483 | Fail to reject H0 |                                                                                                                                                           |
| H8           | Are post-monsoon (Oct-Dec) festivals associated with larger trade than other seasons?   | Mann-Whitney U on log trade (national CAIT-type estimates)   |     52      |  nan |   0.1088  |       -0.4857 | Fail to reject H0 | median post-monsoon INR 125,000 cr (n=7) vs other INR 27,386 cr (n=10)                                                                                    |
| H9           | Has reported festive trade grown significantly over time (2018-2026)?                   | OLS log(trade) ~ year + festival fixed effects               |     12.469  |   11 |   0       |        0.3399 | Reject H0         | implied growth 34.0%/yr (95% CI 27.2 to 41.1); R^2=0.990, n=17                                                                                            |


### Holiday share vs population share (per faith)

| faith     |   spearman_rho |   p_value |   pearson_r |   pearson_p |   ols_slope_holshare_per_popshare |   mean_pop_share_pct |   mean_holiday_share_pct |
|:----------|---------------:|----------:|------------:|------------:|----------------------------------:|---------------------:|-------------------------:|
| Hindu     |         0.5752 |    0.0011 |      0.7076 |      0      |                            0.2617 |              67.287  |                  46.5824 |
| Muslim    |         0.4225 |    0.0224 |      0.6299 |      0.0003 |                            0.2729 |              12.2827 |                  16.5322 |
| Christian |         0.5316 |    0.003  |      0.851  |      0      |                            0.2381 |              14.0612 |                  14.3563 |
| Sikh      |         0.5365 |    0.0027 |      0.6757 |      0.0001 |                            0.278  |               1.5453 |                   2.7139 |
| Buddhist  |         0.7094 |    0      |      0.8775 |      0      |                            0.6553 |               2.133  |                   3.7439 |
| Jain      |         0.6395 |    0.0002 |      0.7445 |      0      |                            4.6642 |               0.2492 |                   2.2603 |


### Tradition x season contingency (festival counts)

| t4                                               |   Monsoon |   Post-monsoon |   Pre-monsoon |   Winter |
|:-------------------------------------------------|----------:|---------------:|--------------:|---------:|
| Abrahamic (Muslim, Christian)                    |         4 |              3 |             5 |        2 |
| Hindu                                            |        12 |             16 |            11 |        6 |
| Other (Sikh, Buddhist, Jain, Parsi, multi-faith) |         8 |              1 |             5 |        4 |
| Tribal/Indigenous                                |         5 |              6 |             7 |        4 |


## 3. Comparative analysis

### Global spending analogues (USD bn, publishers' conversions)

| event                                     |   usd_bn | source                             |
|:------------------------------------------|---------:|:-----------------------------------|
| Diwali 2025 (India)                       |    68.77 | IBEF / CAIT                        |
| US holiday season 2024                    |   994.1  | NRF                                |
| China Spring Festival 2025 (tourism only) |    94.43 | Ministry of Culture & Tourism, PRC |


### Footfall density

| event                               |   footfall |   days | source                                |          per_day |
|:------------------------------------|-----------:|-------:|:--------------------------------------|-----------------:|
| Maha Kumbh 2025 (Prayagraj)         |  662100000 |     45 | AIR / Govt. of UP                     |      1.47133e+07 |
| Medaram Jatara 2020 (Telangana)     |   15000000 |      4 | The News Minute                       |      3.75e+06    |
| Hornbill Festival 2024 (Nagaland)   |     204986 |     10 | Nagaland Tourism via Nagaland Tribune |  20498.6         |
| Oktoberfest 2025 (Munich)           |    6500000 |     16 | City of Munich / oktoberfest.de       | 406250           |
| Hajj 2025 (Makkah)                  |    1673230 |      6 | GASTAT                                | 278872           |
| Spring Festival 2025 (China, trips) |  501000000 |      8 | gov.cn                                |      6.2625e+07  |


### States ranked by festival holidays per year

| state                     | region     |   hol_days_total_festival |   n_distinct_festivals |   holiday_diversity_shannon |   population_diversity_shannon |
|:--------------------------|:-----------|--------------------------:|-----------------------:|----------------------------:|-------------------------------:|
| Sikkim                    | North-East |                     21.23 |                     42 |                        1.43 |                           1.09 |
| Uttar Pradesh             | North      |                     19.81 |                     45 |                        1.56 |                           0.54 |
| Jharkhand                 | East       |                     19.1  |                     33 |                        1.65 |                           0.96 |
| West Bengal               | East       |                     18.02 |                     34 |                        1.56 |                           0.71 |
| Uttarakhand               | North      |                     17.59 |                     37 |                        1.42 |                           0.56 |
| Karnataka                 | South      |                     17.38 |                     43 |                        1.44 |                           0.54 |
| Odisha                    | East       |                     17.29 |                     40 |                        1.28 |                           0.3  |
| Tripura                   | North-East |                     16.63 |                     32 |                        1.54 |                           0.62 |
| Meghalaya                 | North-East |                     16.56 |                     29 |                        1.52 |                           0.85 |
| Mizoram                   | North-East |                     16.43 |                     39 |                        1.8  |                           0.5  |
| Tamil Nadu                | South      |                     16.32 |                     38 |                        1.56 |                           0.47 |
| Jammu & Kashmir           | North      |                     16.31 |                     38 |                        1.65 |                           0.75 |
| Maharashtra               | West       |                     15.88 |                     41 |                        1.69 |                           0.72 |
| Madhya Pradesh            | Central    |                     15.59 |                     35 |                        1.66 |                           0.39 |
| Telangana                 | South      |                     15.32 |                     39 |                        1.51 |                           0.4  |
| Assam                     | North-East |                     14.68 |                     31 |                        1.37 |                           0.82 |
| Himachal Pradesh          | North      |                     14.66 |                     42 |                        1.42 |                           0.25 |
| Andhra Pradesh            | South      |                     14.49 |                     36 |                        1.43 |                           0.4  |
| Gujarat                   | West       |                     14.45 |                     39 |                        1.49 |                           0.42 |
| Bihar                     | East       |                     14.43 |                     30 |                        1.44 |                           0.47 |
| Chhattisgarh              | Central    |                     14.3  |                     33 |                        1.72 |                           0.34 |
| Manipur                   | North-East |                     14.15 |                     37 |                        1.64 |                           1.17 |
| Kerala                    | South      |                     13.45 |                     29 |                        1.51 |                           1    |
| Rajasthan                 | North      |                     13.28 |                     32 |                        1.34 |                           0.44 |
| Punjab-Haryana-Chandigarh | North      |                     12.99 |                     33 |                        1.47 |                           0.85 |
| Nagaland                  | North-East |                     11.61 |                     19 |                        1.53 |                           0.46 |
| Delhi                     | North      |                     11.6  |                     27 |                        1.88 |                           0.64 |
| Arunachal Pradesh         | North-East |                     11.57 |                     31 |                        1.77 |                           1.42 |
| Goa                       | West       |                     11.27 |                     30 |                        1.52 |                           0.85 |


### Season (IMD) comparison

| season_imd   |   holiday_days_per_office_per_year |
|:-------------|-----------------------------------:|
| Monsoon      |                               4.01 |
| Post-monsoon |                               5.05 |
| Pre-monsoon  |                               5.54 |
| Winter       |                               0.93 |


### Distinct festivals observed per month

| month   |   festival |
|:--------|-----------:|
| Jan     |         11 |
| Feb     |          7 |
| Mar     |         15 |
| Apr     |         22 |
| May     |          4 |
| Jun     |          8 |
| Jul     |          8 |
| Aug     |         14 |
| Sep     |         15 |
| Oct     |         14 |
| Nov     |         14 |
| Dec     |          6 |

