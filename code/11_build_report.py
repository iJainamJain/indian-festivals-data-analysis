"""Final project report (DOCX -> PDF) in the course submission format (VIT header + info tables from the
Experiment 8 submission), filled with the real outputs of scripts 01-10.
Output: report/DAV Project Report_23108B0084.docx / .pdf"""
import os, copy, json
import pandas as pd
import docx
from project_config import YEARS, PERIOD
from docx.shared import Pt, Inches, RGBColor
from docx.oxml.ns import qn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(os.path.dirname(ROOT), "lab exp", "lab 8", "DAV lab 8.docx")
OUTD = os.path.join(ROOT, "report"); os.makedirs(OUTD, exist_ok=True)
FIG = os.path.join(ROOT, "outputs", "figures")
ST, ML = os.path.join(ROOT, "outputs", "stats"), os.path.join(ROOT, "outputs", "ml")
T = pd.read_csv(os.path.join(ST, "T6_hypothesis_tests.csv"))
desc = pd.read_csv(os.path.join(ST, "T1_descriptive_statistics.csv"), index_col=0)
bytrad = pd.read_csv(os.path.join(ST, "T2_by_tradition.csv"))
mls = json.load(open(os.path.join(ML, "ml_summary.json")))
clsm = pd.read_csv(os.path.join(ML, "B_classifier_cv_metrics.csv"))
regm = pd.read_csv(os.path.join(ML, "C_regression_metrics.csv")).set_index("metric")["value"]
eng = json.load(open(os.path.join(ROOT, "blog", "engagement", "engagement_metrics.json")))
obs = pd.read_csv(os.path.join(ROOT, "data", "processed", "festival_observations.csv"))
fm = pd.read_csv(os.path.join(ROOT, "data", "processed", "festival_master.csv"))
eco = pd.read_csv(os.path.join(ROOT, "data", "processed", "economic_footfall_clean.csv"))

d = docx.Document(TEMPLATE)
# header: "Experiment No 8" -> "Mini Project"
for s in d.sections:
    for t in s.header._element.iter(qn("w:t")):
        if t.text == "Experiment": t.text = "Mini"
        elif t.text == "No": t.text = "Project"
        elif t.text == "8": t.text = ""
# team members row under Student Name / Roll Number
_st = d.tables[1]; _tr = copy.deepcopy(_st.rows[0]._tr); _st._tbl.append(_tr)
_r = _st.rows[-1]
for _c, _t in zip(_r.cells, ["Team Members", "Jainam Jain, Vrushan Patil, Dhanush Chowke, Aditya Tambe, Vivek Jaiswal"]):
    for _p in _c.paragraphs[1:]: _p._p.getparent().remove(_p._p)
    _runs = _c.paragraphs[0].runs; _runs[0].text = _t
    for _x in _runs[1:]: _x._r.getparent().remove(_x._r)
sp = pd.read_csv(os.path.join(ROOT, "data", "processed", "state_profile.csv")).set_index("state")
cr = pd.read_csv(os.path.join(ST, "T5_holiday_vs_population_share.csv"))
raw_n = len(pd.read_csv(os.path.join(ROOT, "data", "raw", "rbi_holiday_matrix_raw.csv")))
HIN = bytrad.set_index("tradition").loc["Hindu", "share_of_all_festival_holidays_pct"]
RHO = f"{cr.spearman_rho.min():.2f}-{cr.spearman_rho.max():.2f}"
top = sp.hol_days_total_festival.sort_values(ascending=False); N_UNSURE = int((~fm.reach_identifiable).sum())
main = d.tables[2]
proto_first, proto = copy.deepcopy(main.rows[0]._tr), copy.deepcopy(main.rows[1]._tr)
for r in list(main.rows): main._tbl.remove(r._tr)

def set_runs(par, text, bold=False, font=None, size=10):
    for r in list(par.runs): r._r.getparent().remove(r._r)
    run = par.add_run(text); run.bold = bold; run.font.size = Pt(size)
    if font: run.font.name = font; run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    return run

def add_row(label, content, first=False):
    tr = copy.deepcopy(proto_first if first else proto); main._tbl.append(tr)
    row = main.rows[-1]; lc, rc = row.cells[0], row.cells[1]
    for p in lc.paragraphs[1:]: p._p.getparent().remove(p._p)
    set_runs(lc.paragraphs[0], label)
    for p in rc.paragraphs[1:]: p._p.getparent().remove(p._p)
    first_par = rc.paragraphs[0]; set_runs(first_par, "")
    items = content if isinstance(content, list) else [content]
    started = False
    for it in items:
        par = first_par if not started else rc.add_paragraph(style=first_par.style)
        started = True
        if isinstance(it, tuple) and it[0] == "img":
            par.add_run().add_picture(os.path.join(FIG, it[1]), width=Inches(it[3] if len(it) > 3 else 4.6))
            cap = rc.add_paragraph(style=first_par.style); r_ = set_runs(cap, it[2], size=8.5); r_.italic = True
        elif isinstance(it, tuple) and it[0] == "table":
            df = it[1]; tb = rc.add_table(rows=1, cols=len(df.columns)); tb.style = d.tables[0].style
            for j, c in enumerate(df.columns): set_runs(tb.rows[0].cells[j].paragraphs[0], str(c), bold=True, size=8)
            for _, rr in df.iterrows():
                cells = tb.add_row().cells
                for j, v in enumerate(rr): set_runs(cells[j].paragraphs[0], str(v), size=8)
            _borders(tb)
        elif isinstance(it, tuple) and it[0] == "code":
            set_runs(par, it[1], font="Consolas", size=8.5)
        elif isinstance(it, tuple) and it[0] == "b":
            set_runs(par, it[1], bold=True)
        else:
            set_runs(par, it, bold=first)
    return row

def _borders(tb):
    tblPr = tb._tbl.tblPr
    b = docx.oxml.OxmlElement("w:tblBorders")
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = docx.oxml.OxmlElement(f"w:{e}"); el.set(qn("w:val"), "single"); el.set(qn("w:sz"), "4"); el.set(qn("w:color"), "999999"); b.append(el)
    tblPr.append(b)

h = T.set_index("id")
A_, C_ = mls["A"], mls["C"]
add_row("Mini Project", "Socio-Economic & Demographic Analysis of Indian Festivals", first=True)
add_row("Problem Statement", [
    "India exhibits immense cultural and regional diversity, with hundreds of festivals celebrated across states, communities and calendar "
    "months. Unstructured information leads to biased representations and missing comparative insight. The project must (1) collect an "
    "authentic multi-faith festival dataset with zero synthetic records and exact source URLs, (2) build and evaluate ML models, "
    "(3) perform rigorous statistical testing and EDA, (4) publish a public data-visualisation blog with 40+ external interactions, "
    "and (5) produce a synthesis video."])
add_row("Resources", [
    "Software: Python 3.12, Windows 11, ffmpeg, Windows SAPI (System.Speech) for narration, Microsoft Word (PDF export), MS Edge + Playwright.",
    "Libraries: pandas, numpy, scipy, statsmodels, scikit-learn, joblib, matplotlib, plotly, requests, BeautifulSoup, xlrd, markdown.",
    f"Data sources (all real, cited per record): Reserve Bank of India holiday matrix {PERIOD} (rbi.org.in); DoPT compulsory-holiday list (O.M. F.No.12/2/2023-JCA); Census of India 2011 Table C-01 "
    "(censusindia.gov.in); Wikipedia infoboxes via MediaWiki API + Govt. portals (utsav.gov.in, soreng.nic.in, dtahills.mn.gov.in, megtourism.gov.in); "
    "CAIT (cait.in) and verified news for spending; NRF, gov.cn, GASTAT, muenchen.de for global analogues; DataMeet state boundaries (CC BY 2.5 IN)."])
add_row("Deliverables", [
    "Task 1 - data/raw/*.csv|json (raw with source columns), data/processed/*.csv (clean), data/data_dictionary.md|csv",
    "Task 2 - code/06_ml_models.py, model weights outputs/models/*.joblib, metrics outputs/ml/*.csv, ml_summary.json",
    "Task 3 - outputs/stats/statistical_summary.md + T1-T10 validation tables, figures F01-F10",
    "Task 4 - blog/blog_post.md|html, blog/images, blog/interactive/*.html, blog/engagement (log template, audit report)",
    "Task 5 - video/Indian_Festivals_Project_Report.mp4 (1080p, narrated), video/narration_script.md, this report"])
add_row("Approach", [
    f"1. Scrape the RBI holiday matrix for every office and month of {YEARS[0]}-{YEARS[-1]} ({raw_n:,} office-date rows), save raw HTML + CSV with source URL per row.",
    f"2. Build a {fm.festival.nunique()}-festival regex catalog and resolve each RBI label into festivals. Shared dates are credited by evidence: a festival counts in full "
    "where the office is confirmed to observe it (closed on a date where it stood alone, on the DoPT compulsory list and never absent, or the festival's home community); "
    "the rest is split by an evidence score and flagged. Sunday correction: each festival is averaged only over the years it could be listed.",
    "3. Source-ground each festival's tradition from its Wikipedia infobox ('Observed by') or an official Govt. page.",
    "4. Download Census 2011 C-01, map 34 RBI offices to 29 states/UTs, build festival-, observation- and state-level tables.",
    "5. Collect 78 economic/footfall figures; open every page to confirm the figure (snippet-only figures were excluded).",
    "6. EDA & hypothesis tests (chi-square, permutation, Spearman, Kruskal-Wallis, Mann-Whitney, OLS).",
    "7. ML: K-Means/Ward clustering of states, Random Forest vs Logistic tradition classifier, log-linear trade regression with LOO and temporal hold-out.",
    "8. Blog + interactive Plotly charts, engagement audit tooling; 9. narrated video; 10. report."])
add_row("Code", [("code", "01_scrape_rbi_holidays.py   02_verify_wikipedia.py      03_economic_footfall_records.py\n"
                           "04_build_clean_dataset.py   05_eda_statistics.py        06_ml_models.py\n"
                           "07_data_dictionary.py       08_interactive_charts.py    09_blog_and_engagement.py\n"
                           "10_make_video.py            11_build_report.py          festival_catalog.py  viz_style.py"),
                 "Excerpt - fractional attribution of shared-date holidays (04_build_clean_dataset.py):",
                 ("code", 'obs["n_items_on_date"] = obs.groupby(["date","rbi_regional_office"])["festival"]\n'
                          '                             .transform("size") + obs["n_civic_items"]\n'
                          'obs["attribution_weight"] = 1 / obs["n_items_on_date"]\n'
                          'obs["attribution"] = np.where(obs["n_items_on_date"] == 1, "unique", "shared_date")')])
add_row("Task 1: Dataset", [
    f"{len(obs):,} festival-holiday observations | {fm.festival.nunique()} festivals | 34 RBI offices | 29 states/UTs | {YEARS[0]}-{YEARS[-1]} | "
    f"{len(eco)} verified economic/footfall records | Census 2011 demography. Zero synthetic records.",
    ("table", bytrad[["tradition", "festivals", "holiday_days_per_office_per_year", "share_of_all_festival_holidays_pct", "pct_lunar"]]
     .rename(columns={"holiday_days_per_office_per_year": "holiday-days/office/yr", "share_of_all_festival_holidays_pct": "% of festival holidays",
                      "pct_lunar": "% moving-date"})),
    f"Limitations: {N_UNSURE} of {fm.festival.nunique()} festivals always share their date, so their state coverage stays uncertain (flagged); festivals without a bank holiday, restricted and "
    "district-level holidays and UTs without an RBI office are not covered; bank holidays measure official recognition, not participation; trade figures are industry estimates."])
tt = T[["id", "test", "statistic", "p_value", "result"]].copy(); tt["test"] = tt["test"].str.slice(0, 48)
tt["p_value"] = tt["p_value"].map(lambda v: "< 0.001" if v < 0.001 else f"{v:.3f}"); tt["statistic"] = tt["statistic"].map(lambda v: f"{v:.3f}")
add_row("Task 3: Statistics", [
    ("table", desc[["n", "mean", "median", "std", "skewness"]].reset_index().rename(columns={"index": "variable"})),
    ("table", tt),
    f"H1: holidays cluster by month (chi2 = {h.loc['H1', 'statistic']:.0f}, p < 0.001; peaks Mar, Oct, Apr). H2: season independent of tradition "
    f"(perm. p = {h.loc['H2', 'p_value']:.2f}). H3: holiday share correlates with population share for all six faiths (rho {RHO}, all p < 0.05 after Holm correction). "
    f"H4: reach differs by tradition group (p = {h.loc['H4', 'p_value']:.3f}). H5-H8 not significant. H9: festive trade grows {h.loc['H9', 'interpretation'].split('growth ')[1].split(')')[0]})."])
A_, C_ = mls["A"], mls["C"]
add_row("Task 2: Machine Learning", [
    ("b", "A. Clustering states (K-Means vs Ward)"),
    f"Features: Hindu/Muslim/Christian/Tribal shares of festival holidays (chosen by a documented feature-set experiment). k = {A_['best_k']} "
    f"(silhouette {A_['silhouette']:.3f}); bootstrap ARI {A_['bootstrap_ARI_mean']:.2f} +/- {A_['bootstrap_ARI_sd']:.2f}; ARI vs region {A_['ARI_clusters_vs_geographic_region']:.2f}.",
    "; ".join(f"{k}: {', '.join(v)}" for k, v in A_["detail_clusters"].items()) + f" (the {A_['detail_k']}-group view, silhouette {A_['detail_silhouette']:.2f}).",
    ("b", "B. Tradition classifier (5-fold x 20 repeated stratified CV)"),
    ("table", clsm.round(3)),
    ("b", "C. Festive-trade regression (log-linear, festival fixed effects)"),
    f"n = {int(regm['n_train (<=2025)'])}; in-sample R2 (log) {regm['in_sample_R2 (log)']:.3f}; LOO RMSE {regm['LOO_RMSE (log units)']:.3f} log units; "
    f"LOO MAPE {regm['LOO_MAPE_%']:.1f}%; growth {regm['implied_annual_growth_%']:.1f}%/yr; hold-out 2026 MAPE {regm['holdout_2026_MAPE_%']:.1f}% "
    f"(Holi {C_['holdout_2026'][1]['abs_pct_error']}%, Raksha Bandhan {C_['holdout_2026'][0]['abs_pct_error']}%)."])
add_row("Task 4: Blog & Engagement", [
    "Article 'What India's Bank-Holiday Calendar Reveals About How the Country Celebrates' (~1,700 words, 9 figures, 8 footnoted sources, secular framing) "
    "in blog/blog_post.md and a paste-ready blog_post.html; 4 interactive Plotly charts (hover tooltips) in blog/interactive/.",
    f"Publication status: {eng['live_url']}. External interactions logged: {eng['external_interactions']} / 40 target; comments answered: "
    f"{eng['comments_with_author_reply']}. The audit (09_blog_and_engagement.py) counts only people outside VIT and requires a screenshot per row. "
    "Publishing and community engagement must be done by the author; no engagement is simulated."])
add_row("Task 5: Video", [
    "video/Indian_Festivals_Project_Report.mp4 - 1920x1080, H.264/AAC, 11 narrated slides (~5.4 min): motivation & source integrity, statistics, "
    "ML architecture & performance, economics, blog & reception, takeaways. The reception slide reads engagement_metrics.json; re-run "
    "10_make_video.py after publishing to produce the final cut."])
add_row("Output Visuals", [
    ("img", "F02_month_timeline_by_tradition.png", f"Fig 1. Festival bank-holiday days by month and tradition (RBI {PERIOD})."),
    ("img", "F04_state_month_heatmap.png", "Fig 2. State x month heatmap.", 4.2),
    ("img", "F05_map_festival_holidays.png", "Fig 3. Festival holidays per year by state."),
    ("img", "F07_holiday_vs_population_share.png", "Fig 4. Holiday share vs Census population share."),
    ("img", "F03_correlation_matrix.png", "Fig 5. State-level Spearman correlation matrix.", 4.2),
    ("img", "F08_festive_trade_trend.png", "Fig 6. Festive trade estimates (CAIT)."),
    ("img", "F09_diwali_sector_split.png", "Fig 7. Diwali 2025 sector split.", 4.0),
    ("img", "F10_footfall_density.png", "Fig 8. Footfall density vs global analogues."),
    ("img", "M01_state_clusters.png", "Fig 9. K-Means state clusters (PCA) and model selection."),
    ("img", "M05_cluster_map.png", "Fig 9b. State clusters on the map.", 3.8),
    ("img", "M03_classifier_results.png", "Fig 10. Classifier confusion matrix and permutation importance."),
    ("img", "M04_trade_regression.png", "Fig 11. Trade model: LOO and 2026 hold-out predictions.", 3.8)])
add_row("Insights", [
    "1. Festival holidays peak in April, October and March (about 2.6-2.8 days per office each); January, February and July are quietest.",
    f"2. Every faith's holiday share rises with its population share (Spearman {RHO}), yet the calendar is more plural than the population: "
    f"Hindu festivals are ~{HIN:.0f}% of festival holidays vs 79.8% of population, because Christmas, Good Friday, both Eids, Buddha Purnima, "
    "Mahavir Jayanti and Guru Nanak Jayanti are gazetted almost nationwide.",
    f"3. {top.index[0]} ({top.iloc[0]:.1f}), {top.index[1]} ({top.iloc[1]:.1f}) and {top.index[2]} ({top.iloc[2]:.1f}) have the most festival holidays; {top.index[-1]} ({top.iloc[-1]:.1f}) the fewest. Regions do not differ significantly.",
    f"4. The strongest state grouping is {A_['best_k']} clusters (four north-eastern hill states vs the rest, silhouette {A_['silhouette']:.2f}); calendars otherwise form a continuum that does not follow regions (ARI {A_['detail_ARI_vs_geographic_region']:.2f}).",
    f"5. A festival's date and footprint only weakly reveal its faith (macro-F1 {clsm.set_index('model').loc['Random Forest', 'macro_f1_mean']:.2f}): nationwide festivals of all faiths look alike.",
    "6. Reported festive trade grows ~34%/yr (Diwali: Rs 1.25 lakh cr in 2021 -> Rs 6.05 lakh cr in 2025), but national spending estimates "
    "exist mainly for Hindu festivals - a measurement blind spot."])
add_row("Conclusion", [
    "A fully source-grounded, multi-faith festival dataset was built from official RBI and Census data plus 78 verified economic figures, "
    "analysed with hypothesis tests and three ML models, and communicated through a footnoted blog, interactive charts and a narrated video. "
    "Remaining author actions: publish the article, collect 40+ genuine external interactions, fill the engagement log, and re-run the audit and video scripts."])
add_row("References", [
    "[1] RBI, Holidays under NI Act - https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx",
    "[2] Census of India 2011, C-01 - https://censusindia.gov.in/nada/index.php/catalog/11361",
    "[3] CAIT Diwali 2025 report - https://cait.in (10 Nov 2025); other economic sources listed per record in data/raw/economic_footfall_raw.csv",
    "[4] All India Radio, Maha Kumbh concludes - https://www.newsonair.gov.in/maha-kumbh-mela-2025-concludes-in-prayagraj-on-maha-shivratri",
    "[5] NRF (16 Jan 2025); gov.cn (5 Feb 2025); GASTAT (5 Jun 2025); muenchen.de - global analogues",
    "[6] DataMeet India state boundaries (CC BY 2.5 IN) - github.com/datameet/maps"])
out = os.path.join(OUTD, "DAV Project Report_23108B0084.docx"); d.save(out); print("docx ->", out)

import win32com.client
w = win32com.client.DispatchEx("Word.Application"); w.Visible = False; w.DisplayAlerts = 0
try:
    doc = w.Documents.Open(out); doc.SaveAs2(out.replace(".docx", ".pdf"), FileFormat=17); doc.Close(False)
finally:
    w.Quit()
print("pdf ->", out.replace(".docx", ".pdf"))
