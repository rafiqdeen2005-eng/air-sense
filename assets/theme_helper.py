import streamlit as st
import streamlit.components.v1 as components
from assets.logo import LEAF_LOGO_SVG

# ====================== THEME TOKENS ======================
LIGHT_VARS = """
--bg-1:#e0f2fe; --bg-2:#ede9fe; --bg-3:#f7f9fd; --bg-4:#f1f5f9;
--surface:#ffffff; --surface-alt:#fbfcff; --border:#e6eaf2;
--text:#0b1220; --text-2:#475569; --muted:#7c8aa5;
--accent:#5b6cff; --accent-2:#8b5cf6; --accent-3:#06b6d4;
--success:#10b981; --danger:#ef4444; --warning:#f59e0b;
--grid-line:rgba(91,108,255,0.08); --chip-bg:#f1f5f9;
--shadow:0 10px 30px rgba(15,23,42,.06);
--shadow-hover:0 18px 44px rgba(91,108,255,.18);
--rail-active-bg:linear-gradient(135deg,#eef2ff 0%,#f5f3ff 100%);
--rail-active-txt:#3b4cca;
--sidebar-bg:#ffffff; --sidebar-border:#e6eaf2; --title-color:#0b1220;
"""

DARK_VARS = """
--bg-1:#132049; --bg-2:#221043; --bg-3:#0a0f1f; --bg-4:#070b16;
--surface:#111a2e; --surface-alt:#0d1526; --border:#1e2a44;
--text:#eef2ff; --text-2:#a5b0c7; --muted:#8a97b5;
--accent:#7c8dff; --accent-2:#a78bfa; --accent-3:#22d3ee;
--success:#10b981; --danger:#ef4444; --warning:#f59e0b;
--grid-line:rgba(124,141,255,0.10); --chip-bg:#0f1a30;
--shadow:0 10px 30px rgba(0,0,0,.5);
--shadow-hover:0 18px 44px rgba(124,141,255,.35);
--rail-active-bg:linear-gradient(135deg,#1e2a5a 0%,#2a1e5a 100%);
--rail-active-txt:#c7d2fe;
--sidebar-bg:#0d1526; --sidebar-border:#1e2a44; --title-color:#eef2ff;
"""


def load_css():
    """Inject theme variables + base CSS."""
    theme = st.session_state.get("theme", "light")
    vars_block = DARK_VARS if theme == "dark" else LIGHT_VARS

    with open("assets/style.css") as f:
        base_css = f.read()

    st.markdown(
        f"<style>:root {{ {vars_block} }}</style>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<style>{base_css}</style>", unsafe_allow_html=True)


# ====================== FULLSCREEN SPLASH ======================
def show_splash_once():
    """
    Fullscreen overlay splash — injected into parent document via JS.
    Returns True  → caller should time.sleep + rerun
    Returns False → splash already dismissed
    """
    if st.session_state.get("splash_done", False):
        return False

    splash_html = """
    <script>
    (function () {
        try {
            const doc = window.parent.document;

            // Remove any leftover splash
            const old = doc.getElementById('as-fullscreen-splash');
            if (old) old.remove();

            // Build the overlay
            const el = doc.createElement('div');
            el.id = 'as-fullscreen-splash';
            el.innerHTML = `
                <style>
                    #as-fullscreen-splash {
                        position: fixed !important;
                        top: 0 !important;
                        left: 0 !important;
                        width: 100vw !important;
                        height: 100vh !important;
                        z-index: 2147483647 !important;
                        background:
                            radial-gradient(800px 400px at 30% 30%, rgba(91,108,255,.35), transparent 60%),
                            radial-gradient(700px 400px at 70% 70%, rgba(139,92,246,.35), transparent 60%),
                            linear-gradient(135deg, #0a0f1f 0%, #1a1040 50%, #0a0f1f 100%);
                        display: flex !important;
                        align-items: center;
                        justify-content: center;
                        font-family: 'Inter', sans-serif;
                        animation: asFadeOut 4.2s ease-in-out forwards;
                    }
                    @keyframes asFadeOut {
                        0%   { opacity: 1; }
                        75%  { opacity: 1; }
                        100% { opacity: 0; }
                    }
                    #as-fullscreen-splash .as-wrap {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        gap: 24px;
                    }
                    #as-fullscreen-splash .as-logo {
                        width: 240px;
                        height: 240px;
                        filter: drop-shadow(0 0 40px rgba(139,92,246,.65));
                    }
                    #as-fullscreen-splash .as-ring {
                        transform-origin: 200px 200px;
                        animation: asSpinCW 6s linear infinite;
                    }
                    #as-fullscreen-splash .as-ring-rev {
                        transform-origin: 200px 200px;
                        animation: asSpinCCW 9s linear infinite;
                    }
                    @keyframes asSpinCW  { to { transform: rotate(360deg); } }
                    @keyframes asSpinCCW { to { transform: rotate(-360deg); } }

                    #as-fullscreen-splash .as-leaf {
                        transform-origin: 200px 200px;
                        animation: asBreathe 3s ease-in-out infinite;
                    }
                    @keyframes asBreathe {
                        0%, 100% { transform: scale(1); }
                        50%      { transform: scale(1.04); }
                    }

                    #as-fullscreen-splash .as-wave-1 {
                        stroke-dasharray: 250; stroke-dashoffset: 250;
                        animation: asDraw 2.6s ease-out .8s forwards,
                                   asWavePulse 2.4s ease-in-out 3.4s infinite;
                    }
                    #as-fullscreen-splash .as-wave-2 {
                        stroke-dasharray: 250; stroke-dashoffset: 250;
                        animation: asDraw 2.6s ease-out 1.3s forwards,
                                   asWavePulse 2.6s ease-in-out 3.8s infinite;
                    }
                    @keyframes asDraw {
                        0%   { stroke-dashoffset: 250; opacity: 0; }
                        15%  { opacity: 1; }
                        100% { stroke-dashoffset: 0; opacity: 1; }
                    }
                    @keyframes asWavePulse {
                        0%, 100% { transform: translateY(0); opacity: .9; }
                        50%      { transform: translateY(-4px); opacity: 1; }
                    }

                    #as-fullscreen-splash .as-dot {
                        transform-origin: 262px 140px;
                        animation: asDotPulse 1.6s ease-in-out 1.6s infinite;
                    }
                    @keyframes asDotPulse {
                        0%   { opacity: 0; transform: scale(.4); }
                        20%  { opacity: 1; transform: scale(1); }
                        50%  { opacity: .5; transform: scale(1.6); }
                        100% { opacity: 0; transform: scale(.4); }
                    }

                    #as-fullscreen-splash .as-sparkles circle {
                        animation: asTwinkle 2.4s ease-in-out infinite;
                    }
                    #as-fullscreen-splash .as-sparkles circle:nth-child(1) { animation-delay: 0s; }
                    #as-fullscreen-splash .as-sparkles circle:nth-child(2) { animation-delay: .4s; }
                    #as-fullscreen-splash .as-sparkles circle:nth-child(3) { animation-delay: .8s; }
                    #as-fullscreen-splash .as-sparkles circle:nth-child(4) { animation-delay: 1.2s; }
                    @keyframes asTwinkle {
                        0%, 100% { opacity: .2; transform: scale(.6); }
                        50%      { opacity: 1;  transform: scale(1.3); }
                    }

                    #as-fullscreen-splash .as-brand {
                        font-family: 'Sora', sans-serif;
                        font-size: 3rem;
                        font-weight: 900;
                        letter-spacing: 4px;
                        background: linear-gradient(90deg, #5b6cff, #8b5cf6, #22d3ee, #5b6cff);
                        background-size: 300% auto;
                        -webkit-background-clip: text;
                        background-clip: text;
                        -webkit-text-fill-color: transparent;
                        opacity: 0;
                        animation: asBrandIn 1.2s ease-out 1.2s forwards,
                                   asShine 3s linear infinite 2.4s;
                    }
                    @keyframes asBrandIn {
                        from { opacity: 0; transform: translateY(20px); letter-spacing: 14px; }
                        to   { opacity: 1; transform: translateY(0);    letter-spacing: 4px; }
                    }
                    @keyframes asShine {
                        to { background-position: 300% center; }
                    }

                    #as-fullscreen-splash .as-tag {
                        font-size: 1rem;
                        letter-spacing: 6px;
                        font-weight: 700;
                        color: #a5b0c7;
                        text-transform: uppercase;
                        opacity: 0;
                        animation: asTagIn 1.2s ease-out 1.8s forwards;
                    }
                    @keyframes asTagIn {
                        from { opacity: 0; transform: translateY(12px); }
                        to   { opacity: 1; transform: translateY(0); }
                    }
                </style>

                <div class="as-wrap">
                    <svg class="as-logo" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="asRingGrad" x1="0" y1="0" x2="1" y2="1">
                                <stop offset="0%"   stop-color="#5b6cff"/>
                                <stop offset="50%"  stop-color="#8b5cf6"/>
                                <stop offset="100%" stop-color="#22d3ee"/>
                            </linearGradient>
                            <linearGradient id="asLeafInner" x1="0" y1="0" x2="1" y2="1">
                                <stop offset="0%"   stop-color="#ffffff"/>
                                <stop offset="100%" stop-color="#cfe9ff"/>
                            </linearGradient>
                            <radialGradient id="asGlow" cx="50%" cy="50%" r="50%">
                                <stop offset="0%"   stop-color="#8b5cf6" stop-opacity="0.55"/>
                                <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0"/>
                            </radialGradient>
                            <filter id="asSoftGlow" x="-50%" y="-50%" width="200%" height="200%">
                                <feGaussianBlur stdDeviation="6" result="blur"/>
                                <feMerge>
                                    <feMergeNode in="blur"/>
                                    <feMergeNode in="SourceGraphic"/>
                                </feMerge>
                            </filter>
                        </defs>

                        <g class="as-ring" filter="url(#asSoftGlow)">
                            <circle cx="200" cy="200" r="140" fill="none"
                                    stroke="url(#asRingGrad)"
                                    stroke-width="3" stroke-dasharray="18 12" opacity="0.85"/>
                        </g>
                        <g class="as-ring-rev" filter="url(#asSoftGlow)">
                            <circle cx="200" cy="200" r="118" fill="none"
                                    stroke="url(#asRingGrad)"
                                    stroke-width="2" stroke-dasharray="6 10" opacity="0.6"/>
                        </g>
                        <circle cx="200" cy="200" r="100" fill="url(#asGlow)"/>

                        <g class="as-leaf" filter="url(#asSoftGlow)">
                            <path d="M200 100 C140 100 100 150 100 200 C100 250 140 300 200 300
                                     C260 300 300 250 300 200 C300 150 260 100 200 100 Z"
                                  fill="none" stroke="url(#asLeafInner)"
                                  stroke-width="4" opacity="0.55"/>
                            <path d="M200 118 C156 118 118 158 118 200 C118 242 156 282 200 282
                                     C244 282 282 242 282 200 C282 158 244 118 200 118 Z"
                                  fill="url(#asLeafInner)" opacity="0.18"/>
                            <path d="M200 122 C200 200 200 240 200 290"
                                  stroke="url(#asLeafInner)"
                                  stroke-width="2.5" opacity="0.7"/>
                        </g>

                        <path class="as-wave-1" d="M118 205 Q150 180 200 205 T 282 205"
                              fill="none" stroke="#ffffff" stroke-width="4"
                              stroke-linecap="round" opacity="0"/>
                        <path class="as-wave-2" d="M118 235 Q150 210 200 235 T 282 235"
                              fill="none" stroke="#ffffff" stroke-width="3"
                              stroke-linecap="round" opacity="0"/>

                        <circle class="as-dot" cx="262" cy="140" r="7"
                                fill="#ffffff" opacity="0"/>

                        <g class="as-sparkles">
                            <circle cx="90"  cy="120" r="3"   fill="#ffffff" opacity="0.9"/>
                            <circle cx="320" cy="130" r="2.5" fill="#ffffff" opacity="0.85"/>
                            <circle cx="100" cy="290" r="2.5" fill="#ffffff" opacity="0.85"/>
                            <circle cx="310" cy="280" r="3"   fill="#ffffff" opacity="0.9"/>
                        </g>
                    </svg>

                    <div class="as-brand">AIRSENSE AI</div>
                    <div class="as-tag">Quality Console · Loading</div>
                </div>
            `;
            doc.body.appendChild(el);

            // Remove after animation completes
            setTimeout(function () {
                const e = doc.getElementById('as-fullscreen-splash');
                if (e) e.remove();
            }, 4400);

        } catch (err) {
            console.error('Splash injection failed:', err);
        }
    })();
    </script>
    <div style="height:1px;"></div>
    """

    components.html(splash_html, height=1, scrolling=False)
    return True


# ====================== CYBER TITLE BAR ======================
def cyber_title(page_title: str, ticker_items: list, clock_date: str, clock_time: str):
    ticker_html = "".join([f"<span>{t}</span>" for t in ticker_items] * 2)
    st.markdown(f"""
    <div class="cyber-bar fade">
        <div class="grid-layer"></div>
        <div class="aurora"><span class="a1"></span><span class="a2"></span><span class="a3"></span></div>
        <svg class="waves" viewBox="0 0 1200 140" preserveAspectRatio="none">
            <path class="w1" d="M0,100 C180,60 320,120 520,80 C720,40 900,110 1200,70" />
            <path class="w2" d="M0,80  C180,120 340,40 540,90 C740,130 920,50 1200,90" />
            <path class="w3" d="M0,120 C180,90 340,140 540,100 C740,60 920,130 1200,100" />
        </svg>
        <div class="particles">
            <span class="p1"></span><span class="p2"></span><span class="p3"></span><span class="p4"></span>
            <span class="p5"></span><span class="p6"></span><span class="p7"></span><span class="p8"></span>
        </div>
        <div class="scan"></div>
        <div class="inner">
            <div class="brand-logo-wrap">{LEAF_LOGO_SVG}</div>
            <div class="title-block">
                <h1>{page_title}</h1>
                <div class="ticker"><div class="ticker-track">{ticker_html}</div></div>
            </div>
            <div class="radar-wrap">
                <div class="radar"></div>
                <div class="radar-text">
                    <div class="t1">3-Sensor Monitoring</div>
                    <div class="t2">Live</div>
                </div>
            </div>
            <div class="clock-wrap">
                <div class="date">{clock_date}</div>
                <div class="time">{clock_time}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)