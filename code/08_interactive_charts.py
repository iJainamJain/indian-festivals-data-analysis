"""Task 4a - Interactive (hover-enabled) Plotly versions of the key blog visuals.
Output: blog/interactive/*.html (self-contained; can be embedded or linked from the blog post)."""
import os, json
import numpy as np, pandas as pd
import plotly.graph_objects as go
import viz_style as vs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed"); OUT = os.path.join(ROOT, "blog", "interactive"); os.makedirs(OUT, exist_ok=True)
obs = pd.read_csv(os.path.join(P, "festival_observations.csv")); sp = pd.read_csv(os.path.join(P, "state_profile.csv"))
obs["tgroup"] = obs.tradition.map(vs.trad_group)
FONT = dict(family="Segoe UI, Arial", size=13, color=vs.INK)
def layout(fig, title, src):
    fig.update_layout(title=dict(text=f"<b>{title}</b><br><sup>Source: {src}</sup>", x=0.01), font=FONT,
                      paper_bgcolor=vs.SURFACE, plot_bgcolor=vs.SURFACE, margin=dict(l=60, r=30, t=90, b=60),
                      hoverlabel=dict(bgcolor="white", font_size=12))
    fig.update_xaxes(gridcolor=vs.GRID); fig.update_yaxes(gridcolor=vs.GRID)
def write(fig, name): fig.write_html(os.path.join(OUT, name), include_plotlyjs="cdn", full_html=True)

# 1. month timeline (stacked, hover shows festivals)
M = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
g = obs.groupby(["month", "tgroup"]).agg(w=("attribution_weight", "sum"), fests=("festival", lambda x: ", ".join(sorted(set(x))[:8]))).reset_index()
fig = go.Figure()
for t in vs.TRAD_ORDER:
    d = g[g.tgroup == t].set_index("month").reindex(range(1, 13))
    fig.add_bar(x=M, y=(d.w / 102).fillna(0).round(2), name=t, marker_color=vs.TRAD_COLOR[t], customdata=d.fests.fillna("-"),
                hovertemplate="<b>%{x}</b> - " + t + "<br>%{y:.2f} holiday-days per office<br>%{customdata}<extra></extra>")
fig.update_layout(barmode="stack", yaxis_title="Festival bank-holiday days per office (avg 2024-26)", legend=dict(orientation="h", y=-0.15))
layout(fig, "When India celebrates: festival holidays by month and tradition", "RBI holiday matrix 2024-26")
write(fig, "1_month_timeline.html")

# 2. choropleth
gj = json.load(open(os.path.join(ROOT, "data", "raw", "geo", "india_states_datameet.geojson"), encoding="utf-8"))
G2S = {"Arunanchal Pradesh": "Arunachal Pradesh", "NCT of Delhi": "Delhi", "Punjab": "Punjab-Haryana-Chandigarh",
       "Haryana": "Punjab-Haryana-Chandigarh", "Chandigarh": "Punjab-Haryana-Chandigarh"}
def thin(ring, step):  # display-only simplification: keep every n-th vertex, 3-decimal coordinates
    r = ring[::step] if len(ring) > 60 else ring
    r = [[round(x, 3), round(y, 3)] for x, y, *_ in r]
    return r + [r[0]] if r[0] != r[-1] else r
for f in gj["features"]:
    g_ = f["geometry"]
    if g_["type"] == "Polygon": g_["coordinates"] = [thin(r, 12) for r in g_["coordinates"]]
    else: g_["coordinates"] = [[thin(r, 12) for r in poly] for poly in g_["coordinates"]]
rows = []
for f in gj["features"]:
    nm = f["properties"]["ST_NM"]; st = G2S.get(nm, nm)
    if st in set(sp.state): rows.append({"geo": nm, **sp.set_index("state").loc[st].to_dict(), "state": st})
d = pd.DataFrame(rows)
fig = go.Figure(go.Choropleth(geojson=gj, featureidkey="properties.ST_NM", locations=d.geo, z=d.hol_days_total_festival.round(1),
                              colorscale=[[0, "#f4f8fd"], [0.5, "#3987e5"], [1, "#0d366b"]], marker_line_color="white",
                              colorbar_title="Days/yr", customdata=np.stack([d.state, d.n_distinct_festivals, d.hol_share_hindu.round(1),
                              d.hol_share_muslim.round(1), d.hol_share_christian.round(1), d.hol_share_tribal_indigenous.round(1)], axis=1),
                              hovertemplate="<b>%{customdata[0]}</b><br>%{z} festival holidays / yr<br>%{customdata[1]} distinct festivals (2024-26)"
                                            "<br>Hindu %{customdata[2]}% | Muslim %{customdata[3]}% | Christian %{customdata[4]}% | Tribal %{customdata[5]}%<extra></extra>"))
fig.update_geos(fitbounds="locations", visible=False, bgcolor=vs.SURFACE)
layout(fig, "Festival bank holidays per year, by state (hover for the tradition mix)", "RBI holiday matrix 2024-26; boundaries DataMeet (CC BY 2.5 IN)")
fig.update_layout(height=700); write(fig, "2_state_map.html")

# 3. holiday share vs population share
fig = go.Figure()
for faith, h, c in [("Hindu", "hol_share_hindu", "census_pct_hindu"), ("Muslim", "hol_share_muslim", "census_pct_muslim"),
                    ("Christian", "hol_share_christian", "census_pct_christian")]:
    fig.add_scatter(x=sp[c].round(1), y=sp[h].round(1), mode="markers", name=faith, text=sp.state,
                    marker=dict(size=11, color=vs.TRAD_COLOR[faith], line=dict(color="white", width=1.5)),
                    hovertemplate="<b>%{text}</b><br>" + faith + ": %{x}% of population, %{y}% of festival holidays<extra></extra>")
fig.add_scatter(x=[0, 100], y=[0, 100], mode="lines", line=dict(color=vs.INK2, dash="dot", width=1), name="parity (y = x)", hoverinfo="skip")
fig.update_layout(xaxis_title="Share of state population, % (Census 2011)", yaxis_title="Share of state festival holidays, %")
layout(fig, "Do holiday calendars mirror demography?", "RBI holiday matrix 2024-26; Census of India 2011 C-01")
write(fig, "3_holiday_vs_population.html")

# 4. trade trend
eco = pd.read_csv(os.path.join(P, "economic_footfall_clean.csv"))
t = eco[(eco.metric == "festive_trade") & (eco.geography == "India")]
fig = go.Figure()
for i, f in enumerate(["Diwali (Deepavali)", "Holi", "Karva Chauth", "Raksha Bandhan", "Ganesh Chaturthi"]):
    x = t[t.festival == f].sort_values("year")
    fig.add_scatter(x=x.year, y=x.value, mode="lines+markers", name=f, line=dict(color=vs.SLOTS[i], width=2),
                    marker=dict(size=9, symbol=["circle-open" if e == "projection" else "circle" for e in x.estimate_type]),
                    customdata=np.stack([x.estimate_type, x.publisher], axis=1),
                    hovertemplate=f"<b>{f}</b> %{{x}}<br>INR %{{y:,.0f}} crore<br>%{{customdata[0]}} - %{{customdata[1]}}<extra></extra>")
fig.update_layout(yaxis_type="log", yaxis_title="Trade, INR crore (log)", xaxis_title="Year")
layout(fig, "Festive trade estimates (open marker = pre-event projection)", "CAIT press releases & cited news (see footnotes)")
write(fig, "4_trade_trend.html")
print("interactive charts ->", OUT, os.listdir(OUT))
