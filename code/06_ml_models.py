"""Task 2 - Machine-learning pipeline (preprocessing -> feature engineering -> training -> validation).

Model A  (Clustering)      : group the 29 states/UTs by the *shape* of their festival calendar
                             (shares of Hindu, Muslim, Christian and Tribal festival holidays).  KMeans vs Agglomerative (Ward); k chosen by
                             silhouette; stability via bootstrap Adjusted Rand Index.
Model B  (Classification)  : can a festival's calendar + geographic footprint identify its tradition group?
                             Logistic Regression vs Random Forest, repeated stratified 5-fold CV,
                             macro precision / recall / F1 vs a majority-class baseline; permutation importance.
Model C  (Regression)      : pooled log-linear model of festive trade (festival fixed effects + year),
                             leave-one-out CV (RMSE, R^2), temporal hold-out: train <=2025, predict CAIT's 2026 figures.
Weights: outputs/models/*.joblib ; metrics: outputs/ml/*.csv ; figures: outputs/figures/M*.png
"""
import os, json, warnings
import numpy as np, pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import (silhouette_score, adjusted_rand_score, davies_bouldin_score, calinski_harabasz_score,
                             precision_recall_fscore_support, confusion_matrix, mean_squared_error, r2_score, accuracy_score)
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_predict, LeaveOneOut, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.inspection import permutation_importance
from scipy.cluster.hierarchy import linkage, dendrogram
import viz_style as vs

warnings.filterwarnings("ignore")
vs.apply()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
FIG, ML, MOD = (os.path.join(ROOT, "outputs", d) for d in ("figures", "ml", "models"))
for d in (FIG, ML, MOD): os.makedirs(d, exist_ok=True)
SEED = 42
obs = pd.read_csv(os.path.join(P, "festival_observations.csv"))
fm = pd.read_csv(os.path.join(P, "festival_master.csv"))
sp = pd.read_csv(os.path.join(P, "state_profile.csv")).set_index("state")
eco = pd.read_csv(os.path.join(P, "economic_footfall_clean.csv"))
log = {}

# =============================== MODEL A: STATE CLUSTERING =====================================
# Feature engineering: tradition shares (%) + monthly share of festival holidays (%) + calendar size & diversity
month = obs.groupby(["state", "month"])["attribution_weight"].sum().unstack(fill_value=0).reindex(columns=range(1, 13), fill_value=0)
month = 100 * month.div(month.sum(axis=1), axis=0); month.columns = [f"month_share_{m:02d}" for m in month.columns]
# Feature selection (documented experiment in outputs/ml/A_feature_set_experiment.csv): the four major tradition
# shares give far better-separated clusters than adding the 12 monthly shares (curse of dimensionality at n=29).
share_cols = ["hol_share_hindu", "hol_share_muslim", "hol_share_christian", "hol_share_tribal_indigenous"]
exp_rows = []
for set_name, cols in {"all 9 tradition shares": [c for c in sp.columns if c.startswith("hol_share_")],
                       "9 shares + 12 month shares + size + diversity": [c for c in sp.columns if c.startswith("hol_share_")] + ["hol_days_total_festival", "holiday_diversity_shannon"],
                       "4 major tradition shares (selected)": share_cols}.items():
    Xe = sp[cols].join(month) if "month" in set_name else sp[cols]
    Xe = StandardScaler().fit_transform(Xe.fillna(0))
    exp_rows.append({"feature_set": set_name, "n_features": Xe.shape[1],
                     **{f"silhouette_k{k}": silhouette_score(Xe, KMeans(k, n_init=50, random_state=SEED).fit_predict(Xe)) for k in range(2, 8)}})
pd.DataFrame(exp_rows).round(4).to_csv(os.path.join(ML, "A_feature_set_experiment.csv"), index=False)
XA = sp[share_cols].fillna(0)
XA_s = StandardScaler().fit_transform(XA)
rows = []
for k in range(2, 9):
    km = KMeans(k, n_init=50, random_state=SEED).fit(XA_s)
    ag = AgglomerativeClustering(k, linkage="ward").fit(XA_s)
    rows.append({"k": k, "kmeans_silhouette": silhouette_score(XA_s, km.labels_), "kmeans_davies_bouldin": davies_bouldin_score(XA_s, km.labels_),
                 "kmeans_calinski_harabasz": calinski_harabasz_score(XA_s, km.labels_), "kmeans_inertia": km.inertia_,
                 "ward_silhouette": silhouette_score(XA_s, ag.labels_), "ari_kmeans_vs_ward": adjusted_rand_score(km.labels_, ag.labels_)})
sel = pd.DataFrame(rows).round(4); sel.to_csv(os.path.join(ML, "A_cluster_model_selection.csv"), index=False)
# k: among ks within 0.02 of the best silhouette, take the lowest Davies-Bouldin (compactness/separation tie-break)
cand = sel[sel.kmeans_silhouette >= sel.kmeans_silhouette.max() - 0.02]
best_k = int(cand.loc[cand.kmeans_davies_bouldin.idxmin(), "k"])
km = KMeans(best_k, n_init=100, random_state=SEED).fit(XA_s)
labels = km.labels_
# bootstrap stability: refit on resampled states, compare labels on the overlapping states
rng = np.random.default_rng(SEED); aris = []
for _ in range(200):
    idx = rng.choice(len(XA_s), len(XA_s), replace=True); u = np.unique(idx)
    kb = KMeans(best_k, n_init=10, random_state=int(rng.integers(1e6))).fit(XA_s[idx])
    aris.append(adjusted_rand_score(labels[u], kb.predict(XA_s[u])))
region_ari = adjusted_rand_score(sp["region"], labels)
prof = XA.assign(cluster=labels).groupby("cluster").mean()
# name clusters by their dominant distinguishing trait (largest z-score deviation among tradition shares)
z = (prof[share_cols] - XA[share_cols].mean()) / XA[share_cols].std()
names = {}
for c in prof.index:
    top = z.loc[c].idxmax().replace("hol_share_", "").replace("_", " ").title()
    names[c] = f"C{c + 1}: above-avg {top} holiday share" if z.loc[c].max() > 0.5 else f"C{c + 1}: average mix"
sp_out = sp[["region"]].assign(cluster=labels, cluster_name=[names[l] for l in labels])
sp_out.to_csv(os.path.join(ML, "A_state_clusters.csv"))
prof.assign(n_states=pd.Series(labels).value_counts().sort_index(), name=[names[c] for c in prof.index]).round(2).T.to_csv(
    os.path.join(ML, "A_cluster_profiles.csv"))
joblib.dump({"scaler_features": list(XA.columns), "kmeans": km}, os.path.join(MOD, "A_state_kmeans.joblib"))
log["A"] = {"best_k": best_k, "silhouette": float(sel.loc[sel.k == best_k, "kmeans_silhouette"].iloc[0]),
            "bootstrap_ARI_mean": float(np.mean(aris)), "bootstrap_ARI_sd": float(np.std(aris)),
            "ARI_clusters_vs_geographic_region": float(region_ari),
            "clusters": {names[c]: sorted(sp_out.index[labels == c].tolist()) for c in sorted(set(labels))}}

# figures: PCA map + dendrogram + silhouette curve
pca = PCA(2, random_state=SEED).fit(XA_s); Z2 = pca.transform(XA_s)
fig, ax = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.5, 1]})
for c in sorted(set(labels)):
    m = labels == c
    ax[0].scatter(Z2[m, 0], Z2[m, 1], s=70, color=vs.SLOTS[c], label=names[c], edgecolor=vs.SURFACE, linewidth=1.5, zorder=3)
for i, s in enumerate(XA.index):
    ax[0].annotate(s.replace("Punjab-Haryana-Chandigarh", "Pb-Hr-Ch"), Z2[i], fontsize=7, color=vs.INK2, xytext=(4, 3), textcoords="offset points")
ax[0].set(xlabel=f"PC1 ({100 * pca.explained_variance_ratio_[0]:.0f}% var.)", ylabel=f"PC2 ({100 * pca.explained_variance_ratio_[1]:.0f}% var.)",
          title=f"K-Means state clusters (k={best_k}), PCA projection")
ax[0].legend(fontsize=8, loc="best")
ax[1].plot(sel.k, sel.kmeans_silhouette, marker="o", color=vs.SLOTS[0], label="K-Means")
ax[1].plot(sel.k, sel.ward_silhouette, marker="s", color=vs.SLOTS[1], label="Agglomerative (Ward)")
ax[1].axvline(best_k, color=vs.INK2, lw=1, ls=":"); ax[1].set(xlabel="k", ylabel="Silhouette score", title="Model selection"); ax[1].legend(fontsize=8)
fig.tight_layout(); vs.source_note(fig, "RBI holiday matrix 2024-26; features = Hindu, Muslim, Christian, Tribal shares of festival holidays (standardised)")
fig.savefig(os.path.join(FIG, "M01_state_clusters.png")); plt.close(fig)
fig, ax = plt.subplots(figsize=(11, 4.5))
dendrogram(linkage(XA_s, "ward"), labels=[s.replace("Punjab-Haryana-Chandigarh", "Pb-Hr-Ch") for s in XA.index], leaf_rotation=90,
           leaf_font_size=8, ax=ax, color_threshold=None, above_threshold_color=vs.INK2)
ax.set_title("Hierarchical clustering of state festival calendars (Ward linkage)"); ax.grid(False); ax.set_ylabel("Ward distance")
vs.source_note(fig, "RBI holiday matrix 2024-26"); fig.savefig(os.path.join(FIG, "M02_state_dendrogram.png")); plt.close(fig)

# blog-friendly view of the same clusters: a map of India coloured by cluster
from matplotlib.patches import Polygon as _Poly, Patch
from matplotlib.collections import PatchCollection
_gj = json.load(open(os.path.join(ROOT, "data", "raw", "geo", "india_states_datameet.geojson"), encoding="utf-8"))
_G2S = {"Arunanchal Pradesh": "Arunachal Pradesh", "NCT of Delhi": "Delhi", "Punjab": "Punjab-Haryana-Chandigarh",
        "Haryana": "Punjab-Haryana-Chandigarh", "Chandigarh": "Punjab-Haryana-Chandigarh"}
_lab = dict(zip(XA.index, labels))
# colour follows the tradition that defines the cluster (same colours as every other chart)
_ccol = {c: vs.TRAD_COLOR.get(next((t for t in vs.TRAD_ORDER if t.split("/")[0] in names[c]), ""), vs.INK2) for c in names}
fig, ax = plt.subplots(figsize=(9.5, 10.2))
for f in _gj["features"]:
    st = _G2S.get(f["properties"]["ST_NM"], f["properties"]["ST_NM"]); g_ = f["geometry"]
    polys = g_["coordinates"] if g_["type"] == "MultiPolygon" else [g_["coordinates"]]
    fc = _ccol[_lab[st]] if st in _lab else "#e4e3df"
    ax.add_collection(PatchCollection([_Poly(np.array(p_[0])[:, :2], closed=True) for p_ in polys], facecolor=fc, edgecolor="white", linewidth=0.6))
ax.set_xlim(67.5, 98); ax.set_ylim(7.5, 37.5); ax.set_aspect("equal"); ax.axis("off")
_nice = {c: names[c].split(": ")[1].replace("above-avg ", "More ").replace(" holiday share", " holidays than average").replace("Tribal Indigenous", "Tribal/indigenous")
         for c in names}
_cnt = pd.Series(labels).value_counts()
ax.legend(handles=[Patch(facecolor=_ccol[c], label=f"{_nice[c]} ({_cnt[c]} states)") for c in sorted(names, key=lambda c: -_cnt[c])] +
          [Patch(facecolor="#e4e3df", label="No RBI office (no data)")], loc="upper left", bbox_to_anchor=(0.0, -0.01), fontsize=11, frameon=False)
ax.set_title("Four kinds of festival calendar in India", fontsize=16, pad=24)
ax.text(0, 1.015, "States grouped by the share of Hindu, Muslim, Christian and tribal festivals in their bank holidays (K-Means clustering)", transform=ax.transAxes, fontsize=10, color=vs.INK2)
ax.text(0.0, -0.22, "Source: RBI holiday matrix 2024-26; boundaries DataMeet (CC BY 2.5 IN); island UTs not shown", transform=ax.transAxes, fontsize=7.5, color=vs.INK2, va="top")
fig.savefig(os.path.join(FIG, "M05_cluster_map.png")); plt.close(fig)

# =============================== MODEL B: TRADITION CLASSIFIER =================================
REG = ["North", "East", "Central", "West", "South", "North-East"]
reg_share = obs.groupby(["festival", "region"])["attribution_weight"].sum().unstack(fill_value=0).reindex(columns=REG, fill_value=0)
reg_share = reg_share.div(reg_share.sum(axis=1), axis=0); reg_share.columns = [f"region_share_{r}" for r in REG]
B = fm.set_index("festival").join(reg_share)
B["month_sin"] = np.sin(2 * np.pi * B.modal_month / 12); B["month_cos"] = np.cos(2 * np.pi * B.modal_month / 12)
B["is_moving_date"] = B.calendar_basis.str.startswith("Lunar").astype(int)
B["log_expected_states"] = np.log1p(B.expected_states_per_year)
num = ["month_sin", "month_cos", "is_moving_date", "date_drift_days", "log_expected_states", "mean_holiday_days",
       "share_shared_date", "n_regions"] + list(reg_share.columns)
def t4(t):
    if t in ("Hindu", "Tribal/Indigenous"): return t
    return "Abrahamic (Muslim/Christian)" if t in ("Muslim", "Christian") else "Other (Sikh/Buddhist/Jain/Parsi/multi-faith)"
y = B.tradition.map(t4); X = B[num].astype(float)
classes = sorted(y.unique())
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=SEED)
models = {"Majority baseline": DummyClassifier(strategy="most_frequent"),
          "Logistic Regression": Pipeline([("sc", StandardScaler()), ("lr", LogisticRegression(max_iter=2000, class_weight="balanced", C=1.0))]),
          "Random Forest": RandomForestClassifier(n_estimators=500, min_samples_leaf=2, class_weight="balanced", random_state=SEED)}
res = []
for name, mdl in models.items():
    ps, rs, fs, accs = [], [], [], []
    for tr, te in cv.split(X, y):
        mdl.fit(X.iloc[tr], y.iloc[tr]); pr = mdl.predict(X.iloc[te])
        p, r, f, _ = precision_recall_fscore_support(y.iloc[te], pr, average="macro", zero_division=0)
        ps.append(p); rs.append(r); fs.append(f); accs.append(accuracy_score(y.iloc[te], pr))
    res.append({"model": name, "accuracy_mean": np.mean(accs), "macro_precision_mean": np.mean(ps), "macro_recall_mean": np.mean(rs),
                "macro_f1_mean": np.mean(fs), "macro_f1_sd": np.std(fs)})
resB = pd.DataFrame(res).round(4); resB.to_csv(os.path.join(ML, "B_classifier_cv_metrics.csv"), index=False)
best = resB.iloc[1:].sort_values("macro_f1_mean").iloc[-1]["model"]
# per-class report from a single out-of-fold prediction with the best model
oof = cross_val_predict(models[best], X, y, cv=StratifiedKFold(5, shuffle=True, random_state=SEED))
p, r, f, sup = precision_recall_fscore_support(y, oof, labels=classes, zero_division=0)
pcr = pd.DataFrame({"class": classes, "precision": p, "recall": r, "f1": f, "support": sup}).round(3)
pcr.to_csv(os.path.join(ML, "B_per_class_report.csv"), index=False)
cm = confusion_matrix(y, oof, labels=classes)
final = models[best].fit(X, y)
joblib.dump({"model": final, "features": num, "classes": classes}, os.path.join(MOD, "B_tradition_classifier.joblib"))
pi = permutation_importance(final, X, y, n_repeats=50, random_state=SEED, scoring="f1_macro")
imp = pd.Series(pi.importances_mean, index=num).sort_values(); imp.round(4).to_csv(os.path.join(ML, "B_permutation_importance.csv"))
mis = pd.DataFrame({"festival": X.index, "true": y.values, "predicted": oof}).query("true != predicted")
mis.to_csv(os.path.join(ML, "B_misclassified_festivals.csv"), index=False)
log["B"] = {"best_model": best, "cv": "5-fold x 20 repeats, stratified", "n_festivals": len(X),
            "metrics": resB.set_index("model").to_dict(orient="index")}

fig, ax = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1, 1.2]})
short = [c.split(" (")[0] for c in classes]
im = ax[0].imshow(cm, cmap=vs.SEQ); ax[0].grid(False)
ax[0].set_xticks(range(len(classes)), short, rotation=20, ha="right"); ax[0].set_yticks(range(len(classes)), short)
for i in range(len(classes)):
    for j in range(len(classes)):
        ax[0].text(j, i, cm[i, j], ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else vs.INK)
ax[0].set(xlabel="Predicted", ylabel="True", title=f"{best}: out-of-fold confusion matrix")
top = imp.tail(10)
ax[1].barh([t.replace("region_share_", "share in ").replace("_", " ") for t in top.index], top.values, color=vs.SLOTS[0], height=0.62)
ax[1].set(xlabel="Mean drop in macro-F1 when shuffled", title="Permutation feature importance"); ax[1].grid(axis="y", visible=False)
fig.tight_layout(); vs.source_note(fig, "Festival features derived from RBI holiday matrix 2024-26; labels from Wikipedia / Govt. attribution (festival_master.csv)")
fig.savefig(os.path.join(FIG, "M03_classifier_results.png")); plt.close(fig)

# =============================== MODEL C: FESTIVE-TRADE REGRESSION =============================
tr_ = eco[(eco.metric == "festive_trade") & (eco.unit == "INR crore") & (eco.geography == "India")].copy()
tr_["log_value"] = np.log(tr_.value); tr_["t"] = tr_.year - 2018; tr_["is_projection"] = (tr_.estimate_type == "projection").astype(int)
enc = OneHotEncoder(drop="first", sparse_output=False)
def design(d, fit=False):
    F = enc.fit_transform(d[["festival"]]) if fit else enc.transform(d[["festival"]])
    return np.column_stack([d[["t", "is_projection"]].values, F])
# (i) leave-one-out CV on all <=2025 points
train = tr_[tr_.year <= 2025].reset_index(drop=True); test = tr_[tr_.year == 2026].reset_index(drop=True)
Xall = design(train, fit=True); yall = train.log_value.values
loo_pred = np.zeros(len(train))
for tr_i, te_i in LeaveOneOut().split(Xall):
    # a festival seen only once cannot be predicted when held out -> fall back to model without that dummy (it is all-zero column)
    lm = LinearRegression().fit(Xall[tr_i], yall[tr_i]); loo_pred[te_i] = lm.predict(Xall[te_i])
loo_rmse_log = mean_squared_error(yall, loo_pred) ** .5
loo_mape = np.mean(np.abs(np.exp(loo_pred) - train.value) / train.value) * 100
lm = LinearRegression().fit(Xall, yall)
in_r2 = r2_score(yall, lm.predict(Xall)); growth = np.exp(lm.coef_[0]) - 1
# (ii) temporal hold-out: predict 2026 CAIT figures (all 2026 values are CAIT pre-event projections)
Xte = design(test); pte = lm.predict(Xte)
hold = test[["festival", "year", "value", "source_url"]].assign(predicted_inr_crore=np.exp(pte).round(0),
                                                                 abs_pct_error=(100 * np.abs(np.exp(pte) - test.value) / test.value).round(1))
# (iii) forecasts for 2026 for festivals without a 2026 figure yet (reported-basis)
fc = []
for f in sorted(tr_.festival.unique()):
    d = pd.DataFrame({"festival": [f], "t": [2026 - 2018], "is_projection": [0]})
    fc.append({"festival": f, "year": 2026, "forecast_inr_crore": float(np.exp(lm.predict(design(d))[0]))})
fc = pd.DataFrame(fc).round(0)
pd.DataFrame({"metric": ["n_train (<=2025)", "in_sample_R2 (log)", "LOO_RMSE (log units)", "LOO_MAPE_%", "implied_annual_growth_%",
                         "holdout_2026_MAPE_%", "holdout_2026_RMSE_INR_crore"],
              "value": [len(train), in_r2, loo_rmse_log, loo_mape, 100 * growth, hold.abs_pct_error.mean(),
                        mean_squared_error(hold.value, hold.predicted_inr_crore) ** .5]}).round(4).to_csv(os.path.join(ML, "C_regression_metrics.csv"), index=False)
hold.to_csv(os.path.join(ML, "C_holdout_2026.csv"), index=False); fc.to_csv(os.path.join(ML, "C_forecast_2026.csv"), index=False)
pd.DataFrame({"festival": train.festival, "year": train.year, "actual": train.value, "loo_predicted": np.exp(loo_pred).round(0)}).to_csv(
    os.path.join(ML, "C_loo_predictions.csv"), index=False)
joblib.dump({"model": lm, "encoder": enc, "features": ["t=year-2018", "is_projection", "festival dummies"]}, os.path.join(MOD, "C_trade_loglinear.joblib"))
log["C"] = {"n_train": len(train), "R2_in_sample_log": in_r2, "LOO_RMSE_log": loo_rmse_log, "LOO_MAPE_pct": loo_mape,
            "annual_growth_pct": 100 * growth, "projection_premium_pct": 100 * (np.exp(lm.coef_[1]) - 1),
            "holdout_2026": hold[["festival", "value", "predicted_inr_crore", "abs_pct_error"]].to_dict(orient="records"),
            "forecast_2026": fc.to_dict(orient="records")}

fig, ax = plt.subplots(figsize=(7, 5.4))
lim = [np.log10(2000), np.log10(900000)]
ax.plot([10 ** lim[0], 10 ** lim[1]], [10 ** lim[0], 10 ** lim[1]], color=vs.INK2, lw=1, ls=":")
ax.scatter(train.value, np.exp(loo_pred), s=55, color=vs.SLOTS[0], edgecolor=vs.SURFACE, linewidth=1.5, label="Leave-one-out (<=2025)", zorder=3)
ax.scatter(hold.value, hold.predicted_inr_crore, s=70, marker="D", color=vs.SLOTS[1], edgecolor=vs.SURFACE, linewidth=1.5, label="Hold-out: CAIT 2026", zorder=3)
for _, r_ in hold.iterrows(): ax.annotate(f"{r_.festival.split(' (')[0]} 2026", (r_.value, r_.predicted_inr_crore), fontsize=8, color=vs.INK2, xytext=(5, -10), textcoords="offset points")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set(xlabel="Published trade (INR crore)", ylabel="Model prediction (INR crore)",
       title=f"Festive-trade model: LOO MAPE {loo_mape:.0f}%, growth {100 * growth:.0f}%/yr")
ax.legend(fontsize=8)
vs.source_note(fig, "CAIT and cited trade estimates (economic_footfall_clean.csv)")
fig.savefig(os.path.join(FIG, "M04_trade_regression.png")); plt.close(fig)

json.dump(log, open(os.path.join(ML, "ml_summary.json"), "w"), indent=1, default=float)
print(json.dumps(log, indent=1, default=float)[:6000])
print(resB.to_string()); print(pcr.to_string()); print(imp.tail(8).to_string()); print(hold.to_string()); print(sel.to_string())
