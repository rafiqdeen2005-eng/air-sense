import streamlit as st
from datetime import datetime
from esp32_client import test_connection
from assets.theme_helper import load_css, cyber_title

st.set_page_config(page_title="Settings · AirSense AI",
                   page_icon="🌿", layout="wide")

for k, v in {
    "theme": "light", "mode": "idle", "esp_ip": "",
    "threshold": 1800, "temp_max": 35.0, "hum_max": 80.0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

load_css()

_now = datetime.now()
cyber_title("AIRSENSE <span class='accent'>AI</span> · SETTINGS",
            ["ESP32 Connection", "Thresholds", "System Info"],
            _now.strftime("%a, %d %b %Y").upper(),
            _now.strftime("%I:%M %p"))

st.markdown('<div class="sec-title fade">⚙️ Settings</div>', unsafe_allow_html=True)

st.markdown('<div class="panel fade"><div class="panel-title"><h3>🌐 ESP32 Connection</h3><span class="pill">WIFI</span></div></div>', unsafe_allow_html=True)
ip = st.text_input("ESP32 IP address", value=st.session_state.esp_ip, placeholder="192.168.1.42")
c1, c2 = st.columns(2)
with c1:
    if st.button("🧪 Test Connection", use_container_width=True):
        ok, msg = test_connection(ip)
        (st.success if ok else st.error)(msg)
with c2:
    if st.button("💾 Save & Connect", use_container_width=True):
        st.session_state.esp_ip = ip.strip()
        ok, msg = test_connection(ip.strip())
        if ok:
            st.session_state.mode = "real"
            st.success(msg)
        else:
            st.error(msg)

st.markdown("---")
st.markdown('<div class="panel fade"><div class="panel-title"><h3>🎚️ Alarm Thresholds</h3><span class="pill">LIVE</span></div></div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.session_state.threshold = st.slider("🌫️ Air Quality Max (ppm)", 500, 4000, st.session_state.threshold, 50)
with c2:
    st.session_state.temp_max = st.slider("🌡️ Temperature Max (°C)", 0.0, 60.0, st.session_state.temp_max, 0.5)
with c3:
    st.session_state.hum_max = st.slider("💧 Humidity Max (%)", 0.0, 100.0, st.session_state.hum_max, 1.0)
st.caption("⚠️ To make the ESP32's LED/buzzer use these thresholds, update the same values in `air_quality_esp32.ino`.")

st.markdown("---")
st.markdown('<div class="panel fade"><div class="panel-title"><h3>ℹ️ System Info</h3></div></div>', unsafe_allow_html=True)
st.write(f"**Mode:** `{st.session_state.mode.upper()}`")
st.write(f"**IP:** `{st.session_state.esp_ip or '—'}`")
st.write(f"**Air limit:** `{st.session_state.threshold}` ppm")
st.write(f"**Temp limit:** `{st.session_state.temp_max}` °C")
st.write(f"**Humidity limit:** `{st.session_state.hum_max}` %")