import os
import re
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import google.generativeai as genai

from taxipred.utils.helpers import predict_api_endpoint

st.set_page_config(page_title="Taxi Fare – Simple Dashboard", layout="wide")

# Gemini API-nyckel
API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
GEMINI_READY = bool(API_KEY)
if GEMINI_READY:
    genai.configure(api_key=API_KEY)

GEMINI_MODEL_NAME = "models/gemini-2.5-flash"
GENERATION_CONFIG = {
    "temperature": 0.2,
    "response_mime_type": "application/json",
}

# Pydantic limits
MIN_DIST = 1.2
MIN_DUR  = 5.0
MIN_BASE, MAX_BASE = 2.0, 5.0
MIN_KM,   MAX_KM   = 0.5, 2.0
MIN_MIN,  MAX_MIN  = 0.1, 0.5

# ---------------- Session state ----------------
if "driver" not in st.session_state:
    st.session_state.driver = {"Base_Fare": 3.5, "Per_Km_Rate": 1.2, "Per_Minute_Rate": 0.3}
if "history" not in st.session_state:
    st.session_state.history = []
if "ai_route" not in st.session_state:
    st.session_state.ai_route = None


st.title("Taxi Fare Prediction Dashboard")

left, right = st.columns([0.55, 0.45], gap="large")

# left: Inputs (AI and Manual)
with left:
    st.subheader("Input")

    tabs = st.tabs(["AI-sök", "Manuellt"])
    
    with tabs[0]:
        st.text("Fyll i adresser. AI hämtar distans och tid.")
        c1, c2 = st.columns(2)
        with c1:
            start = st.text_input("From", placeholder="Ex: Linnégatan 12, Göteborg")
        with c2:
            end = st.text_input("To", placeholder="Ex: Nordstan, Göteborg")

        ai_ok = st.button("Beräkna distans & tid med AI", use_container_width=True, type="primary", disabled=not GEMINI_READY)
        if not GEMINI_READY:
            st.info("Lägg din Gemini-nyckel i .streamlit/secrets.toml som GEMINI_API_KEY för att aktivera AI-sök.")

        def _extract_json(text: str):
            m = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not m:
                raise ValueError("Hittade ingen JSON i AI-svaret.")
            return json.loads(m.group(0))

        if ai_ok and start and end and GEMINI_READY:
            prompt = f"""
Du är en reseassistent. Beräkna körsträcka (km) och restid (minuter)
för en resa från "{start}" till "{end}" i Sverige.
Returnera exakt JSON (inga extra ord) med nycklarna:
{{
  "distance_km": <number>,
  "duration_min": <number>
}}
""".strip()
            try:
                model = genai.GenerativeModel(GEMINI_MODEL_NAME, generation_config=GENERATION_CONFIG)
                resp = model.generate_content(prompt)

                # ev. safety block
                if hasattr(resp, "prompt_feedback") and resp.prompt_feedback and getattr(resp.prompt_feedback, "block_reason", None):
                    raise ValueError(f"Gemini block: {resp.prompt_feedback.block_reason}")

                raw_text = getattr(resp, "text", None)
                if not raw_text and getattr(resp, "candidates", None):
                    parts = []
                    for c in resp.candidates:
                        content = getattr(c, "content", None)
                        if content and getattr(content, "parts", None):
                            for part in content.parts:
                                t = getattr(part, "text", None)
                                if t:
                                    parts.append(t)
                    raw_text = "\n".join(parts) if parts else None
                if not raw_text:
                    raise ValueError("Tomt AI-svar.")

                try:
                    data = json.loads(raw_text)
                except Exception:
                    data = _extract_json(raw_text)

                distance_km = float(data["distance_km"])
                duration_min = float(data["duration_min"])

                # use pydantic limits
                distance_km = max(MIN_DIST, distance_km)
                duration_min = max(MIN_DUR, duration_min)

                st.session_state.ai_route = {"distance_km": distance_km, "duration_min": duration_min}
                st.success(f"AI-resultat: {distance_km:.2f} km, {duration_min:.0f} min")
            except Exception as e:
                st.error(f"Kunde inte tolka AI-svaret: {e}")

        if st.session_state.ai_route:
            st.write(f"Aktuell AI-resa: {st.session_state.ai_route['distance_km']:.2f} km, {st.session_state.ai_route['duration_min']:.0f} min")

    # manual page
    with tabs[1]:
        st.text("Fyll i alla fält manuellt.")
        d1, d2 = st.columns(2)
        with d1:
            dist = st.number_input("Trip Distance (km)", min_value=MIN_DIST, value=5.0, step=0.1)
            dura = st.number_input("Trip Duration (min)", min_value=MIN_DUR, value=15.0, step=1.0)
        with d2:
            base = st.number_input("Base Fare", min_value=MIN_BASE, max_value=MAX_BASE, value=float(st.session_state.driver["Base_Fare"]), step=0.1)
            per_km = st.number_input("Per Km Rate", min_value=MIN_KM, max_value=MAX_KM, value=float(st.session_state.driver["Per_Km_Rate"]), step=0.1)
            per_min = st.number_input("Per Minute Rate", min_value=MIN_MIN, max_value=MAX_MIN, value=float(st.session_state.driver["Per_Minute_Rate"]), step=0.1)

        st.session_state.driver.update({"Base_Fare": base, "Per_Km_Rate": per_km, "Per_Minute_Rate": per_min})
        manual_predict = st.button("Predict fare (manuellt)", use_container_width=True)

# right: Results
with right:
    st.subheader("Resultat")

    # CSS (chagpt)
    st.markdown("""
    <style>
      .big-price { font-size: 36px; font-weight: 700; margin: 8px 0 16px 0; }
      .sub-kpi { font-size: 16px; color: #444; }
    </style>
    """, unsafe_allow_html=True)

    # Prediktion från AI-route
    if st.session_state.ai_route:
        payload_ai = {
            "Trip_Distance_km": float(st.session_state.ai_route["distance_km"]),
            "Trip_Duration_Minutes": float(st.session_state.ai_route["duration_min"]),
            "Base_Fare": float(st.session_state.driver["Base_Fare"]),
            "Per_Km_Rate": float(st.session_state.driver["Per_Km_Rate"]),
            "Per_Minute_Rate": float(st.session_state.driver["Per_Minute_Rate"]),
        }
        if st.button("Predict fare (AI-sök)", use_container_width=True):
            try:
                res = predict_api_endpoint(payload_ai, endpoint="/taxi/predict")
                if not res.ok:
                    st.error(f"API {res.status_code}: {res.text}")
                    st.write("Payload:", payload_ai)
                res.raise_for_status()
                price = float(res.json()["Predicted_Price"])
                st.markdown(f"<div class='big-price'>Predicted price: {price:.2f}</div>", unsafe_allow_html=True)

                # KPIs
                k1, k2 = st.columns(2)
                with k1:
                    st.markdown(f"<div class='sub-kpi'>Pris / km: {(price/max(payload_ai['Trip_Distance_km'],1e-9)):.2f}</div>", unsafe_allow_html=True)
                with k2:
                    st.markdown(f"<div class='sub-kpi'>Pris / min: {(price/max(payload_ai['Trip_Duration_Minutes'],1e-9)):.2f}</div>", unsafe_allow_html=True)

                st.session_state.history.insert(0, {
                    "Predicted_Price": price, **payload_ai,
                    "source": "AI", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
            except Exception as e:
                st.error(f"API error: {e}")

    # Prediction from manual inputs
    if 'manual_predict' in locals() and manual_predict:
        payload_manual = {
            "Trip_Distance_km": float(dist),
            "Trip_Duration_Minutes": float(dura),
            "Base_Fare": float(st.session_state.driver["Base_Fare"]),
            "Per_Km_Rate": float(st.session_state.driver["Per_Km_Rate"]),
            "Per_Minute_Rate": float(st.session_state.driver["Per_Minute_Rate"]),
        }
        try:
            res = predict_api_endpoint(payload_manual, endpoint="/taxi/predict")
            if not res.ok:
                st.error(f"API {res.status_code}: {res.text}")
                st.write("Payload:", payload_manual)
            res.raise_for_status()
            price = float(res.json()["Predicted_Price"])
            st.markdown(f"<div class='big-price'>Predicted price: {price:.2f}</div>", unsafe_allow_html=True)

            k1, k2 = st.columns(2)
            with k1:
                st.markdown(f"<div class='sub-kpi'>Pris / km: {(price/max(payload_manual['Trip_Distance_km'],1e-9)):.2f}</div>", unsafe_allow_html=True)
            with k2:
                st.markdown(f"<div class='sub-kpi'>Pris / min: {(price/max(payload_manual['Trip_Duration_Minutes'],1e-9)):.2f}</div>", unsafe_allow_html=True)

            st.session_state.history.insert(0, {
                "Predicted_Price": price, **payload_manual,
                "source": "Manual", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        except Exception as e:
            st.error(f"API error: {e}")

    # history
    if st.session_state.history:
        st.write("Historik")
        hdf = pd.DataFrame(st.session_state.history)
        st.dataframe(hdf, use_container_width=True)
        csv = hdf.to_csv(index=False).encode("utf-8")
        st.download_button("Ladda ner historik (CSV)", data=csv, file_name="history.csv", mime="text/csv", use_container_width=True)