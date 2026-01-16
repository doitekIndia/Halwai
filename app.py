import streamlit as st
import pandas as pd
import os, json
from datetime import date, timedelta
from collections import defaultdict

# ===================== PAGE =====================
st.set_page_config(page_title="👑 रामलाल हलवाई कैटरिंग", layout="wide")

# ===================== ORIGINAL CSS (UNCHANGED) =====================
st.markdown("""
<style>
.enterprise-card {background: linear-gradient(145deg, #1e3a8a, #3b82f6); border-radius: 20px; padding: 2.5rem; margin: 1rem 0; box-shadow: 0 20px 40px rgba(0,0,0,0.3); border: 2px solid gold;}
.title-gold {font-size: 3rem !important; background: linear-gradient(45deg, gold, orange); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; text-align: center;}
.admin-panel {background: linear-gradient(145deg, #dc2626, #ef4444); border-radius: 15px; padding: 1.5rem;}
.company-card {background: linear-gradient(145deg, #10b981, #34d399); border-radius: 10px; padding: 1rem;}
.expired {background: linear-gradient(145deg, #ef4444, #dc2626) !important;}
</style>
""", unsafe_allow_html=True)

# ===================== DATA =====================
BASE_PEOPLE = 100

FULL_BOM_TEMPLATE = {
    "मटर पनीर": [
        {"item": "पनीर", "qty": 8, "unit": "किलो"},
        {"item": "हरी मटर", "qty": 6, "unit": "किलो"},
        {"item": "टमाटर", "qty": 5, "unit": "किलो"}
    ],
    "दाल मखनी": [
        {"item": "साबुत उड़द", "qty": 6, "unit": "किलो"},
        {"item": "राजमा", "qty": 2, "unit": "किलो"},
        {"item": "मक्खन", "qty": 2, "unit": "किलो"}
    ],
    "राजमा": [
        {"item": "राजमा", "qty": 7, "unit": "किलो"},
        {"item": "टमाटर", "qty": 6, "unit": "किलो"},
        {"item": "तेल", "qty": 2, "unit": "लीटर"}
    ]
}

COMPANY_INFO = {
    "ramlal_halwai": {
        "name": "रामलाल हलवाई कैटरिंग एंटरप्राइजेज",
        "owners": "श्री सुरेश चौधरी जी | सुनीता चौधरी जी",
        "contact": "9928406444 | 9782266444 | 9414736444"
    }
}

# ===================== SESSION =====================
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "company_logged_in" not in st.session_state:
    st.session_state.company_logged_in = None

# ===================== LOGIN =====================
if not st.session_state.admin_logged_in and not st.session_state.company_logged_in:
    st.markdown("<h1 class='title-gold'>🔐 LOGIN</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👑 Admin")
        au = st.text_input("Username", key="au")
        ap = st.text_input("Password", type="password", key="ap")
        if st.button("🔐 Admin Login"):
            if au == "admin" and ap == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("गलत Admin Login")

    with col2:
        st.markdown("### 🏢 Company")
        comp = st.selectbox("Company", list(COMPANY_INFO.keys()))
        cp = st.text_input("Password", type="password", key="cp")
        if st.button("🏢 Company Login"):
            if cp == "company123":
                st.session_state.company_logged_in = comp
                st.rerun()
            else:
                st.error("गलत Company Password")

    st.stop()

# ===================== ADMIN PANEL =====================
if st.session_state.admin_logged_in:
    st.markdown("<div class='enterprise-card'><h1 class='title-gold'>Admin Panel</h1></div>", unsafe_allow_html=True)
    st.info("Admin login working ✔")
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()
    st.stop()

# ===================== COMPANY DASHBOARD =====================
company = st.session_state.company_logged_in
info = COMPANY_INFO[company]

st.markdown(f"""
<div class='enterprise-card'>
<h1 class='title-gold'>{info['name']}</h1>
<p style="text-align:center">{info['owners']}<br>{info['contact']}</p>
</div>
""", unsafe_allow_html=True)

# ===================== BILL =====================
st.markdown("## 💰 बिल बनाएं")

c1, c2 = st.columns([2,1])
with c1:
    customer = st.text_input("ग्राहक नाम")
with c2:
    people = st.number_input("व्यक्ति", 25, 5000, 150)

dishes = st.multiselect("डिश चुनें", list(FULL_BOM_TEMPLATE.keys()))

if st.button("📄 बिल बनाएं") and customer and dishes:
    factor = people / BASE_PEOPLE
    grouped = defaultdict(list)
    preview = []

    for d in dishes:
        for i in FULL_BOM_TEMPLATE[d]:
            qty = round(i["qty"] * factor, 1)
            grouped[d].append(f"{i['item']} – {qty} {i['unit']}")
            preview.append({"डिश": d, "सामग्री": i["item"], "मात्रा": f"{qty} {i['unit']}"})

    st.dataframe(pd.DataFrame(preview), use_container_width=True)

    bill_html = ""
    for d, items in grouped.items():
        bill_html += f"<h3>{d}</h3><ul>{''.join(f'<li>{x}</li>' for x in items)}</ul>"

    html = f"""
    <html><meta charset="UTF-8"><body>
    <h2>{info['name']}</h2>
    <p>{info['owners']}<br>{info['contact']}</p>
    <p>ग्राहक: {customer} | व्यक्ति: {people} | तारीख: {date.today().strftime('%d/%m/%Y')}</p>
    {bill_html}
    <p style="margin-top:40px;">Signature: ___________________</p>
    </body></html>
    """

    st.download_button(
        "📥 बिल डाउनलोड (PDF)",
        html.encode("utf-8"),
        file_name="bill.html",
        mime="text/html"
    )

if st.button("Logout"):
    st.session_state.company_logged_in = None
    st.rerun()
