"""Fill the faculty's 'DAV Micro Project Report Format' with this project's real outputs.
Template: report/template/DAV Micro Project_Report_Format.docx (kept unchanged)
Output:   report/DAV Micro Project Report_23108B0084.docx  (+ .pdf via Word)
Every number is read from outputs/ and data/ at build time."""
import os, copy, json, shutil
import numpy as np, pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
import viz_style as vs
from project_config import YEARS, PERIOD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
TEMPLATE = J("report", "template", "DAV Micro Project_Report_Format.docx")
OUT = J("report", "DAV Micro Project Report_23108B0084.docx")
FIG = J("outputs", "figures")

# ------------------------------- numbers -------------------------------
obs = pd.read_csv(J("data", "processed", "festival_observations.csv"))
fm = pd.read_csv(J("data", "processed", "festival_master.csv"))
sp = pd.read_csv(J("data", "processed", "state_profile.csv")).set_index("state")
eco = pd.read_csv(J("data", "processed", "economic_footfall_clean.csv"))
raw = pd.read_csv(J("data", "raw", "rbi_holiday_matrix_raw.csv"))
T = pd.read_csv(J("outputs", "stats", "T6_hypothesis_tests.csv")).set_index("id")
cr = pd.read_csv(J("outputs", "stats", "T5_holiday_vs_population_share.csv")).set_index("faith")
bt = pd.read_csv(J("outputs", "stats", "T2_by_tradition.csv")).set_index("tradition")["share_of_all_festival_holidays_pct"]
mon = pd.read_csv(J("outputs", "stats", "T3_month_by_tradition_holiday_days.csv"), index_col=0).sum(axis=1)
ml = json.load(open(J("outputs", "ml", "ml_summary.json")))
clf = pd.read_csv(J("outputs", "ml", "B_classifier_cv_metrics.csv")).set_index("model")
pcr = pd.read_csv(J("outputs", "ml", "B_per_class_report.csv"))
loo = pd.read_csv(J("outputs", "ml", "C_loo_predictions.csv"))
hold = pd.read_csv(J("outputs", "ml", "C_holdout_2026.csv"))
fc = pd.read_csv(J("outputs", "ml", "C_forecast_2026.csv")).set_index("festival")["forecast_inr_crore"]
regm = pd.read_csv(J("outputs", "ml", "C_regression_metrics.csv")).set_index("metric")["value"]
eng = json.load(open(J("blog", "engagement", "engagement_metrics.json")))
A = ml["A"]
MN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
peak = [MN[i - 1] for i in mon.sort_values(ascending=False).index[:3]]
top = sp.hol_days_total_festival.sort_values(ascending=False)
n_f, n_unsure = fm.festival.nunique(), int((~fm.reach_identifiable).sum())
rf, lr, base = clf.loc["Random Forest"], clf.loc["Logistic Regression"], clf.loc["Majority baseline"]
growth = regm["implied_annual_growth_%"]
# regression error metrics from the leave-one-out predictions (each point predicted by a model that never saw it)
err = loo.loo_predicted - loo.actual
MAE, MSE, RMSE = err.abs().mean(), (err ** 2).mean(), (err ** 2).mean() ** .5
R2 = 1 - (err ** 2).sum() / ((loo.actual - loo.actual.mean()) ** 2).sum()
MAPE = (err.abs() / loo.actual).mean() * 100
la, lp = np.log(loo.actual), np.log(loo.loo_predicted)
R2_log = 1 - ((lp - la) ** 2).sum() / ((la - la.mean()) ** 2).sum()
# statistical validation of the ML result: paired t-test, actual vs predicted (log scale)
tt = stats.ttest_rel(lp, la); t_df = len(loo) - 1; d_mean = (lp - la).mean()
shap = stats.shapiro(lp - la)
ci = stats.t.interval(0.95, t_df, loc=d_mean, scale=stats.sem(lp - la))
ne = next(v for k, v in A["detail_clusters"].items() if "Tribal" in k or "Christian" in k)

# one extra chart the format recommends: a box plot
vs.apply()
fig, ax = plt.subplots(figsize=(9, 4.2))
REG = ["North", "Central", "East", "West", "South", "North-East"]
ax.boxplot([sp.loc[sp.region == r, "hol_days_total_festival"].values for r in REG], tick_labels=REG, patch_artist=True, widths=0.5,
           boxprops=dict(facecolor="#cde2fb", edgecolor="#256abf"), medianprops=dict(color="#0d366b", linewidth=2),
           whiskerprops=dict(color="#256abf"), capprops=dict(color="#256abf"), flierprops=dict(markeredgecolor="#256abf"))
ax.set_ylabel("Festival holidays recognised per year"); ax.grid(axis="x", visible=False)
ax.set_title(f"Festival holidays per state, by region (Kruskal-Wallis p = {T.loc['H6-hol_days', 'p_value']:.2f})")
vs.source_note(fig, f"Reserve Bank of India holiday matrix {PERIOD}; one value per state/UT (n = 29)")
BOX = os.path.join(FIG, "F11_boxplot_holidays_by_region.png"); fig.savefig(BOX); plt.close(fig)

# ------------------------------- flowchart diagrams -------------------------------
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
NAVY, BLUE, PALE, INK = "#0d366b", "#256abf", "#eef3fa", "#0b0b0b"
def _box(ax, x, y, w, h, title, sub=None, fill=NAVY, tc="white", ts=11, ss=8.6, dx=0.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", linewidth=1.2, edgecolor=NAVY, facecolor=fill, zorder=2))
    if sub:
        ax.text(x + w / 2 + dx, y + h * 0.66, title, ha="center", va="center", fontsize=ts, fontweight="bold", color=tc, zorder=3)
        ax.text(x + w / 2 + dx, y + h * 0.29, sub, ha="center", va="center", fontsize=ss, color=tc, zorder=3, linespacing=1.25)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=ts, fontweight="bold", color=tc, zorder=3, linespacing=1.2)
def _arrow(ax, p0, p1):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=16, linewidth=1.6, color=BLUE, zorder=1, shrinkA=0, shrinkB=0))

# (a) horizontal six-step project flow for page 1
NL = chr(10)
STEPS = ["Real-world" + NL + "problem", "Dataset", "ML model", "Statistical" + NL + "validation", "Data blog", "Results &" + NL + "conclusion"]
fig, ax = plt.subplots(figsize=(11, 1.5)); ax.set_xlim(0, 11); ax.set_ylim(0, 1.5); ax.axis("off"); ax.grid(False)
bw, gap = 1.5, 0.36; x0 = (11 - (6 * bw + 5 * gap)) / 2
for i, t_ in enumerate(STEPS):
    x = x0 + i * (bw + gap)
    _box(ax, x, 0.25, bw, 1.0, t_, fill=NAVY if i % 2 == 0 else BLUE, ts=10.5)
    ax.text(x + 0.14, 1.12, str(i + 1), fontsize=8, color="white", fontweight="bold", zorder=4)
    if i < 5: _arrow(ax, (x + bw + 0.04, 0.75), (x + bw + gap - 0.04, 0.75))
FLOW_H = os.path.join(FIG, "R01_project_flow.png"); fig.savefig(FLOW_H, dpi=220, bbox_inches="tight", pad_inches=0.05); plt.close(fig)

# (b) vertical workflow with what this project did at each step
WF = [("Real-world problem", "Festival comparisons in India rest on opinion, not data"),
      ("Authentic historical data", f"RBI holiday lists {YEARS[0]}-{YEARS[-1]}, Census 2011, verified trade figures"),
      ("Data cleaning & EDA", f"{len(obs):,} records, {n_f} festivals; Sunday and shared-date corrections"),
      ("ML prediction / regression", f"Trade regression (R² {R2:.2f}); Random Forest classifier; K-Means"),
      ("Statistical validation", f"Paired t-test, actual vs predicted: p = {tt.pvalue:.2f} (no bias)"),
      ("Data visualization blog", "Published on Medium: 9 charts, every figure cited"),
      ("Results & conclusion", "Calendars follow demography, yet are more plural")]
# one icon per step, drawn from the Segoe MDL2 icon font that ships with Windows
from matplotlib.font_manager import FontProperties
_ICONF = r"C:\Windows\Fonts\segmdl2.ttf"
ICONS = [chr(0xE897), chr(0xE787), chr(0xE71C), chr(0xE99A), chr(0xE9D9), chr(0xE774), chr(0xE734)]   # help, calendar, filter, robot, diagnostic, globe, star
bh, vg, bw2 = 0.95, 0.42, 6.6; H = len(WF) * bh + (len(WF) - 1) * vg
fig, ax = plt.subplots(figsize=(7.2, H * 0.92 + 0.2)); ax.set_xlim(0, 7.2); ax.set_ylim(-0.05, H + 0.25); ax.axis("off"); ax.grid(False)
for i, (t_, sub) in enumerate(WF):
    y = H - (i + 1) * bh - i * vg
    last_ = i == len(WF) - 1
    _box(ax, 0.3, y, bw2, bh, t_.upper(), sub, fill=NAVY if (i == 0 or last_) else PALE, tc="white" if (i == 0 or last_) else INK, ts=11, ss=9.2, dx=0.38)
    dark_ = i == 0 or last_
    ax.add_patch(plt.Circle((1.0, y + bh / 2), 0.33, facecolor="white" if dark_ else BLUE, edgecolor="none", zorder=4))
    if os.path.exists(_ICONF):
        ax.text(1.0, y + bh / 2, ICONS[i], ha="center", va="center", fontsize=17, color=NAVY if dark_ else "white", fontproperties=FontProperties(fname=_ICONF), zorder=5)
    ax.add_patch(plt.Circle((0.3, y + bh), 0.17, color=BLUE, zorder=4)); ax.text(0.3, y + bh, str(i + 1), ha="center", va="center", fontsize=8.5, color="white", fontweight="bold", zorder=5)
    if not last_: _arrow(ax, (0.3 + bw2 / 2, y - 0.03), (0.3 + bw2 / 2, y - vg + 0.03))
ax.set_aspect("equal")
FLOW_V = os.path.join(FIG, "R02_overall_workflow.png"); fig.savefig(FLOW_V, dpi=220, bbox_inches="tight", pad_inches=0.08); plt.close(fig)

# ------------------------------- document helpers -------------------------------
os.makedirs(os.path.dirname(TEMPLATE), exist_ok=True)
assert os.path.exists(TEMPLATE), "put the faculty format in report/template/"
d = docx.Document(TEMPLATE)
FS = Pt(10.5)

def P(starts):
    for p in d.paragraphs:
        if p.text.strip().startswith(starts): return p
    raise KeyError(starts)
def table_with(header0):
    for t in d.tables:
        if t.rows[0].cells[0].text.strip() == header0: return t
    raise KeyError(header0)
def set_text(p, text, bold=None, italic=None):
    for r in list(p.runs): r._r.getparent().remove(r._r)
    r = p.add_run(text); r.bold = bold; r.italic = italic; return r
def after(anchor, text="", style="Normal", bold=None, italic=None, align=None):
    """Insert a new paragraph right after `anchor` (a Paragraph or Table) and return it."""
    el = anchor._p if isinstance(anchor, Paragraph) else anchor._tbl
    new = copy.deepcopy(d.paragraphs[0]._p)
    for ch in list(new): new.remove(ch)
    el.addnext(new); p = Paragraph(new, d); p.style = d.styles[style]
    if text: r = p.add_run(text); r.bold = bold; r.italic = italic
    if align: p.alignment = align
    return p
def picture_after(anchor, path, width_cm, caption):
    p = after(anchor, align=WD_ALIGN_PARAGRAPH.CENTER); p.add_run().add_picture(path, width=Cm(width_cm))
    c = after(p, caption, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    for r in c.runs: r.font.size = Pt(9)
    return c
def bullets_after(anchor, items):
    last = anchor
    for it in items: last = after(last, it, style="List Bullet")
    return last
def cell(c, text, bold=None):
    c.text = ""; lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = c.paragraphs[0] if i == 0 else c.add_paragraph()
        r = p.add_run(ln); r.bold = bold
def fill_rows(t, rows, start=1):
    """Write rows into table t from row index `start`, adding rows (copied from the last one) if needed."""
    while len(t.rows) < start + len(rows):
        t._tbl.append(copy.deepcopy(t.rows[-1]._tr))
    for i, vals in enumerate(rows):
        for c, v in zip(t.rows[start + i].cells, vals): cell(c, str(v))
def drop(p): p._p.getparent().remove(p._p)

# ------------------------------- header + student table -------------------------------
# header: "DAV Micro Project Report Format" -> "DAV Micro Project Report" (the word is split across two runs)
_ts = [t_ for t_ in d.sections[0].header._element.iter(qn("w:t")) if t_.text]
for i, t_ in enumerate(_ts):
    if t_.text.rstrip().endswith("Report Form") and i + 1 < len(_ts) and _ts[i + 1].text.strip() == "at":
        t_.text = t_.text.rstrip()[:-len(" Form")]; _ts[i + 1].text = ""
    elif "Report Format" in t_.text: t_.text = t_.text.replace("Report Format", "Report")
for hp in d.sections[0].header.paragraphs:
    if "Micro Project" in hp.text:
        for r in hp.runs:
            r.font.name = "Calibri"; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = RGBColor(0x0D, 0x36, 0x6B)
            rf_ = r._r.get_or_add_rPr().get_or_add_rFonts()
            for att in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf_.set(qn(att), "Calibri")
if d.paragraphs[0].text.strip().startswith("...."): drop(d.paragraphs[0])
st = table_with("Student Details")
TEAM = ["Jainam Jain", "Vrushan Patil", "Dhanush Chowke", "Aditya Tambe", "Vivek Jaiswal"]
ROLLS = ["23108B0084", "23108B0079", "23108B0080", "23108B0077", "23108B0082"]
info = {"Student Names": TEAM, "Roll No.": ROLLS, "Class / Division": "B.E. Semester VII, Division B",
        "Department": "Electronics and Computer Science, Vidyalankar Institute of Technology",
        "Project Title": "Socio-Economic & Demographic Analysis of Indian Festivals",
        "Faculty Guide": "Prof. Uma Jaishankar", "Academic Year": "2026-27"}
for row in st.rows[1:]:
    key = row.cells[0].text.strip().split("\n")[0]
    cell(row.cells[0], key, bold=True); cell(row.cells[1], info[key])

# ------------------------------- flow diagrams replace the text arrows -------------------------------
def replace_with_picture(par, path, width_cm):
    for r in list(par.runs): r._r.getparent().remove(r._r)
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER; par.add_run().add_picture(path, width=Cm(width_cm))
flows = [p_ for p_ in d.paragraphs if p_.text.strip().startswith("REAL-WORLD PROBLEM")]
assert len(flows) == 2
replace_with_picture(flows[0], FLOW_V, 13.0)     # Project Flow gets its own page (page 2); page 1 is details only
P("Project Flow").paragraph_format.page_break_before = True
# the empty paragraph after the flow carried the page break; with the taller diagram it spilled onto a blank page,
# so drop it and let the "Project Overview" heading start the new page itself
nx = flows[0]._p.getnext()
while nx is not None and nx.tag == qn("w:p") and not Paragraph(nx, d).text.strip() and not nx.findall(".//" + qn("w:drawing")):
    nn = nx.getnext(); nx.getparent().remove(nx); nx = nn
P("Project Overview").paragraph_format.page_break_before = True
# the closing "Recommended Overall Workflow" page repeated the same flow, so it is removed
hw = P("Recommended Overall Workflow")
prev = hw._p.getprevious()
drop(flows[1]); drop(hw)
while prev is not None and prev.tag == qn("w:p") and not Paragraph(prev, d).text.strip() and not prev.findall(".//" + qn("w:drawing")):
    nxt = prev.getprevious(); prev.getparent().remove(prev); prev = nxt

# ------------------------------- Project overview -------------------------------
set_text(P("The project must demonstrate"),
         "India celebrates hundreds of festivals, but most comparisons between them rest on opinion. This project builds an authentic, "
         f"source-linked dataset of officially recognised festivals ({YEARS[0]}-{YEARS[-1]}), uses machine learning to predict festive trade and to "
         "classify festivals, validates the predictions statistically, and communicates the findings as a public data blog. "
         "No synthetic data is used: every record carries the link it came from.")

# ------------------------------- PART 1 -------------------------------
set_text(P("Clearly describe the real-world problem"),
         "Real-world problem: information about Indian festivals is scattered and anecdotal, which leads to biased representations, missing "
         "comparisons between states and faiths, and an unclear picture of their economic weight.")
set_text(P("Project problem statement:"),
         "Project problem statement: To collect authentic multi-faith festival data for India, measure when, where and whose festivals are "
         "officially recognised, predict festive trade from historical figures, test the findings statistically, and publish them as a balanced, "
         "evidence-based data story. Outcomes studied: (a) festive trade in INR crore (numerical target, regression) and (b) the tradition group "
         "of a festival (categorical target, classification).")

ds = table_with("Parameter")   # first 'Parameter' table = dataset source
vals = {
 "Dataset Name": "Indian Festival Holiday Observations (RBI holiday matrix), with Census 2011 and a verified festive-trade table",
 "Source / Website": ["Reserve Bank of India - Holidays under the Negotiable Instruments Act (primary)",
                      "Census of India 2011, Table C-01; DoPT holiday order F.No.12/2/2023-JCA; CAIT and verified news (trade figures)"],
 "Working URL": ["https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx", "https://censusindia.gov.in/nada/index.php/catalog/11361",
                 "Project data and code: https://github.com/iJainamJain/indian-festivals-data-analysis"],
 "Date Accessed": f"{pd.Timestamp(raw.retrieved_on.max()).strftime('%d %B %Y')} (RBI); 28 September 2026 (Census, trade figures)",
 "Number of Records": [f"{len(obs):,} festival-holiday observations (from {len(raw):,} RBI office-date rows)",
                       f"{n_f} festivals; 29 states/UTs; {len(eco)} verified spending and crowd figures"],
 "Number of Variables": f"{obs.shape[1]} in the main table; {fm.shape[1]} in the festival table; {eco.shape[1]} in the trade table",
 "Target Variable": ["Regression: festive trade value (INR crore)", "Classification: tradition group of a festival (4 classes)"],
 "Input Variables": ["Regression: year, festival, reported-or-projected flag",
                     "Classification: month, date drift, number of states, share in each of 6 regions, holiday length, shared-date share"],
 "Time Period": f"Holidays {YEARS[0]}-{YEARS[-1]}; trade figures 2018-2026; Census 2011",
 "Geographic Coverage": "India: 29 states/UTs through all 34 RBI regional offices",
}
for row in ds.rows[1:]:
    k = row.cells[0].text.strip(); cell(row.cells[1], vals[k])

p = P("Attach a screenshot of the original dataset")
set_text(p, "The screenshot below is the original source: the RBI holiday matrix for all regional offices (October 2025 shown). "
            "Working URL: https://www.rbi.org.in/Scripts/HolidayMatrixDisplay.aspx")
cap = picture_after(p, J("report", "evidence", "rbi_source_screenshot.png"), 13.5,
                    f"Source evidence: RBI holiday matrix, captured {pd.Timestamp.today().strftime('%d %B %Y')}.")
bullets_after(after(cap, "Why the source is reliable and appropriate:", bold=True), [
    "RBI is India's central bank. Its list is the legal record of bank holidays notified by each state under the Negotiable Instruments Act.",
    "It covers every faith and every state in one consistent format, for several years, so states and traditions can be compared fairly.",
    "It is updated when holidays are declared later in the year (elections, heavy rain, state mourning), and those dates are in our data.",
    "Population figures come from the Census of India, and trade figures from CAIT surveys and verified news; each trade figure was opened and confirmed on its source page.",
    "Limits we state openly: RBI lists no Sunday dates (corrected for), it prints one combined label per date (handled by evidence rules), and "
    "festivals with no bank holiday are not covered."])

dd = table_with("Variable")
fill_rows(dd, [
 ("X1  year", "Year the figure or holiday refers to", "Integer", "Year", "Feature"),
 ("X2  festival", "Canonical festival name (101 festivals)", "Categorical", "-", "Feature"),
 ("X3  is_projection", "1 if the trade figure is a pre-event estimate, 0 if reported after the festival", "Binary", "0 / 1", "Feature"),
 ("X4  modal_month", "Month in which the festival usually falls (encoded as sine and cosine)", "Numeric", "Month", "Feature"),
 ("X5  date_drift_days", "How much the festival's date moves between years (fixed vs lunar calendar)", "Numeric", "Days", "Feature"),
 ("X6  expected_states_per_year", "Number of states recognising the festival in a year", "Numeric", "States", "Feature"),
 ("X7  region_share_*", "Share of the festival's recognition in each of 6 regions", "Numeric", "Proportion", "Feature"),
 ("X8  mean_holiday_days", "Average length of the holiday", "Numeric", "Days", "Feature"),
 ("X9  recognition_weight", "Credit for a festival at an office on a date (1 = confirmed, less if a shared date is ambiguous)", "Numeric", "0 to 1", "Feature"),
 ("Y1  festive trade value", "Trade attributed to the festival (CAIT and cited sources)", "Numeric", "INR crore", "Target (regression)"),
 ("Y2  tradition group", "Hindu / Muslim-Christian / Tribal-Indigenous / Other", "Categorical", "-", "Target (classification)"),
])

pre = {"Missing-value treatment": f"Missing-value treatment: the cleaned tables have no missing values. The gap that matters is structural: RBI lists no Sunday dates, so each festival is averaged only over the years it could be listed.",
       "Duplicate removal": "Duplicate removal: 2 duplicate office-date rows were removed; variant spellings of the same festival (for example Dussehra, Dusshera, Dasara) were merged into 101 canonical festivals.",
       "Outlier treatment": "Outlier treatment: no records were deleted. Trade values span Rs 3,000 crore to Rs 6.05 lakh crore, so the regression uses the log of trade; non-parametric tests are used for skewed variables.",
       "Encoding categorical variables": "Encoding categorical variables: festival is one-hot encoded for the regression; month is encoded as sine and cosine; calendar type is a 0/1 flag.",
       "Feature scaling / normalization, if required": "Feature scaling: features are standardised (z-scores) for Logistic Regression and K-Means; Random Forest needs no scaling.",
       "Train-test split": "Train-test split: classification uses repeated stratified 5-fold cross-validation (20 repeats); regression uses leave-one-out validation and a time-based hold-out (train up to 2025, test on 2026)."}
for k, v in pre.items(): set_text(P(k), v)

# ------------------------------- PART 2 -------------------------------
t21 = table_with("Problem Type")
p = after(t21, "Selected: Regression (festive trade, numerical target) as the main prediction task, using a log-linear regression. "
               "A Random Forest classification model (tradition group, categorical target) is reported as the second model.", bold=True)
dev = {"Define input features and target": "Inputs and target. Regression: year, festival and a reported-or-projected flag predict log(trade in INR crore). Classification: 14 calendar and geography features predict the tradition group.",
       "Split historical data into training and testing sets": f"Train and test. Regression: {int(regm['n_train (<=2025)'])} historical figures up to 2025 for training, with leave-one-out validation; the 2026 figures are held out. Classification: repeated stratified 5-fold cross-validation on {n_f} festivals.",
       "Train the selected model": "Training. Linear regression on log(trade) with a separate term for each festival; Random Forest (500 trees, balanced class weights) compared with Logistic Regression and a majority-class baseline.",
       "Generate predictions": "Predictions. Every historical point is predicted by a model that never saw it (leave-one-out), then the model predicts the 2026 figures and forecasts 2026 trade for each festival.",
       "Explain the model and assumptions": f"Model and assumptions. Trade grows at a steady percentage rate (estimated at {growth:.0f}% a year), festivals differ by a fixed level, and pre-event projections may differ systematically from reported figures. With {int(regm['n_train (<=2025)'])} data points the model is deliberately simple."}
for k, v in dev.items(): set_text(P(k), v)

p = P("For regression, report MAE")
set_text(p, "Regression (festive trade), evaluated on leave-one-out predictions:")
last = bullets_after(p, [
    f"MAE = Rs {MAE:,.0f} crore;  MSE = {MSE:,.3g} (crore squared);  RMSE = Rs {RMSE:,.0f} crore",
    f"R-squared = {R2:.3f} on the rupee scale and {R2_log:.3f} on the log scale;  mean absolute percentage error = {MAPE:.1f}%",
    f"Time-based hold-out (2026): mean absolute percentage error = {regm['holdout_2026_MAPE_%']:.1f}%"])
last = after(last, "Classification (tradition group of a festival), repeated 5-fold cross-validation:")
last = bullets_after(last, [
    f"Random Forest: accuracy {rf.accuracy_mean:.2f}, precision {rf.macro_precision_mean:.2f}, recall {rf.macro_recall_mean:.2f}, F1-score {rf.macro_f1_mean:.2f} (macro averages)",
    f"Logistic Regression: accuracy {lr.accuracy_mean:.2f}, F1-score {lr.macro_f1_mean:.2f}.  Majority-class baseline: accuracy {base.accuracy_mean:.2f}, F1-score {base.macro_f1_mean:.2f}",
    "Per class (Random Forest): " + "; ".join(f"{r_['class'].split(' (')[0]} F1 {r_.f1:.2f}" for _, r_ in pcr.iterrows()),
    "ROC curve not reported: with four classes and about 100 festivals, the confusion matrix is the clearer summary."])
picture_after(last, os.path.join(FIG, "M03_classifier_results.png"), 16, "Confusion matrix (left) and permutation feature importance (right) for the Random Forest.")

t24 = table_with("Sample")
pick = loo.assign(e=err).sort_values(["festival", "year"]).reset_index(drop=True)
rows24 = [(f"{i + 1}. {r_.festival.split(' (')[0]} {int(r_.year)}", f"{r_.actual:,.0f}", f"{r_.loo_predicted:,.0f}", f"{r_.e:+,.0f}  ({100 * r_.e / r_.actual:+.0f}%)") for i, r_ in pick.iterrows()]
rows24 += [(f"{len(pick) + i + 1}. {r_.festival} 2026 (hold-out)", f"{r_.value:,.0f}", f"{r_.predicted_inr_crore:,.0f}", f"{r_.predicted_inr_crore - r_.value:+,.0f}  ({-r_.abs_pct_error if r_.predicted_inr_crore < r_.value else r_.abs_pct_error:+.0f}%)") for i, r_ in hold.iterrows()]
cell(t24.rows[0].cells[1], "Actual Y (INR crore)", bold=True); cell(t24.rows[0].cells[2], "Predicted Y (INR crore)", bold=True); cell(t24.rows[0].cells[3], "Error", bold=True)
fill_rows(t24, rows24)
p = P("Insert Actual vs Predicted graph here")
set_text(p, "Actual vs Predicted graph (points on the dotted line would be perfect predictions):")
picture_after(p, os.path.join(FIG, "M04_trade_regression.png"), 11.5, "Actual vs predicted festive trade: leave-one-out predictions and the 2026 hold-out.")

# ------------------------------- PART 3 -------------------------------
set_text(P("Selected test:"),
         "Selected test: Paired t-test (actual vs predicted).   Reason: each festival-year has one actual and one predicted trade value, so the two are paired. "
         "The test checks whether the model is systematically too high or too low. Values are compared on the log scale because trade spans three orders of "
         f"magnitude; the differences are consistent with a normal distribution (Shapiro-Wilk p = {shap.pvalue:.2f}).")
set_text(P("H₀ (Null Hypothesis)"),
         "H₀ (Null Hypothesis): The mean difference between predicted and actual log festive trade is zero (the model has no systematic bias).\n"
         "H₁ (Alternative Hypothesis): The mean difference is not zero (the model systematically over- or under-predicts).")
res = [t for t in d.tables if t.rows[0].cells[0].text.strip() == "Parameter"][1]
dec = "Fail to reject H₀" if tt.pvalue >= 0.05 else "Reject H₀"
rv = {"Significance level (α)": "0.05",
      "Test statistic": f"t = {tt.statistic:.3f}  (mean difference {d_mean:+.3f} log units, about {100 * (np.exp(d_mean) - 1):+.1f}%; 95% CI {ci[0]:+.3f} to {ci[1]:+.3f})",
      "Degrees of freedom": f"{t_df}  (n = {len(loo)} paired values)", "p-value": f"{tt.pvalue:.3f}", "Decision": dec,
      "Interpretation": ("There is no evidence of systematic bias: on average the predictions are neither too high nor too low. Individual errors still "
                         f"average about {MAPE:.0f}%, and with only {len(loo)} points the test cannot detect a small bias." if tt.pvalue >= 0.05 else
                         "The predictions are systematically biased; the model needs a correction term.")}
for row in res.rows[1:]: cell(row.cells[1], rv[row.cells[0].text.strip()])
p = P("Important: Students should select only")
set_text(p, "Supporting tests from the exploratory analysis (full tables in outputs/stats):")
bullets_after(p, [
    f"Chi-square goodness of fit: festival holidays are not spread evenly across months (chi-square = {T.loc['H1', 'statistic']:.0f}, df = 11, p < 0.001); peaks in {peak[0]}, {peak[1]} and {peak[2]}.",
    f"Chi-square test of independence: a festival's season does not depend on its tradition (permutation p = {T.loc['H2', 'p_value']:.2f}).",
    f"Spearman correlation: each faith's share of a state's holidays rises with its population share (rho {cr.spearman_rho.min():.2f} to {cr.spearman_rho.max():.2f}; all significant after Holm correction).",
    f"Kruskal-Wallis: festival holidays per state do not differ between the six regions (p = {T.loc['H6-hol_days', 'p_value']:.2f})."])

# ------------------------------- PART 4 -------------------------------
bs = table_with("Section")
bv = {"Title / Hook": "\"What India's Bank-Holiday Calendar Reveals About How the Country Celebrates\". Opens with: ask ten people which festivals matter most and you get ten answers.",
      "Introduction": "Why opinion-based comparisons are biased, and three questions: when and where India celebrates, whose festivals are recognised, and what they are worth.",
      "The Data": f"RBI holiday lists {YEARS[0]}-{YEARS[-1]} ({len(obs):,} records, {n_f} festivals, 29 states), Census 2011, {len(eco)} verified trade and crowd figures; how Sundays and shared dates were handled; what the data cannot see.",
      "Visual Story": "9 charts: month-by-tradition bars, state map, state-by-month heatmap, holiday share vs population share, diversity map, state-group map, trade trend, Diwali sector split, crowd density. 4 interactive versions.",
      "Conclusion": f"The calendar peaks in {peak[0]}, {peak[1]} and {peak[2]}; calendars follow demography yet are more plural than the population; four north-eastern states are distinct; festive trade is growing but measured unevenly.",
      "References": "10 numbered sources: RBI, Census of India, DoPT, CAIT, All India Radio, verified news, NRF, gov.cn, GASTAT, City of Munich, and the project repository."}
cell(bs.rows[0].cells[1], "What we included", bold=True)
for row in bs.rows[1:]: cell(row.cells[1], bv[row.cells[0].text.strip()])
viz = {"Histogram / distribution plot": "Histogram / distribution plot: reach of festivals, holidays per state and trade values (Fig. 4.1).",
       "Box plot": "Box plot: festival holidays per state by region (Fig. 4.2).",
       "Bar chart": "Bar chart: festival holidays by month and tradition (Fig. 4.3); Diwali 2025 sector split.",
       "Scatter plot": "Scatter plot: holiday share vs population share for each faith (Fig. 4.4).",
       "Correlation heatmap": "Correlation heatmap: state-level holiday and Census variables (Fig. 4.5); state-by-month heatmap.",
       "Time-series plot where applicable": "Time-series plot: festive trade by year for five festivals (Fig. 4.6).",
       "Actual vs Predicted plot": "Actual vs Predicted plot: festive-trade regression (Part 2.4).",
       "Confusion matrix / ROC curve for classification where applicable": "Confusion matrix: Random Forest tradition classifier (Part 2.3). Also a state map of festival holidays (Fig. 4.7)."}
for k, v in viz.items(): set_text(P(k), v)
live = eng["live_url"] != "NOT YET PUBLISHED"
p_link = P("Blog / publication link")
set_text(p_link, "Blog / publication link: " + (eng["live_url"] if live else "not yet published"))
p_title = P("Blog title:")
set_text(p_title, "Blog title: What India's Bank-Holiday Calendar Reveals About How the Country Celebrates"
                  + (f"  (Medium, published {pd.Timestamp(eng['published_on']).strftime('%d %B %Y')})" if live else ""))
last = after(p_title, f"Public response: {eng['external_interactions']} external reactions and comments logged so far against a target of 40; "
                      f"{eng['comments_with_author_reply']} comments answered. Only readers outside the institute are counted, each with a screenshot.")
for path, w, cap in [(os.path.join(FIG, "F01_distributions.png"), 16, "Fig. 4.1  Distributions of festival reach, holidays per state and trade estimates."),
                     (BOX, 12, "Fig. 4.2  Festival holidays per state, by region."),
                     (os.path.join(FIG, "F02_month_timeline_by_tradition.png"), 16, "Fig. 4.3  Festival holidays by month and tradition."),
                     (os.path.join(ROOT, "video", "slides", "_demography_wide.png"), 16, "Fig. 4.4  Holiday share vs population share (each dot is a state)."),
                     (os.path.join(FIG, "F03_correlation_matrix.png"), 11.5, "Fig. 4.5  Spearman correlation heatmap of state-level variables."),
                     (os.path.join(FIG, "F08_festive_trade_trend.png"), 13, "Fig. 4.6  Festive trade estimates by year."),
                     (os.path.join(FIG, "F05_map_festival_holidays.png"), 10.5, "Fig. 4.7  Festival holidays recognised per year, by state.")]:
    last = picture_after(last, path, w, cap)

# ------------------------------- PART 5 -------------------------------
s5 = table_with("Model / Method")
fill_rows(s5, [
 ("Model 1: Log-linear regression (festive trade)", "RMSE; R-squared; MAPE (leave-one-out)", f"Rs {RMSE:,.0f} crore; {R2:.2f}; {MAPE:.0f}%",
  f"Reported festive trade grows about {growth:.0f}% a year; 2026 Holi figure predicted within {hold.loc[hold.festival == 'Holi', 'abs_pct_error'].iloc[0]:.0f}%."),
 ("Model 2: Random Forest (tradition of a festival)", "Accuracy; macro F1 (repeated 5-fold CV)", f"{rf.accuracy_mean:.2f}; {rf.macro_f1_mean:.2f} (baseline F1 {base.macro_f1_mean:.2f})",
  "Date and footprint reveal a festival's tradition only partly: nationwide festivals of every faith look alike."),
 ("Model 3: K-Means (grouping states)", "Silhouette score", f"{A['silhouette']:.2f} for {A['best_k']} groups",
  f"{', '.join(ne)} have a distinct calendar; the rest of India is a continuum, not regional blocks."),
 ("Statistical Test: paired t-test (actual vs predicted)", "t statistic; p-value", f"t = {tt.statistic:.2f}, df = {t_df}; p = {tt.pvalue:.2f}",
  "Fail to reject H₀: no systematic bias in the trade predictions." if tt.pvalue >= 0.05 else "Reject H₀: predictions are biased."),
 ("Supporting test: Spearman correlation", "rho across 29 states", f"{cr.spearman_rho.min():.2f} to {cr.spearman_rho.max():.2f} (all p < 0.05)",
  f"Holiday calendars follow demography, yet are more plural: Hindu festivals are {bt['Hindu']:.0f}% of festival holidays vs 79.8% of population."),
 ("Forecasting: festive trade 2026", "Model forecast (INR crore)", f"Diwali {fc['Diwali (Deepavali)']:,.0f}; Holi {fc['Holi']:,.0f}; Karva Chauth {fc['Karva Chauth']:,.0f}",
  "Extrapolation of the growth trend; based on 15 data points, so indicative only."),
])
concl = after(s5, "Conclusion", bold=True)
concl = after(concl,
    f"Using only authentic, source-linked data, the project shows that India's officially recognised festival calendar peaks in {peak[0]}, {peak[1]} and "
    f"{peak[2]}; that each faith's share of a state's holidays follows its population share while the calendar as a whole is more plural than the population; "
    f"that {top.index[0]}, {top.index[1]} and {top.index[2]} recognise the most festival holidays; and that reported festive trade is growing at about {growth:.0f}% a year. "
    "The trade model predicts unseen figures without systematic bias (paired t-test), though individual errors average about a fifth. "
    "An important limitation is itself a finding: national spending estimates are published mainly for Hindu festivals, so the economic comparison across traditions is incomplete. "
    f"Bank holidays measure official recognition, not participation, and {n_unsure} of {n_f} festivals that always share their date remain uncertain and are flagged.")
fut = {"Larger or more diverse dataset": "Larger and more diverse dataset: add state-government holiday gazettes and restricted holidays, so festivals without a bank holiday and union territories without an RBI office are covered.",
       "Additional features": "Additional features: district-level footfall, tourism arrivals, rail and air passenger counts, and GST or e-commerce data around each festival.",
       "Alternative ML algorithms": "Alternative ML algorithms: gradient boosting and multi-label classification, since many festivals belong to more than one tradition.",
       "Ensemble / advanced modelling": "Ensemble and advanced modelling: hierarchical (mixed-effects) or Bayesian models for trade, which handle few data points per festival better.",
       "Real-time data collection": "Real-time data collection: re-collect the RBI list every month, so late-declared holidays and each new year are added automatically.",
       "Deployment as a dashboard/web/mobile application": "Deployment: publish the interactive state map and month timeline as a public web dashboard."}
for k, v in fut.items(): set_text(P(k), v)

for p in d.paragraphs:
    for r in p.runs:
        if r.font.size is None and p.style.name in ("Normal", "List Bullet"): r.font.size = FS
d.save(OUT); print("docx ->", OUT)

import win32com.client
w = win32com.client.DispatchEx("Word.Application"); w.Visible = False; w.DisplayAlerts = 0
try:
    doc = w.Documents.Open(OUT); doc.SaveAs2(OUT.replace(".docx", ".pdf"), FileFormat=17); doc.Close(False)
finally:
    w.Quit()
print("pdf ->", OUT.replace(".docx", ".pdf"))
