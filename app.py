import streamlit as st
import pandas as pd
import os
import json
from datetime import date, timedelta
from collections import defaultdict

st.set_page_config(page_title="👑 रामलाल हलवाई कैटरिंग", layout="wide")

# ===================== ENTERPRISE CSS (UNCHANGED) =====================
st.markdown("""
<style>
.enterprise-card {background: linear-gradient(145deg, #1e3a8a, #3b82f6); border-radius: 20px; padding: 2.5rem; margin: 1rem 0; box-shadow: 0 20px 40px rgba(0,0,0,0.3); border: 2px solid gold;}
.title-gold {font-size: 3rem !important; background: linear-gradient(45deg, gold, orange); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; text-align: center;}
.admin-panel {background: linear-gradient(145deg, #dc2626, #ef4444); border: 2px solid #b91c1c; border-radius: 15px; padding: 1.5rem;}
.company-card {background: linear-gradient(145deg, #10b981, #34d399); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;}
.expired {background: linear-gradient(145deg, #ef4444, #dc2626) !important; animation: pulse 2s infinite;}
@keyframes pulse {0% {opacity: 1;} 50% {opacity: 0.7;} 100% {opacity: 1;}}
</style>
""", unsafe_allow_html=True)

# ===================== CONSTANTS =====================
BASE_PEOPLE = 100

# ===================== BOM =====================
FULL_BOM_TEMPLATE = {
    "मटर पनीर": [{"item": "पनीर", "qty": 8, "unit": "किलो"}, {"item": "हरी मटर", "qty": 6, "unit": "किलो"}, {"item": "टमाटर", "qty": 5, "unit": "किलो"}],
    "दाल मखनी": [{"item": "साबुत उड़द", "qty": 6, "unit": "किलो"}, {"item": "राजमा", "qty": 2, "unit": "किलो"}, {"item": "मक्खन", "qty": 2, "unit": "किलो"}],
    "तड़का दाल": [{"item": "अरहर दाल", "qty": 6, "unit": "किलो"}, {"item": "घी", "qty": 1, "unit": "किलो"}, {"item": "मसाले", "qty": 0.5, "unit": "किलो"}],
    "राजमा": [{"item": "राजमा", "qty": 7, "unit": "किलो"}, {"item": "टमाटर", "qty": 6, "unit": "किलो"}, {"item": "तेल", "qty": 2, "unit": "लीटर"}],
    "वेज मंचूरियन": [{"item": "पत्ता गोभी", "qty": 6, "unit": "किलो"}, {"item": "गाजर", "qty": 4, "unit": "किलो"}, {"item": "मैदा", "qty": 3, "unit": "किलो"}, {"item": "तेल", "qty": 3, "unit": "लीटर"}],
    "शाही पनीर": [{"item": "पनीर", "qty": 10, "unit": "किलो"}, {"item": "टमाटर", "qty": 8, "unit": "किलो"}, {"item": "काजू", "qty": 2, "unit": "किलो"}, {"item": "क्रीम", "qty": 3, "unit": "लीटर"}],
    "छोले": [{"item": "काबुली चना", "qty": 8, "unit": "किलो"}, {"item": "प्याज़", "qty": 5, "unit": "किलो"}, {"item": "मसाले", "qty": 1, "unit": "किलो"}]
}

# ===================== COMPANY INFO =====================
COMPANY_INFO = {
    "ramlal_halwai": {
        "name": "रामलाल हलवाई कैटरिंग एंटरप्राइजेज",
        "owners": "श्री सुरेश चौधरी जी | सुनीता चौधरी जी",
        "contact": "9928406444 | 9782266444 | 9414736444"
    }
}

# ===================== SESSION =====================
if "company_logged_in" not in st.session_state:
    st.session_state.company_logged_in = None

# ===================== LOGIN =====================
if not st.session_state.company_logged_in:
    st.markdown("<h1 class='title-gold'>🏢 Company Login</h1>", unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == "company123":
            st.session_state.company_logged_in = "ramlal_halwai"
            st.rerun()
    st.stop()

# ===================== DASHBOARD =====================
company = st.session_state.company_logged_in
company_info = COMPANY_INFO[company]
company_bom = FULL_BOM_TEMPLATE

st.markdown(f"""
<div class='enterprise-card'>
<h1 class='title-gold'>{company_info['name']}</h1>
<p style='text-align:center'>{company_info['owners']}<br>{company_info['contact']}</p>
</div>
""", unsafe_allow_html=True)

# ===================== BILL (FIXED FORMAT ONLY) =====================
st.markdown("## 💰 बिल बनाएं")

col1, col2 = st.columns([2,1])
with col1:
    customer = st.text_input("ग्राहक का नाम", placeholder="Manish")
with col2:
    people = st.number_input("व्यक्ति", 25, 5000, 150)

dishes = st.multiselect("🍽️ डिशेज", list(company_bom.keys()), default=list(company_bom.keys())[:3])

if st.button("📄 बिल बनाएं", type="primary") and customer and dishes:

    factor = people / BASE_PEOPLE
    grouped_bill = defaultdict(list)
    preview = []

    for dish in dishes:
        for item in company_bom[dish]:
            qty = round(item["qty"] * factor, 1)
            grouped_bill[dish].append(f"{item['item']} – {qty} {item['unit']}")
            preview.append({"डिश": dish, "सामग्री": item["item"], "मात्रा": f"{qty} {item['unit']}"})

    st.markdown("### 📋 सामग्री आवश्यकता (Preview)")
    st.dataframe(pd.DataFrame(preview), use_container_width=True)

    bill_html = ""
    for dish, items in grouped_bill.items():
        bill_html += f"""
        <div style="margin-top:20px;">
            <h3 style="color:#1e3a8a;">{dish}</h3>
            <ul>
                {''.join(f"<li>{i}</li>" for i in items)}
            </ul>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"></head>
    <body>
    <h2>{company_info['name']}</h2>
    <p>{company_info['owners']}<br>{company_info['contact']}</p>
    <p><strong>ग्राहक:</strong> {customer} |
       <strong>व्यक्ति:</strong> {people} |
       <strong>तारीख:</strong> {date.today().strftime('%d/%m/%Y')}</p>
    {bill_html}
    <p style="margin-top:40px;">Signature: ___________________</p>
    </body></html>
    """

    st.download_button(
        "📥 बिल डाउनलोड (Print → PDF)",
        html_content.encode("utf-8"),
        file_name=f"{company}_{customer}_{date.today().strftime('%d%m%Y')}.html",
        mime="text/html"
    )

st.markdown("---")
st.markdown("<p style='text-align:center;color:#666;'>© 2026 CREATED BY: NITIN KHATRI - Bikaner</p>", unsafe_allow_html=True)
