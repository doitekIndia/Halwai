import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="👑 रामलाल हलवाई कैटरिंग", layout="wide")

st.markdown("""
<style>
.enterprise-card {background: linear-gradient(145deg, #1e3a8a, #3b82f6); border-radius: 20px; padding: 2.5rem; margin: 1rem 0;}
.title-gold {font-size: 3rem !important; background: linear-gradient(45deg, gold, orange); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center;}
</style>
""", unsafe_allow_html=True)

# Company profiles
COMPANY_PROFILES = {
    "ramlal_halwai": {"name": "रामलाल हलवाई कैटरिंग", "contact": "9928406444"},
    "bhanwarlal_halwai": {"name": "भंवरलाल कैटरिंग", "contact": "9414141414"}
}

# Simple hardcoded login (NO secrets!)
username = st.sidebar.selectbox("Select Company", ["ramlal_halwai", "bhanwarlal_halwai"])
if st.sidebar.button("🔐 Login", type="primary"):
    st.session_state.user = username
    st.rerun()

if "user" not in st.session_state:
    st.sidebar.info("👆 Company चुनें → Login दबाएं")
    st.title("👑 रामलाल हलवाई कैटरिंग एंटरप्राइजेज")
    st.stop()

# Main app
user = st.session_state.user
company = COMPANY_PROFILES[user]
st.markdown(f"""
<div class='enterprise-card'>
    <h1 class='title-gold'>Welcome {company["name"]}! 👑</h1>
</div>
""", unsafe_allow_html=True)

# Bill generator
tab1, tab2 = st.tabs(["💰 नया बिल", "📊 इतिहास"])

with tab1:
    with st.form("bill_form"):
        customer = st.text_input("ग्राहक का नाम", placeholder="Bikaji Foods...")
        people = st.number_input("कुल व्यक्ति", 25, 5000, 150, 25)
        submitted = st.form_submit_button("📄 बिल बनाएं")

    if submitted and customer:
        # Simple BOM calculation
        bom_data = {
            "पनीर टिक्का": {"पनीर": 12, "दही": 6},
            "शाही पनीर": {"पनीर": 10, "टमाटर": 8}
        }
        
        bill_items = []
        for dish in ["पनीर टिक्का", "शाही पनीर"]:
            factor = people / 100
            for item, base_qty in bom_data[dish].items():
                bill_items.append({
                    "डिश": dish, "सामग्री": item, 
                    "मात्रा": round(base_qty * factor, 1)
                })
        
        bill_df = pd.DataFrame(bill_items)
        st.markdown("### 📋 सामग्री आवश्यकता")
        st.dataframe(bill_df)

        # HTML Invoice
        html = f"""
        <!DOCTYPE html>
        <html><head><meta charset="UTF-8">
        <title>{company['name']} बिल</title>
        <style>
        body {{font-family: Arial; margin: 20px;}}
        h1 {{color: #1e3a8a; text-align: center;}}
        table {{width: 100%; border-collapse: collapse;}}
        th, td {{border: 1px solid #333; padding: 10px;}}
        th {{background: #1e3a8a; color: white;}}
        </style></head><body>
        <h1>{company['name']}</h1>
        <p>ग्राहक: {customer} | व्यक्ति: {people} | तारीख: {date.today()}</p>
        {bill_df.to_html(index=False)}
        <p style='text-align:center; margin-top:40px'>Signature: ______________</p>
        </body></html>
        """
        
        st.download_button(
            "📥 HTML बिल डाउनलोड (Print → PDF)",
            html.encode('utf-8'),
            f"{user}_{customer}_{date.today()}.html",
            "text/html"
        )
        st.success("✅ बिल तैयार!")

with tab2:
    st.info("📊 History coming soon...")

st.sidebar.markdown(f"### {company['name']}\n{company['contact']}")
if st.sidebar.button("🔐 Logout"):
    del st.session_state.user
    st.rerun()
