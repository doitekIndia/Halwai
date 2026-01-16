import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="👑 रामलाल हलवाई कैटरिंग", layout="wide")

st.markdown("""
<style>
.enterprise-card {background: linear-gradient(145deg, #1e3a8a, #3b82f6); border-radius: 20px; padding: 2.5rem; margin: 1rem 0; box-shadow: 0 20px 40px rgba(0,0,0,0.3); border: 2px solid gold;}
.title-gold {font-size: 3rem !important; background: linear-gradient(45deg, gold, orange); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ===================== COMPANY PROFILES =====================
COMPANY_PROFILES = {
    "ramlal_halwai": {
        "name": "रामलाल हलवाई कैटरिंग एंटरप्राइजेज",
        "owners": "श्री सुरेश चौधरी जी | सुनीता चौधरी जी",
        "contact": "9928406444 | 9782266444 | 9414736444"
    },
    "bhanwarlal_halwai": {
        "name": "भंवरलाल कैटरिंग सर्विसेज", 
        "owners": "श्री भंवरलाल जी | सीमा देवी जी",
        "contact": "9414141414 | 9784141414 | 9928141414"
    },
    "motilal_sweet": {
        "name": "मोतिलाल स्वीट्स एंड कैटरर्स",
        "owners": "श्री मोतीलाल जी | राधा देवी जी", 
        "contact": "9829242424 | 9784242424 | 9414242424"
    },
    "gopal_mithai": {
        "name": "गोपाल मिठाई वाले कैटरिंग",
        "owners": "श्री गोपाल जी | कमला जी",
        "contact": "9939333333 | 9784333333 | 9414333333"
    },
    "shyamlal_caterers": {
        "name": "श्यामलाल कैटरिंग सर्विसेज", 
        "owners": "श्री श्यामलाल जी | मीना जी",
        "contact": "9949444444 | 9784444444 | 9414444444"
    }
}

# ===================== BOM DATABASE =====================
BASE_PEOPLE = 100
BOM = {
    "पनीर टिक्का": {"पनीर": 12, "दही": 6},
    "शाही पनीर": {"पनीर": 10, "टमाटर": 8}, 
    "दाल मखनी": {"साबुत उड़द": 6, "मक्खन": 2},
    "जीरा राइस": {"बासमती चावल": 8},
    "बटर नान": {"मैदा": 10},
    "गुलाब जामुन": {"खोया": 6}
}

def generate_bill(dishes, people):
    factor = people / BASE_PEOPLE
    bill_items = []
    for dish in dishes:
        for item, base_qty in BOM[dish].items():
            bill_items.append({
                "डिश": dish, 
                "सामग्री": item, 
                "आवश्यक मात्रा": f"{round(base_qty * factor, 1)} किलो"
            })
    return pd.DataFrame(bill_items)

def generate_invoice_html(bill_df, customer, people, company_profile):
    rows = ""
    for _, row in bill_df.iterrows():
        rows += f"""
        <tr>
            <td style='padding: 10px; border: 1px solid #333; font-weight: bold;'>{row['डिश']}</td>
            <td style='padding: 10px; border: 1px solid #333;'>{row['सामग्री']}</td>
            <td style='padding: 10px; border: 1px solid #333; text-align: right;'>{row['आवश्यक मात्रा']}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8">
    <title>{company_profile['name']} - बिल</title>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap');
    body {{font-family: 'Noto Sans Devanagari', Arial; margin: 20px; line-height: 1.6;}}
    .header {{text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid #1e3a8a;}}
    .header h1 {{color: #1e3a8a; font-size: 28px; margin-bottom: 10px;}}
    .bill-info {{margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-left: 5px solid #1e3a8a;}}
    table {{width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;}}
    th {{background: linear-gradient(145deg, #1e3a8a, #3b82f6); color: white; padding: 12px; text-align: left;}}
    td {{padding: 10px; border: 1px solid #ddd; vertical-align: top;}}
    tr:nth-child(even) {{background-color: #f8f9fa;}}
    .signature {{margin-top: 40px; text-align: center; padding-top: 30px; border-top: 2px dashed #1e3a8a;}}
    @media print {{body {{margin: 0;}}}}
    </style></head><body>
    <div class="header">
        <h1>{company_profile['name']}</h1>
        <div style='font-size:16px; color:#333;'>{company_profile['owners']}</div>
        <div style='font-size:14px; color:#666;'>{company_profile['contact']}</div>
    </div>
    <div class="bill-info">
        <strong>बिल तिथि:</strong> {date.today().strftime('%d-%m-%Y')}<br>
        <strong>ग्राहक:</strong> {customer}<br>
        <strong>कुल व्यक्ति:</strong> {people}
    </div>
    <table>
        <tr><th>डिश</th><th>सामग्री</th><th>आवश्यक मात्रा</th></tr>
        {rows}
    </table>
    <div class="signature">
        <p><strong>तैयार किया:</strong> {company_profile['name']}</p>
        <p style='margin-top:30px; font-size:16px;'>Authorized Signature: ______________________</p>
    </div>
    </body></html>
    """

# ===================== SIMPLE LOGIN =====================
if "user" not in st.session_state:
    st.session_state.user = None

st.sidebar.title("🏢 कंपनी चुनें")
selected_company = st.sidebar.selectbox(
    "कैटरिंग कंपनी:", 
    list(COMPANY_PROFILES.keys()),
    format_func=lambda x: COMPANY_PROFILES[x]["name"]
)

if st.sidebar.button("🔐 लॉगिन", type="primary", use_container_width=True):
    st.session_state.user = selected_company
    st.rerun()

if st.session_state.user is None:
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h1 style='color: #1e3a8a; font-size: 3rem;'>👑 रामलाल हलवाई</h1>
        <h2 style='color: #666;'>कैटरिंग एंटरप्राइजेज</h2>
        <p style='font-size: 1.2rem; color: #888;'>बीकानेर</p>
        <div style='margin-top: 30px;'>
            <p>👆 Sidebar में कंपनी चुनें → लॉगिन दबाएं</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ===================== MAIN APP =====================
user = st.session_state.user
company_profile = COMPANY_PROFILES[user]

st.markdown(f"""
<div class='enterprise-card'>
    <h1 class='title-gold'>स्वागत है {company_profile['name']}! 👑</h1>
</div>
""", unsafe_allow_html=True)

# History folder
USER_DIR = f"data/{user}"
os.makedirs(USER_DIR, exist_ok=True)
HISTORY_FILE = f"{USER_DIR}/history.csv"
if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=["Date", "Customer", "People", "Dishes"]).to_csv(HISTORY_FILE, index=False)

# Tabs
tab1, tab2 = st.tabs(["💰 नया बिल", "📊 बिल इतिहास"])

with tab1:
    with st.form("bill_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            customer = st.text_input("👨‍👩‍👧‍👦 ग्राहक का नाम", placeholder="Bikaji Foods International...")
        with col2:
            people = st.number_input("👥 कुल व्यक्ति", 25, 5000, 150, 25)
        
        st.markdown("### 🍽️ डिशेज चुनें")
        dishes = st.multiselect(
            "डिश संयोजन (एक से अधिक चुनें):",
            list(BOM.keys()),
            default=["पनीर टिक्का", "जीरा राइस", "बटर नान"],
            help="लोकप्रिय डिशेज पहले से चुनी हुई हैं। आवश्यक अनुसार बदलें।"
        )
        
        submitted = st.form_submit_button("📄 बिल जनरेट करें", type="primary", use_container_width=True)

    if submitted and customer and dishes:
        bill_df = generate_bill(dishes, people)
        st.markdown("### 📋 सामग्री आवश्यकता सूची")
        st.dataframe(bill_df, use_container_width=True, hide_index=True)

        # Generate & Download HTML Invoice
        html_content = generate_invoice_html(bill_df, customer, people, company_profile)
        safe_filename = f"{user}_{customer.replace(' ', '_')}_{date.today().strftime('%d-%m-%Y')}.html"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.download_button(
                label="📥 HTML बिल डाउनलोड (Chrome → Print → PDF)",
                data=html_content.encode('utf-8'),
                file_name=safe_filename,
                mime="text/html",
                use_container_width=True
            )
        with col2:
            st.success(f"✅ **{len(dishes)} डिशेज** का बिल तैयार!")
        
        # Save to history
        new_record = pd.DataFrame({
            "Date": [date.today().strftime('%d-%m-%Y')],
            "Customer": [customer],
            "People": [people],
            "Dishes": [", ".join(dishes)]
        })
        history_df = pd.read_csv(HISTORY_FILE)
        history_df = pd.concat([history_df, new_record], ignore_index=True)
        history_df.to_csv(HISTORY_FILE, index=False)

with tab2:
    if os.path.exists(HISTORY_FILE):
        history = pd.read_csv(HISTORY_FILE)
        st.markdown("### 📊 आपका बिल इतिहास")
        st.dataframe(history.tail(20), use_container_width=True)
        
        if st.button("🗑️ सभी इतिहास साफ़ करें"):
            history = pd.DataFrame(columns=["Date", "Customer", "People", "Dishes"])
            history.to_csv(HISTORY_FILE, index=False)
            st.success("✅ इतिहास साफ़ किया गया!")
            st.rerun()
    else:
        st.info("❓ पहला बिल बनाएं - इतिहास स्वतः सेव हो जाएगा")

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("### 🏢 वर्तमान कंपनी")
    st.markdown(f"**{company_profile['name']}**")
    st.markdown(f"*{company_profile['owners']}*")
    st.markdown(f"📞 {company_profile['contact']}")
    
    st.markdown("---")
    if st.button("🔐 लॉगआउट", type="secondary"):
        st.session_state.user = None
        st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem;'>© 2026 रामलाल हलवाई कैटरिंग एंटरप्राइजेज - बीकानेर | Made with ❤️</p>", unsafe_allow_html=True)
