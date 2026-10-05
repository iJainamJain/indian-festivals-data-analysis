# Statistical Valuation & EDA Report

All tests two-sided, alpha = 0.05. Data: RBI holiday matrix 2022-26 (34 offices, 29 states/UTs), Sunday-corrected, Census 2011 C-01, and 78 verified economic/footfall records.

## 1. Descriptive statistics

|                                              |   n |      mean |   median |       std |     min |       q1 |        q3 |       max |      iqr |   cv_pct |   skewness |   kurtosis |
|:---------------------------------------------|----:|----------:|---------:|----------:|--------:|---------:|----------:|----------:|---------:|---------:|-----------:|-----------:|
| festival_expected_states_per_year            | 101 |      4.29 |     1.03 |      7    |    0.2  |     1    |      2.57 |     29    |     1.57 |   163.11 |       2.22 |       3.76 |
| festival_mean_holiday_days (duration)        | 101 |      1.05 |     1    |      0.18 |    1    |     1    |      1    |      2.12 |     0    |    16.88 |       4.11 |      17.4  |
| festival_date_drift_days (moving festivals)  |  69 |     31.65 |    22    |     58.01 |    2    |    20    |     24    |    364    |     4    |   183.28 |       5.38 |      27.84 |
| state_festival_holidays_per_year (frequency) |  29 |     17.01 |    17.23 |      3.44 |    9.35 |    15.77 |     19.34 |     22.87 |     3.56 |    20.26 |      -0.5  |      -0.08 |
| state_holiday_diversity_shannon              |  29 |      1.33 |     1.3  |      0.18 |    1.04 |     1.17 |      1.46 |      1.71 |     0.29 |    13.8  |       0.46 |      -1    |
| state_distinct_festivals_2024_26             |  29 |     14.59 |    15    |      2.99 |    8    |    13    |     16    |     19    |     3    |    20.53 |      -0.78 |      -0.04 |
| festive_trade_INR_crore (spending)           |  18 | 118167    | 37500    | 173145    | 3000    | 18250    | 113750    | 605000    | 95500    |   146.53 |       1.77 |       1.88 |


### By tradition

| tradition              |   festivals |   mean_expected_states |   median_expected_states |   mean_duration_days |   pct_lunar |   holiday_days_per_office_per_year |   share_of_all_festival_holidays_pct |
|:-----------------------|------------:|-----------------------:|-------------------------:|---------------------:|------------:|-----------------------------------:|-------------------------------------:|
| Hindu                  |          45 |                   4.48 |                     1.51 |                 1.06 |       77.78 |                               8.58 |                                 49.4 |
| Tribal/Indigenous      |          23 |                   1.19 |                     1    |                 1    |       60.87 |                               0.91 |                                  5.2 |
| Buddhist               |           7 |                   2.54 |                     1    |                 1.09 |       71.43 |                               0.69 |                                  4   |
| Muslim                 |           7 |                  12.34 |                    15.09 |                 1.02 |      100    |                               3.41 |                                 19.6 |
| Christian              |           7 |                   8.21 |                     1    |                 1.01 |       14.29 |                               2.07 |                                 11.9 |
| Sikh                   |           5 |                   3.93 |                     1    |                 1    |       80    |                               0.73 |                                  4.2 |
| Cultural (multi-faith) |           4 |                   1.9  |                     1.96 |                 1.38 |       25    |                               0.36 |                                  2.1 |
| Jain                   |           2 |                   7.35 |                     7.35 |                 1    |      100    |                               0.53 |                                  3.1 |
| Parsi                  |           1 |                   1    |                     1    |                 1    |        0    |                               0.09 |                                  0.5 |


## 2. Hypothesis tests

| id           | question                                                                                | test                                                         |   statistic |   df |   p_value |   effect_size | result            | interpretation                                                                                                                                            |
|:-------------|:----------------------------------------------------------------------------------------|:-------------------------------------------------------------|------------:|-----:|----------:|--------------:|:------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------|
| H1           | Festival holiday-days uniformly distributed across months?                              | Chi-square goodness-of-fit (12 months, weighted office-days) |    825.499  |   11 |   0       |      nan      | Reject H0         | Peak months: Oct, Mar, Apr                                                                                                                                |
| H2           | Is a festival's season independent of its tradition?                                    | Chi-square test of independence (+5,000-permutation p)       |      5.6911 |    9 |   0.78464 |        0.137  | Fail to reject H0 | Cramer's V = 0.14; asymptotic p = 0.770; 6 cells expected<5 -> permutation p reported                                                                     |
| H3-Hindu     | State holiday share for Hindu festivals correlates with Hindu population share?         | Spearman rank correlation (n=29 states/UTs)                  |      0.6143 |   27 |   0.00039 |        0.6143 | Reject H0         | slope 0.32 holiday-pp per population-pp                                                                                                                   |
| H3-Muslim    | State holiday share for Muslim festivals correlates with Muslim population share?       | Spearman rank correlation (n=29 states/UTs)                  |      0.3837 |   27 |   0.03987 |        0.3837 | Reject H0         | slope 0.33 holiday-pp per population-pp                                                                                                                   |
| H3-Christian | State holiday share for Christian festivals correlates with Christian population share? | Spearman rank correlation (n=29 states/UTs)                  |      0.4946 |   27 |   0.00638 |        0.4946 | Reject H0         | slope 0.26 holiday-pp per population-pp                                                                                                                   |
| H3-Sikh      | State holiday share for Sikh festivals correlates with Sikh population share?           | Spearman rank correlation (n=29 states/UTs)                  |      0.6421 |   27 |   0.00017 |        0.6421 | Reject H0         | slope 0.53 holiday-pp per population-pp                                                                                                                   |
| H3-Buddhist  | State holiday share for Buddhist festivals correlates with Buddhist population share?   | Spearman rank correlation (n=29 states/UTs)                  |      0.6454 |   27 |   0.00016 |        0.6454 | Reject H0         | slope 0.78 holiday-pp per population-pp                                                                                                                   |
| H3-Jain      | State holiday share for Jain festivals correlates with Jain population share?           | Spearman rank correlation (n=29 states/UTs)                  |      0.6624 |   27 |   9e-05   |        0.6624 | Reject H0         | slope 5.85 holiday-pp per population-pp                                                                                                                   |
| H4           | Does festival geographic reach differ across tradition groups?                          | Kruskal-Wallis H (identifiable-reach festivals)              |     10.283  |    3 |   0.01631 |        0.0934 | Reject H0         | epsilon^2 effect size; medians: Abrahamic (Muslim, Christian)=1.6; Hindu=1.5; Other (Sikh, Buddhist, Jain, Parsi, multi-faith)=1.0; Tribal/Indigenous=1.0 |
| H5           | Do lunar/moving-date festivals reach more states than fixed-date ones?                  | Mann-Whitney U                                               |    870.5    |  nan |   0.70758 |       -0.0513 | Fail to reject H0 | median lunar 1.13 (n=69) vs fixed 1.23 (n=24); effect = rank-biserial                                                                                     |
| H6-hol_days  | Does festival holidays/yr differ across the 6 regions?                                  | Kruskal-Wallis H                                             |      2.3625 |    5 |   0.79704 |       -0.1147 | Fail to reject H0 | Central=16.50; East=19.65; North=17.44; North-East=16.91; South=17.18; West=16.73                                                                         |
| H6-holiday_  | Does holiday diversity (Shannon) differ across the 6 regions?                           | Kruskal-Wallis H                                             |      6.2251 |    5 |   0.28493 |        0.0533 | Fail to reject H0 | Central=1.48; East=1.32; North=1.35; North-East=1.35; South=1.18; West=1.24                                                                               |
| H7           | Are religiously more diverse states (Census) also more diverse in festival holidays?    | Spearman rank correlation                                    |      0.3138 |   27 |   0.09734 |        0.3138 | Fail to reject H0 |                                                                                                                                                           |
| H8           | Are post-monsoon (Oct-Dec) festivals associated with larger trade than other seasons?   | Mann-Whitney U on log trade (national CAIT-type estimates)   |     52      |  nan |   0.1088  |       -0.4857 | Fail to reject H0 | median post-monsoon INR 125,000 cr (n=7) vs other INR 27,386 cr (n=10)                                                                                    |
| H9           | Has reported festive trade grown significantly over time (2018-2026)?                   | OLS log(trade) ~ year + festival fixed effects               |     12.469  |   11 |   0       |        0.3399 | Reject H0         | implied growth 34.0%/yr (95% CI 27.2 to 41.1); R^2=0.990, n=17                                                                                            |


### Holiday share vs population share (per faith)

| faith     |   spearman_rho |   p_value |   pearson_r |   pearson_p |   ols_slope_holshare_per_popshare |   mean_pop_share_pct |   mean_holiday_share_pct |   rho_ci95_low |   rho_ci95_high |   p_holm |
|:----------|---------------:|----------:|------------:|------------:|----------------------------------:|---------------------:|-------------------------:|---------------:|----------------:|---------:|
| Hindu     |         0.6143 |    0.0004 |      0.7146 |      0      |                            0.3217 |              67.2536 |                  49.3668 |         0.2613 |          0.8465 |   0.0012 |
| Muslim    |         0.3837 |    0.0399 |      0.572  |      0.0012 |                            0.3288 |              12.3138 |                  18.5599 |        -0.0485 |          0.7273 |   0.0399 |
| Christian |         0.4946 |    0.0064 |      0.8414 |      0      |                            0.2645 |              14.0606 |                  13.3798 |         0.0819 |          0.7742 |   0.0128 |
| Sikh      |         0.6421 |    0.0002 |      0.7385 |      0      |                            0.525  |               1.5457 |                   3.9641 |         0.3095 |          0.8528 |   0.0008 |
| Buddhist  |         0.6454 |    0.0002 |      0.8475 |      0      |                            0.7819 |               2.1335 |                   3.6203 |         0.3667 |          0.8158 |   0.0008 |
| Jain      |         0.6624 |    0.0001 |      0.7274 |      0      |                            5.8512 |               0.2493 |                   2.9431 |         0.3409 |          0.8442 |   0.0005 |


### Tradition x season contingency (festival counts)

| t4                                               |   Monsoon |   Post-monsoon |   Pre-monsoon |   Winter |
|:-------------------------------------------------|----------:|---------------:|--------------:|---------:|
| Abrahamic (Muslim, Christian)                    |         4 |              3 |             5 |        2 |
| Hindu                                            |        12 |             16 |            11 |        6 |
| Other (Sikh, Buddhist, Jain, Parsi, multi-faith) |         8 |              2 |             5 |        4 |
| Tribal/Indigenous                                |         6 |              6 |             7 |        4 |


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
| Uttar Pradesh             | North      |                     22.87 |                     17 |                        1.35 |                           0.54 |
| Sikkim                    | North-East |                     22.77 |                     14 |                        1.17 |                           1.09 |
| Jharkhand                 | East       |                     21.97 |                     18 |                        1.53 |                           0.96 |
| Karnataka                 | South      |                     20.08 |                     16 |                        1.18 |                           0.54 |
| West Bengal               | East       |                     19.95 |                     17 |                        1.46 |                           0.71 |
| Maharashtra               | West       |                     19.69 |                     18 |                        1.63 |                           0.72 |
| Uttarakhand               | North      |                     19.47 |                     16 |                        1.13 |                           0.56 |
| Odisha                    | East       |                     19.34 |                     19 |                        1.14 |                           0.3  |
| Jammu & Kashmir           | North      |                     19.1  |                     15 |                        1.4  |                           0.75 |
| Manipur                   | North-East |                     18.88 |                     15 |                        1.3  |                           1.17 |
| Tripura                   | North-East |                     18.2  |                     15 |                        1.55 |                           0.62 |
| Tamil Nadu                | South      |                     17.94 |                     14 |                        1.14 |                           0.47 |
| Mizoram                   | North-East |                     17.52 |                     17 |                        1.71 |                           0.5  |
| Himachal Pradesh          | North      |                     17.44 |                     19 |                        1.19 |                           0.25 |
| Madhya Pradesh            | Central    |                     17.23 |                     16 |                        1.43 |                           0.39 |
| Telangana                 | South      |                     17.18 |                     15 |                        1.22 |                           0.47 |
| Gujarat                   | West       |                     16.73 |                     16 |                        1.15 |                           0.42 |
| Punjab-Haryana-Chandigarh | North      |                     16.57 |                     16 |                        1.4  |                           0.85 |
| Meghalaya                 | North-East |                     16.3  |                     15 |                        1.34 |                           0.85 |
| Assam                     | North-East |                     16.1  |                     10 |                        1.18 |                           0.82 |
| Kerala                    | South      |                     16.06 |                     13 |                        1.21 |                           1    |
| Chhattisgarh              | Central    |                     15.77 |                     14 |                        1.54 |                           0.34 |
| Bihar                     | East       |                     15.27 |                     12 |                        1.17 |                           0.47 |
| Rajasthan                 | North      |                     15.26 |                     13 |                        1.17 |                           0.44 |
| Delhi                     | North      |                     12.56 |                     12 |                        1.62 |                           0.64 |
| Andhra Pradesh            | South      |                     12.21 |                     16 |                        1.04 |                           0.35 |
| Goa                       | West       |                     11.54 |                      9 |                        1.24 |                           0.85 |
| Nagaland                  | North-East |                      9.85 |                      8 |                        1.37 |                           0.46 |
| Arunachal Pradesh         | North-East |                      9.35 |                      8 |                        1.57 |                           1.42 |


### Season (IMD) comparison

| season_imd   |   holiday_days_per_office_per_year |
|:-------------|-----------------------------------:|
| Monsoon      |                               4.3  |
| Post-monsoon |                               5.64 |
| Pre-monsoon  |                               6.47 |
| Winter       |                               0.96 |


### Distinct festivals observed per month

| month   |   festival |
|:--------|-----------:|
| Jan     |         11 |
| Feb     |         10 |
| Mar     |         16 |
| Apr     |         23 |
| May     |          6 |
| Jun     |          9 |
| Jul     |          9 |
| Aug     |         15 |
| Sep     |         16 |
| Oct     |         15 |
| Nov     |         15 |
| Dec     |          7 |

