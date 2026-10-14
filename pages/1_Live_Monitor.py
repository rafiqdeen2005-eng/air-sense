import streamlit as st
from datetime import datetime
from esp32_client import fetch_real, simulate
from assets.theme_helper import load_css, cyber_title

st.set_page_config(page_title="Live Monitor · AirSense AI",
                   page_icon="🌿", layout="wide")

for k, v in {
    "theme": "light", "mode": "idle", "esp_ip": "",
    "threshold": 1800, "temp_max": 35.0, "hum_max": 80.0,
    "man_air": 800, "man_temp": 26.0, "man_hum": 55.0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

load_css()

_now = datetime.now()
cyber_title("AIRSENSE <span class='accent'>AI</span> · LIVE MONITOR",
            ["Snapshot", "Raw JSON", "3 Sensors", "Real-Time"],
            _now.strftime("%a, %d %b %Y").upper(),
            _now.strftime("%I:%M %p"))

st.markdown('<div class="sec-title fade">📊 Live Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Real-time snapshot from your ESP32 (or simulated).</div>', unsafe_allow_html=True)

mode = st.session_state.mode
if mode == "real":
    data = fetch_real(st.session_state.esp_ip)
elif mode == "manual":
    data = simulate(
        st.session_state.man_air, st.session_state.man_temp, st.session_state.man_hum,
        st.session_state.threshold, st.session_state.temp_max, st.session_state.hum_max,
    )
else:
    st.warning("⚠️ No mode active. Choose a mode from the sidebar.")
    st.stop()

if not data or "error" in data:
    st.error(f"⚠️ {data.get('error') if data else 'No data'}")
    st.stop()

air = data["air"]; temp = data["temp"]; hum = data["hum"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("🌫️ Air Quality", f"{air} ppm")
c2.metric("🌡️ Temperature", f"{temp} °C")
c3.metric("💧 Humidity", f"{hum} %")
c4.metric("📡 Source", data.get("source", "—"))

if data.get("air_alert") or data.get("temp_alert") or data.get("hum_alert"):
    st.error("🚨 DANGER — sensor above limit")
else:
    st.success("✅ All sensors within safe range")

st.markdown("#### 🔎 Raw Sensor JSON")
st.json(data)