"""Task 3 - Statistical valuation & exploratory data analysis (independent of the ML models).

Produces: outputs/stats/*.csv (validation tables), outputs/figures/*.png (distribution plots, heatmaps,
correlation matrix, timelines, choropleth, economic charts) and outputs/stats/statistical_summary.md
"""
import os, json, warnings
import numpy as np, pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import viz_style as vs
from project_config import PERIOD, N_YEARS

warnings.filterwarnings("ignore")
vs.apply()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
FIG, ST = os.path.join(ROOT, "outputs", "figures"), os.path.join(ROOT, "outputs", "stats")
os.makedirs(FIG, exist_ok=True); os.makedirs(ST, exist_ok=True)
SRC_RBI = f"Reserve Bank of India holiday matrix {PERIOD} (rbi.org.in)"
SRC_CEN = "Census of India 2011, Table C-01 (censusindia.gov.in)"

obs = pd.read_csv(os.path.join(P, "festival_observations.csv"))
fm = pd.read_csv(os.path.join(P, "festival_master.csv"))
sp = pd.read_csv(os.path.join(P, "state_profile.csv")).set_index("state")
eco = pd.read_csv(os.path.join(P, "economic_footfall_clean.csv"))
obs["tgroup"] = obs["tradition"].map(vs.trad_group); fm["tgroup"] = fm["tradition"].map(vs.trad_group)
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
report = ["# Statistical Valuation & EDA Report\n",
          f"All tests two-sided, alpha = 0.05. Data: RBI holiday matrix {PERIOD} (34 offices, 29 states/UTs), Sunday-corrected, "
          "Census 2011 C-01, and 78 verified economic/footfall records.\n"]
def save(fig, name, src):
    vs.source_note(fig, src); fig.savefig(os.path.join(FIG, name)); plt.close(fig)

# ============ 1. DESCRIPTIVE STATISTICS ============================================================
def describe(s):
    s = pd.Series(s).dropna()
    return pd.Series({"n": len(s), "mean": s.mean(), "median": s.median(), "std": s.std(), "min": s.min(),
                      "q1": s.quantile(.25), "q3": s.quantile(.75), "max": s.max(), "iqr": s.quantile(.75) - s.quantile(.25),
                      "cv_pct": 100 * s.std() / s.mean() if s.mean() else np.nan, "skewness": stats.skew(s), "kurtosis": stats.kurtosis(s)})
desc = pd.DataFrame({
    "festival_expected_states_per_year": describe(fm.expected_states_per_year),
    "festival_mean_holiday_days (duration)": describe(fm.mean_holiday_days),
    "festival_date_drift_days (moving festivals)": describe(fm.loc[fm.calendar_basis.str.startswith("Lunar"), "date_drift_days"]),
    "state_festival_holidays_per_year (frequency)": describe(sp.hol_days_total_festival),
    "state_holiday_diversity_shannon": describe(sp.holiday_diversity_shannon),
    "state_distinct_festivals_2024_26": describe(sp.n_distinct_festivals),
    "festive_trade_INR_crore (spending)": describe(eco.loc[eco.metric == "festive_trade", "value"]),
}).T.round(2)
desc.to_csv(os.path.join(ST, "T1_descriptive_statistics.csv"))
report += ["## 1. Descriptive statistics\n", desc.to_markdown(), "\n"]

by_trad = fm.groupby("tradition").agg(festivals=("festival", "size"),
                                      mean_expected_states=("expected_states_per_year", "mean"),
                                      median_expected_states=("expected_states_per_year", "median"),
                                      mean_duration_days=("mean_holiday_days", "mean"),
                                      pct_lunar=("calendar_basis", lambda x: 100 * x.str.startswith("Lunar").mean())).round(2)
w = obs.groupby("tradition")["annual_weight"].sum() / 34
by_trad["holiday_days_per_office_per_year"] = w.round(2)
by_trad["share_of_all_festival_holidays_pct"] = (100 * w / w.sum()).round(1)
by_trad.sort_values("festivals", ascending=False).to_csv(os.path.join(ST, "T2_by_tradition.csv"))
report += ["### By tradition\n", by_trad.sort_values("festivals", ascending=False).to_markdown(), "\n"]

# distribution plots
fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
ax[0].hist(fm.expected_states_per_year, bins=15, color=vs.SLOTS[0], edgecolor=vs.SURFACE, linewidth=2)
ax[0].set(title="Festival reach", xlabel="Expected states observing per year", ylabel="Festivals")
ax[1].hist(sp.hol_days_total_festival, bins=10, color=vs.SLOTS[0], edgecolor=vs.SURFACE, linewidth=2)
ax[1].set(title="Festival bank holidays per state", xlabel="Days per year (office average)", ylabel="States/UTs")
tv = eco.loc[eco.metric == "festive_trade", "value"]
ax[2].hist(np.log10(tv), bins=8, color=vs.SLOTS[1], edgecolor=vs.SURFACE, linewidth=2)
ax[2].set(title="Festive trade estimates", xlabel="log10(INR crore)", ylabel="Records")
fig.tight_layout(); save(fig, "F01_distributions.png", f"{SRC_RBI}; CAIT & other cited trade estimates (economic_footfall_clean.csv)")

# ============ 2. TEMPORAL: month-wise density timeline ============================================
mt = obs.groupby(["month", "tgroup"])["annual_weight"].sum().unstack(fill_value=0) / 34
mt = mt.reindex(index=range(1, 13), columns=vs.TRAD_ORDER, fill_value=0)
mt.round(3).to_csv(os.path.join(ST, "T3_month_by_tradition_holiday_days.csv"))
fig, ax = plt.subplots(figsize=(11, 4.4))
bottom = np.zeros(12)
for t in vs.TRAD_ORDER:
    ax.bar(range(12), mt[t].values, bottom=bottom, color=vs.TRAD_COLOR[t], label=t, width=0.72, edgecolor=vs.SURFACE, linewidth=1.5)
    bottom += mt[t].values
for i, v in enumerate(bottom): ax.text(i, v + 0.03, f"{v:.1f}", ha="center", fontsize=8, color=vs.INK2)
ax.set_xticks(range(12), MONTHS); ax.set_ylabel("Festival bank-holiday days per office")
ax.set_title(f"When India celebrates: festival holidays by month and tradition ({PERIOD} average)")
ax.set_ylim(0, bottom.max() * 1.12)
ax.legend(fontsize=9, loc="upper left", bbox_to_anchor=(1.01, 1.0), title="Tradition", title_fontsize=9, alignment="left"); ax.grid(axis="x", visible=False)
save(fig, "F02_month_timeline_by_tradition.png", SRC_RBI + ". Sunday-corrected; shared dates credited by evidence score.")

# distinct festivals per month (festival "density")
dens = obs.groupby("month")["festival"].nunique().reindex(range(1, 13), fill_value=0)
# H1: are festival-holiday days uniformly spread over months?  (chi-square goodness of fit on office-days)
od = obs.groupby("month")["attribution_weight"].sum().reindex(range(1, 13)).values
chi_u = stats.chisquare(od)
# ============ 3. HYPOTHESIS TESTS =================================================================
tests = []
tests.append({"id": "H1", "question": "Festival holiday-days uniformly distributed across months?",
              "test": "Chi-square goodness-of-fit (12 months, weighted office-days)", "statistic": chi_u.statistic,
              "df": 11, "p_value": chi_u.pvalue, "effect_size": np.nan,
              "result": "Reject H0" if chi_u.pvalue < .05 else "Fail to reject H0",
              "interpretation": f"Peak months: {', '.join(MONTHS[i] for i in np.argsort(od)[::-1][:3])}"})

# H2: tradition x IMD season (festival-level contingency, grouped to keep expected counts reasonable)
fm["season"] = fm["modal_season_imd"]
fm["t4"] = fm["tradition"].map(lambda t: t if t in ("Hindu", "Tribal/Indigenous") else ("Abrahamic (Muslim, Christian)" if t in ("Muslim", "Christian") else "Other (Sikh, Buddhist, Jain, Parsi, multi-faith)"))
ct = pd.crosstab(fm.t4, fm.season)
chi2, p2, dof2, exp2 = stats.chi2_contingency(ct)
cv = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
# Monte-Carlo permutation p-value (robust to small expected counts)
rng = np.random.default_rng(42); perm = []
for _ in range(5000):
    perm.append(stats.chi2_contingency(pd.crosstab(fm.t4.values, rng.permutation(fm.season.values)))[0])
p2_mc = (np.sum(np.array(perm) >= chi2) + 1) / 5001
ct.to_csv(os.path.join(ST, "T4_tradition_by_season_contingency.csv"))
tests.append({"id": "H2", "question": "Is a festival's season independent of its tradition?",
              "test": "Chi-square test of independence (+5,000-permutation p)", "statistic": chi2, "df": dof2,
              "p_value": p2_mc, "effect_size": cv, "result": "Reject H0" if p2_mc < .05 else "Fail to reject H0",
              "interpretation": f"Cramer's V = {cv:.2f}; asymptotic p = {p2:.3f}; {int((exp2 < 5).sum())} cells expected<5 -> permutation p reported"})

# H3: does holiday share track population share?  Spearman across states, per faith
corr_rows = []
for faith, hcol, ccol in [("Hindu", "hol_share_hindu", "census_pct_hindu"), ("Muslim", "hol_share_muslim", "census_pct_muslim"),
                          ("Christian", "hol_share_christian", "census_pct_christian"), ("Sikh", "hol_share_sikh", "census_pct_sikh"),
                          ("Buddhist", "hol_share_buddhist", "census_pct_buddhist"), ("Jain", "hol_share_jain", "census_pct_jain")]:
    r, p = stats.spearmanr(sp[ccol], sp[hcol]); pr, pp = stats.pearsonr(sp[ccol], sp[hcol])
    slope = np.polyfit(sp[ccol], sp[hcol], 1)[0]
    corr_rows.append({"faith": faith, "spearman_rho": r, "p_value": p, "pearson_r": pr, "pearson_p": pp,
                      "ols_slope_holshare_per_popshare": slope, "mean_pop_share_pct": sp[ccol].mean(),
                      "mean_holiday_share_pct": sp[hcol].mean()})
    tests.append({"id": f"H3-{faith}", "question": f"State holiday share for {faith} festivals correlates with {faith} population share?",
                  "test": "Spearman rank correlation (n=29 states/UTs)", "statistic": r, "df": 27, "p_value": p,
                  "effect_size": r, "result": "Reject H0" if p < .05 else "Fail to reject H0",
                  "interpretation": f"slope {slope:.2f} holiday-pp per population-pp"})
cr = pd.DataFrame(corr_rows)
# robustness: 95% bootstrap CI (5,000 resamples of states) and Holm correction across the six faith tests
_rng = np.random.default_rng(42); lo, hi = [], []
for faith, hcol, ccol in [("Hindu", "hol_share_hindu", "census_pct_hindu"), ("Muslim", "hol_share_muslim", "census_pct_muslim"),
                          ("Christian", "hol_share_christian", "census_pct_christian"), ("Sikh", "hol_share_sikh", "census_pct_sikh"),
                          ("Buddhist", "hol_share_buddhist", "census_pct_buddhist"), ("Jain", "hol_share_jain", "census_pct_jain")]:
    bs = []
    for _ in range(5000):
        ix = _rng.integers(0, len(sp), len(sp)); r_ = stats.spearmanr(sp[ccol].values[ix], sp[hcol].values[ix])[0]
        if not np.isnan(r_): bs.append(r_)
    lo.append(np.percentile(bs, 2.5)); hi.append(np.percentile(bs, 97.5))
cr["rho_ci95_low"], cr["rho_ci95_high"] = lo, hi
_order = np.argsort(cr.p_value.values); _adj = np.empty(len(cr)); _run = 0
for rank, i in enumerate(_order):
    _run = max(_run, min(1, cr.p_value.values[i] * (len(cr) - rank))); _adj[i] = _run
cr["p_holm"] = _adj
cr = cr.round(4); cr.to_csv(os.path.join(ST, "T5_holiday_vs_population_share.csv"), index=False)

# H4: reach differs by tradition? (Kruskal-Wallis, identifiable festivals only)
idf = fm[fm.reach_identifiable]
groups = [g.expected_states_per_year.values for _, g in idf.groupby("t4")]
kw = stats.kruskal(*groups)
eps2 = (kw.statistic - len(groups) + 1) / (len(idf) - len(groups))
tests.append({"id": "H4", "question": "Does festival geographic reach differ across tradition groups?",
              "test": "Kruskal-Wallis H (identifiable-reach festivals)", "statistic": kw.statistic, "df": len(groups) - 1,
              "p_value": kw.pvalue, "effect_size": eps2, "result": "Reject H0" if kw.pvalue < .05 else "Fail to reject H0",
              "interpretation": "epsilon^2 effect size; medians: " + "; ".join(f"{k}={v:.1f}" for k, v in idf.groupby('t4').expected_states_per_year.median().items())})

# H5: moving (lunar) vs fixed (Gregorian) festivals - reach
lun = fm[fm.calendar_basis.str.startswith("Lunar")].expected_states_per_year
fix = fm[fm.calendar_basis.str.startswith("Gregorian")].expected_states_per_year
mw = stats.mannwhitneyu(lun, fix)
tests.append({"id": "H5", "question": "Do lunar/moving-date festivals reach more states than fixed-date ones?",
              "test": "Mann-Whitney U", "statistic": mw.statistic, "df": np.nan, "p_value": mw.pvalue,
              "effect_size": 1 - 2 * mw.statistic / (len(lun) * len(fix)),
              "result": "Reject H0" if mw.pvalue < .05 else "Fail to reject H0",
              "interpretation": f"median lunar {lun.median():.2f} (n={len(lun)}) vs fixed {fix.median():.2f} (n={len(fix)}); effect = rank-biserial"})

# H6: regional differences in festival-holiday frequency and diversity
for var, lab in [("hol_days_total_festival", "festival holidays/yr"), ("holiday_diversity_shannon", "holiday diversity (Shannon)")]:
    g = [x[var].values for _, x in sp.groupby("region")]
    k = stats.kruskal(*g)
    tests.append({"id": f"H6-{var[:8]}", "question": f"Does {lab} differ across the 6 regions?", "test": "Kruskal-Wallis H",
                  "statistic": k.statistic, "df": len(g) - 1, "p_value": k.pvalue,
                  "effect_size": (k.statistic - len(g) + 1) / (len(sp) - len(g)),
                  "result": "Reject H0" if k.pvalue < .05 else "Fail to reject H0",
                  "interpretation": "; ".join(f"{r}={v:.2f}" for r, v in sp.groupby('region')[var].median().items())})

# H7: population diversity vs holiday diversity (do more religiously diverse states host a more diverse holiday calendar?)
r7, p7 = stats.spearmanr(sp.population_diversity_shannon, sp.holiday_diversity_shannon)
tests.append({"id": "H7", "question": "Are religiously more diverse states (Census) also more diverse in festival holidays?",
              "test": "Spearman rank correlation", "statistic": r7, "df": 27, "p_value": p7, "effect_size": r7,
              "result": "Reject H0" if p7 < .05 else "Fail to reject H0", "interpretation": ""})

# H8: timing vs economic spikes - festive trade by month-of-festival (post-monsoon vs rest), log values
trade = eco[(eco.metric == "festive_trade") & (eco.unit == "INR crore") & (eco.geography == "India")].copy()
tm = fm.set_index("festival")["modal_season_imd"]
trade["season"] = trade.festival.map(tm)
a = np.log(trade.loc[trade.season == "Post-monsoon", "value"]); b = np.log(trade.loc[trade.season != "Post-monsoon", "value"])
t8 = stats.mannwhitneyu(a, b)
tests.append({"id": "H8", "question": "Are post-monsoon (Oct-Dec) festivals associated with larger trade than other seasons?",
              "test": "Mann-Whitney U on log trade (national CAIT-type estimates)", "statistic": t8.statistic, "df": np.nan,
              "p_value": t8.pvalue, "effect_size": 1 - 2 * t8.statistic / (len(a) * len(b)),
              "result": "Reject H0" if t8.pvalue < .05 else "Fail to reject H0",
              "interpretation": f"median post-monsoon INR {np.exp(a.median()):,.0f} cr (n={len(a)}) vs other INR {np.exp(b.median()):,.0f} cr (n={len(b)})"})

# H9: growth - is the trend in festive trade significant? log-linear OLS pooled over festivals with festival fixed effects
import statsmodels.formula.api as smf
tr = trade.copy(); tr["log_value"] = np.log(tr.value)
ols = smf.ols("log_value ~ year + C(festival)", data=tr).fit()
g_rate = np.exp(ols.params["year"]) - 1
tests.append({"id": "H9", "question": "Has reported festive trade grown significantly over time (2018-2026)?",
              "test": "OLS log(trade) ~ year + festival fixed effects", "statistic": ols.tvalues["year"], "df": ols.df_resid,
              "p_value": ols.pvalues["year"], "effect_size": g_rate,
              "result": "Reject H0" if ols.pvalues["year"] < .05 else "Fail to reject H0",
              "interpretation": f"implied growth {100 * g_rate:.1f}%/yr (95% CI {100 * (np.exp(ols.conf_int().loc['year', 0]) - 1):.1f} to "
                                f"{100 * (np.exp(ols.conf_int().loc['year', 1]) - 1):.1f}); R^2={ols.rsquared:.3f}, n={int(ols.nobs)}"})

T = pd.DataFrame(tests)
T["statistic"] = T["statistic"].astype(float).round(4); T["p_value"] = T["p_value"].astype(float).round(5)
T["effect_size"] = T["effect_size"].astype(float).round(4)
T.to_csv(os.path.join(ST, "T6_hypothesis_tests.csv"), index=False)
report += ["## 2. Hypothesis tests\n", T.to_markdown(index=False), "\n",
           "### Holiday share vs population share (per faith)\n", cr.to_markdown(index=False), "\n",
           "### Tradition x season contingency (festival counts)\n", ct.to_markdown(), "\n"]

# ============ 4. CORRELATION MATRIX (state level) ================================================
cm_cols = {"hol_days_total_festival": "Festival holidays/yr", "holiday_diversity_shannon": "Holiday diversity",
           "n_distinct_festivals": "Distinct festivals", "hol_share_hindu": "Hindu hol. %", "hol_share_muslim": "Muslim hol. %",
           "hol_share_christian": "Christian hol. %", "hol_share_tribal_indigenous": "Tribal hol. %",
           "census_pct_hindu": "Hindu pop. %", "census_pct_muslim": "Muslim pop. %", "census_pct_christian": "Christian pop. %",
           "census_pct_other": "Other-religion pop. %", "population_diversity_shannon": "Population diversity"}
C = sp[list(cm_cols)].rename(columns=cm_cols).corr(method="spearman")
C.round(3).to_csv(os.path.join(ST, "T7_state_spearman_correlation_matrix.csv"))
fig, ax = plt.subplots(figsize=(9.5, 8))
im = ax.imshow(C.values, cmap=vs.DIV, vmin=-1, vmax=1)
ax.set_xticks(range(len(C)), C.columns, rotation=45, ha="right"); ax.set_yticks(range(len(C)), C.index); ax.grid(False)
for i in range(len(C)):
    for j in range(len(C)):
        ax.text(j, i, f"{C.values[i, j]:.2f}", ha="center", va="center", fontsize=7.5,
                color="white" if abs(C.values[i, j]) > .6 else vs.INK)
fig.colorbar(im, ax=ax, shrink=.75, label="Spearman rho")
ax.set_title("State-level correlation matrix: holiday calendar vs religious demography (n=29)")
save(fig, "F03_correlation_matrix.png", f"{SRC_RBI}; {SRC_CEN}")

# ============ 5. STATE-WISE HEATMAP (state x month) =============================================
sm = obs.groupby(["state", "month"])["annual_weight"].sum().unstack(fill_value=0).reindex(columns=range(1, 13), fill_value=0)
sm = sm.div(sp["n_rbi_offices"], axis=0)
REG_ORDER = ["North", "Central", "East", "West", "South", "North-East"]
order = sp.assign(_r=sp.region.map(REG_ORDER.index)).sort_values(["_r", "hol_days_total_festival"], ascending=[True, False]).index
sm = sm.loc[order]; sm.round(3).to_csv(os.path.join(ST, "T8_state_by_month_holiday_days.csv"))
fig, ax = plt.subplots(figsize=(12, 10.5))
im = ax.imshow(sm.values, cmap=vs.SEQ, aspect="auto", vmin=0, vmax=5)
ax.set_xticks(range(12), MONTHS, fontsize=11); ax.xaxis.tick_top(); ax.tick_params(length=0)
ax.set_yticks(range(len(sm)), [st.replace("Punjab-Haryana-Chandigarh", "Punjab / Haryana / Chd.") for st in sm.index], fontsize=10.5)
ax.grid(False); [sp_.set_visible(False) for sp_ in ax.spines.values()]
for j in range(1, 12): ax.axvline(j - 0.5, color=vs.SURFACE, lw=1.2)
for i in range(1, len(sm)): ax.axhline(i - 0.5, color=vs.SURFACE, lw=1.2)
for i in range(sm.shape[0]):
    for j in range(12):
        v = sm.values[i, j]
        if v >= 1: ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=8.5, color="white" if v > 2.2 else vs.INK)
# region groups: thick separators + labels in the left margin
regs = sp.loc[sm.index, "region"].tolist(); b0 = 0
for k in range(1, len(regs) + 1):
    if k == len(regs) or regs[k] != regs[b0]:
        if k < len(regs): ax.axhline(k - 0.5, color=vs.INK, lw=1.6)
        ax.text(-0.235, (b0 + k - 1) / 2, regs[b0].upper(), transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=9.5, fontweight="bold", color=vs.INK2)
        b0 = k
cb = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.025, pad=0.02, aspect=40)
cb.set_label(f"Festival bank-holiday days per RBI office per year ({PERIOD} avg); numbers shown for cells >= 1 day", fontsize=9.5)
cb.outline.set_visible(False)
ax.set_title("State-wise festival heatmap: when each state's holidays fall", pad=30, fontsize=15)
fig.tight_layout()
save(fig, "F04_state_month_heatmap.png", SRC_RBI)

# ============ 6. CHOROPLETH (states) ==============================================================
gj = json.load(open(os.path.join(ROOT, "data", "raw", "geo", "india_states_datameet.geojson"), encoding="utf-8"))
GEO2STATE = {"Arunanchal Pradesh": "Arunachal Pradesh", "NCT of Delhi": "Delhi", "Punjab": "Punjab-Haryana-Chandigarh",
             "Haryana": "Punjab-Haryana-Chandigarh", "Chandigarh": "Punjab-Haryana-Chandigarh"}
def choropleth(values, title, fname, label, cmap=vs.SEQ, vmin=None, vmax=None, src=SRC_RBI):
    fig, ax = plt.subplots(figsize=(8.4, 7.2))
    vmin = values.min() if vmin is None else vmin; vmax = values.max() if vmax is None else vmax
    patches, cols, miss = [], [], []
    for f in gj["features"]:
        nm = f["properties"]["ST_NM"]; st = GEO2STATE.get(nm, nm)
        geom = f["geometry"]; polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ring = np.array(poly[0])
            if st in values.index:
                patches.append(Polygon(ring[:, :2], closed=True)); cols.append(values[st])
            else:
                miss.append(Polygon(ring[:, :2], closed=True))
    pc_ = PatchCollection(patches, cmap=cmap, edgecolor="white", linewidth=0.5); pc_.set_array(np.array(cols)); pc_.set_clim(vmin, vmax)
    ax.add_collection(pc_); ax.add_collection(PatchCollection(miss, facecolor="#e4e3df", edgecolor="white", linewidth=0.5, hatch="///"))
    ax.set_xlim(67.5, 98); ax.set_ylim(7.5, 37.5); ax.set_aspect("equal"); ax.axis("off")
    fig.colorbar(pc_, ax=ax, shrink=.55, label=label); ax.set_title(title)
    ax.text(0.01, 0.01, "Grey hatched: UTs without an RBI regional office (no data); island UTs not shown", transform=ax.transAxes, fontsize=7.5, color=vs.INK2)
    ax.text(0.0, -0.03, "Source: " + src + ". Boundaries: DataMeet India states (CC BY 2.5 IN)", transform=ax.transAxes,
            fontsize=7.5, color=vs.INK2, va="top")
    fig.savefig(os.path.join(FIG, fname)); plt.close(fig)
choropleth(sp.hol_days_total_festival, "Festival bank holidays per year, by state", "F05_map_festival_holidays.png", "Days per year")
choropleth(sp.holiday_diversity_shannon, "Diversity of the festival calendar (Shannon index over traditions)",
           "F06_map_holiday_diversity.png", "Shannon index")

# ============ 7. Holiday share vs population share scatter (small multiples, stacked for blog width) ====
SHORT = lambda n: n.replace("Punjab-Haryana-Chandigarh", "Punjab/Haryana/Chd.")
PICK = {"Hindu": ["Odisha", "Jammu & Kashmir", "Kerala", "Manipur", "Mizoram", "Arunachal Pradesh", "Delhi"],
        "Muslim": ["Jammu & Kashmir", "Kerala", "Assam", "Delhi", "Uttar Pradesh", "Himachal Pradesh"],
        "Christian": ["Nagaland", "Mizoram", "Meghalaya", "Manipur", "Goa", "Kerala", "Arunachal Pradesh"]}
fig, axes = plt.subplots(3, 1, figsize=(10, 15.5))
for ax, (faith, h, c) in zip(axes, [("Hindu", "hol_share_hindu", "census_pct_hindu"), ("Muslim", "hol_share_muslim", "census_pct_muslim"),
                                     ("Christian", "hol_share_christian", "census_pct_christian")]):
    col = vs.TRAD_COLOR[faith]
    ax.scatter(sp[c], sp[h], s=70, color=col, edgecolor=vs.SURFACE, linewidth=1.5, zorder=3)
    k_, b_ = np.polyfit(sp[c], sp[h], 1); xx = np.linspace(0, sp[c].max() * 1.05, 50)
    ax.plot(xx, k_ * xx + b_, color=col, lw=1.2, ls="--", alpha=.7, zorder=2)
    sel_ = [s_ for s_ in PICK[faith] if s_ in sp.index]
    vs.label_points(ax, sp.loc[sel_, c].values, sp.loc[sel_, h].values, [SHORT(s_) for s_ in sel_], fontsize=10.5, min_gap=18)
    rr = cr.set_index("faith").loc[faith]
    ax.set_xlabel(f"{faith} share of state population, % (Census 2011)", fontsize=11)
    ax.set_ylabel(f"{faith} share of festival holidays, %", fontsize=11); ax.tick_params(labelsize=10)
    ax.set_title(f"{faith}   Spearman rho = {rr.spearman_rho:.2f},  p = {rr.p_value:.3f}", fontsize=13.5)
    ax.set_xlim(left=-2, right=sp[c].max() * 1.22)
fig.suptitle("Do holiday calendars mirror demography?  (each dot = one state; dashed = trend)", x=0.01, y=0.995, ha="left",
             fontweight="bold", fontsize=15)
fig.tight_layout(h_pad=2.5, rect=(0, 0, 1, 0.975)); save(fig, "F07_holiday_vs_population_share.png", f"{SRC_RBI}; {SRC_CEN}")

# ============ 8. Economic charts ==================================================================
fig, ax = plt.subplots(figsize=(10, 5.8))
ser = ["Diwali (Deepavali)", "Holi", "Ganesh Chaturthi", "Karva Chauth", "Raksha Bandhan"]
ends = []
for i, f in enumerate(ser):
    d = trade[trade.festival == f].sort_values("year"); ci = vs.SLOTS[i]
    ax.plot(d.year, d.value / 1000, color=ci, lw=2.2, zorder=2)
    for _, r_ in d.iterrows():
        proj = r_.estimate_type == "projection"
        ax.scatter(r_.year, r_.value / 1000, s=60, zorder=3, facecolor=vs.SURFACE if proj else ci, edgecolor=ci, linewidth=2)
    last = d.iloc[-1]; ends.append((last.year, last.value / 1000, f"{f.split(' (')[0]}  {int(last.year)}: Rs {last.value / 1000:,.0f}k cr"))
# right-hand label column; labels nudged apart in log space, leader line back to each series' last point
ends.sort(key=lambda e: -e[1]); ly = []
for e in ends:
    y_ = e[1] if not ly else min(e[1], ly[-1] / 1.4); ly.append(y_)
for (x_, y0, t_), y_ in zip(ends, ly):
    ax.annotate(t_, (x_, y0), xytext=(2026.45, y_), textcoords="data", fontsize=10.5, color=vs.INK2, va="center",
                arrowprops=dict(arrowstyle="-", color="#b9b8b3", lw=0.8, shrinkA=0, shrinkB=6))
ax.set_yscale("log"); ax.set_xlim(2017.6, 2029.6); ax.set_xticks(range(2018, 2027, 2))
ticks = [3, 10, 30, 100, 300, 600]
ax.set_yticks(ticks, [f"{t:,}" for t in ticks]); ax.minorticks_off(); ax.tick_params(labelsize=10.5)
ax.set_ylabel("Trade, Rs thousand crore (log scale)", fontsize=11)
ax.spines["bottom"].set_bounds(2017.6, 2026.4); ax.grid(axis="x", visible=False)
ax.set_title("Festive trade estimates keep rising", fontsize=15, pad=26)
ax.text(0.0, 1.02, "Filled dot = reported after the festival;  open dot = pre-event projection", transform=ax.transAxes, fontsize=10, color=vs.INK2)
save(fig, "F08_festive_trade_trend.png", "CAIT press releases & reports (cait.in, via The Tribune, Inshorts, Outlook Business, AIR); Ganesh 2025: Complete Circle via Business Today")

sec = eco[(eco.metric == "sector_share_of_goods_sales")].sort_values("value")
fig, ax = plt.subplots(figsize=(8, 5.2))
ax.barh(sec.sector, sec.value, color=vs.SLOTS[0], height=0.66)
for y, v in enumerate(sec.value): ax.text(v + 0.2, y, f"{v:.0f}%", va="center", fontsize=8, color=vs.INK2)
ax.set_xlabel("% of Diwali 2025 goods sales (INR 5.40 lakh crore)"); ax.grid(axis="y", visible=False)
ax.set_title("Market-sector impact: where Diwali 2025 money went")
save(fig, "F09_diwali_sector_split.png", "CAIT, Research Report on Diwali Festival Sales 2025 (cait.in)")

# Global analogues (USD, publishers' own conversions) and footfall density
glob = pd.DataFrame([
    ("Diwali 2025 (India)", 68.77, "IBEF / CAIT"), ("US holiday season 2024", 994.1, "NRF"),
    ("China Spring Festival 2025 (tourism only)", 94.43, "Ministry of Culture & Tourism, PRC")], columns=["event", "usd_bn", "source"])
glob.to_csv(os.path.join(ST, "T9_global_spending_comparison.csv"), index=False)
foot = pd.DataFrame([
    ("Maha Kumbh 2025 (Prayagraj)", 662_100_000, 45, "AIR / Govt. of UP"), ("Medaram Jatara 2020 (Telangana)", 15_000_000, 4, "The News Minute"),
    ("Hornbill Festival 2024 (Nagaland)", 204_986, 10, "Nagaland Tourism via Nagaland Tribune"),
    ("Oktoberfest 2025 (Munich)", 6_500_000, 16, "City of Munich / oktoberfest.de"),
    ("Hajj 2025 (Makkah)", 1_673_230, 6, "GASTAT"),
    ("Spring Festival 2025 (China, trips)", 501_000_000, 8, "gov.cn")], columns=["event", "footfall", "days", "source"])
foot["per_day"] = foot.footfall / foot.days
foot.to_csv(os.path.join(ST, "T10_footfall_density.csv"), index=False)
fig, ax = plt.subplots(figsize=(9, 3.8))
f2 = foot.sort_values("per_day")
cols_ = [vs.SLOTS[1] if "Kumbh" in e or "Medaram" in e or "Hornbill" in e else vs.INK2 for e in f2.event]
ax.barh(f2.event, f2.per_day / 1e6, color=cols_, height=0.62)
for y, v in enumerate(f2.per_day / 1e6): ax.text(v * 1.05, y, f"{v:,.2f} M/day", va="center", fontsize=8, color=vs.INK2)
ax.set_xscale("log"); ax.set_xlabel("Average visits per event-day, millions (log scale)"); ax.grid(axis="y", visible=False)
ax.set_title("Footfall density: Indian festivals (orange) vs global analogues (grey)")
save(fig, "F10_footfall_density.png", "; ".join(foot.source) + ". Hajj duration = 6 ritual days (8-13 Dhul Hijjah)")

report += ["## 3. Comparative analysis\n", "### Global spending analogues (USD bn, publishers' conversions)\n", glob.to_markdown(index=False), "\n",
           "### Footfall density\n", foot.to_markdown(index=False), "\n",
           "### States ranked by festival holidays per year\n",
           sp.sort_values("hol_days_total_festival", ascending=False)[["region", "hol_days_total_festival", "n_distinct_festivals",
               "holiday_diversity_shannon", "population_diversity_shannon"]].round(2).to_markdown(), "\n",
           "### Season (IMD) comparison\n",
           obs.groupby("season_imd")["annual_weight"].sum().div(34).round(2).rename("holiday_days_per_office_per_year").to_markdown(), "\n",
           "### Distinct festivals observed per month\n", dens.rename(index=dict(enumerate(MONTHS, 1))).to_markdown(), "\n"]
open(os.path.join(ST, "statistical_summary.md"), "w", encoding="utf-8").write("\n".join(report))
print(T[["id", "test", "statistic", "p_value", "effect_size", "result"]].to_string())
print("\n", cr.to_string())
