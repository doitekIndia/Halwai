import streamlit as st
import pandas as pd
import os, json
from datetime import date, timedelta
from collections import defaultdict

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="👑 रामलाल हलवाई कैटरिंग", layout="wide")

# ===================== CSS =====================
st.markdown("""
<style>
.enterprise-card {background: linear-gradient(145deg, #1e3a8a, #3b82f6); border-radius: 20px; padding: 2rem; margin: 1rem 0;}
.title-gold {font-size: 2.5rem; background: linear-gradient(45deg, gold, orange); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align:center;}
.expired {background:#dc2626;color:white;}
</style>
""", unsafe_allow_html=True)

# ===================== CONSTANTS =====================
BASE_PEOPLE = 100

# ===================== BOM =====================
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
    "तड़का दाल": [
        {"item": "अरहर दाल", "qty": 6, "unit": "किलो"},
        {"item": "घी", "qty": 1, "unit": "किलो"},
        {"item": "मसाले", "qty": 0.5, "unit": "किलो"}
    ],
    "राजमा": [
        {"item": "राजमा", "qty": 7, "unit": "किलो"},
        {"item": "टमाटर", "qty": 6, "unit": "किलो"},
        {"item": "तेल", "qty": 2, "unit": "लीटर"}
    ],
    "वेज मंचूरियन": [
        {"item": "पत्ता गोभी", "qty": 6, "unit": "किलो"},
        {"item": "गाजर", "qty": 4, "unit": "किलो"},
        {"item": "मैदा", "qty": 3, "unit": "किलो"},
        {"item": "तेल", "qty": 3, "unit": "लीटर"}
    ],
    "शाही पनीर": [
        {"item": "पनीर", "qty": 10, "unit": "किलो"},
        {"item": "टमाटर", "qty": 8, "unit": "किलो"},
        {"item": "काजू", "qty": 2, "unit": "किलो"},
        {"item": "क्रीम", "qty": 3, "unit": "लीटर"}
    ],
    "छोले": [
        {"item": "काबुली चना", "qty": 8, "unit": "किलो"},
        {"item": "प्याज़", "qty": 5, "unit": "किलो"},
        {"item": "मसाले", "qty": 1, "unit": "किलो"}
    ]
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
if "company" not in st.session_state:
    st.session_state.company = None

# ===================== LOGIN =====================
if not st.session_state.company:
    st.markdown("<h1 class='title-gold'>🏢 Company Login</h1>", unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == "company123":
            st.session_state.company = "ramlal_halwai"
            st.rerun()
    st.stop()

# ===================== DASHBOARD =====================
company = st.session_state.company
company_info = COMPANY_INFO[company]
company_bom = FULL_BOM_TEMPLATE

st.markdown(f"""
<div class='enterprise-card'>
<h1 class='title-gold'>{company_info['name']}</h1>
<p style='text-align:center'>{company_info['owners']}<br>{company_info['contact']}</p>
</div>
""", unsafe_allow_html=True)

# ===================== BILL =====================
st.markdown("## 💰 बिल बनाएं")

col1, col2 = st.columns([2,1])
with col1:
    customer = st.text_input("ग्राहक का नाम", placeholder="Manish")
with col2:
    people = st.number_input("व्यक्ति", 25, 5000, 150)

dishes = st.multiselect(
    "डिश चुनें",
    list(company_bom.keys()),
    default=list(company_bom.keys())[:3]
)

if st.button("📄 बिल बनाएं", type="primary") and customer and dishes:

    factor = people / BASE_PEOPLE
    grouped_bill = defaultdict(list)
    preview_rows = []

    for dish in dishes:
        for item in company_bom[dish]:
            qty = round(item["qty"] * factor, 1)
            grouped_bill[dish].append(f"{item['item']} – {qty} {item['unit']}")
            preview_rows.append({
                "डिश": dish,
                "सामग्री": item["item"],
                "मात्रा": f"{qty} {item['unit']}"
            })

    # 👁 Preview
    st.markdown("### 📋 Preview")
    st.dataframe(pd.DataFrame(preview_rows), use_container_width=True)

    # 🧾 Bill HTML
    bill_html = ""
    for dish, items in grouped_bill.items():
        bill_html += f"""
        <h3>{dish}</h3>
        <ul>
            {''.join(f"<li>{i}</li>" for i in items)}
        </ul>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    body {{ font-family: Arial; }}
    h3 {{ color:#1e3a8a; }}
    </style>
    </head>
    <body>

    <h2>{company_info['name']}</h2>
    <p>{company_info['owners']}<br>{company_info['contact']}</p>

    <p>
    <strong>ग्राहक:</strong> {customer} |
    <strong>व्यक्ति:</strong> {people} |
    <strong>तारीख:</strong> {date.today().strftime('%d/%m/%Y')}
    </p>

    {bill_html}

    <p style="margin-top:40px;">Signature: ___________________</p>

    </body>
    </html>
    """

    st.download_button(
        "📥 बिल डाउनलोड (PDF)",
        html_content.encode("utf-8"),
        file_name=f"bill_{customer}_{date.today().strftime('%d%m%Y')}.html",
        mime="text/html"
    )

# ===================== FOOTER =====================
st.markdown("---")
st.markdown("<center>© 2026 CREATED BY: NITIN KHATRI - BIKANER</center>", unsafe_allow_html=True)
