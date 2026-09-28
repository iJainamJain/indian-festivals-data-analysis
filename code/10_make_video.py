"""Task 5 - Final synthesis video (1920x1080 MP4, narrated).

Pipeline: slides rendered with matplotlib (real project figures + real numbers read from outputs/) ->
narration synthesised with Windows SAPI (System.Speech, voice 'Microsoft Zira Desktop') -> ffmpeg (H.264 + AAC).
The blog-reception slide reads blog/engagement/engagement_metrics.json, so re-run this script after the blog
is published and the engagement log is filled to produce the final cut.
Output: video/Indian_Festivals_Project_Report.mp4 (+ slides/*.png, audio/*.wav, narration_script.md)
"""
import os, json, subprocess, textwrap
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import viz_style as vs

vs.apply()
plt.rcParams['savefig.bbox'] = 'standard'  # exact 1920x1080 canvas for the encoder
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "video"); S, A = os.path.join(V, "slides"), os.path.join(V, "audio")
for d in (S, A): os.makedirs(d, exist_ok=True)
FIG = os.path.join(ROOT, "outputs", "figures")
ml = json.load(open(os.path.join(ROOT, "outputs", "ml", "ml_summary.json")))
T = pd.read_csv(os.path.join(ROOT, "outputs", "stats", "T6_hypothesis_tests.csv")).set_index("id")
eng = json.load(open(os.path.join(ROOT, "blog", "engagement", "engagement_metrics.json")))
fm = pd.read_csv(os.path.join(ROOT, "data", "processed", "festival_master.csv"))
eco = pd.read_csv(os.path.join(ROOT, "data", "processed", "economic_footfall_clean.csv"))
obs = pd.read_csv(os.path.join(ROOT, "data", "processed", "festival_observations.csv"))
H9 = T.loc["H9", "interpretation"]
growth = H9.split("growth ")[1].split("%")[0]

def slide(i, title, bullets=None, image=None, subtitle=None):
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(vs.SURFACE)
    fig.add_artist(plt.Rectangle((0, 0.93), 1, 0.07, color="#0d366b", transform=fig.transFigure))
    fig.text(0.03, 0.965, "Socio-Economic & Demographic Analysis of Indian Festivals", color="white", fontsize=17, va="center")
    fig.text(0.97, 0.965, f"{i}", color="white", fontsize=17, va="center", ha="right")
    fig.text(0.03, 0.87, title, fontsize=38, fontweight="bold", color=vs.INK, va="top")
    if subtitle: fig.text(0.03, 0.79, subtitle, fontsize=22, color=vs.INK2, va="top")
    if image:
        ax = fig.add_axes([0.40 if bullets else 0.12, 0.05, 0.57 if bullets else 0.76, 0.72]); ax.imshow(mpimg.imread(os.path.join(FIG, image))); ax.axis("off")
    if bullets:
        y = 0.72
        for b in bullets:
            lines = textwrap.wrap(b, 34 if image else 80)
            fig.text(0.035, y, "•", fontsize=24, color="#2a78d6", va="top")
            fig.text(0.055, y, "\n".join(lines), fontsize=24 if image else 27, color=vs.INK, va="top", linespacing=1.35)
            y -= 0.058 * len(lines) + 0.035
    fig.text(0.03, 0.02, "Jainam Jain  |  Vrushan Patil  |  Dhanush Chowke  |  Aditya Tambe  |  Vivek Jaiswal  |  B.E. ECS, VIT  |  DAV Project", fontsize=13, color=vs.INK2)
    p = os.path.join(S, f"slide_{i:02d}.png"); fig.savefig(p, dpi=100, bbox_inches=None); plt.close(fig); return p

eng_line = (f"The article is live at {eng['live_url']}. It has {eng['external_interactions']} external reactions and comments, "
            f"{'meeting' if eng['target_met'] else 'working towards'} the target of 40, and we replied to {eng['comments_with_author_reply']} comments."
            if eng["live_url"] != "NOT YET PUBLISHED" else
            "The blog article is written, with every chart footnoted to its source, and it is ready to publish on LinkedIn or Medium. "
            "Engagement is tracked in an audit log that counts only readers from outside our institution. "
            "This slide updates automatically once the post is live.")
A_ = ml["A"]; B_ = ml["B"]["metrics"]; C_ = ml["C"]
SL = [
 dict(title="What India's Holiday Calendar Reveals", subtitle="A data-driven study by Jainam Jain, Vrushan Patil, Dhanush Chowke, Aditya Tambe and Vivek Jaiswal",
      bullets=["Task 1: verified multi-faith dataset", "Task 2: machine-learning models", "Task 3: statistical valuation and EDA",
               "Task 4: public blog and engagement", "Task 5: this synthesis"],
      say="Hello. We are Jainam Jain, Vrushan Patil, Dhanush Chowke, Aditya Tambe and Vivek Jaiswal. This video summarises our data analytics project on the socio-economic and demographic patterns of Indian festivals. "
          "It covers the dataset, the statistics, the machine learning models, and the public blog."),
 dict(title="1. Motivation", bullets=["Festival data is scattered and often anecdotal, which invites biased comparisons",
                                    "Goal: a secular, evidence-only view of when, where and whose festivals are officially recognised, and what they are worth",
                                    "Rule: zero synthetic data. Every record carries its source URL"],
      say="India celebrates hundreds of festivals, but most information about them is scattered and anecdotal, which makes biased comparisons easy. "
          "My goal was an evidence-only picture: when and where festivals are officially recognised, whose festivals they are, and what they are worth economically. "
          "The strict rule was zero synthetic data. Every record carries its source link."),
 dict(title="1. Dataset curation and source integrity",
      bullets=[f"RBI holiday matrix: 34 offices, 29 states and UTs, 2024 to 2026, giving {len(obs):,} festival observations and {fm.festival.nunique()} festivals",
               "Tradition labels from Wikipedia infoboxes, or Government tourism portals where no article exists",
               "Census 2011 religion table C-01 for demography",
               f"{len(eco)} economic and footfall records, each opened and verified on its source page"],
      image="F04_state_month_heatmap.png",
      say=f"The backbone is the Reserve Bank of India's official holiday matrix. We scraped every holiday for all thirty-four regional offices, covering twenty-nine states, for 2024 to 2026. "
          f"That gave {len(obs):,} festival observations across {fm.festival.nunique()} festivals. "
          f"Each festival's tradition comes from its Wikipedia infobox, or a government tourism portal. Demography comes from Census 2011. "
          f"We also added {len(eco)} economic and crowd figures, every one checked on its original page. "
          "Where RBI lists several festivals on one date, the day is split equally, and we flag festivals whose reach cannot be separated."),
 dict(title="2. When India celebrates", image="F02_month_timeline_by_tradition.png",
      bullets=["Holidays are not uniform across months (chi-square p < 0.001)", "Peaks: March, October, April",
               f"Season is independent of tradition (permutation p = {T.loc['H2', 'p_value']:.2f})"],
      say="First, timing. Festival holidays are strongly concentrated. A chi-square test rejects a uniform spread across months. "
          "March, October and April are the peak months. But a festival's season does not depend on its faith: every tradition has festivals spread through the year."),
 dict(title="2. Do calendars mirror demography?", image="F07_holiday_vs_population_share.png",
      bullets=["Holiday share rises with population share for all six faiths tested (Spearman rho 0.42 to 0.71, all p < 0.05)",
               "But the calendar is more plural than the population: about 46% of festival holidays are Hindu, against 79.8% of the population"],
      say="Next, demography. For every faith we tested, a state's share of holidays for that faith rises with its population share. The correlations run from 0.42 to 0.71, all significant. "
          "But the calendar is flatter than the population. Hindu festivals are about forty-six percent of festival holidays, against a population share near eighty percent, "
          "because Christmas, both Eids, Buddha Purnima, Mahavir Jayanti and Guru Nanak Jayanti are recognised almost nationwide."),
 dict(title="2. Where India celebrates", image="F05_map_festival_holidays.png",
      bullets=["Most festival holidays: Sikkim, Uttar Pradesh, Jharkhand", "Fewest: Goa, Arunachal Pradesh, Delhi, Nagaland",
               f"No significant difference between the 6 regions (p = {T.loc['H6-hol_days', 'p_value']:.2f})"],
      say="Geographically, Sikkim, Uttar Pradesh and Jharkhand have the most festival bank holidays, while Goa, Arunachal Pradesh, Delhi and Nagaland have the fewest. "
          "Differences exist between individual states, not between the six broad regions."),
 dict(title="3. Machine learning: state clusters", image="M01_state_clusters.png",
      bullets=[f"K-Means on tradition shares: k = {A_['best_k']}, silhouette {A_['silhouette']:.2f}, bootstrap ARI {A_['bootstrap_ARI_mean']:.2f}",
               f"Clusters versus geographic regions: ARI = {A_['ARI_clusters_vs_geographic_region']:.2f}. States group by calendar culture, not geography"],
      say=f"For machine learning, we first clustered states by the mix of their festival calendar. K-Means selected {A_['best_k']} clusters with a silhouette of {A_['silhouette']:.2f}, "
          "and bootstrap resampling shows they are reasonably stable. "
          "The clusters hardly overlap with geographic regions, so neighbouring states often celebrate differently."),
 dict(title="3. Machine learning: classification and forecasting", image="M03_classifier_results.png",
      bullets=[f"Random Forest tradition classifier: macro-F1 {B_['Random Forest']['macro_f1_mean']:.2f} vs baseline {B_['Majority baseline']['macro_f1_mean']:.2f}",
               "Top signal: North-East presence. Nationwide festivals of every faith look alike",
               f"Trade model: about {growth}% growth per year; 2026 Holi predicted within {C_['holdout_2026'][1]['abs_pct_error']:.0f}%"],
      say=f"Second, we asked whether a festival's timing and geography reveal its tradition. A Random Forest reached a macro F1 of {B_['Random Forest']['macro_f1_mean']:.2f}, "
          f"well above the {B_['Majority baseline']['macro_f1_mean']:.2f} baseline but far from perfect. "
          "The model confuses Diwali and Holi with the Eids and Christmas, because India's big festivals share the same nationwide footprint. "
          f"Third, a log-linear trade model estimates about {growth} percent growth a year in reported festive trade. Trained only on data up to 2025, "
          f"it predicted the 2026 Holi estimate within {C_['holdout_2026'][1]['abs_pct_error']:.0f} percent."),
 dict(title="Economics and crowds", image="F10_footfall_density.png",
      bullets=["Diwali 2025: Rs 6.05 lakh crore (CAIT)", "Maha Kumbh 2025: 66.21 crore visits in 45 days",
               "Blind spot: national spending estimates rarely exist for minority and tribal festivals"],
      say="On economics, CAIT reports Diwali 2025 trade of six point zero five lakh crore rupees. Maha Kumbh recorded sixty-six crore visits in forty-five days, "
          "far denser than Oktoberfest or the Hajj. One important finding is a measurement blind spot: national spending estimates are published for Hindu festivals, "
          "but rarely for Eid, Christmas, Gurpurab or tribal festivals. That gap reflects what gets measured, not what matters."),
 dict(title="4. Public blog and reception",
      bullets=["Visually rich article with 9 charts and interactive versions, every figure footnoted",
               f"Status: {'LIVE: ' + eng['live_url'] if eng['live_url'] != 'NOT YET PUBLISHED' else 'ready to publish on LinkedIn / Medium'}",
               f"External interactions logged: {eng['external_interactions']} of 40 target (same-institution peers excluded)",
               f"Comments answered by author: {eng['comments_with_author_reply']}"],
      say=eng_line),
 dict(title="Key takeaways",
      bullets=["India's official festival calendar peaks in March-April and October",
               "Calendars track demography, yet are more plural than the population",
               "States cluster by calendar culture, not geography",
               "Festive trade is growing fast, but measurement is uneven across traditions"],
      say="To conclude: the official calendar peaks in spring and October. It tracks demography, yet it is more plural than the population. "
          "States cluster by calendar culture rather than geography. And festive trade is growing quickly, but it is measured unevenly across traditions. "
          "All code, data and sources are in the project repository. Thank you."),
]
script = ["# Narration script\n"]
segs = []
for i, s in enumerate(SL, 1):
    img = slide(i, s["title"], s.get("bullets"), s.get("image"), s.get("subtitle"))
    wav = os.path.join(A, f"narration_{i:02d}.wav")
    txt = os.path.join(A, f"narration_{i:02d}.txt"); open(txt, "w", encoding="utf-8").write(s["say"])
    ps = ("Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
          "$s.SelectVoice('Microsoft Zira Desktop'); $s.Rate = 0; "
          f"$s.SetOutputToWaveFile('{wav}'); $s.Speak([IO.File]::ReadAllText('{txt}')); $s.Dispose()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    seg = os.path.join(V, f"seg_{i:02d}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", img, "-i", wav, "-af", "apad=pad_dur=0.8",
                    "-vf", "scale=1920:1080", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", seg], check=True)
    segs.append(seg); script.append(f"## Slide {i}: {s['title']}\n\n{s['say']}\n")
open(os.path.join(V, "narration_script.md"), "w", encoding="utf-8").write("\n".join(script))
lst = os.path.join(V, "segments.txt"); open(lst, "w").write("\n".join(f"file '{p}'" for p in segs))
out = os.path.join(V, "Indian_Festivals_Project_Report.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
for p in segs: os.remove(p)
os.remove(lst)
dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout
print("video ->", out, "duration s:", dur.strip())
