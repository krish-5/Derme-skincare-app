# # import io
# # import time
# # import streamlit as st
# # import numpy as np
# # import cv2
# # from PIL import Image
# # from skin_analyzer import SkinAnalyzer

# # st.set_page_config(page_title="DERMÉ | Personal Skin Insights", page_icon="✦", layout="wide")

# # st.markdown("""
# # <style>
# # @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');
# # html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
# # .hero {padding:2.4rem 2.2rem; border-radius:22px; background:linear-gradient(120deg,#f7eee9,#f8f5f0 55%,#e9f0eb); margin-bottom:1.2rem;}
# # .brand {font-family:'Playfair Display',serif; font-size:2.8rem; letter-spacing:.12em; color:#293d35;}
# # .sub {color:#59645e; font-size:1.05rem;}
# # .panel {padding:1.1rem 1.25rem; border:1px solid #e8e5df; border-radius:16px; background:#fff;}
# # .muted {color:#6b716d; font-size:.9rem;}
# # </style>
# # <div class="hero">
# #   <div class="brand">DERMÉ</div>
# #   <div class="sub">Your personal AI skin insights</div>
# #   <p style="margin-top:1rem;color:#3e4943">Explore an image-based skin analysis and discover skincare ingredients and routine ideas.</p>
# # </div>
# # """, unsafe_allow_html=True)

# # st.warning("DERMÉ is an experimental student project. Image-based estimates can be inaccurate and are not medically validated. It does not diagnose or treat skin conditions and is not a substitute for a dermatologist.")

# # with st.expander("Before you upload a photo — privacy & consent", expanded=True):
# #     st.write("Use a clear, front-facing photo in good lighting. Avoid photos containing other people.")
# #     st.write("The app processes the image during this session to generate a result. This app does not intentionally save uploaded photos or analysis reports. The hosting provider may process technical logs; do not upload an image unless you are comfortable sharing it with this experimental app.")
# #     consent = st.checkbox("I understand this is an experimental, non-medical tool and I consent to processing this photo for this session.")

# # uploaded = st.file_uploader("Upload a face photo", type=["jpg","jpeg","png"], accept_multiple_files=False)
# # if uploaded:
# #     pil = Image.open(uploaded).convert("RGB")
# #     st.image(pil, caption="Uploaded photo", width=280)
# #     if not consent:
# #         st.info("Please read and accept the consent statement before analysis.")
# #     elif st.button("Analyse my skin", type="primary", use_container_width=True):
# #         with st.spinner("Analysing image. This may take a little while..."):
# #             try:
# #                 rgb = np.array(pil)
# #                 bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
# #                 h, w = bgr.shape[:2]
# #                 scale = min(900 / max(h,w), 1)
# #                 if scale < 1:
# #                     bgr = cv2.resize(bgr, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
# #                 analyzer = SkinAnalyzer(use_mediapipe=False)
# #                 result = analyzer.analyze(bgr, detailed=True)
# #                 st.session_state["derme_result"] = result
# #             except Exception as e:
# #                 st.error("The analysis could not be completed for this image. Try another clear, well-lit, front-facing photo.")
# #                 st.caption(f"Technical detail: {type(e).__name__}: {e}")

# # result = st.session_state.get("derme_result")
# # if result:
# #     if result.get("status") != "complete":
# #         st.error(result.get("error","Analysis could not be completed."))
# #     else:
# #         st.divider()
# #         st.subheader("Your skin insights")
# #         a,b,c = st.columns(3)
# #         a.metric("Image analysis score", f'{result.get("overall_score",0):.0f}/100')
# #         b.metric("Estimated skin type", result.get("skin_type",{}).get("type","Not available"))
# #         c.metric("Processing time", result.get("processing_time","—"))
# #         st.caption("The score is an experimental image-processing output, not a clinical measure of skin health.")
# #         tone = result.get("skin_tone",{})
# #         if tone:
# #             st.markdown("#### Skin tone estimate")
# #             st.write(f"**Category:** {tone.get('category','Not available')}  ·  **Undertone:** {tone.get('undertone',{}).get('type','Not available') if isinstance(tone.get('undertone'),dict) else tone.get('undertone','Not available')}")
# #         concerns = result.get("recommendations",{}).get("concerns",[])
# #         st.markdown("#### Potential concerns detected")
# #         if concerns:
# #             for item in concerns:
# #                 st.markdown(f"- **{item.get('name','Concern')}** — {item.get('severity','')} · {item.get('details','')}")
# #         else:
# #             st.write("No concerns were flagged by the project's current detection thresholds.")
# #         ingredients = result.get("recommendations",{}).get("recommended_ingredients",[])
# #         st.markdown("#### Ingredient ideas")
# #         if ingredients:
# #             for item in ingredients:
# #                 if isinstance(item,dict):
# #                     st.markdown(f"- **{item.get('name', item.get('ingredient','Ingredient'))}** — {item.get('benefits', item.get('reason','Explore suitability and tolerance before use.'))}")
# #                 else:
# #                     st.markdown(f"- {item}")
# #         else:
# #             st.write("No specific ingredient suggestions were generated.")
# #         routine = result.get("routine",{})
# #         st.markdown("#### Routine ideas")
# #         for title,key in [("Morning routine","morning_routine"),("Night routine","night_routine"),("Weekly treatments","weekly_treatments")]:
# #             with st.expander(title, expanded=(key=="morning_routine")):
# #                 steps = routine.get(key,[])
# #                 if steps:
# #                     for step in steps:
# #                         if isinstance(step,dict):
# #                             st.markdown(f"**{step.get('step','')} · {step.get('product','')}**")
# #                             st.write(f"Ingredient: {step.get('ingredient','—')}")
# #                             st.caption(step.get('how_to',''))
# #                         else:
# #                             st.write(step)
# #                 else:
# #                     st.write("No routine steps available.")
# #         tips = result.get("recommendations",{}).get("specific_tips",[])
# #         if tips:
# #             st.markdown("#### General tips")
# #             for tip in tips:
# #                 st.write(f"• {tip}")
# #         st.info("Introduce skincare ingredients gradually, patch test new products, and seek a qualified dermatologist for persistent, painful, worsening or concerning skin issues.")
# #         if st.button("Clear this session's result"):
# #             st.session_state.pop("derme_result",None)
# #             st.rerun()

# # st.divider()
# # st.markdown("<p class='muted'>DERMÉ · Student-built prototype · For educational and exploratory use only</p>", unsafe_allow_html=True)


# import streamlit as st
# from PIL import Image
# import base64

# # ---------------- PAGE CONFIG ----------------
# st.set_page_config(
#     page_title="DERMÉ | AI Skin Insights",
#     page_icon="✨",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # ---------------- CUSTOM CSS ----------------
# st.markdown("""
# <style>
#     /* Import elegant fonts */
#     @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=Inter:wght@300;400;500;600&display=swap');
    
#     /* Hide Streamlit branding */
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     header {visibility: hidden;}
    
#     /* Global background - soft gradient */
#     .stApp {
#         background: linear-gradient(135deg, #fdf6f0 0%, #f8e8e0 50%, #f5dcd0 100%);
#         font-family: 'Inter', sans-serif;
#     }
    
#     /* Main container */
#     .block-container {
#         padding-top: 2rem;
#         padding-bottom: 2rem;
#         max-width: 1100px;
#     }
    
#     /* Hero section */
#     .hero {
#         background: linear-gradient(135deg, #ffffff 0%, #fef5f0 100%);
#         padding: 4rem 3rem;
#         border-radius: 24px;
#         box-shadow: 0 20px 60px rgba(180, 120, 100, 0.08);
#         text-align: center;
#         margin-bottom: 2rem;
#         border: 1px solid rgba(220, 180, 160, 0.2);
#     }
    
#     .hero-title {
#         font-family: 'Cormorant Garamond', serif;
#         font-size: 5rem;
#         font-weight: 300;
#         letter-spacing: 0.5rem;
#         color: #2d2419;
#         margin: 0;
#         line-height: 1;
#     }
    
#     .hero-subtitle {
#         font-family: 'Cormorant Garamond', serif;
#         font-style: italic;
#         font-size: 1.4rem;
#         color: #8b6f5c;
#         margin-top: 0.5rem;
#         letter-spacing: 0.1rem;
#     }
    
#     .hero-description {
#         font-size: 1rem;
#         color: #6b5d52;
#         margin-top: 1.5rem;
#         max-width: 600px;
#         margin-left: auto;
#         margin-right: auto;
#         line-height: 1.7;
#     }
    
#     .divider-ornament {
#         text-align: center;
#         color: #c9a690;
#         font-size: 1.2rem;
#         letter-spacing: 1rem;
#         margin: 1.5rem 0;
#     }
    
#     /* Feature cards */
#     .feature-card {
#         background: white;
#         padding: 1.8rem;
#         border-radius: 16px;
#         text-align: center;
#         box-shadow: 0 4px 20px rgba(180, 120, 100, 0.06);
#         border: 1px solid rgba(220, 180, 160, 0.15);
#         transition: transform 0.3s ease, box-shadow 0.3s ease;
#         height: 100%;
#     }
    
#     .feature-card:hover {
#         transform: translateY(-4px);
#         box-shadow: 0 8px 30px rgba(180, 120, 100, 0.12);
#     }
    
#     .feature-icon {
#         font-size: 2rem;
#         margin-bottom: 0.8rem;
#     }
    
#     .feature-title {
#         font-family: 'Cormorant Garamond', serif;
#         font-size: 1.3rem;
#         color: #2d2419;
#         margin-bottom: 0.5rem;
#         font-weight: 500;
#     }
    
#     .feature-text {
#         font-size: 0.85rem;
#         color: #8b6f5c;
#         line-height: 1.5;
#     }
    
#     /* Disclaimer banner */
#     .disclaimer {
#         background: linear-gradient(135deg, #fff8e7 0%, #fef3d4 100%);
#         border-left: 4px solid #d4a574;
#         padding: 1.2rem 1.5rem;
#         border-radius: 12px;
#         margin: 1.5rem 0;
#         font-size: 0.9rem;
#         color: #6b5230;
#         line-height: 1.6;
#     }
    
#     .disclaimer-title {
#         font-weight: 600;
#         color: #8b6914;
#         margin-bottom: 0.3rem;
#         display: flex;
#         align-items: center;
#         gap: 0.5rem;
#     }
    
#     /* Section container */
#     .section-card {
#         background: white;
#         padding: 2rem;
#         border-radius: 20px;
#         box-shadow: 0 4px 20px rgba(180, 120, 100, 0.06);
#         margin: 1.5rem 0;
#         border: 1px solid rgba(220, 180, 160, 0.15);
#     }
    
#     .section-title {
#         font-family: 'Cormorant Garamond', serif;
#         font-size: 1.8rem;
#         color: #2d2419;
#         margin-bottom: 1rem;
#         font-weight: 500;
#     }
    
#     /* File uploader styling */
#     [data-testid="stFileUploader"] {
#         background: white;
#         padding: 1.5rem;
#         border-radius: 16px;
#         border: 2px dashed #d4a89a;
#     }
    
#     [data-testid="stFileUploader"] section {
#         background: transparent;
#         border: none;
#     }
    
#     [data-testid="stFileUploader"] button {
#         background: linear-gradient(135deg, #8b6f5c 0%, #6b5240 100%);
#         color: white !important;
#         border: none;
#         border-radius: 25px;
#         padding: 0.5rem 1.5rem;
#         font-weight: 500;
#         letter-spacing: 0.05rem;
#         transition: all 0.3s ease;
#     }
    
#     [data-testid="stFileUploader"] button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 6px 20px rgba(139, 111, 92, 0.3);
#     }
    
#     /* Checkbox */
#     .stCheckbox {
#         background: #faf3ee;
#         padding: 0.8rem 1rem;
#         border-radius: 10px;
#     }
    
#     /* Expander */
#     .streamlit-expanderHeader {
#         background: white !important;
#         border-radius: 12px !important;
#         font-family: 'Cormorant Garamond', serif;
#         font-size: 1.1rem !important;
#         color: #2d2419 !important;
#     }
    
#     /* Buttons */
#     .stButton button {
#         background: linear-gradient(135deg, #8b6f5c 0%, #6b5240 100%);
#         color: white;
#         border: none;
#         border-radius: 25px;
#         padding: 0.6rem 2rem;
#         font-weight: 500;
#         letter-spacing: 0.05rem;
#         transition: all 0.3s ease;
#     }
    
#     .stButton button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 6px 20px rgba(139, 111, 92, 0.3);
#     }
    
#     /* Footer */
#     .footer {
#         text-align: center;
#         padding: 2rem 0 1rem 0;
#         color: #a08a7a;
#         font-size: 0.8rem;
#         letter-spacing: 0.1rem;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ---------------- HERO SECTION ----------------
# st.markdown("""
# <div class="hero">
#     <h1 class="hero-title">DERMÉ</h1>
#     <div class="divider-ornament">· · ·</div>
#     <p class="hero-subtitle">Your personal AI skin insights</p>
#     <p class="hero-description">
#         Discover a thoughtful, image-based exploration of your skin —
#         uncover gentle ingredient suggestions and routine ideas crafted for you.
#     </p>
# </div>
# """, unsafe_allow_html=True)

# # ---------------- FEATURE CARDS ----------------
# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     <div class="feature-card">
#         <div class="feature-icon">🔍</div>
#         <div class="feature-title">Analyze</div>
#         <div class="feature-text">AI-powered image analysis of your skin's current state</div>
#     </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown("""
#     <div class="feature-card">
#         <div class="feature-icon">🌿</div>
#         <div class="feature-title">Discover</div>
#         <div class="feature-text">Explore ingredients suited to your skin's needs</div>
#     </div>
#     """, unsafe_allow_html=True)

# with col3:
#     st.markdown("""
#     <div class="feature-card">
#         <div class="feature-icon">✨</div>
#         <div class="feature-title">Glow</div>
#         <div class="feature-text">Build a personalized routine for radiant skin</div>
#     </div>
#     """, unsafe_allow_html=True)

# # ---------------- DISCLAIMER ----------------
# st.markdown("""
# <div class="disclaimer">
#     <div class="disclaimer-title">⚠️ Important Notice</div>
#     DERMÉ is an experimental student project. Image-based estimates can be inaccurate 
#     and are not medically validated. It does not diagnose or treat skin conditions and 
#     is not a substitute for a licensed dermatologist.
# </div>
# """, unsafe_allow_html=True)

# # ---------------- PRIVACY SECTION ----------------
# with st.expander("🔒  Before you upload — Privacy & Consent", expanded=False):
#     st.markdown("""
#     **📸 Photo guidelines**  
#     Use a clear, front-facing photo in good lighting. Avoid photos containing other people.
    
#     **🛡️ Your privacy**  
#     The app processes the image during this session to generate a result. This app does 
#     not intentionally save uploaded photos or analysis reports. The hosting provider may 
#     process technical logs — do not upload an image unless you are comfortable sharing it 
#     with this experimental app.
#     """)
    
#     consent = st.checkbox("I understand this is an experimental, non-medical tool and I consent to processing this photo for this session.")

# # ---------------- UPLOAD SECTION ----------------
# st.markdown('<div class="section-title">📷 Upload Your Photo</div>', unsafe_allow_html=True)

# uploaded_file = st.file_uploader(
#     "Choose a face photo",
#     type=["jpg", "jpeg", "png"],
#     label_visibility="collapsed"
# )

# if uploaded_file is not None:
#     if not consent:
#         st.warning("⚠️ Please confirm consent above before we analyze your photo.")
#     else:
#         col_a, col_b = st.columns([1, 1])
#         with col_a:
#             image = Image.open(uploaded_file)
#             st.image(image, caption="Your uploaded photo", use_container_width=True)
        
#         with col_b:
#             st.markdown('<div class="section-title">Analysis</div>', unsafe_allow_html=True)
#             with st.spinner("Analyzing your skin..."):
#                 # Your existing analysis logic here
#                 st.success("✨ Analysis complete!")
#                 # st.write(your_analysis_results)

# # ---------------- FOOTER ----------------
# st.markdown("""
# <div class="footer">
#     DERMÉ · Crafted with care · Experimental AI Project
# </div>
# """, unsafe_allow_html=True)

import streamlit as st
from PIL import Image
import time

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
        margin: 1.5rem auto 0 auto;
        max-width: 550px;
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
        col_a, col_b = st.columns([1, 1])
        with col_a:
            image = Image.open(uploaded_file)
            st.image(image, caption="✨ your beautiful photo", use_container_width=True)
        
        with col_b:
            st.markdown('<div class="section-label">your results ♡</div>', unsafe_allow_html=True)
            with st.spinner("reading your skin story..."):
                time.sleep(1.5)
                st.success("✨ analysis complete! your results are ready ♡")
                # YOUR EXISTING ANALYSIS LOGIC HERE

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    made with <span class="footer-heart">♡</span> by dermé<br>
    <small>˚ ༘ ♡ ⋆｡ experimental ai · skincare dreams · 2025</small>
</div>
""", unsafe_allow_html=True)
