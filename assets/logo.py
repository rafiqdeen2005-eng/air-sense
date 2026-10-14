# Small leaf logo used in sidebar and title bar
LEAF_LOGO_SVG = """
<svg class="brand-logo-svg" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="leafGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="100%" stop-color="#cfe9ff"/>
        </linearGradient>
    </defs>
    <path d="M32 6 C18 6 8 18 8 32 C8 46 18 58 32 58 C46 58 56 46 56 32 C56 18 46 6 32 6 Z"
          fill="none" stroke="url(#leafGrad)" stroke-width="2.5" opacity="0.5"/>
    <path d="M32 12 C22 12 14 22 14 32 C14 42 22 52 32 52 C42 52 50 42 50 32 C50 22 42 12 32 12 Z"
          fill="url(#leafGrad)" opacity="0.15"/>
    <path d="M32 14 C32 30 32 40 32 52" stroke="url(#leafGrad)" stroke-width="1.5" opacity="0.6"/>
    <path d="M14 34 Q22 26 32 34 T 50 34"
          fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"
          stroke-dasharray="60" stroke-dashoffset="60"
          style="animation: drawWave 3s ease-in-out infinite alternate"/>
    <path d="M14 42 Q22 34 32 42 T 50 42"
          fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity="0.7"
          stroke-dasharray="60" stroke-dashoffset="60"
          style="animation: drawWave 3.5s ease-in-out infinite alternate"/>
    <circle cx="46" cy="20" r="4" fill="#ffffff" opacity="0.9"
            style="animation: pulseDot 1.8s ease-in-out infinite"/>
</svg>
"""