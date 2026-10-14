import streamlit as st
from datetime import datetime
from esp32_client import test_connection
from assets.theme_helper import load_css, cyber_title

st.set_page_config(page_title="Manual Test · AirSense AI",
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
cyber_title("AIRSENSE <span class='accent'>AI</span> · MANUAL TEST",
            ["Simulate", "3 Sensors", "Test Alarms", "No Hardware"],
            _now.strftime("%a, %d %b %Y").upper(),
            _now.strftime("%I:%M %p"))

st.markdown('<div class="sec-title fade">🎯 Manual Test Console</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">One slider per sensor — alarm fires when the reading goes above it.</div>', unsafe_allow_html=True)

st.markdown('<div class="panel fade"><div class="panel-title"><h3>🎚️ Alarm Thresholds</h3><span class="pill">LIVE</span></div></div>', unsafe_allow_html=True)
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown('<div class="feature-card"><div class="feature-label">🌫️ Air Quality Threshold</div><div class="feature-desc">Alarm if reading exceeds this value</div></div>', unsafe_allow_html=True)
    st.session_state.threshold = st.slider("Air Quality", 500, 4000, st.session_state.threshold, 50, label_visibility="collapsed")
with t2:
    st.markdown('<div class="feature-card"><div class="feature-label">🌡️ Temperature Threshold</div><div class="feature-desc">Alarm if temperature exceeds this value</div></div>', unsafe_allow_html=True)
    st.session_state.temp_max = st.slider("Temperature Max", 0.0, 60.0, st.session_state.temp_max, 0.5, label_visibility="collapsed")
with t3:
    st.markdown('<div class="feature-card"><div class="feature-label">💧 Humidity Threshold</div><div class="feature-desc">Alarm if humidity exceeds this value</div></div>', unsafe_allow_html=True)
    st.session_state.hum_max = st.slider("Humidity Max", 0.0, 100.0, st.session_state.hum_max, 1.0, label_visibility="collapsed")

st.markdown("---")
st.markdown('<div class="panel fade"><div class="panel-title"><h3>🧪 Simulated Sensor Input</h3><span class="pill">MANUAL</span></div></div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.session_state.man_air = st.slider("Simulated Air", 0, 4000, st.session_state.man_air, 10)
with c2:
    st.session_state.man_temp = st.slider("Simulated Temperature", 0.0, 60.0, st.session_state.man_temp, 0.5)
with c3:
    st.session_state.man_hum = st.slider("Simulated Humidity", 0.0, 100.0, st.session_state.man_hum, 1.0)

if st.button("🎯 Activate Manual Mode", use_container_width=True):
    st.session_state.mode = "manual"
    st.success("✅ Manual mode active.")

st.markdown("---")
st.markdown('<div class="sec-title">👁️ Live Preview</div>', unsafe_allow_html=True)
sim_air = st.session_state.man_air
sim_temp = st.session_state.man_temp
sim_hum = st.session_state.man_hum

air_alert  = sim_air > st.session_state.threshold
temp_alert = sim_temp > st.session_state.temp_max
hum_alert  = sim_hum > st.session_state.hum_max
any_danger = air_alert or temp_alert or hum_alert

st.markdown(f'<div class="readout-grid"><div class="readout-box"><div class="readout-label">Air Quality</div><div class="big-readout" style="color:{"#ef4444" if air_alert else "var(--text)"};">{sim_air}<span class="unit">ppm</span></div><div style="color:var(--muted);font-size:12px;margin-top:6px;">Limit: {st.session_state.threshold}</div></div><div class="readout-box"><div class="readout-label">Temperature</div><div class="big-readout" style="color:{"#ef4444" if temp_alert else "var(--text)"};">{sim_temp}<span class="unit">°C</span></div><div style="color:var(--muted);font-size:12px;margin-top:6px;">Limit: {st.session_state.temp_max}</div></div><div class="readout-box"><div class="readout-label">Humidity</div><div class="big-readout" style="color:{"#ef4444" if hum_alert else "var(--text)"};">{sim_hum}<span class="unit">%</span></div><div style="color:var(--muted);font-size:12px;margin-top:6px;">Limit: {st.session_state.hum_max}</div></div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="panel fade" style="padding:1.2rem 1.3rem;"><div class="panel-title"><h3>💡 Hardware Simulation</h3><span class="pill" style="color:{"#ef4444" if any_danger else "#10b981"};background:{"rgba(239,68,68,.12)" if any_danger else "rgba(16,185,129,.12)"};">{"DANGER" if any_danger else "SAFE"}</span></div><div class="led-row" style="gap:30px;font-size:15px;"><div class="led-item"><span class="led {"on-green" if not any_danger else ""}"></span>🟢 Green LED → {"ON" if not any_danger else "OFF"}</div><div class="led-item"><span class="led {"on-red" if any_danger else ""}"></span>🔴 Red LED → {"ON" if any_danger else "OFF"}</div><div class="led-item"><span class="led {"on-buzz" if any_danger else ""}"></span>🔔 Buzzer → {"ON" if any_danger else "OFF"}</div></div></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="panel fade"><div class="panel-title"><h3>🌐 Real ESP32 Test</h3><span class="pill">HARDWARE</span></div></div>', unsafe_allow_html=True)
ip = st.text_input("ESP32 IP address", value=st.session_state.get("esp_ip", ""), placeholder="192.168.1.42")
if st.button("🧪 Test Connection", use_container_width=True):
    ok, msg = test_connection(ip)
    (st.success if ok else st.error)(msg)
    if ok:
        st.session_state.esp_ip = ip.strip()
        st.session_state.mode = "real"