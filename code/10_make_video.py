"""Task 5 - Final synthesis video (1920x1080 MP4, narrated in Indian English).

Pipeline: slides are HTML/CSS pages filled with real numbers from outputs/ and rendered to PNG with
Playwright (MS Edge) -> narration synthesised with Microsoft's online neural voice (edge-tts, en-IN) ->
ffmpeg (H.264 + AAC, short fade between slides).
The blog-reception slide reads blog/engagement/engagement_metrics.json, so re-run this script after the
engagement log is updated to produce the final cut.
Output: video/Indian_Festivals_Project_Report.mp4 (+ slides/*.png, audio/*.mp3, narration_script.md)
"""
import os, json, subprocess, asyncio, html as _html
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import edge_tts
from playwright.sync_api import sync_playwright
import viz_style as vs

VOICE = "en-IN-PrabhatNeural"      # Indian English, male.  Female alternative: "en-IN-NeerjaNeural"
RATE = "-4%"
vs.apply()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
V = J("video"); S, A = J("video", "slides"), J("video", "audio")
for d in (S, A): os.makedirs(d, exist_ok=True)
FIG = J("outputs", "figures")
ml = json.load(open(J("outputs", "ml", "ml_summary.json")))
T = pd.read_csv(J("outputs", "stats", "T6_hypothesis_tests.csv")).set_index("id")
eng = json.load(open(J("blog", "engagement", "engagement_metrics.json")))
meta = json.load(open(J("blog", "engagement", "post_meta.json"), encoding="utf-8"))
fm = pd.read_csv(J("data", "processed", "festival_master.csv"))
sp = pd.read_csv(J("data", "processed", "state_profile.csv")).set_index("state")
eco = pd.read_csv(J("data", "processed", "economic_footfall_clean.csv"))
obs = pd.read_csv(J("data", "processed", "festival_observations.csv"))
raw = pd.read_csv(J("data", "raw", "rbi_holiday_matrix_raw.csv"))
cr = pd.read_csv(J("outputs", "stats", "T5_holiday_vs_population_share.csv")).set_index("faith")
imp = pd.read_csv(J("outputs", "ml", "B_permutation_importance.csv"), index_col=0).iloc[:, 0].sort_values(ascending=False)
A_, B_, C_ = ml["A"], ml["B"]["metrics"], ml["C"]
growth = T.loc["H9", "interpretation"].split("growth ")[1].split("%")[0].split(".")[0]
TEAM = ["Jainam Jain", "Vrushan Patil", "Dhanush Chowke", "Aditya Tambe", "Vivek Jaiswal"]
# data-accuracy facts, computed from the raw scrape
_dts = pd.to_datetime(raw.drop_duplicates("date").date)
n_sunday = int((_dts.dt.dayofweek == 6).sum())
n_adhoc = int(raw[raw.rbi_holiday_description.str.contains("Demise|rains|respect|Consecration|Election|Poll|Cyclone", case=False, na=False)].date.nunique())
top3 = sp.hol_days_total_festival.sort_values(ascending=False).head(3)
low3 = sp.hol_days_total_festival.sort_values().head(3)
live = eng["live_url"] != "NOT YET PUBLISHED"
pub = pd.Timestamp(eng["published_on"]).strftime("%d %b %Y") if live else ""

# ---- a wide (16:9-friendly) version of the demography chart, for the video only ----
fig, axes = plt.subplots(1, 3, figsize=(16, 5.6))
for ax, (faith, h, c) in zip(axes, [("Hindu", "hol_share_hindu", "census_pct_hindu"), ("Muslim", "hol_share_muslim", "census_pct_muslim"),
                                     ("Christian", "hol_share_christian", "census_pct_christian")]):
    col = vs.TRAD_COLOR[faith]
    ax.scatter(sp[c], sp[h], s=110, color=col, edgecolor=vs.SURFACE, linewidth=1.8, zorder=3)
    k_, b_ = np.polyfit(sp[c], sp[h], 1); xx = np.linspace(0, sp[c].max() * 1.03, 50)
    ax.plot(xx, k_ * xx + b_, color=col, lw=1.6, ls="--", alpha=.75)
    ax.set_title(f"{faith}:  rho = {cr.loc[faith, 'spearman_rho']:.2f}", fontsize=19)
    ax.set_xlabel("Share of state population, %", fontsize=15); ax.tick_params(labelsize=13)
axes[0].set_ylabel("Share of festival holidays, %", fontsize=15)
fig.tight_layout(); fig.savefig(os.path.join(S, "_demography_wide.png"), dpi=130); plt.close(fig)

# ------------------------------------ slide templates ------------------------------------
CSS = """
*{box-sizing:border-box} body{margin:0;background:#fcfcfb;font-family:'Segoe UI',Arial,sans-serif;color:#0b0b0b}
.slide{width:1920px;height:1080px;position:relative;overflow:hidden;padding:84px 100px 0 120px}
.bar{position:absolute;left:0;top:0;bottom:0;width:26px;background:#0d366b}
.kicker{font-size:25px;letter-spacing:4px;text-transform:uppercase;color:#256abf;font-weight:600}
h1{font-size:60px;line-height:1.12;margin:12px 0 0;font-weight:700;max-width:1640px}
.lede{font-size:31px;color:#52514e;margin-top:14px;max-width:1560px;line-height:1.35}
.foot{position:absolute;left:120px;right:100px;bottom:34px;display:flex;justify-content:space-between;font-size:19px;color:#52514e}
.prog{position:absolute;left:26px;bottom:0;height:8px;background:#2a78d6}
.grid{display:grid;gap:56px;margin-top:38px;align-items:center}
.chart img{width:100%;max-height:690px;object-fit:contain;display:block}
.pts{display:flex;flex-direction:column;gap:30px}
.pt{border-left:6px solid #2a78d6;padding:4px 0 4px 24px}
.pt b{display:block;font-size:54px;line-height:1.05;color:#0d366b;font-weight:700}
.pt span{font-size:27px;color:#0b0b0b;line-height:1.3;display:block;margin-top:6px}
.tiles{display:grid;gap:28px;margin-top:46px}
.tile{background:#eef3fa;border-radius:14px;padding:30px 32px}
.tile b{display:block;font-size:76px;color:#0d366b;line-height:1}
.tile span{display:block;font-size:26px;margin-top:12px;color:#0b0b0b;line-height:1.3}
.tiles.sm{margin-top:18px;gap:22px} .tiles.sm .tile{padding:18px 26px} .tiles.sm .tile b{font-size:46px} .tiles.sm .tile span{font-size:22px;margin-top:6px}
ul.big{font-size:33px;line-height:1.4;margin:40px 0 0;padding-left:0;list-style:none;max-width:1560px}
ul.big li{margin-bottom:26px;padding-left:44px;position:relative} ul.big li:before{content:'';position:absolute;left:0;top:17px;width:18px;height:18px;border-radius:50%;background:#2a78d6}
.two{display:grid;grid-template-columns:1fr 1fr;gap:44px;margin-top:40px}
.card{border-radius:14px;padding:30px 34px} .card h3{margin:0 0 14px;font-size:31px} .card li{font-size:26px;line-height:1.35;margin-bottom:11px} .card ul{margin:0;padding-left:28px}
.good{background:#e6f5ec} .good h3{color:#0b5d2a} .warn{background:#fdf1d8} .warn h3{color:#7a4b00}
.src{font-size:20px;color:#52514e;margin-top:14px}
.hbar{display:grid;grid-template-columns:330px 1fr;align-items:center;gap:16px;font-size:24px;margin-bottom:13px}
.hbar i{display:block;height:26px;background:#2a78d6;border-radius:0 5px 5px 0}
.title{background:#0d366b;color:#fff;padding:230px 130px 0} .title .kicker{color:#9ec5f4} .title h1{font-size:86px;max-width:1500px}
.title .lede{color:#cde2fb;font-size:36px} .names{margin-top:70px;font-size:33px;line-height:1.6} .names small{display:block;font-size:25px;color:#9ec5f4;margin-top:16px}
"""
N_SLIDES = 13
def page(i, kicker, title, body, lede="", cls=""):
    foot = "" if cls == "title" else (f'<div class="foot"><span>{" &nbsp;|&nbsp; ".join(TEAM)} &nbsp;|&nbsp; B.E. ECS, VIT</span><span>{i} / {N_SLIDES}</span></div>'
                                      f'<div class="prog" style="width:{1894 * i / N_SLIDES:.0f}px"></div>')
    bar = "" if cls == "title" else '<div class="bar"></div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="slide {cls}">{bar}'
            f'<div class="kicker">{kicker}</div><h1>{title}</h1>{f"<div class=lede>{lede}</div>" if lede else ""}{body}{foot}</div></body></html>')
def img(f, folder=FIG): return "file:///" + os.path.join(folder, f).replace("\\", "/").replace(" ", "%20")
def chart(f, pts, cols="1.62fr 1fr", folder=FIG):
    return (f'<div class="grid" style="grid-template-columns:{cols}"><div class="chart"><img src="{img(f, folder)}"></div><div class="pts">'
            + "".join(f'<div class="pt"><b>{b}</b><span>{s}</span></div>' for b, s in pts) + "</div></div>")
def tiles(items, n=4, small=False):
    return f'<div class="tiles{" sm" if small else ""}" style="grid-template-columns:repeat({n},1fr)">' + "".join(f'<div class="tile"><b>{b}</b><span>{s}</span></div>' for b, s in items) + "</div>"

NICE = {"region_share_North-East": "Presence in the North-East", "share_shared_date": "Shares its date with other holidays", "month_cos": "Time of year (winter vs summer)",
        "region_share_South": "Presence in the South", "region_share_East": "Presence in the East", "date_drift_days": "How much the date moves",
        "month_sin": "Time of year (spring vs autumn)", "region_share_North": "Presence in the North", "region_share_West": "Presence in the West",
        "log_expected_states": "Number of states observing"}
bars = "".join(f'<div class="hbar"><span>{NICE.get(k, k)}</span><i style="width:{100 * v / imp.iloc[0]:.0f}%"></i></div>' for k, v in imp.head(6).items())

SL = [
 dict(html=page(1, "Data Analytics &amp; Visualization &middot; Mini Project", "What India's Holiday Calendar Reveals",
                f'<div class="names">{" &nbsp;&middot;&nbsp; ".join(TEAM)}<small>B.E. Semester VII, Electronics &amp; Computer Science &middot; Vidyalankar Institute of Technology &middot; Guide: Prof. Uma Jaishankar</small></div>',
                "Festivals, demography and the economics of celebration, measured from official data", "title"),
      say=f"Hello. We are {', '.join(TEAM[:-1])} and {TEAM[-1]}. This video summarises our data analytics project on the socio-economic and demographic patterns of Indian festivals. "
          "We will cover the dataset, the statistics, the machine learning models, and our public blog."),
 dict(html=page(2, "01 &middot; Motivation", "Festival comparisons usually rest on opinion, not data",
                '<ul class="big"><li>Information about festivals is scattered and anecdotal, so comparisons are easily biased towards whatever is familiar.</li>'
                '<li>We wanted a secular, evidence-only picture: <b>when</b>, <b>where</b> and <b>whose</b> festivals are officially recognised, and what they are worth.</li>'
                '<li>One strict rule: <b>zero synthetic data</b>. Every record carries the link it came from.</li></ul>'),
      say="India celebrates hundreds of festivals, but most information about them is scattered and anecdotal. That makes biased comparisons easy. "
          "Our goal was an evidence-only picture: when and where festivals are officially recognised, whose festivals they are, and what they are worth economically. "
          "We followed one strict rule. Zero synthetic data. Every record carries the link it came from."),
 dict(html=page(3, "02 &middot; Dataset", "An official, source-linked festival dataset",
                tiles([(f"{len(obs):,}", "festival-holiday records, 2024 to 2026"), (f"{fm.festival.nunique()}", "festivals across 9 tradition groups"),
                       ("29", "states and UTs, from 34 RBI offices"), (f"{len(eco)}", "spending and crowd figures, each checked on its source page")]) +
                '<ul class="big" style="font-size:29px;margin-top:44px"><li><b>Reserve Bank of India</b> holiday lists: festival dates and which states observe them.</li>'
                '<li><b>Census of India 2011</b>: religion by state. &nbsp;<b>Wikipedia and Government portals</b>: each festival\'s tradition.</li>'
                '<li><b>CAIT, state governments, All India Radio, verified news</b>: spending and crowd sizes.</li></ul>'),
      say=f"The backbone is the Reserve Bank of India's official holiday list. We collected every bank holiday for all thirty-four regional offices, covering twenty-nine states, for 2024 to 2026. "
          f"That gave {len(obs):,} festival holiday records across {fm.festival.nunique()} festivals. "
          f"Each festival's tradition comes from its Wikipedia page or a government portal, and demography comes from Census 2011. "
          f"We also added {len(eco)} spending and crowd figures, each one checked on its original page."),
 dict(html=page(4, "02 &middot; Dataset", "How accurate is it? What the RBI list covers, and what it misses",
                f'<div class="two"><div class="card good"><h3>What it captures well</h3><ul><li>The official, state-wise record of bank holidays, for every faith, in one consistent format.</li>'
                f'<li>Holidays declared later in the year: our data includes <b>{n_adhoc} such dates</b> (elections, heavy rain, state mourning, the Ram temple consecration).</li>'
                f'<li>Holidays on second and fourth Saturdays are listed.</li></ul></div>'
                f'<div class="card warn"><h3>What it misses</h3><ul><li><b>Holidays that fall on a Sunday are not listed</b> (no Sunday date appears in three years of data), so roughly one festival day in seven is absent in any single year.</li>'
                f'<li>Holidays only for government offices or schools, restricted (optional) holidays and district-level local holidays.</li>'
                f'<li>RBI gives one combined label per date, so festivals sharing a date are split equally.</li></ul></div></div>'
                '<div class="lede" style="margin-top:34px">So our numbers measure <b>official bank-holiday recognition</b>, not every celebration. We average three years to soften the Sunday gap.</div>'),
      say=f"How accurate is this data? The RBI list is the official record of bank holidays, and it is updated when holidays are declared later. Our data includes {n_adhoc} such dates, for elections, heavy rain and state mourning. "
          "But it has limits. A holiday that falls on a Sunday is not listed, so roughly one festival day in seven is missing in any single year. "
          "Holidays meant only for government offices or schools, optional holidays, and district-level holidays are also not covered. "
          "So our numbers measure official bank holiday recognition, not every celebration. We average three years to reduce the Sunday effect."),
 dict(html=page(5, "03 &middot; Statistics", "India's festival calendar peaks in March, April and October",
                chart("F02_month_timeline_by_tradition.png", [("Mar &middot; Oct &middot; Apr", "the three busiest months"), ("p &lt; 0.001", "holidays are not spread evenly (chi-square test)"),
                                                             (f"p = {T.loc['H2', 'p_value']:.2f}", "a festival's season does not depend on its faith")], "1.75fr 1fr")),
      say="First, timing. Festival holidays are strongly concentrated. A chi-square test rejects an even spread across months. "
          "March, October and April are the peaks. But a festival's season does not depend on its faith. Every tradition has festivals spread through the year."),
 dict(html=page(6, "03 &middot; Statistics", "Holiday counts vary by state, not by region",
                chart("F05_map_festival_holidays.png", [(f"{top3.index[0]} {top3.iloc[0]:.1f}", f"most festival holidays a year, then {top3.index[1]} ({top3.iloc[1]:.1f}) and {top3.index[2]} ({top3.iloc[2]:.1f})"),
                                                        (f"{low3.index[0]} {low3.iloc[0]:.1f}", f"fewest, with {low3.index[1]} and {low3.index[2]} close behind"),
                                                        (f"p = {T.loc['H6-hol_days', 'p_value']:.2f}", "no significant difference between the six regions")], "1fr 1fr")),
      say=f"Next, geography. {top3.index[0]}, {top3.index[1]} and {top3.index[2]} have the most festival bank holidays. {low3.index[0]}, {low3.index[1]} and {low3.index[2]} have the fewest. "
          "The differences are between individual states, not between the six broad regions."),
 dict(html=page(7, "03 &middot; Statistics", "Calendars follow demography, but are more plural than the population",
                f'<div class="chart" style="margin-top:22px"><img src="{img("_demography_wide.png", S)}" style="max-height:470px"></div>' +
                tiles([("0.42 to 0.71", "correlation between population share and holiday share, all six faiths tested"),
                       ("46% vs 79.8%", "Hindu share of festival holidays vs share of population"),
                       ("Nationwide", "Christmas, Good Friday, both Eids, Buddha Purnima, Mahavir Jayanti, Guru Nanak Jayanti")], 3, small=True)),
      say="Now, demography. For every faith we tested, a state's share of holidays for that faith rises with its share of the population. The correlations run from zero point four two to zero point seven one, and all are significant. "
          "But the calendar is flatter than the population. Hindu festivals are about forty-six percent of festival holidays, against a population share near eighty percent. "
          "That is because Christmas, both Eids, Buddha Purnima, Mahavir Jayanti and Guru Nanak Jayanti are recognised almost nationwide."),
 dict(html=page(8, "04 &middot; Machine Learning", "Model 1: states group by calendar culture, not geography",
                chart("M05_cluster_map.png", [(f"k = {A_['best_k']}", "clusters chosen by K-Means on each state's holiday mix"),
                                              (f"{A_['silhouette']:.2f}", f"silhouette score; bootstrap stability {A_['bootstrap_ARI_mean']:.2f}"),
                                              (f"{A_['ARI_clusters_vs_geographic_region']:.2f}", "agreement with geographic regions: almost none")], "1fr 1.05fr")),
      say=f"For machine learning, we first clustered states by the mix of their festival calendar. K-Means selected {A_['best_k']} clusters, with a silhouette score of {A_['silhouette']:.2f}. "
          "Resampling shows the groups are reasonably stable. And they hardly match geographic regions. Neighbouring states often celebrate differently."),
 dict(html=page(9, "04 &middot; Machine Learning", "Model 2: can a festival's date and footprint reveal its faith?",
                f'<div class="grid" style="grid-template-columns:1fr 1.15fr"><div class="pts">'
                f'<div class="pt"><b>{B_["Random Forest"]["macro_f1_mean"]:.2f}</b><span>macro-F1 for the Random Forest, repeated 5-fold cross-validation</span></div>'
                f'<div class="pt"><b>{B_["Majority baseline"]["macro_f1_mean"]:.2f}</b><span>macro-F1 for a baseline that always guesses the largest group</span></div>'
                f'<div class="pt"><b>Only partly</b><span>Diwali and Holi are confused with the Eids and Christmas: nationwide festivals of every faith look alike</span></div></div>'
                f'<div><div style="font-size:29px;font-weight:600;margin-bottom:20px">What the model relies on most</div>{bars}<div class="src">Permutation importance: drop in macro-F1 when the feature is shuffled</div></div></div>'),
      say=f"Second, we asked whether a festival's timing and geography reveal its tradition. A Random Forest reached a macro F one score of {B_['Random Forest']['macro_f1_mean']:.2f}. "
          f"That is well above the baseline of {B_['Majority baseline']['macro_f1_mean']:.2f}, but far from perfect. "
          "The strongest signal is presence in the North East. The model confuses Diwali and Holi with the Eids and Christmas, because India's big festivals share the same nationwide footprint."),
 dict(html=page(10, "04 &middot; Machine Learning &middot; Economics", "Model 3: reported festive trade is growing fast",
                chart("F08_festive_trade_trend.png", [(f"~{growth}% a year", "growth in reported festive trade (log-linear model, p &lt; 0.001)"),
                                                      ("Rs 6.05 lakh cr", "Diwali 2025 trade reported by CAIT, up from Rs 1.25 lakh crore in 2021"),
                                                      (f"within {C_['holdout_2026'][1]['abs_pct_error']:.0f}%", "of the 2026 Holi estimate, using only data up to 2025")], "1.55fr 1fr")),
      say=f"Third, economics. A log-linear model estimates about {growth} percent growth a year in reported festive trade. "
          "The traders' body C A I T reports Diwali 2025 trade of six point zero five lakh crore rupees. "
          f"Trained only on data up to 2025, our model predicted the 2026 Holi estimate within {C_['holdout_2026'][1]['abs_pct_error']:.0f} percent."),
 dict(html=page(11, "05 &middot; Economics", "Crowds are huge, and spending data has a blind spot",
                chart("F10_footfall_density.png", [("66.21 crore", "visits to Maha Kumbh 2025 in 45 days, about 1.47 crore a day"),
                                                   ("Blind spot", "national spending estimates exist mainly for Hindu festivals, rarely for Eid, Christmas, Gurpurab or tribal festivals"),
                                                   ("Measured &ne; valued", "the gap shows what gets measured, not what matters")], "1.5fr 1fr")),
      say="On crowds, Maha Kumbh 2025 recorded sixty-six crore visits in forty-five days. That is far denser than Oktoberfest or the Hajj. "
          "We also found a measurement blind spot. National spending estimates are published for Hindu festivals, but rarely for Eid, Christmas, Gurpurab or tribal festivals. "
          "That gap shows what gets measured, not what matters."),
 dict(html=page(12, "06 &middot; Public Blog", "The findings are published, with every figure cited",
                tiles([("Live" if live else "Ready", f"on {meta.get('platform', 'Medium')}, {pub}" if live else "to publish on Medium or LinkedIn"),
                       (f"{eng['external_interactions']} / 40", "external reactions and comments logged (people outside VIT only)"),
                       (f"{eng['comments_with_author_reply']}", "comments answered by the team"), ("9 + 4", "charts in the article, plus interactive versions")]) +
                (f'<div class="lede" style="margin-top:50px">{eng["live_url"].split("//")[-1].split("/what")[0]} &nbsp;&middot;&nbsp; github.com/iJainamJain/indian-festivals-data-analysis</div>' if live else "") +
                '<ul class="big" style="font-size:29px;margin-top:34px"><li>Secular, balanced framing. No festival is ranked as better than another.</li>'
                '<li>Engagement is audited from a log with a screenshot for every interaction.</li></ul>'),
      say=(f"Our article is live on {meta.get('platform', 'Medium')}, with every chart cited to its source. So far we have logged {eng['external_interactions']} external reactions and comments, "
           f"{'meeting' if eng['target_met'] else 'against'} a target of forty, and we have replied to {eng['comments_with_author_reply']} comments. "
           "Only readers from outside our institution are counted, and each one is backed by a screenshot. The code and data are public on GitHub."
           if live else "Our article is written, with every chart cited to its source, and is ready to publish. Engagement will be audited from a log that counts only readers outside our institution.")),
 dict(html=page(13, "Summary", "Four things the data shows",
                '<ul class="big"><li>The official festival calendar <b>peaks in March, April and October</b>.</li>'
                '<li>Calendars <b>follow demography</b>, yet are <b>more plural than the population</b>.</li>'
                '<li>States group by <b>calendar culture, not geography</b>.</li>'
                '<li>Festive trade is <b>growing fast</b>, but it is <b>measured unevenly</b> across traditions.</li></ul>'
                '<div class="lede" style="margin-top:30px">Limits: bank holidays only, Sundays not listed, Census 2011, industry trade estimates.</div>'),
      say="To conclude. The official calendar peaks in spring and in October. It follows demography, yet it is more plural than the population. "
          "States group by calendar culture, not geography. And festive trade is growing quickly, but it is measured unevenly across traditions. "
          "All our code, data and sources are public. Thank you."),
]
assert len(SL) == N_SLIDES

async def tts(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)

script, segs = ["# Narration script\n", f"Voice: {VOICE} (Indian English)\n"], []
with sync_playwright() as p:
    br = p.chromium.launch(channel="msedge"); pg = br.new_page(viewport={"width": 1920, "height": 1080})
    for i, s in enumerate(SL, 1):
        hp = os.path.join(S, "_slide.html"); open(hp, "w", encoding="utf-8").write(s["html"])
        pg.goto("file:///" + hp.replace("\\", "/").replace(" ", "%20")); pg.wait_for_timeout(250)
        png = os.path.join(S, f"slide_{i:02d}.png"); pg.screenshot(path=png)
        s["png"] = png
    br.close()
os.remove(os.path.join(S, "_slide.html"))
for i, s in enumerate(SL, 1):
    mp3 = os.path.join(A, f"narration_{i:02d}.mp3")
    for attempt in range(4):
        try: asyncio.run(tts(s["say"], mp3)); break
        except Exception as e:
            if attempt == 3: raise
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3], capture_output=True, text=True).stdout)
    total = dur + 0.9
    seg = os.path.join(V, f"seg_{i:02d}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", f"{total:.2f}", "-i", s["png"], "-i", mp3,
                    "-vf", f"scale=1920:1080,fade=t=in:st=0:d=0.35,fade=t=out:st={total - 0.35:.2f}:d=0.35",
                    "-af", f"adelay=300|300,apad=whole_dur={total:.2f}", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-t", f"{total:.2f}", seg], check=True)
    segs.append(seg); title = _html.unescape(s["html"].split("<h1>")[1].split("</h1>")[0])
    script.append(f"## Slide {i}: {title}\n\n{s['say']}\n")
open(os.path.join(V, "narration_script.md"), "w", encoding="utf-8").write("\n".join(script))
lst = os.path.join(V, "segments.txt"); open(lst, "w").write("\n".join(f"file '{p_}'" for p_ in segs))
out = os.path.join(V, "Indian_Festivals_Project_Report.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
for p_ in segs: os.remove(p_)
os.remove(lst)
for f in os.listdir(A):          # remove narration files from the old voice
    if f.endswith((".wav", ".txt")): os.remove(os.path.join(A, f))
for f in os.listdir(S):
    if f.startswith("slide_") and int(f[6:8]) > N_SLIDES: os.remove(os.path.join(S, f))
dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout
print("video ->", out, "duration s:", dur.strip())
