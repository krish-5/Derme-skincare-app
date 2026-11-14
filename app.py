import io
import time
import streamlit as st
import numpy as np
import cv2
from PIL import Image
from skin_analyzer import SkinAnalyzer

st.set_page_config(page_title="DERMÉ | Personal Skin Insights", page_icon="✦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.hero {padding:2.4rem 2.2rem; border-radius:22px; background:linear-gradient(120deg,#f7eee9,#f8f5f0 55%,#e9f0eb); margin-bottom:1.2rem;}
.brand {font-family:'Playfair Display',serif; font-size:2.8rem; letter-spacing:.12em; color:#293d35;}
.sub {color:#59645e; font-size:1.05rem;}
.panel {padding:1.1rem 1.25rem; border:1px solid #e8e5df; border-radius:16px; background:#fff;}
.muted {color:#6b716d; font-size:.9rem;}
</style>
<div class="hero">
  <div class="brand">DERMÉ</div>
  <div class="sub">Your personal AI skin insights</div>
  <p style="margin-top:1rem;color:#3e4943">Explore an image-based skin analysis and discover skincare ingredients and routine ideas.</p>
</div>
""", unsafe_allow_html=True)

st.warning("DERMÉ is an experimental student project. Image-based estimates can be inaccurate and are not medically validated. It does not diagnose or treat skin conditions and is not a substitute for a dermatologist.")

with st.expander("Before you upload a photo — privacy & consent", expanded=True):
    st.write("Use a clear, front-facing photo in good lighting. Avoid photos containing other people.")
    st.write("The app processes the image during this session to generate a result. This app does not intentionally save uploaded photos or analysis reports. The hosting provider may process technical logs; do not upload an image unless you are comfortable sharing it with this experimental app.")
    consent = st.checkbox("I understand this is an experimental, non-medical tool and I consent to processing this photo for this session.")

uploaded = st.file_uploader("Upload a face photo", type=["jpg","jpeg","png"], accept_multiple_files=False)
if uploaded:
    pil = Image.open(uploaded).convert("RGB")
    st.image(pil, caption="Uploaded photo", width=280)
    if not consent:
        st.info("Please read and accept the consent statement before analysis.")
    elif st.button("Analyse my skin", type="primary", use_container_width=True):
        with st.spinner("Analysing image. This may take a little while..."):
            try:
                rgb = np.array(pil)
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                h, w = bgr.shape[:2]
                scale = min(900 / max(h,w), 1)
                if scale < 1:
                    bgr = cv2.resize(bgr, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
                analyzer = SkinAnalyzer(use_mediapipe=False)
                result = analyzer.analyze(bgr, detailed=True)
                st.session_state["derme_result"] = result
            except Exception as e:
                st.error("The analysis could not be completed for this image. Try another clear, well-lit, front-facing photo.")
                st.caption(f"Technical detail: {type(e).__name__}: {e}")

result = st.session_state.get("derme_result")
if result:
    if result.get("status") != "complete":
        st.error(result.get("error","Analysis could not be completed."))
    else:
        st.divider()
        st.subheader("Your skin insights")
        a,b,c = st.columns(3)
        a.metric("Image analysis score", f'{result.get("overall_score",0):.0f}/100')
        b.metric("Estimated skin type", result.get("skin_type",{}).get("type","Not available"))
        c.metric("Processing time", result.get("processing_time","—"))
        st.caption("The score is an experimental image-processing output, not a clinical measure of skin health.")
        tone = result.get("skin_tone",{})
        if tone:
            st.markdown("#### Skin tone estimate")
            st.write(f"**Category:** {tone.get('category','Not available')}  ·  **Undertone:** {tone.get('undertone',{}).get('type','Not available') if isinstance(tone.get('undertone'),dict) else tone.get('undertone','Not available')}")
        concerns = result.get("recommendations",{}).get("concerns",[])
        st.markdown("#### Potential concerns detected")
        if concerns:
            for item in concerns:
                st.markdown(f"- **{item.get('name','Concern')}** — {item.get('severity','')} · {item.get('details','')}")
        else:
            st.write("No concerns were flagged by the project's current detection thresholds.")
        ingredients = result.get("recommendations",{}).get("recommended_ingredients",[])
        st.markdown("#### Ingredient ideas")
        if ingredients:
            for item in ingredients:
                if isinstance(item,dict):
                    st.markdown(f"- **{item.get('name', item.get('ingredient','Ingredient'))}** — {item.get('benefits', item.get('reason','Explore suitability and tolerance before use.'))}")
                else:
                    st.markdown(f"- {item}")
        else:
            st.write("No specific ingredient suggestions were generated.")
        routine = result.get("routine",{})
        st.markdown("#### Routine ideas")
        for title,key in [("Morning routine","morning_routine"),("Night routine","night_routine"),("Weekly treatments","weekly_treatments")]:
            with st.expander(title, expanded=(key=="morning_routine")):
                steps = routine.get(key,[])
                if steps:
                    for step in steps:
                        if isinstance(step,dict):
                            st.markdown(f"**{step.get('step','')} · {step.get('product','')}**")
                            st.write(f"Ingredient: {step.get('ingredient','—')}")
                            st.caption(step.get('how_to',''))
                        else:
                            st.write(step)
                else:
                    st.write("No routine steps available.")
        tips = result.get("recommendations",{}).get("specific_tips",[])
        if tips:
            st.markdown("#### General tips")
            for tip in tips:
                st.write(f"• {tip}")
        st.info("Introduce skincare ingredients gradually, patch test new products, and seek a qualified dermatologist for persistent, painful, worsening or concerning skin issues.")
        if st.button("Clear this session's result"):
            st.session_state.pop("derme_result",None)
            st.rerun()

st.divider()
st.markdown("<p class='muted'>DERMÉ · Student-built prototype · For educational and exploratory use only</p>", unsafe_allow_html=True)
