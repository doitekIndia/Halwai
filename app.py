import streamlit as st
import pandas as pd
import os
import json
from datetime import date, timedelta

st.set_page_config(page_title="👑 रामलाल हलवाई कैटरिंग", layout="wide")

# ===================== ENTERPRISE CSS =====================
st.markdown("""
<style>
.enterprise-card {background: linear-gradient(145deg, #1e3a8a, #3b82f6); border-radius: 20px; padding: 2.5rem; margin: 1rem 0; box-shadow: 0 20px 40px rgba(0,0,0,0.3); border: 2px solid gold;}
.title-gold {font-size: 3rem !important; background: linear-gradient(45deg, gold, orange); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; text-align: center;}
.admin-panel {background: linear-gradient(145deg, #dc2626, #ef4444); border: 2px solid #b91c1c; border-radius: 15px; padding: 1.5rem;}
.company-card {background: linear-gradient(145deg, #10b981, #34d399); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;}
.expired {background: linear-gradient(145deg, #ef4444, #dc2626) !important; animation: pulse 2s infinite;}
.bom-upload {background: linear-gradient(145deg, #8b5cf6, #a78bfa); border: 2px solid #7c3aed;}
@keyframes pulse {0% {opacity: 1;} 50% {opacity: 0.7;} 100% {opacity: 1;}}
</style>
""", unsafe_allow_html=True)

# ===================== FULL ENTERPRISE BOM (EXACT FORMAT) =====================
BASE_PEOPLE = 100

FULL_BOM_TEMPLATE = {
    # ====== स्टार्टर्स ======
    "पनीर टिक्का": [
        {"item": "पनीर", "qty": 12, "unit": "किलो"},
        {"item": "दही", "qty": 6, "unit": "किलो"},
        {"item": "मसाले", "qty": 1, "unit": "किलो"},
        {"item": "तेल", "qty": 2, "unit": "लीटर"},
    ],
    "हरा भरा कबाब": [
        {"item": "पालक", "qty": 5, "unit": "किलो"},
        {"item": "हरी मटर", "qty": 4, "unit": "किलो"},
        {"item": "आलू", "qty": 6, "unit": "किलो"},
        {"item": "ब्रेड क्रम्ब्स", "qty": 2, "unit": "किलो"},
    ],
    "वेज मंचूरियन": [
        {"item": "पत्ता गोभी", "qty": 6, "unit": "किलो"},
        {"item": "गाजर", "qty": 4, "unit": "किलो"},
        {"item": "मैदा", "qty": 3, "unit": "किलो"},
        {"item": "तेल", "qty": 3, "unit": "लीटर"},
    ],
    "स्प्रिंग रोल": [
        {"item": "स्प्रिंग रोल शीट", "qty": 2, "unit": "किलो"},
        {"item": "मिक्स सब्ज़ियाँ", "qty": 6, "unit": "किलो"},
        {"item": "तेल", "qty": 3, "unit": "लीटर"},
    ],
    "कटलेट": [
        {"item": "आलू", "qty": 8, "unit": "किलो"},
        {"item": "मिक्स सब्ज़ियाँ", "qty": 5, "unit": "किलो"},
        {"item": "ब्रेड क्रम्ब्स", "qty": 2, "unit": "किलो"},
    ],
    # ====== मुख्य सब्ज़ियाँ ======
    "शाही पनीर": [
        {"item": "पनीर", "qty": 10, "unit": "किलो"},
        {"item": "टमाटर", "qty": 8, "unit": "किलो"},
        {"item": "काजू", "qty": 2, "unit": "किलो"},
        {"item": "क्रीम", "qty": 3, "unit": "लीटर"},
    ],
    "पनीर बटर मसाला": [
        {"item": "पनीर", "qty": 10, "unit": "किलो"},
        {"item": "मक्खन", "qty": 2, "unit": "किलो"},
        {"item": "टमाटर", "qty": 7, "unit": "किलो"},
    ],
    "मटर पनीर": [
        {"item": "पनीर", "qty": 8, "unit": "किलो"},
        {"item": "हरी मटर", "qty": 6, "unit": "किलो"},
        {"item": "टमाटर", "qty": 5, "unit": "किलो"},
    ],
    "दाल मखनी": [
        {"item": "साबुत उड़द", "qty": 6, "unit": "किलो"},
        {"item": "राजमा", "qty": 2, "unit": "किलो"},
        {"item": "मक्खन", "qty": 2, "unit": "किलो"},
    ],
    "तड़का दाल": [
        {"item": "अरहर दाल", "qty": 6, "unit": "किलो"},
        {"item": "घी", "qty": 1, "unit": "किलो"},
        {"item": "मसाले", "qty": 0.5, "unit": "किलो"},
    ],
    "राजमा": [
        {"item": "राजमा", "qty": 7, "unit": "किलो"},
        {"item": "टमाटर", "qty": 6, "unit": "किलो"},
        {"item": "तेल", "qty": 2, "unit": "लीटर"},
    ],
    "छोले": [
        {"item": "काबुली चना", "qty": 8, "unit": "किलो"},
        {"item": "प्याज़", "qty": 5, "unit": "किलो"},
        {"item": "मसाले", "qty": 1, "unit": "किलो"},
    ],
    "आलू दम": [
        {"item": "आलू", "qty": 12, "unit": "किलो"},
        {"item": "दही", "qty": 3, "unit": "किलो"},
        {"item": "मसाले", "qty": 1, "unit": "किलो"},
    ],
    "मिक्स वेज": [
        {"item": "मिक्स सब्ज़ियाँ", "qty": 14, "unit": "किलो"},
        {"item": "प्याज़", "qty": 5, "unit": "किलो"},
        {"item": "तेल", "qty": 2, "unit": "लीटर"},
    ],
    "कढ़ी पकौड़ा": [
        {"item": "दही", "qty": 8, "unit": "किलो"},
        {"item": "बेसन", "qty": 4, "unit": "किलो"},
        {"item": "तेल", "qty": 2, "unit": "लीटर"},
    ],
    # ====== चावल ======
    "जीरा राइस": [
        {"item": "बासमती चावल", "qty": 8, "unit": "किलो"},
        {"item": "घी", "qty": 1, "unit": "किलो"},
    ],
    "वेज पुलाव": [
        {"item": "बासमती चावल", "qty": 9, "unit": "किलो"},
        {"item": "मिक्स सब्ज़ियाँ", "qty": 5, "unit": "किलो"},
    ],
    "वेज बिरयानी": [
        {"item": "बासमती चावल", "qty": 10, "unit": "किलो"},
        {"item": "दही", "qty": 4, "unit": "किलो"},
    ],
    "कश्मीरी पुलाव": [
        {"item": "बासमती चावल", "qty": 8, "unit": "किलो"},
        {"item": "सूखे मेवे", "qty": 2, "unit": "किलो"},
    ],
    # ====== रोटी ======
    "बटर नान": [
        {"item": "मैदा", "qty": 10, "unit": "किलो"},
        {"item": "मक्खन", "qty": 2, "unit": "किलो"},
    ],
    "तंदूरी रोटी": [
        {"item": "गेहूं आटा", "qty": 12, "unit": "किलो"},
    ],
    "लच्छा पराठा": [
        {"item": "मैदा", "qty": 9, "unit": "किलो"},
        {"item": "घी", "qty": 2, "unit": "किलो"},
    ],
    # ====== रायता / सलाद ======
    "बूंदी रायता": [
        {"item": "दही", "qty": 10, "unit": "किलो"},
        {"item": "बूंदी", "qty": 3, "unit": "किलो"},
    ],
    "मिक्स रायता": [
        {"item": "दही", "qty": 9, "unit": "किलो"},
        {"item": "सब्ज़ियाँ", "qty": 3, "unit": "किलो"},
    ],
    "ग्रीन सलाद": [
        {"item": "खीरा", "qty": 6, "unit": "किलो"},
        {"item": "टमाटर", "qty": 5, "unit": "किलो"},
        {"item": "प्याज़", "qty": 4, "unit": "किलो"},
    ],
    # ====== मिठाइयाँ ======
    "गुलाब जामुन": [
        {"item": "खोया", "qty": 6, "unit": "किलो"},
        {"item": "चीनी", "qty": 5, "unit": "किलो"},
    ],
    "रसगुल्ला": [
        {"item": "छेना", "qty": 7, "unit": "किलो"},
        {"item": "चीनी", "qty": 6, "unit": "किलो"},
    ],
    "रसमलाई": [
        {"item": "दूध", "qty": 15, "unit": "लीटर"},
        {"item": "छेना", "qty": 5, "unit": "किलो"},
    ],
    "गाजर का हलवा": [
        {"item": "गाजर", "qty": 20, "unit": "किलो"},
        {"item": "दूध", "qty": 15, "unit": "लीटर"},
        {"item": "घी", "qty": 4, "unit": "किलो"},
    ],
    "सूजी हलवा": [
        {"item": "सूजी", "qty": 8, "unit": "किलो"},
        {"item": "घी", "qty": 3, "unit": "किलो"},
        {"item": "चीनी", "qty": 6, "unit": "किलो"},
    ],
    # ====== पेय ======
    "मीठी लस्सी": [
        {"item": "दही", "qty": 12, "unit": "किलो"},
        {"item": "चीनी", "qty": 4, "unit": "किलो"},
    ],
    "चाय": [
        {"item": "चाय पत्ती", "qty": 0.6, "unit": "किलो"},
        {"item": "दूध", "qty": 15, "unit": "लीटर"},
        {"item": "चीनी", "qty": 4, "unit": "किलो"},
    ],
    "कॉफी": [
        {"item": "कॉफी पाउडर", "qty": 0.5, "unit": "किलो"},
        {"item": "दूध", "qty": 12, "unit": "लीटर"},
    ],
}

# ===================== COMPANY BOM STORAGE =====================
def load_company_bom(company_id):
    os.makedirs("data/bom", exist_ok=True)
    bom_file = f"data/bom/{company_id}.json"
    if os.path.exists(bom_file):
        with open(bom_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return FULL_BOM_TEMPLATE.copy()

def save_company_bom(company_id, bom_data):
    os.makedirs("data/bom", exist_ok=True)
    bom_file = f"data/bom/{company_id}.json"
    with open(bom_file, 'w', encoding='utf-8') as f:
        json.dump(bom_data, f, ensure_ascii=False, indent=2)

def download_bom_template():
    return json.dumps(FULL_BOM_TEMPLATE, ensure_ascii=False, indent=2).encode('utf-8')

# ===================== SUBSCRIPTION FUNCTIONS =====================
def load_subscriptions():
    os.makedirs("data", exist_ok=True)
    SUB_FILE = "data/subscriptions.json"
    if not os.path.exists(SUB_FILE):
        default_subs = {
            "ramlal_halwai": {"expiry": (date.today() + timedelta(days=30)).isoformat(), "active": True, "paid": 5000},
            "bhanwarlal_halwai": {"expiry": date.today().isoformat(), "active": False, "paid": 0},
            "motilal_sweet": {"expiry": date.today().isoformat(), "active": False, "paid": 0}
        }
        with open(SUB_FILE, 'w') as f:
            json.dump(default_subs, f)
        return default_subs
    with open(SUB_FILE, 'r') as f:
        return json.load(f)

def save_subscriptions(data):
    with open("data/subscriptions.json", 'w') as f:
        json.dump(data, f)

subscriptions = load_subscriptions()

# ===================== COMPANY INFO =====================
COMPANY_INFO = {
    "ramlal_halwai": {
        "name": "रामलाल हलवाई कैटरिंग एंटरप्राइजेज",
        "owners": "श्री सुरेश चौधरी जी | सुनीता चौधरी जी",
        "contact": "9928406444 | 9782266444 | 9414736444",
    },
    "bhanwarlal_halwai": {
        "name": "भंवरलाल कैटरिंग सर्विसेज",
        "owners": "श्री भंवरलाल जी | सीमा देवी जी",
        "contact": "9414141414 | 9784141414 | 9928141414",
    },
    "motilal_sweet": {
        "name": "मोतिलाल स्वीट्स एंड कैटरर्स",
        "owners": "श्री मोतीलाल जी | राधा देवी जी",
        "contact": "9829242424 | 9784242424 | 9414242424",
    }
}

# Session state
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "company_logged_in" not in st.session_state:
    st.session_state.company_logged_in = None

# ===================== LOGIN =====================
if not st.session_state.admin_logged_in and not st.session_state.company_logged_in:
    st.markdown("<h1 class='title-gold'>🔐 LOGIN</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔧 Admin")
        admin_user = st.text_input("Username", placeholder="admin")
        admin_pass = st.text_input("Password", type="password", placeholder="admin123")
        if st.button("🔐 Admin Login", type="primary"):
            if admin_user == "admin" and admin_pass == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
    
    with col2:
        st.markdown("### 🏢 Company")
        company_list = list(COMPANY_INFO.keys())
        selected_company = st.selectbox("Company", company_list)
        password = st.text_input("Password", type="password", placeholder="company123")
        if st.button("🏢 Company Login", type="primary"):
            if password == "company123":
                st.session_state.company_logged_in = selected_company
                st.rerun()

# ===================== ADMIN PANEL =====================
elif st.session_state.admin_logged_in:
    st.markdown(f"<div class='enterprise-card'><h1 class='title-gold'>Admin Panel 👑</h1></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💳 Subscriptions", "📦 BOM Manager", "🔐 Settings"])
    
    with tab1:
        sub_df = pd.DataFrame([
            {
                "Company": COMPANY_INFO[c]["name"],
                "Status": "✅ Active" if sub["active"] and date.fromisoformat(sub["expiry"]) > date.today() else "❌ Expired",
                "Expiry": sub["expiry"],
                "Paid": f"₹{sub['paid']}",
                "Days": max(0, (date.fromisoformat(sub["expiry"]) - date.today()).days)
            }
            for c, sub in subscriptions.items()
        ])
        st.dataframe(sub_df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            company_to_renew = st.selectbox("Renew", list(subscriptions.keys()))
        with col2:
            days = st.number_input("Days", 1, 365, 30)
        if st.button("💰 Renew ₹5000", type="primary", use_container_width=True):
            subscriptions[company_to_renew]["expiry"] = (date.today() + timedelta(days=days)).isoformat()
            subscriptions[company_to_renew]["active"] = True
            subscriptions[company_to_renew]["paid"] += 5000
            save_subscriptions(subscriptions)
            st.success(f"✅ {COMPANY_INFO[company_to_renew]['name']} Renewed!")
            st.rerun()
    
    with tab2:
        st.markdown("### 📦 BOM Management")
        company = st.selectbox("Company", list(COMPANY_INFO.keys()))
        company_name = COMPANY_INFO[company]["name"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Download Template**")
            st.download_button(
                "Download BOM Template",
                download_bom_template(),
                f"{company}_BOM_TEMPLATE.json",
                "application/json",
                use_container_width=True
            )
        with col2:
            st.markdown("**📤 Upload BOM**")
            uploaded_file = st.file_uploader("JSON File", type="json", key=f"admin_{company}")
            if uploaded_file and st.button(f"Save {company_name} BOM", key=f"save_{company}"):
                try:
                    bom_data = json.load(uploaded_file)
                    save_company_bom(company, bom_data)
                    st.success(f"✅ {company_name} BOM Updated!")
                    st.rerun()
                except:
                    st.error("❌ Invalid JSON format!")
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset All Data"):
                for c in COMPANY_INFO.keys():
                    save_company_bom(c, FULL_BOM_TEMPLATE.copy())
                os.remove("data/subscriptions.json") if os.path.exists("data/subscriptions.json") else None
                st.success("✅ Reset!")
                st.rerun()
        with col2:
            if st.button("🔐 Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()

# ===================== COMPANY DASHBOARD =====================
else:
    company = st.session_state.company_logged_in
    company_info = COMPANY_INFO[company]
    company_bom = load_company_bom(company)
    sub_data = subscriptions[company]
    
    is_active = sub_data["active"] and date.fromisoformat(sub_data["expiry"]) > date.today()
    
    st.markdown(f"<div class='enterprise-card'><h1 class='title-gold'>स्वागत है {company_info['name']}!</h1></div>", unsafe_allow_html=True)
    
    if not is_active:
        st.markdown("<div class='expired enterprise-card'><h2>❌ SUBSCRIPTION EXPIRED</h2></div>", unsafe_allow_html=True)
        if st.button("🔄 Renew ₹5000 (30 days)", type="primary", use_container_width=True):
            subscriptions[company]["expiry"] = (date.today() + timedelta(days=30)).isoformat()
            subscriptions[company]["active"] = True
            subscriptions[company]["paid"] += 5000
            save_subscriptions(subscriptions)
            st.rerun()
        st.stop()
    
    tab1, tab2 = st.tabs(["💰 Bill", "📦 BOM"])
    
    with tab1:
        with st.form("bill"):
            col1, col2 = st.columns([2,1])
            with col1:
                customer = st.text_input("ग्राहक का नाम")
            with col2:
                people = st.number_input("व्यक्ति", 25, 5000, 150)
            
            dishes = st.multiselect("डिशेज", list(company_bom.keys()), default=list(company_bom.keys())[:3])
            if st.form_submit_button("📄 Generate Bill", type="primary"):
                factor = people / BASE_PEOPLE
                bill_items = []
                for dish in dishes:
                    for item_data in company_bom[dish]:
                        qty = item_data["qty"] * factor
                        bill_items.append({
                            "डिश": dish,
                            "सामग्री": item_data["item"],
                            "मात्रा": f"{round(qty, 1)} {item_data['unit']}"
                        })
                
                st.dataframe(pd.DataFrame(bill_items), use_container_width=True)
                
                html_content = f"""
                <html><body>
                <h1>{company_info['name']}</h1>
                <p>{company_info['owners']}<br>{company_info['contact']}</p>
                <p>ग्राहक: {customer} | व्यक्ति: {people} | {date.today()}</p>
                {pd.DataFrame(bill_items).to_html(index=False)}
                </body></html>
                """
                st.download_button("📥 Download", html_content.encode(), f"{company}_{customer}.html", "text/html")
    
    with tab2:
        st.markdown("### 📦 My BOM")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Template**")
            st.download_button("Download", download_bom_template(), f"{company}_BOM.json", "application/json")
        with col2:
            uploaded_file = st.file_uploader("Upload JSON")
            if uploaded_file and st.button("💾 Update BOM", type="primary"):
                try:
                    bom_data = json.load(uploaded_file)
                    save_company_bom(company, bom_data)
                    st.success("✅ BOM Updated!")
                    st.rerun()
                except:
                    st.error("❌ Invalid format!")
    
    st.button("🔐 Logout", on_click=lambda: setattr(st.session_state, 'company_logged_in', None) or st.rerun())

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>© 2026 रामलाल हलवाई - Bikaner</p>", unsafe_allow_html=True)
