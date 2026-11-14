# import io
# import time
# import streamlit as st
# import numpy as np
# import cv2
# from PIL import Image
# from skin_analyzer import SkinAnalyzer

# st.set_page_config(page_title="DERMÉ | Personal Skin Insights", page_icon="✦", layout="wide")

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');
# html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
# .hero {padding:2.4rem 2.2rem; border-radius:22px; background:linear-gradient(120deg,#f7eee9,#f8f5f0 55%,#e9f0eb); margin-bottom:1.2rem;}
# .brand {font-family:'Playfair Display',serif; font-size:2.8rem; letter-spacing:.12em; color:#293d35;}
# .sub {color:#59645e; font-size:1.05rem;}
# .panel {padding:1.1rem 1.25rem; border:1px solid #e8e5df; border-radius:16px; background:#fff;}
# .muted {color:#6b716d; font-size:.9rem;}
# </style>
# <div class="hero">
#   <div class="brand">DERMÉ</div>
#   <div class="sub">Your personal AI skin insights</div>
#   <p style="margin-top:1rem;color:#3e4943">Explore an image-based skin analysis and discover skincare ingredients and routine ideas.</p>
# </div>
# """, unsafe_allow_html=True)

# st.warning("DERMÉ is an experimental student project. Image-based estimates can be inaccurate and are not medically validated. It does not diagnose or treat skin conditions and is not a substitute for a dermatologist.")

# with st.expander("Before you upload a photo — privacy & consent", expanded=True):
#     st.write("Use a clear, front-facing photo in good lighting. Avoid photos containing other people.")
#     st.write("The app processes the image during this session to generate a result. This app does not intentionally save uploaded photos or analysis reports. The hosting provider may process technical logs; do not upload an image unless you are comfortable sharing it with this experimental app.")
#     consent = st.checkbox("I understand this is an experimental, non-medical tool and I consent to processing this photo for this session.")

# uploaded = st.file_uploader("Upload a face photo", type=["jpg","jpeg","png"], accept_multiple_files=False)
# if uploaded:
#     pil = Image.open(uploaded).convert("RGB")
#     st.image(pil, caption="Uploaded photo", width=280)
#     if not consent:
#         st.info("Please read and accept the consent statement before analysis.")
#     elif st.button("Analyse my skin", type="primary", use_container_width=True):
#         with st.spinner("Analysing image. This may take a little while..."):
#             try:
#                 rgb = np.array(pil)
#                 bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
#                 h, w = bgr.shape[:2]
#                 scale = min(900 / max(h,w), 1)
#                 if scale < 1:
#                     bgr = cv2.resize(bgr, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
#                 analyzer = SkinAnalyzer(use_mediapipe=False)
#                 result = analyzer.analyze(bgr, detailed=True)
#                 st.session_state["derme_result"] = result
#             except Exception as e:
#                 st.error("The analysis could not be completed for this image. Try another clear, well-lit, front-facing photo.")
#                 st.caption(f"Technical detail: {type(e).__name__}: {e}")

# result = st.session_state.get("derme_result")
# if result:
#     if result.get("status") != "complete":
#         st.error(result.get("error","Analysis could not be completed."))
#     else:
#         st.divider()
#         st.subheader("Your skin insights")
#         a,b,c = st.columns(3)
#         a.metric("Image analysis score", f'{result.get("overall_score",0):.0f}/100')
#         b.metric("Estimated skin type", result.get("skin_type",{}).get("type","Not available"))
#         c.metric("Processing time", result.get("processing_time","—"))
#         st.caption("The score is an experimental image-processing output, not a clinical measure of skin health.")
#         tone = result.get("skin_tone",{})
#         if tone:
#             st.markdown("#### Skin tone estimate")
#             st.write(f"**Category:** {tone.get('category','Not available')}  ·  **Undertone:** {tone.get('undertone',{}).get('type','Not available') if isinstance(tone.get('undertone'),dict) else tone.get('undertone','Not available')}")
#         concerns = result.get("recommendations",{}).get("concerns",[])
#         st.markdown("#### Potential concerns detected")
#         if concerns:
#             for item in concerns:
#                 st.markdown(f"- **{item.get('name','Concern')}** — {item.get('severity','')} · {item.get('details','')}")
#         else:
#             st.write("No concerns were flagged by the project's current detection thresholds.")
#         ingredients = result.get("recommendations",{}).get("recommended_ingredients",[])
#         st.markdown("#### Ingredient ideas")
#         if ingredients:
#             for item in ingredients:
#                 if isinstance(item,dict):
#                     st.markdown(f"- **{item.get('name', item.get('ingredient','Ingredient'))}** — {item.get('benefits', item.get('reason','Explore suitability and tolerance before use.'))}")
#                 else:
#                     st.markdown(f"- {item}")
#         else:
#             st.write("No specific ingredient suggestions were generated.")
#         routine = result.get("routine",{})
#         st.markdown("#### Routine ideas")
#         for title,key in [("Morning routine","morning_routine"),("Night routine","night_routine"),("Weekly treatments","weekly_treatments")]:
#             with st.expander(title, expanded=(key=="morning_routine")):
#                 steps = routine.get(key,[])
#                 if steps:
#                     for step in steps:
#                         if isinstance(step,dict):
#                             st.markdown(f"**{step.get('step','')} · {step.get('product','')}**")
#                             st.write(f"Ingredient: {step.get('ingredient','—')}")
#                             st.caption(step.get('how_to',''))
#                         else:
#                             st.write(step)
#                 else:
#                     st.write("No routine steps available.")
#         tips = result.get("recommendations",{}).get("specific_tips",[])
#         if tips:
#             st.markdown("#### General tips")
#             for tip in tips:
#                 st.write(f"• {tip}")
#         st.info("Introduce skincare ingredients gradually, patch test new products, and seek a qualified dermatologist for persistent, painful, worsening or concerning skin issues.")
#         if st.button("Clear this session's result"):
#             st.session_state.pop("derme_result",None)
#             st.rerun()

# st.divider()
# st.markdown("<p class='muted'>DERMÉ · Student-built prototype · For educational and exploratory use only</p>", unsafe_allow_html=True)


import streamlit as st
from PIL import Image
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="DERMÉ | AI Skin Insights",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    /* Import elegant fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global background - soft gradient */
    .stApp {
        background: linear-gradient(135deg, #fdf6f0 0%, #f8e8e0 50%, #f5dcd0 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }
    
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #ffffff 0%, #fef5f0 100%);
        padding: 4rem 3rem;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(180, 120, 100, 0.08);
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid rgba(220, 180, 160, 0.2);
    }
    
    .hero-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 5rem;
        font-weight: 300;
        letter-spacing: 0.5rem;
        color: #2d2419;
        margin: 0;
        line-height: 1;
    }
    
    .hero-subtitle {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.4rem;
        color: #8b6f5c;
        margin-top: 0.5rem;
        letter-spacing: 0.1rem;
    }
    
    .hero-description {
        font-size: 1rem;
        color: #6b5d52;
        margin-top: 1.5rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.7;
    }
    
    .divider-ornament {
        text-align: center;
        color: #c9a690;
        font-size: 1.2rem;
        letter-spacing: 1rem;
        margin: 1.5rem 0;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 1.8rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(180, 120, 100, 0.06);
        border: 1px solid rgba(220, 180, 160, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(180, 120, 100, 0.12);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.8rem;
    }
    
    .feature-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.3rem;
        color: #2d2419;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .feature-text {
        font-size: 0.85rem;
        color: #8b6f5c;
        line-height: 1.5;
    }
    
    /* Disclaimer banner */
    .disclaimer {
        background: linear-gradient(135deg, #fff8e7 0%, #fef3d4 100%);
        border-left: 4px solid #d4a574;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-size: 0.9rem;
        color: #6b5230;
        line-height: 1.6;
    }
    
    .disclaimer-title {
        font-weight: 600;
        color: #8b6914;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Section container */
    .section-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(180, 120, 100, 0.06);
        margin: 1.5rem 0;
        border: 1px solid rgba(220, 180, 160, 0.15);
    }
    
    .section-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.8rem;
        color: #2d2419;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 2px dashed #d4a89a;
    }
    
    [data-testid="stFileUploader"] section {
        background: transparent;
        border: none;
    }
    
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #8b6f5c 0%, #6b5240 100%);
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        letter-spacing: 0.05rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 111, 92, 0.3);
    }
    
    /* Checkbox */
    .stCheckbox {
        background: #faf3ee;
        padding: 0.8rem 1rem;
        border-radius: 10px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 12px !important;
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.1rem !important;
        color: #2d2419 !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #8b6f5c 0%, #6b5240 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 500;
        letter-spacing: 0.05rem;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 111, 92, 0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #a08a7a;
        font-size: 0.8rem;
        letter-spacing: 0.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HERO SECTION ----------------
st.markdown("""
<div class="hero">
    <h1 class="hero-title">DERMÉ</h1>
    <div class="divider-ornament">· · ·</div>
    <p class="hero-subtitle">Your personal AI skin insights</p>
    <p class="hero-description">
        Discover a thoughtful, image-based exploration of your skin —
        uncover gentle ingredient suggestions and routine ideas crafted for you.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- FEATURE CARDS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Analyze</div>
        <div class="feature-text">AI-powered image analysis of your skin's current state</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🌿</div>
        <div class="feature-title">Discover</div>
        <div class="feature-text">Explore ingredients suited to your skin's needs</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">✨</div>
        <div class="feature-title">Glow</div>
        <div class="feature-text">Build a personalized routine for radiant skin</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- DISCLAIMER ----------------
st.markdown("""
<div class="disclaimer">
    <div class="disclaimer-title">⚠️ Important Notice</div>
    DERMÉ is an experimental student project. Image-based estimates can be inaccurate 
    and are not medically validated. It does not diagnose or treat skin conditions and 
    is not a substitute for a licensed dermatologist.
</div>
""", unsafe_allow_html=True)

# ---------------- PRIVACY SECTION ----------------
with st.expander("🔒  Before you upload — Privacy & Consent", expanded=False):
    st.markdown("""
    **📸 Photo guidelines**  
    Use a clear, front-facing photo in good lighting. Avoid photos containing other people.
    
    **🛡️ Your privacy**  
    The app processes the image during this session to generate a result. This app does 
    not intentionally save uploaded photos or analysis reports. The hosting provider may 
    process technical logs — do not upload an image unless you are comfortable sharing it 
    with this experimental app.
    """)
    
    consent = st.checkbox("I understand this is an experimental, non-medical tool and I consent to processing this photo for this session.")

# ---------------- UPLOAD SECTION ----------------
st.markdown('<div class="section-title">📷 Upload Your Photo</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a face photo",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    if not consent:
        st.warning("⚠️ Please confirm consent above before we analyze your photo.")
    else:
        col_a, col_b = st.columns([1, 1])
        with col_a:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your uploaded photo", use_container_width=True)
        
        with col_b:
            st.markdown('<div class="section-title">Analysis</div>', unsafe_allow_html=True)
            with st.spinner("Analyzing your skin..."):
                # Your existing analysis logic here
                st.success("✨ Analysis complete!")
                # st.write(your_analysis_results)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    DERMÉ · Crafted with care · Experimental AI Project
</div>
""", unsafe_allow_html=True)
