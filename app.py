import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from collections import deque
import time
from esp32_client import fetch_real, simulate
from assets.theme_helper import load_css, cyber_title, show_splash_once
from assets.logo import LEAF_LOGO_SVG

# ======================== PAGE CONFIG ========================
st.set_page_config(
    page_title="AirSense AI · Air Quality Console",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================== STATE ========================
DEFAULTS = {
    "theme": "light",
    "mode": "idle",
    "esp_ip": "",
    "threshold": 1800,
    "temp_max": 35.0,
    "hum_max": 80.0,
    "man_air": 800,
    "man_temp": 26.0,
    "man_hum": 55.0,
    "air_h": deque(maxlen=60),
    "temp_h": deque(maxlen=60),
    "hum_h": deque(maxlen=60),
    "time_h": deque(maxlen=60),
    "splash_done": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================== CSS ========================
load_css()

# ======================== SPLASH ========================
if show_splash_once():
    time.sleep(4.0)
    st.session_state.splash_done = True
    st.rerun()

# ======================== THEME TOKENS ========================
T = {
    "accent":   "#5b6cff",
    "accent_2": "#8b5cf6",
    "danger":   "#ef4444",
    "success":  "#10b981",
    "warning":  "#f59e0b",
    "muted":    "#7c8aa5",
}

# ======================== SPARKLINE HELPER ========================
def sparkline_svg(points, color, width=180, height=30):
    if not points:
        points = [0, 0]
    pts = np.array(points, dtype=float)
    mn, mx = pts.min(), pts.max()
    rng = (mx - mn) or 1
    step = width / max(1, len(pts) - 1)
    coords = [(i * step, height - ((v - mn) / rng) * (height - 4) - 2)
              for i, v in enumerate(pts)]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = d + f" L {width},{height} L 0,{height} Z"
    gid = f"g{abs(hash(tuple(points))) % 99999}"
    return (
        f'<svg class="spark" viewBox="0 0 {width} {height}" preserveAspectRatio="none">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{color}" stop-opacity="0.35"/>'
        f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
        f'</linearGradient></defs>'
        f'<path d="{area}" fill="url(#{gid})"/>'
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )

# ======================== SIDEBAR ========================
with st.sidebar:
    st.markdown(f"""
    <div class="brand">
        <div class="brand-badge">{LEAF_LOGO_SVG}</div>
        <div>
            <div class="brand-name">AirSense AI</div>
            <div class="brand-sub">QUALITY CONSOLE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="rail-label">Connection Mode</div>', unsafe_allow_html=True)
    if st.button("🌐  Connect Real ESP32", key="conn_real", use_container_width=True):
        st.session_state.mode = "real"
        st.switch_page("pages/4_Settings.py")
    if st.button("🎯  Manual Simulation", key="conn_sim", use_container_width=True):
        st.session_state.mode = "manual"
        st.switch_page("pages/2_Manual_Test.py")

    st.markdown('<div class="rail-label">Appearance</div>', unsafe_allow_html=True)
    theme_label = "🌙  Dark Mode" if st.session_state.theme == "light" else "☀️  Light Mode"
    st.markdown('<div class="theme-pill">', unsafe_allow_html=True)
    if st.button(theme_label, key="theme_toggle", use_container_width=True):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="rail-label">Engine</div>', unsafe_allow_html=True)
    mode = st.session_state.mode
    if mode == "real":
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'padding:.5rem .6rem;background:rgba(16,185,129,.08);'
            f'border:1px solid rgba(16,185,129,.25);border-radius:12px;'
            f'color:{T["success"]};font-weight:700;font-size:.8rem;letter-spacing:1.2px;">'
            f'<span style="width:8px;height:8px;border-radius:50%;'
            f'background:{T["success"]};"></span>REAL HARDWARE</div>',
            unsafe_allow_html=True,
        )
    elif mode == "manual":
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'padding:.5rem .6rem;background:rgba(245,158,11,.08);'
            f'border:1px solid rgba(245,158,11,.25);border-radius:12px;'
            f'color:{T["warning"]};font-weight:700;font-size:.8rem;letter-spacing:1.2px;">'
            f'<span style="width:8px;height:8px;border-radius:50%;'
            f'background:{T["warning"]};"></span>MANUAL SIMULATION</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'padding:.5rem .6rem;background:rgba(239,68,68,.08);'
            f'border:1px solid rgba(239,68,68,.25);border-radius:12px;'
            f'color:{T["danger"]};font-weight:700;font-size:.8rem;letter-spacing:1.2px;">'
            f'<span style="width:8px;height:8px;border-radius:50%;'
            f'background:{T["danger"]};"></span>OFFLINE</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="rail-label">Live Stats</div>', unsafe_allow_html=True)
    n_pts = len(st.session_state.air_h)
    n_alert = sum(1 for a in st.session_state.air_h if a > st.session_state.threshold)
    st.markdown(
        f'<div class="tile" style="margin-bottom:.5rem;">'
        f'<div class="v" style="color:{T["accent"]};">{n_pts}</div>'
        f'<div class="l">Readings</div></div>'
        f'<div class="tile">'
        f'<div class="v" style="color:{T["danger"]};">{n_alert}</div>'
        f'<div class="l">Air Alerts</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align:center;color:{T['muted']};font-size:.68rem;"
        f"margin-top:1rem;'>v2.1 · PREMIUM</p>",
        unsafe_allow_html=True,
    )

# ======================== TITLE BAR ========================
_now = datetime.now()
cyber_title(
    "AIRSENSE <span class='accent'>AI</span> · DASHBOARD",
    ["Monitor", "Detect", "Respond", "Breathe Safe",
     "MQ-135", "DHT22", "Air · Temp · Humidity", "ESP32"],
    _now.strftime("%a, %d %b %Y").upper(),
    _now.strftime("%I:%M %p"),
)

# ======================== IDLE GATE ========================
if st.session_state.mode == "idle":
    st.info("👉 Choose a mode from the sidebar:\n"
            "• **🌐 Connect Real ESP32** — read actual hardware\n"
            "• **🎯 Manual Simulation** — test threshold logic without hardware")
    with st.expander("❓ Where do I find the ESP32 IP?"):
        st.markdown("""
        1. Open **Arduino IDE → Tools → Serial Monitor** (115200 baud)
        2. Press **EN/RST** on ESP32
        3. Wait for `ESP32 IP: 192.168.1.42`
        4. Go to **Settings** → paste IP → **Test Connection**
        5. PC and ESP32 must be on the **same Wi-Fi**
        """)
    st.stop()

# ======================== FETCH DATA ========================
if st.session_state.mode == "real":
    data = fetch_real(st.session_state.esp_ip)
    if not data or "error" in data:
        st.error(f"⚠️ {data.get('error') if data else 'No data'}")
        st.stop()
elif st.session_state.mode == "manual":
    data = simulate(
        st.session_state.man_air,
        st.session_state.man_temp,
        st.session_state.man_hum,
        st.session_state.threshold,
        st.session_state.temp_max,
        st.session_state.hum_max,
    )
else:
    st.stop()

air = data["air"]
temp = data["temp"]
hum = data["hum"]
ts = data["timestamp"]
ip = data.get("ip", "—")
source = data.get("source", "REAL")

air_alert  = air > st.session_state.threshold
temp_alert = temp > st.session_state.temp_max
hum_alert  = hum > st.session_state.hum_max
any_danger = air_alert or temp_alert or hum_alert

st.session_state.air_h.append(air)
st.session_state.temp_h.append(temp)
st.session_state.hum_h.append(hum)
st.session_state.time_h.append(ts)

# ======================== KPI CARDS ========================
total = len(st.session_state.air_h)
alerts = sum(1 for a in st.session_state.air_h if a > st.session_state.threshold)
safe = total - alerts
safety_pct = (safe / total * 100) if total else 100

spark_a = list(st.session_state.air_h)[-20:] or [0, 0]
spark_t = list(st.session_state.temp_h)[-20:] or [0, 0]
spark_h = list(st.session_state.hum_h)[-20:] or [0, 0]

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "AIR QUALITY", air, f"limit {st.session_state.threshold}",
     "up" if not air_alert else "down", "🌫️", T['accent'], spark_a),
    (k2, "TEMPERATURE", f"{temp}°C", f"limit {st.session_state.temp_max}°C",
     "up" if not temp_alert else "down", "🌡️", T['danger'], spark_t),
    (k3, "HUMIDITY", f"{hum}%", f"limit {st.session_state.hum_max}%",
     "up" if not hum_alert else "down", "💧", T['success'], spark_h),
    (k4, "SAFETY SCORE", f"{safety_pct:.0f}%", f"{alerts} alerts",
     "up" if alerts == 0 else "down", "🛡️", T['accent_2'], spark_a),
]

for col, label, value, delta, kind, icon, color, spark in kpis:
    with col:
        st.markdown(
            f'<div class="kpi fade">'
            f'<div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-delta kpi-{kind}">'
            f'{"▲" if kind=="up" else "▼"} {delta}</div>'
            f'{sparkline_svg(spark, color)}'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ======================== ALERT BANNER ========================
if any_danger:
    triggers = []
    if air_alert:
        triggers.append(f"Air <b>{air}</b> &gt; {st.session_state.threshold}")
    if temp_alert:
        triggers.append(f"Temp <b>{temp}°C</b> &gt; {st.session_state.temp_max}°C")
    if hum_alert:
        triggers.append(f"Humidity <b>{hum}%</b> &gt; {st.session_state.hum_max}%")
    st.markdown(
        f'<div class="alert-banner danger">'
        f'<div style="font-size:52px;">🚨</div>'
        f'<div>'
        f'<div class="alert-text-main">DANGER DETECTED</div>'
        f'<div class="alert-text-sub">Triggered by: {" &nbsp;·&nbsp; ".join(triggers)}'
        f'<br>Red LED ON &nbsp;·&nbsp; Buzzer ACTIVE &nbsp;·&nbsp; at <b>{ts}</b></div>'
        f'<div class="led-row">'
        f'<div class="led-item"><span class="led"></span> Green LED OFF</div>'
        f'<div class="led-item"><span class="led on-red"></span> Red LED ON</div>'
        f'<div class="led-item"><span class="led on-buzz"></span> Buzzer ON</div>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="alert-banner safe">'
        f'<div style="font-size:52px;">✅</div>'
        f'<div>'
        f'<div class="alert-text-main">ALL CLEAR — ALL SENSORS IN SAFE RANGE</div>'
        f'<div class="alert-text-sub">Air <b>{air}</b> ≤ {st.session_state.threshold} '
        f'&nbsp;·&nbsp; Temp <b>{temp}°C</b> ≤ {st.session_state.temp_max}°C '
        f'&nbsp;·&nbsp; Humidity <b>{hum}%</b> ≤ {st.session_state.hum_max}%</div>'
        f'<div class="led-row">'
        f'<div class="led-item"><span class="led on-green"></span> Green LED ON</div>'
        f'<div class="led-item"><span class="led"></span> Red LED OFF</div>'
        f'<div class="led-item"><span class="led"></span> Buzzer OFF</div>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )

# ======================== BIG READOUTS ========================
st.markdown(
    f'<div class="readout-grid">'
    f'<div class="readout-box">'
    f'<div class="readout-label">Air Quality</div>'
    f'<div class="big-readout" style="color:{"#ef4444" if air_alert else "var(--text)"};">'
    f'{air}<span class="unit">ppm</span></div></div>'
    f'<div class="readout-box">'
    f'<div class="readout-label">Temperature</div>'
    f'<div class="big-readout" style="color:{"#ef4444" if temp_alert else "var(--text)"};">'
    f'{temp}<span class="unit">°C</span></div></div>'
    f'<div class="readout-box">'
    f'<div class="readout-label">Humidity</div>'
    f'<div class="big-readout" style="color:{"#ef4444" if hum_alert else "var(--text)"};">'
    f'{hum}<span class="unit">%</span></div></div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ======================== MAIN CHART ========================
st.markdown(
    '<div class="panel fade">'
    '<div class="panel-title"><h3>All-Sensor Trends</h3>'
    '<span class="pill">LIVE</span></div></div>',
    unsafe_allow_html=True,
)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(st.session_state.time_h),
    y=list(st.session_state.air_h),
    mode="lines+markers",
    name="Air (ppm)",
    line=dict(color="#5b6cff", width=3, shape="spline"),
))
fig.add_trace(go.Scatter(
    x=list(st.session_state.time_h),
    y=list(st.session_state.temp_h),
    mode="lines+markers",
    name="Temp (°C)",
    line=dict(color="#ef4444", width=3, shape="spline"),
))
fig.add_trace(go.Scatter(
    x=list(st.session_state.time_h),
    y=list(st.session_state.hum_h),
    mode="lines+markers",
    name="Humidity (%)",
    line=dict(color="#10b981", width=3, shape="spline"),
))
fig.add_hline(
    y=st.session_state.threshold,
    line_dash="dash",
    line_color="#ef4444",
    annotation_text=f"Air threshold {st.session_state.threshold}",
    annotation_position="top right",
)
fig.update_layout(
    height=380,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#475569"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(226,232,240,0.5)"),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ======================== ACTIVE LIMITS ========================
st.markdown(
    '<div class="panel fade">'
    '<div class="panel-title"><h3>Active Limits</h3>'
    '<span class="pill">SETTINGS</span></div></div>',
    unsafe_allow_html=True,
)

tc1, tc2, tc3 = st.columns(3)
with tc1:
    st.markdown(
        f'<div class="tile">'
        f'<div class="v" style="color:{T["accent"]};">{st.session_state.threshold}</div>'
        f'<div class="l">🌫️ Air Limit (ppm)</div></div>',
        unsafe_allow_html=True,
    )
with tc2:
    st.markdown(
        f'<div class="tile">'
        f'<div class="v" style="color:{T["danger"]};">{st.session_state.temp_max}</div>'
        f'<div class="l">🌡️ Temp Limit (°C)</div></div>',
        unsafe_allow_html=True,
    )
with tc3:
    st.markdown(
        f'<div class="tile">'
        f'<div class="v" style="color:{T["success"]};">{st.session_state.hum_max}</div>'
        f'<div class="l">💧 Humidity Limit (%)</div></div>',
        unsafe_allow_html=True,
    )

# ======================== RECENT READINGS ========================
st.markdown(
    '<div class="panel fade">'
    '<div class="panel-title"><h3>Recent Readings</h3>'
    '<span class="pill">SESSION</span></div></div>',
    unsafe_allow_html=True,
)

n_recent = min(8, len(st.session_state.air_h))
if n_recent > 0:
    df = pd.DataFrame({
        "Time": list(st.session_state.time_h)[-n_recent:][::-1],
        "Air (ppm)": list(st.session_state.air_h)[-n_recent:][::-1],
        "Temp (°C)": list(st.session_state.temp_h)[-n_recent:][::-1],
        "Humidity (%)": list(st.session_state.hum_h)[-n_recent:][::-1],
    })
    df["Status"] = df.apply(
        lambda r: "POOR" if (
            r["Air (ppm)"] > st.session_state.threshold or
            r["Temp (°C)"] > st.session_state.temp_max or
            r["Humidity (%)"] > st.session_state.hum_max
        ) else "OK",
        axis=1,
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

# ======================== FOOTER ========================
st.markdown("---")
st.markdown(
    f'<div style="text-align:center;color:{T["muted"]};font-size:.8rem;">'
    f'<span style="font-family:Sora;font-weight:800;letter-spacing:2px;'
    f'background:linear-gradient(90deg,{T["accent"]},{T["accent_2"]},#ec4899);'
    f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
    f'AIRSENSE AI</span> · 3-Sensor Monitoring</div>',
    unsafe_allow_html=True,
)

# ======================== AUTO REFRESH ========================
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=3000, key="auto_refresh")
except ImportError:
    pass