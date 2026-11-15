import streamlit as st
import numpy as np
import cv2
from PIL import Image
from skin_analyzer import SkinAnalyzer

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="DERMÉ ⋆｡˚ ✧",
    page_icon="🌷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Jost:wght@300;400;500&family=Dancing+Script:wght@400;600&display=swap');
    
    /* Hide Streamlit stuff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ---- Background with moving gradient ---- */
    .stApp {
        background: linear-gradient(-45deg, #fde8e4, #f5d5e0, #e8d5ec, #fde4d4, #f9e2d0);
        background-size: 400% 400%;
        animation: gradientShift 18s ease infinite;
        font-family: 'Jost', sans-serif;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating shapes background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(255, 192, 203, 0.3) 0%, transparent 25%),
            radial-gradient(circle at 80% 70%, rgba(221, 160, 221, 0.25) 0%, transparent 25%),
            radial-gradient(circle at 50% 50%, rgba(255, 218, 185, 0.2) 0%, transparent 30%);
        pointer-events: none;
        z-index: 0;
    }
    
    .block-container {
        padding-top: 1rem;
        max-width: 1200px;
        position: relative;
        z-index: 1;
    }
    
    /* ---- Floating sparkles ---- */
    .sparkle {
        position: fixed;
        pointer-events: none;
        font-size: 1.2rem;
        opacity: 0.6;
        animation: float 8s ease-in-out infinite;
        z-index: 0;
    }
    
    .sparkle:nth-child(1) { top: 10%; left: 5%; animation-delay: 0s; }
    .sparkle:nth-child(2) { top: 20%; right: 8%; animation-delay: 2s; }
    .sparkle:nth-child(3) { top: 60%; left: 3%; animation-delay: 4s; }
    .sparkle:nth-child(4) { top: 75%; right: 5%; animation-delay: 1s; }
    .sparkle:nth-child(5) { top: 40%; left: 7%; animation-delay: 3s; }
    .sparkle:nth-child(6) { top: 85%; left: 50%; animation-delay: 5s; }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.4; }
        50% { transform: translateY(-30px) rotate(180deg); opacity: 0.8; }
    }
    
    /* ---- Hero section ---- */
    .hero {
        text-align: center;
        padding: 3rem 2rem 2rem 2rem;
        position: relative;
        animation: fadeInDown 1.2s ease-out;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .tagline-top {
        font-family: 'Dancing Script', cursive;
        font-size: 1.5rem;
        color: #c48b9f;
        margin-bottom: 0.5rem;
        letter-spacing: 0.05rem;
    }
    
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 6.5rem;
        font-weight: 400;
        letter-spacing: 1rem;
        background: linear-gradient(135deg, #8b5a7a 0%, #c48b9f 50%, #d4a574 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.15); }
    }
    
    .hero-subtitle {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.5rem;
        color: #8b6f7c;
        margin-top: 1rem;
        letter-spacing: 0.1rem;
    }
    
    .ornament {
        color: #c48b9f;
        font-size: 1rem;
        margin: 1rem 0;
        letter-spacing: 1rem;
    }
    
    .hero-description {
        font-family: 'Jost', sans-serif;
        font-size: 1rem;
        color: #7a6168;
        margin: 1.5rem auto 0 auto !important;
        max-width: 550px;
        text-align: center;
        line-height: 1.8;
        font-weight: 300;
    }
    
    /* ---- Mood board grid (Pinterest style) ---- */
    .mood-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 2rem 0;
        animation: fadeInUp 1.4s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .mood-card {
        border-radius: 20px;
        padding: 2rem 1.2rem;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .mood-card::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    .mood-card:hover::before { opacity: 1; }
    .mood-card:hover { transform: translateY(-8px) rotate(-1deg); box-shadow: 0 20px 40px rgba(196, 139, 159, 0.25); }
    
    .mood-1 { background: linear-gradient(135deg, rgba(255,218,224,0.7), rgba(255,200,210,0.5)); }
    .mood-2 { background: linear-gradient(135deg, rgba(230,215,240,0.7), rgba(215,200,230,0.5)); }
    .mood-3 { background: linear-gradient(135deg, rgba(255,230,210,0.7), rgba(245,220,200,0.5)); }
    .mood-4 { background: linear-gradient(135deg, rgba(220,235,220,0.7), rgba(200,225,210,0.5)); }
    
    .mood-emoji {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
        display: block;
        animation: bounce 3s ease-in-out infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    .mood-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.3rem;
        color: #5a4551;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }
    
    .mood-text {
        font-size: 0.8rem;
        color: #8b6f7c;
        line-height: 1.5;
        font-weight: 300;
    }
    
    /* ---- Quote card ---- */
    .quote-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.6), rgba(255,240,245,0.4));
        backdrop-filter: blur(15px);
        padding: 2.5rem;
        border-radius: 25px;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.5);
        animation: fadeIn 1.6s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .quote-text {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.6rem;
        color: #7a5565;
        line-height: 1.5;
    }
    
    .quote-author {
        font-family: 'Dancing Script', cursive;
        font-size: 1.2rem;
        color: #c48b9f;
        margin-top: 1rem;
    }
    
    /* ---- Glass sections ---- */
    .glass-card {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px rgba(196, 139, 159, 0.15);
        margin: 1.5rem 0;
        animation: fadeInUp 1s ease-out;
    }
    
    .section-label {
        font-family: 'Dancing Script', cursive;
        font-size: 1.3rem;
        color: #c48b9f;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    
    .section-title {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        color: #5a4551;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* ---- Disclaimer (pinterest sticky-note style) ---- */
    .disclaimer {
        background: linear-gradient(135deg, #fff9e6, #fef3d0);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        font-size: 0.9rem;
        color: #8b7340;
        line-height: 1.7;
        position: relative;
        box-shadow: 0 4px 15px rgba(210, 180, 100, 0.15);
        transform: rotate(-0.5deg);
        transition: transform 0.3s;
        border: 1px dashed rgba(180, 140, 80, 0.3);
    }
    
    .disclaimer:hover { transform: rotate(0deg) scale(1.01); }
    
    .disclaimer-title {
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        color: #8b6914;
        margin-bottom: 0.5rem;
        font-size: 1.05rem;
    }
    
    /* ---- Streamlit components ---- */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 2px dashed #c48b9f;
        transition: all 0.3s;
    }
    
    [data-testid="stFileUploader"]:hover {
        background: rgba(255, 255, 255, 0.75);
        border-color: #8b5a7a;
    }
    
    [data-testid="stFileUploader"] section { background: transparent; border: none; }
    
    [data-testid="stFileUploader"] button, .stButton button {
        background: linear-gradient(135deg, #c48b9f, #8b5a7a) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 0.6rem 2rem !important;
        font-family: 'Jost', sans-serif !important;
        font-weight: 500 !important;
        letter-spacing: 0.1rem !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(196, 139, 159, 0.3) !important;
    }
    
    [data-testid="stFileUploader"] button:hover, .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(196, 139, 159, 0.5) !important;
    }
    
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px !important;
        font-family: 'Playfair Display', serif !important;
        color: #5a4551 !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
    }
    
    .stCheckbox {
        background: rgba(255, 255, 255, 0.5);
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* ---- Marquee ---- */
    .marquee-container {
        overflow: hidden;
        background: rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
        padding: 0.8rem 0;
        border-radius: 50px;
        margin: 1.5rem 0;
        border: 1px solid rgba(255,255,255,0.4);
    }
    
    .marquee {
        display: inline-block;
        white-space: nowrap;
        animation: scroll 25s linear infinite;
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.1rem;
        color: #8b5a7a;
    }
    
    @keyframes scroll {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    .marquee span { margin: 0 2rem; }
    
    /* ---- Footer ---- */
    .footer {
        text-align: center;
        padding: 3rem 0 1rem 0;
        color: #a08a94;
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
    }
    
    .footer-heart {
        font-size: 1.5rem;
        animation: heartbeat 1.5s ease-in-out infinite;
        display: inline-block;
    }
    
    @keyframes heartbeat {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
</style>

<!-- Floating sparkles -->
<div class="sparkle">✧</div>
<div class="sparkle">⋆</div>
<div class="sparkle">˚</div>
<div class="sparkle">✦</div>
<div class="sparkle">⋆</div>
<div class="sparkle">✧</div>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <div class="tagline-top">˗ˏˋ your skin story begins here ˎˊ˗</div>
    <h1 class="hero-title">DERMÉ</h1>
    <div class="ornament">✧ ⋆ ˚ ⋆ ✧</div>
    <p class="hero-subtitle">a soft little space for your skin</p>
    <p class="hero-description">
        upload a photo, discover your glow ✨ get gentle ingredient ideas, 
        dreamy routines & skincare wisdom — all tailored just for you.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- MARQUEE ----------------
st.markdown("""
<div class="marquee-container">
    <div class="marquee">
        <span>✿ glow from within</span>
        <span>˚ ༘ ♡ ⋆｡ gentle skincare</span>
        <span>✦ know your skin</span>
        <span>🌸 clean beauty</span>
        <span>⋆ self-care sunday</span>
        <span>✧ hydration is key</span>
        <span>🤍 you are radiant</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- MOOD BOARD ----------------
st.markdown("""
<div class="mood-grid">
    <div class="mood-card mood-1">
        <span class="mood-emoji">🌸</span>
        <div class="mood-title">Analyze</div>
        <div class="mood-text">AI reads your skin like a soft diary</div>
    </div>
    <div class="mood-card mood-2">
        <span class="mood-emoji">🪞</span>
        <div class="mood-title">Discover</div>
        <div class="mood-text">ingredients that love you back</div>
    </div>
    <div class="mood-card mood-3">
        <span class="mood-emoji">🫧</span>
        <div class="mood-title">Routine</div>
        <div class="mood-text">a ritual made just for you</div>
    </div>
    <div class="mood-card mood-4">
        <span class="mood-emoji">✨</span>
        <div class="mood-title">Glow</div>
        <div class="mood-text">bloom into your softest self</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- QUOTE ----------------
st.markdown("""
<div class="quote-card">
    <div class="quote-text">"your skin is telling a story —<br>let's listen softly."</div>
    <div class="quote-author">— dermé ♡</div>
</div>
""", unsafe_allow_html=True)

# ---------------- DISCLAIMER ----------------
st.markdown("""
<div class="disclaimer">
    <div class="disclaimer-title">🌼 a gentle reminder</div>
    DERMÉ is an experimental student project made with love. image-based estimates 
    can be inaccurate and are not medically validated. it does not diagnose or treat 
    skin conditions — please visit a real dermatologist for anything serious ♡
</div>
""", unsafe_allow_html=True)

# ---------------- PRIVACY ----------------
with st.expander("🔒  before you upload — privacy & consent"):
    st.markdown("""
    **📸 photo tips**  
    use a clear, front-facing photo in good lighting. no other people in the frame please!
    
    **🤍 your privacy matters**  
    your image is processed only during this session — we don't save your photos or results. 
    only upload if you're comfortable sharing with this experimental little app.
    """)
    consent = st.checkbox("i understand this is experimental & i consent ♡")

# ---------------- ANALYSIS HELPERS ----------------
def run_analysis(pil_image):
    """Run the real DERMÉ image analysis on an uploaded photo."""
    rgb = np.array(pil_image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]
    scale = min(900 / max(h, w), 1)
    if scale < 1:
        bgr = cv2.resize(bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return SkinAnalyzer(use_mediapipe=False).analyze(bgr, detailed=True)


def show_results(result):
    """Display the analysis report: score, concerns, ingredients and routines."""
    st.markdown('<div class="section-label">˗ˏˋ your report ˎˊ˗</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">your skin insights</div>', unsafe_allow_html=True)

    a, b, c = st.columns(3)
    a.metric("Image analysis score", f'{result.get("overall_score", 0):.0f}/100')
    b.metric("Estimated skin type", result.get("skin_type", {}).get("type", "Not available"))
    c.metric("Processing time", result.get("processing_time", "—"))
    st.caption("The score is an experimental image-processing output, not a clinical measure of skin health.")

    tone = result.get("skin_tone", {})
    if tone:
        undertone = tone.get("undertone", {})
        undertone = undertone.get("type", "Not available") if isinstance(undertone, dict) else undertone or "Not available"
        st.markdown("#### Skin tone estimate")
        st.write(f"**Category:** {tone.get('category', 'Not available')}  ·  **Undertone:** {undertone}")

    rec = result.get("recommendations", {})
    st.markdown("#### Potential concerns detected")
    concerns = rec.get("concerns", [])
    if concerns:
        for item in concerns:
            st.markdown(f"- **{item.get('name', 'Concern')}** — {item.get('severity', '')} · {item.get('details', '')}")
    else:
        st.write("No concerns were flagged by the project's current detection thresholds.")

    st.markdown("#### Ingredient ideas")
    ingredients = rec.get("recommended_ingredients", [])
    if ingredients:
        for item in ingredients:
            if isinstance(item, dict):
                name = item.get("name", item.get("ingredient", "Ingredient"))
                why = item.get("benefits", item.get("reason", "Explore suitability and tolerance before use."))
                st.markdown(f"- **{name}** — {why}")
            else:
                st.markdown(f"- {item}")
    else:
        st.write("No specific ingredient suggestions were generated.")

    routine = result.get("routine", {})
    st.markdown("#### Routine ideas")
    for title, key in [("Morning routine", "morning_routine"),
                       ("Night routine", "night_routine"),
                       ("Weekly treatments", "weekly_treatments")]:
        with st.expander(title, expanded=(key == "morning_routine")):
            steps = routine.get(key, [])
            if steps:
                for step in steps:
                    if isinstance(step, dict):
                        st.markdown(f"**{step.get('step', '')} · {step.get('product', step.get('name', ''))}**")
                        st.write(f"Ingredient: {step.get('ingredient', '—')}")
                        st.caption(step.get("how_to", step.get("description", "")))
                    else:
                        st.write(step)
            else:
                st.write("No routine steps available.")

    tips = rec.get("specific_tips", [])
    if tips:
        st.markdown("#### General tips")
        for tip in tips:
            if isinstance(tip, dict):
                title = tip.get("title", "Tip")
                text = tip.get("tip", "")
                urgency = tip.get("urgency", "")
                label = f" _(priority: {urgency})_" if urgency else ""
                st.markdown(f"- **{title}** — {text}{label}")
            else:
                st.markdown(f"- {tip}")

    st.info("Introduce skincare ingredients gradually, patch test new products, and see a qualified "
            "dermatologist for persistent, painful, worsening or concerning skin issues.")


# ---------------- UPLOAD ----------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">˗ˏˋ step one ˎˊ˗</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">upload your photo 📷</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "choose a face photo",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    if not consent:
        st.warning("🌸 please confirm consent above before we analyze your photo")
    else:
        try:
            pil_image = Image.open(uploaded_file).convert("RGB")
        except Exception:
            pil_image = None
            st.error("We couldn't open that file. Please upload a JPG or PNG photo.")

        if pil_image is not None:
            file_id = (uploaded_file.name, uploaded_file.size)
            if st.session_state.get("derme_file_id") != file_id:
                with st.spinner("reading your skin story..."):
                    try:
                        st.session_state["derme_result"] = run_analysis(pil_image)
                    except Exception as e:
                        st.session_state["derme_result"] = {"status": "error",
                                                            "error": f"{type(e).__name__}: {e}"}
                    st.session_state["derme_file_id"] = file_id

            result = st.session_state.get("derme_result", {})
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.image(pil_image, caption="✨ your photo", use_container_width=True)
            with col_b:
                if result.get("status") == "complete":
                    st.success("✨ analysis complete! your report is below ♡")
                else:
                    st.error("The analysis could not be completed for this image. "
                             "Try a clear, well-lit, front-facing photo.")
                    if result.get("error"):
                        st.caption(f"Technical detail: {result['error']}")

            if result.get("status") == "complete":
                show_results(result)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    made with <span class="footer-heart">♡</span> by dermé<br>
    <small>˚ ༘ ♡ ⋆｡ experimental ai · skincare dreams · 2025</small>
</div>
""", unsafe_allow_html=True)
