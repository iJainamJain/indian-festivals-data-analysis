"""Project status report (what is done per task, key results, links, what is pending) -> PDF.
Reads live numbers from outputs/ and blog/engagement so it can be regenerated at any time.
Output: report/Project Status Report.pdf"""
import os, json, base64, datetime
import pandas as pd
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
ml = json.load(open(J("outputs", "ml", "ml_summary.json")))
eng = json.load(open(J("blog", "engagement", "engagement_metrics.json")))
T = pd.read_csv(J("outputs", "stats", "T6_hypothesis_tests.csv")).set_index("id")
obs = pd.read_csv(J("data", "processed", "festival_observations.csv"))
fm = pd.read_csv(J("data", "processed", "festival_master.csv"))
eco = pd.read_csv(J("data", "processed", "economic_footfall_clean.csv"))
reg = pd.read_csv(J("outputs", "ml", "C_regression_metrics.csv")).set_index("metric")["value"]
A, B, C = ml["A"], ml["B"]["metrics"], ml["C"]
REPO = "https://github.com/iJainamJain/indian-festivals-data-analysis"
live = eng["live_url"] != "NOT YET PUBLISHED"
today = datetime.date.today().strftime("%d %B %Y")
img = lambda f: "data:image/png;base64," + base64.b64encode(open(J("outputs", "figures", f), "rb").read()).decode()
done, prog = '<span class="pill ok">Done</span>', '<span class="pill wip">In progress</span>'
eng_status = done if eng["target_met"] else prog

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 16mm 15mm; }}
body {{ font: 10.3pt/1.45 'Segoe UI', Arial, sans-serif; color: #0b0b0b; }}
h1 {{ font-size: 19pt; margin: 0 0 2px; }} h2 {{ font-size: 12.5pt; margin: 16px 0 6px; color: #0d366b; border-bottom: 1.5px solid #0d366b; padding-bottom: 2px; }}
.sub {{ color: #52514e; margin-bottom: 10px; }} table {{ border-collapse: collapse; width: 100%; margin: 4px 0 8px; }}
th, td {{ border: 1px solid #cfcec9; padding: 5px 7px; vertical-align: top; text-align: left; }} th {{ background: #eef3fa; }}
.pill {{ display: inline-block; padding: 1px 9px; border-radius: 10px; font-size: 9pt; font-weight: 600; white-space: nowrap; }}
.ok {{ background: #d9f2e4; color: #0b5d2a; }} .wip {{ background: #fdeccb; color: #7a4b00; }}
ul {{ margin: 3px 0 6px 18px; padding: 0; }} li {{ margin: 1.5px 0; }} code {{ font: 9pt Consolas, monospace; background: #f1f0ec; padding: 0 3px; }}
.figs {{ display: flex; gap: 10px; margin: 6px 0; }} .figs > div {{ flex: 1; }} .figs img {{ width: 100%; border: 1px solid #cfcec9; }} .cap {{ font-size: 8.5pt; color: #52514e; }}
.box {{ background: #fff6e0; border: 1px solid #e8c877; padding: 7px 10px; margin: 6px 0; }} table, .box, .figs {{ break-inside: avoid; }} h2 {{ break-after: avoid; }}
</style></head><body>
<h1>Project Status Report</h1>
<div class="sub"><b>Socio-Economic &amp; Demographic Analysis of Indian Festivals</b> &middot; DAV Laboratory mini project &middot; B.E. Sem VII ECS, Vidyalankar Institute of Technology<br>
Team: Jainam Jain (23108B0084), Vrushan Patil, Dhanush Chowke, Aditya Tambe, Vivek Jaiswal &middot; Guide: Prof. Uma Jaishankar &middot; Status as of {today}</div>

<h2>1. Status at a glance</h2>
<table><tr><th style="width:21%">Task</th><th style="width:13%">Status</th><th>What exists</th></tr>
<tr><td>1. Data collection &amp; preprocessing</td><td>{done}</td><td>{len(obs):,} festival-holiday records, {fm.festival.nunique()} festivals, 29 states/UTs, 2024&ndash;26; {len(eco)} verified spending and crowd figures; Census 2011 religion data; data dictionary</td></tr>
<tr><td>2. Machine learning</td><td>{done}</td><td>3 models (clustering, classification, regression) with code, saved model files and evaluation metrics</td></tr>
<tr><td>3. Statistics &amp; EDA</td><td>{done}</td><td>{len(T)} hypothesis tests, 10 validation tables, 10 statistical charts, summary report</td></tr>
<tr><td>4a. Blog article</td><td>{done if live else prog}</td><td>{"Published on Medium on " + pd.Timestamp(eng["published_on"]).strftime("%d %b %Y") if live else "Written, not yet published"}; 9 charts, 9 cited sources, 4 interactive charts</td></tr>
<tr><td>4b. External engagement</td><td>{eng_status}</td><td><b>{eng["external_interactions"]} of 40</b> external reactions/comments logged; {eng["comments_with_author_reply"]} comments answered</td></tr>
<tr><td>5. Video &amp; repository</td><td>{done}</td><td>Narrated 1080p video (about 5.4 min); public GitHub repository; 8-page technical report</td></tr></table>

<h2>2. What was done in each task</h2>
<b>Task 1: Data</b>
<ul><li>Scraped the Reserve Bank of India's official bank-holiday lists for all 34 regional offices, every month of 2024, 2025 and 2026 (2,031 office-date rows, source URL on every row).</li>
<li>Resolved RBI's holiday labels into {fm.festival.nunique()} named festivals across 9 tradition groups: Hindu, Muslim, Christian, Sikh, Buddhist, Jain, Parsi, tribal/indigenous and multi-faith cultural.</li>
<li>Took each festival's tradition from its Wikipedia infobox, or a Government portal where no article exists.</li>
<li>Added Census of India 2011 religion-by-state data and {len(eco)} spending and crowd figures, each opened and confirmed on its source page. No synthetic records.</li>
<li>Known limit: RBI gives one combined label per date, so shared dates are split equally; {int((~fm.reach_identifiable).sum())} festivals are flagged as "reach not identifiable".</li></ul>
<b>Task 2: Machine learning</b>
<ul><li><b>State clustering (K-Means):</b> {A["best_k"]} groups, silhouette {A["silhouette"]:.2f}, bootstrap stability {A["bootstrap_ARI_mean"]:.2f}. Groups do not follow geography (agreement with regions {A["ARI_clusters_vs_geographic_region"]:.2f}).</li>
<li><b>Tradition classifier (Random Forest):</b> macro-F1 {B["Random Forest"]["macro_f1_mean"]:.2f} against {B["Majority baseline"]["macro_f1_mean"]:.2f} for a majority-class baseline, repeated 5-fold cross-validation.</li>
<li><b>Festive-trade regression:</b> growth {reg["implied_annual_growth_%"]:.0f}% a year in this model (34% in the Task 3 test, which also uses the 2026 figures), leave-one-out error {reg["LOO_MAPE_%"]:.0f}%; predicted the 2026 Holi figure within {C["holdout_2026"][1]["abs_pct_error"]:.0f}% and Raksha Bandhan within {C["holdout_2026"][0]["abs_pct_error"]:.0f}%.</li></ul>
<b>Task 3: Statistics</b>
<ul><li>Festival holidays are concentrated by month (chi-square = {T.loc["H1", "statistic"]:.0f}, p &lt; 0.001); peaks in March, October and April.</li>
<li>Each faith's share of a state's holidays rises with its population share (Spearman {min(T.loc[[i for i in T.index if i.startswith("H3")], "statistic"]):.2f} to {max(T.loc[[i for i in T.index if i.startswith("H3")], "statistic"]):.2f}, all significant).</li>
<li>Hindu festivals are about 46% of festival holidays against 79.8% of the population, because several minority festivals are recognised almost nationwide.</li>
<li>No significant difference between the six regions (p = {T.loc["H6-hol_days", "p_value"]:.2f}); a festival's season is independent of its tradition (p = {T.loc["H2", "p_value"]:.2f}).</li></ul>
<div class="figs"><div><img src="{img("F02_month_timeline_by_tradition.png")}"><div class="cap">Festival holidays by month and tradition</div></div>
<div><img src="{img("F08_festive_trade_trend.png")}"><div class="cap">Festive trade estimates by year</div></div></div>
<b>Task 4: Blog</b>
<ul><li>Article: "What India's Bank-Holiday Calendar Reveals About How the Country Celebrates", credited to all five team members, neutral and secular framing, every figure cited.</li>
<li>Live at: {eng["live_url"]}</li>
<li>Engagement audit tooling is ready: a log (one row per external reaction or comment, with screenshot) and a script that counts only people outside VIT.</li></ul>
<b>Task 5: Video and repository</b>
<ul><li>Video: 11 narrated slides covering motivation, data integrity, statistics, ML, economics, blog reception and takeaways. The reception slide updates from the engagement log.</li>
<li>Repository (code, datasets, models, charts, report, video): {REPO}</li></ul>

<h2>3. What is still pending</h2>
<div class="box"><b>External engagement: {eng["external_interactions"]} of 40 logged.</b> This is the only open requirement.</div>
<ul><li>All five members share the article outside VIT (LinkedIn, professional and interest groups) and reply to every comment.</li>
<li>Record each external reaction or comment in <code>blog/engagement/engagement_log.csv</code> with a screenshot.</li>
<li>Re-run scripts 09, 10 and 11 so the audit report, video and technical report show the final counts.</li>
<li>Optional: add the other four members' roll numbers to the technical report.</li></ul>

<h2>4. Where everything is</h2>
<table><tr><th style="width:30%">Item</th><th>Location (inside the <code>project</code> folder)</th></tr>
<tr><td>Raw and cleaned datasets, data dictionary</td><td><code>data/raw</code>, <code>data/processed</code>, <code>data/data_dictionary.md</code></td></tr>
<tr><td>Code (12 pipeline scripts, 2 helper modules)</td><td><code>code/01_&hellip;</code> to <code>code/12_&hellip;</code>, <code>festival_catalog.py</code>, <code>viz_style.py</code></td></tr>
<tr><td>Statistics tables and charts</td><td><code>outputs/stats</code>, <code>outputs/figures</code></td></tr>
<tr><td>ML metrics and saved models</td><td><code>outputs/ml</code>, <code>outputs/models</code></td></tr>
<tr><td>Blog source, images, interactive charts</td><td><code>blog/blog_post.md</code>, <code>blog/images</code>, <code>blog/interactive</code></td></tr>
<tr><td>Engagement log and audit</td><td><code>blog/engagement</code></td></tr>
<tr><td>Technical report (8 pages)</td><td><code>report/DAV Project Report_23108B0084.pdf</code></td></tr>
<tr><td>Video</td><td><code>video/Indian_Festivals_Project_Report.mp4</code></td></tr></table>
</body></html>"""
tmp = J("report", "_status.html"); open(tmp, "w", encoding="utf-8").write(html)
out = J("report", "Project Status Report.pdf")
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge"); pg = b.new_page()
    pg.goto("file:///" + tmp.replace("\\", "/").replace(" ", "%20")); pg.pdf(path=out, format="A4", print_background=True); b.close()
os.remove(tmp); print("pdf ->", out)
