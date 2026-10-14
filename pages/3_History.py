import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from assets.theme_helper import load_css, cyber_title

st.set_page_config(page_title="History · AirSense AI",
                   page_icon="🌿", layout="wide")

for k, v in {
    "theme": "light", "threshold": 1800, "temp_max": 35.0, "hum_max": 80.0,
    "air_h": [], "temp_h": [], "hum_h": [], "time_h": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

load_css()

_now = datetime.now()
cyber_title("AIRSENSE <span class='accent'>AI</span> · HISTORY",
            ["Session Log", "Export CSV", "Trends", "Statistics"],
            _now.strftime("%a, %d %b %Y").upper(),
            _now.strftime("%I:%M %p"))

st.markdown('<div class="sec-title fade">📈 Session History</div>', unsafe_allow_html=True)

air_h = list(st.session_state.air_h)
temp_h = list(st.session_state.temp_h)
hum_h = list(st.session_state.hum_h)
time_h = list(st.session_state.time_h)

if not air_h:
    st.markdown('<div class="panel fade" style="text-align:center;padding:3rem 1rem;"><div style="font-size:3rem;">🗂️</div><div style="font-family:Sora;font-weight:700;font-size:1.2rem;">No history yet</div><div style="color:var(--muted);margin-top:.5rem;">Open Dashboard or Live Monitor and let it collect readings.</div></div>', unsafe_allow_html=True)
    st.stop()

thr = st.session_state.threshold
tmax = st.session_state.temp_max
hmax = st.session_state.hum_max

df = pd.DataFrame({
    "Time": time_h, "Air (ppm)": air_h,
    "Temp (°C)": temp_h, "Humidity (%)": hum_h,
})
df["Status"] = df.apply(lambda r: "POOR" if (
    r["Air (ppm)"] > thr or
    r["Temp (°C)"] > tmax or
    r["Humidity (%)"] > hmax
) else "OK", axis=1)

c1, c2, c3, c4 = st.columns(4)
for col, v, l, color in [
    (c1, len(df), "Total Readings", "#5b6cff"),
    (c2, (df["Status"] == "POOR").sum(), "Alerts Fired", "#ef4444"),
    (c3, (df["Status"] == "OK").sum(), "Safe Readings", "#10b981"),
    (c4, f"{df['Air (ppm)'].mean():.0f}", "Avg Air", "#8b5cf6"),
]:
    with col:
        st.markdown(f'<div class="tile fade"><div class="v" style="color:{color};">{v}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="panel fade"><div class="panel-title"><h3>Multi-Metric Trend</h3><span class="pill">SESSION</span></div></div>', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(x=time_h, y=air_h, mode="lines+markers", name="Air (ppm)", line=dict(color="#5b6cff", width=3, shape="spline")))
fig.add_trace(go.Scatter(x=time_h, y=temp_h, mode="lines+markers", name="Temp (°C)", line=dict(color="#ef4444", width=3, shape="spline")))
fig.add_trace(go.Scatter(x=time_h, y=hum_h, mode="lines+markers", name="Humidity (%)", line=dict(color="#10b981", width=3, shape="spline")))
fig.add_hline(y=thr, line_dash="dash", line_color="#ef4444", annotation_text=f"Air threshold {thr}", annotation_position="top right")
fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#475569"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(226,232,240,0.5)"))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown('<div class="sec-title">📋 Records</div>', unsafe_allow_html=True)
st.dataframe(df, use_container_width=True, height=420)
st.download_button("⬇️ Download CSV", df.to_csv(index=False),
                   file_name="air_quality_log.csv", mime="text/csv")