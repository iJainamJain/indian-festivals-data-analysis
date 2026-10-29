"""
Interactive presentation dashboard (single self-contained HTML file, works offline).
Inputs:  data/processed/*, outputs/stats/*, outputs/ml/*, data/raw/geo/india_states_datameet.geojson
Output:  dashboard/India_Festivals_Dashboard.html
"""
import os, json
import numpy as np, pandas as pd
from scipy import stats
import plotly.offline
import viz_style as vs
from project_config import YEARS, PERIOD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
OUT_DIR = J("dashboard"); os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "India_Festivals_Dashboard.html")

obs = pd.read_csv(J("data", "processed", "festival_observations.csv"))
fm = pd.read_csv(J("data", "processed", "festival_master.csv"))
sp = pd.read_csv(J("data", "processed", "state_profile.csv"))
eco = pd.read_csv(J("data", "processed", "economic_footfall_clean.csv"))
T6 = pd.read_csv(J("outputs", "stats", "T6_hypothesis_tests.csv"))
T5 = pd.read_csv(J("outputs", "stats", "T5_holiday_vs_population_share.csv"))
ml = json.load(open(J("outputs", "ml", "ml_summary.json"), encoding="utf-8"))
ksel = pd.read_csv(J("outputs", "ml", "A_cluster_model_selection.csv"))
clf = pd.read_csv(J("outputs", "ml", "B_classifier_cv_metrics.csv"))
pcr = pd.read_csv(J("outputs", "ml", "B_per_class_report.csv"))
imp = pd.read_csv(J("outputs", "ml", "B_permutation_importance.csv")); imp.columns = ["feature", "importance"]
loo = pd.read_csv(J("outputs", "ml", "C_loo_predictions.csv"))
hold = pd.read_csv(J("outputs", "ml", "C_holdout_2026.csv"))
fc = pd.read_csv(J("outputs", "ml", "C_forecast_2026.csv"))
regm = pd.read_csv(J("outputs", "ml", "C_regression_metrics.csv")).set_index("metric")["value"]

# ------------------------------- observations (aggregated in the browser) -------------------------------
obs["tg"] = obs.tradition.map(vs.trad_group)
TG = vs.TRAD_ORDER
FEST = sorted(obs.festival.unique()); STATES = sorted(sp.state)
REGIONS = ["North", "Central", "East", "North-East", "West", "South"]
rows = [[int(r.year), int(r.month), STATES.index(r.state), FEST.index(r.festival), TG.index(r.tg),
         round(float(r.recognition_weight), 4), round(float(r.annual_weight), 4)] for r in obs.itertuples()]

# ------------------------------- state table -------------------------------
FAITHS = ["hindu", "muslim", "christian", "sikh", "buddhist", "jain"]
states = []
for r in sp.set_index("state").loc[STATES].reset_index().itertuples():
    states.append({"name": r.state, "region": r.region, "n_off": int(r.n_rbi_offices),
                   "div": round(r.holiday_diversity_shannon, 3), "popdiv": round(r.population_diversity_shannon, 3),
                   "pop": int(r.pop_total), "census": {f: round(getattr(r, "census_pct_" + f), 2) for f in FAITHS},
                   "hshare": {f: round(getattr(r, "hol_share_" + f), 2) for f in FAITHS}})
N_OFF = int(sp.n_rbi_offices.sum())

# clusters
cl2 = {s: name for name, ss in ml["A"]["clusters"].items() for s in ss}
cl3 = {s: name for name, ss in ml["A"]["detail_clusters"].items() for s in ss}

# ------------------------------- festivals -------------------------------
fest = []
for f in FEST:
    m = fm.set_index("festival").loc[f]
    fest.append({"name": f, "trad": m.tradition, "tg": vs.trad_group(m.tradition), "type": m.festival_type,
                 "reach": round(m.expected_states_per_year, 2), "cert": round(m.attribution_certainty, 2),
                 "ident": bool(m.reach_identifiable), "month": int(m.modal_month) if pd.notna(m.modal_month) else None,
                 "season": m.modal_season_imd, "basis": m.calendar_basis, "states": m.states if isinstance(m.states, str) else "",
                 "src": m.attribution_url if isinstance(m.attribution_url, str) else ""})

# ------------------------------- map geometry (display-only simplification) -------------------------------
gj = json.load(open(J("data", "raw", "geo", "india_states_datameet.geojson"), encoding="utf-8"))
G2S = {"Arunanchal Pradesh": "Arunachal Pradesh", "NCT of Delhi": "Delhi", "Punjab": "Punjab-Haryana-Chandigarh",
       "Haryana": "Punjab-Haryana-Chandigarh", "Chandigarh": "Punjab-Haryana-Chandigarh"}
def thin(ring, step=10):
    r = ring[::step] if len(ring) > 60 else ring
    r = [[round(x, 3), round(y, 3)] for x, y, *_ in r]
    return r + [r[0]] if r[0] != r[-1] else r
shapes = []
for f in gj["features"]:
    nm = f["properties"]["ST_NM"]; st = G2S.get(nm, nm); g = f["geometry"]
    polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    xs, ys = [], []
    for poly in polys:
        ring = thin(poly[0])
        if len(ring) < 4: continue
        xs += [p[0] for p in ring] + [None]; ys += [p[1] for p in ring] + [None]
    shapes.append({"geo": nm, "state": st if st in STATES else None, "x": xs, "y": ys})

# ------------------------------- stats -------------------------------
tests = T6.fillna("").to_dict(orient="records")
scat = {f: [{"s": s["name"], "pop": s["census"][f], "hol": s["hshare"][f]} for s in states] for f in FAITHS}
t5 = T5.to_dict(orient="records")

# national tradition share vs population share (India, Census 2011)
cen = pd.read_csv(J("data", "processed", "state_profile.csv"))
w = cen.pop_total
pop_share = {f: round(float((cen["census_pct_" + f] * w).sum() / w.sum()), 1) for f in FAITHS}

# ------------------------------- ML -------------------------------
loo["err"] = loo.loo_predicted - loo.actual
mae = float(loo.err.abs().mean()); rmse = float(np.sqrt((loo.err ** 2).mean()))
r2 = float(1 - (loo.err ** 2).sum() / ((loo.actual - loo.actual.mean()) ** 2).sum())
mape = float((loo.err.abs() / loo.actual).mean() * 100)
tt = stats.ttest_rel(np.log(loo.loo_predicted), np.log(loo.actual))   # same test as the report (log scale)
mlx = {"ksel": ksel.to_dict(orient="records"), "clf": clf.to_dict(orient="records"), "pcr": pcr.to_dict(orient="records"),
       "imp": imp.sort_values("importance", ascending=False).head(10).to_dict(orient="records"),
       "loo": loo.to_dict(orient="records"), "hold": hold.drop(columns=["source_url"]).to_dict(orient="records"),
       "fc": fc.to_dict(orient="records"),
       "reg": {"mae": mae, "rmse": rmse, "r2": r2, "mape": mape, "t": float(tt.statistic), "df": len(loo) - 1, "p": float(tt.pvalue),
               "r2log": float(regm["in_sample_R2 (log)"]), "growth": float(regm["implied_annual_growth_%"]),
               "hold_mape": float(regm["holdout_2026_MAPE_%"]), "n": int(regm["n_train (<=2025)"])},
       "best_k": ml["A"]["best_k"], "sil": ml["A"]["silhouette"], "sil3": ml["A"]["detail_silhouette"],
       "ari_boot": ml["A"]["bootstrap_ARI_mean"], "ari_region": ml["A"]["ARI_clusters_vs_geographic_region"],
       "cl2": cl2, "cl3": cl3}

# trade history for the prediction tab (national trade estimates used by the model)
trade = eco[(eco.metric == "festive_trade") & (eco.unit == "INR crore") & (eco.geography == "India")]
trade = trade[["festival", "year", "value_inr_crore", "publisher"]].sort_values(["festival", "year"]).to_dict(orient="records")

DATA = {"years": YEARS, "period": PERIOD, "tg": TG, "tcolor": [vs.TRAD_COLOR[t] for t in TG], "fest": fest, "states": states,
        "regions": REGIONS, "rows": rows, "n_off": N_OFF, "shapes": shapes, "tests": tests, "scat": scat, "t5": t5,
        "pop_share": pop_share, "ml": mlx, "trade": trade,
        "counts": {"obs": len(obs), "fest": len(FEST), "states": len(STATES), "offices": N_OFF, "eco": len(eco),
                   "raw": int(len(pd.read_csv(J("data", "raw", "rbi_holiday_matrix_raw.csv")))), "uncertain": int((~fm.reach_identifiable).sum())}}

HTML = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_template.html"), encoding="utf-8").read()
html = (HTML.replace("/*PLOTLY*/", plotly.offline.get_plotlyjs())
            .replace("/*DATA*/", "const D = " + json.dumps(DATA, separators=(",", ":"), default=str) + ";"))
open(OUT, "w", encoding="utf-8").write(html)
print("dashboard ->", OUT, f"({os.path.getsize(OUT) / 1e6:.1f} MB)")
