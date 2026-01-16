import streamlit as st
import pandas as pd
import os
import json
import io
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
@keyframes pulse {0% {opacity: 1;} 50% {opacity: 0.7;} 100% {opacity: 1;}}
.bom-upload {background: linear-gradient(145deg, #8b5cf6, #a78bfa); border: 2px solid #7c3aed;}
</style>
""", unsafe_allow_html=True)

# ===================== ENTERPRISE BOM TEMPLATE =====================
BASE_PEOPLE = 100

BOM_TEMPLATE = {
    # ====== स्टार्टर्स ======
    "पनीर टिक्का": [
        {"item": "पनीर", "qty": 12, "unit": "किलो"},
        {"item": "दही", "qty": 6, "unit": "किलो"},
        {"item": "मसाले", "qty": 1, "unit": "किलो"},
        {"item": "तेल", "qty": 2, "unit": "लीटर"},
    ],
    "शाही पनीर": [
        {"item": "पनीर", "qty": 10, "unit": "किलो"},
        {"item": "टमाटर", "qty": 8, "unit": "किलो"},
        {"item": "काजू", "qty": 2, "unit": "किलो"},
        {"item": "क्रीम", "qty": 3, "unit": "लीटर"},
    ],
    "दाल मखनी": [
        {"item": "साबुत उड़द", "qty": 6, "unit": "किलो"},
        {"item": "राजमा", "qty": 2, "unit": "किलो"},
        {"item": "मक्खन", "qty": 2, "unit": "किलो"},
    ],
    "जीरा राइस": [
        {"item": "बासमती चावल", "qty": 8, "unit": "किलो"},
        {"item": "घी", "qty": 1, "unit": "किलो"},
    ],
    "बटर नान": [
        {"item": "मैदा", "qty": 10, "unit": "किलो"},
        {"item": "मक्खन", "qty": 2, "unit": "किलो"},
    ],
    "गुलाब जामुन": [
        {"item": "खोया", "qty": 6, "unit": "किलो"},
        {"item": "चीनी", "qty": 5, "unit": "किलो"},
    ]
}

# ===================== COMPANY SPECIFIC BOM STORAGE =====================
def load_company_bom(company_id):
    os.makedirs("data/bom", exist_ok=True)
    bom_file = f"data/bom/{company_id}.json"
    if os.path.exists(bom_file):
        with open(bom_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return BOM_TEMPLATE.copy()

def save_company_bom(company_id, bom_data):
    os.makedirs("data/bom", exist_ok=True)
    bom_file = f"data/bom/{company_id}.json"
    with open(bom_file, 'w', encoding='utf-8') as f:
        json.dump(bom_data, f, ensure_ascii=False, indent=2)

def download_bom_template(company_id):
    template = BOM_TEMPLATE.copy()
    json_str = json.dumps(template, ensure_ascii=False, indent=2)
    return json_str.encode('utf-8')

# ===================== DATA FILES =====================
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
COMPANY_BOM = {
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

# ===================== LOGIN SCREEN =====================
if not st.session_state.admin_logged_in and not st.session_state.company_logged_in:
    st.markdown("<h1 class='title-gold'>🔐 LOGIN REQUIRED</h1>", unsafe_allow_html=True)
    
    admin_tab, company_tab = st.tabs(["🔧 Admin Login", "🏢 Company Login"])
    
    with admin_tab:
        st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            admin_user = st.text_input("Username", placeholder="admin")
        with col2:
            admin_pass = st.text_input("Password", type="password", placeholder="admin123")
        
        if st.button("🔐 Admin Login", type="primary", use_container_width=True):
            if admin_user == "admin" and admin_pass == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ admin/admin123")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with company_tab:
        col1, col2 = st.columns(2)
        with col1:
            company_list = list(COMPANY_BOM.keys())
            selected_company = st.selectbox("🏢 Company", company_list, index=0)
            status = "✅ Active" if subscriptions[selected_company]["active"] and date.fromisoformat(subscriptions[selected_company]["expiry"]) > date.today() else "❌ Expired"
            st.info(f"**Status:** {status}")
        with col2:
            password = st.text_input("🔑 Password", type="password", placeholder="company123")
        
        if st.button("🏢 Company Login", type="primary", use_container_width=True):
            if password == "company123":
                st.session_state.company_logged_in = selected_company
                st.rerun()
            else:
                st.error("❌ company123")

# ===================== ADMIN DASHBOARD =====================
elif st.session_state.admin_logged_in:
    st.markdown(f"""
    <div class='enterprise-card'>
        <h1 class='title-gold'>Admin Panel 👑</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💳 Subscriptions", "📦 BOM Management", "🔐 Manage"])
    
    with tab1:
        sub_df = pd.DataFrame([
            {
                "Company": COMPANY_BOM[c]["name"],
                "Status": "✅ Active" if sub["active"] and date.fromisoformat(sub["expiry"]) > date.today() else "❌ Expired",
                "Expiry": sub["expiry"],
                "Paid": f"₹{sub['paid']}",
                "Days Left": max(0, (date.fromisoformat(sub["expiry"]) - date.today()).days)
            }
            for c, sub in subscriptions.items() if c in COMPANY_BOM
        ])
        st.dataframe(sub_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            company_to_extend = st.selectbox("🔄 Renew Company", list(subscriptions.keys()))
        with col2:
            days = st.number_input("Days", 1, 365, 30)
        
        if st.button("💰 RENEW (₹5000)", type="primary", use_container_width=True):
            subscriptions[company_to_extend]["expiry"] = (date.today() + timedelta(days=days)).isoformat()
            subscriptions[company_to_extend]["active"] = True
            subscriptions[company_to_extend]["paid"] += 5000
            save_subscriptions(subscriptions)
            st.success(f"✅ {COMPANY_BOM[company_to_extend]['name']} Renewed!")
            st.rerun()
    
    with tab2:
        st.markdown("### 📦 Company BOM Management")
        company = st.selectbox("Select Company", list(COMPANY_BOM.keys()))
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown("**👇 Download Template**")
            st.download_button(
                "📥 Download BOM Template",
                download_bom_template(company),
                f"{company}_BOM_TEMPLATE.json",
                "application/json",
                use_container_width=True
            )
        with col2:
            st.markdown("**📤 Upload Updated BOM**")
            uploaded_file = st.file_uploader("Choose JSON file", type="json", key=f"admin_bom_{company}")
            if uploaded_file and st.button(f"💾 Save {COMPANY_BOM[company]['name']} BOM", key=f"save_bom_{company}"):
                try:
                    bom_data = json.load(uploaded_file)
                    save_company_bom(company, bom_data)
                    st.success(f"✅ {COMPANY_BOM[company]['name']} BOM Updated!")
                except:
                    st.error("❌ Invalid JSON format!")
        
        st.markdown("---")
        st.info("**Format:** Download template → Edit in Excel/Notepad → Upload JSON")
    
    with tab3:
        if st.button("🔄 Reset All Data", type="secondary"):
            for company in COMPANY_BOM.keys():
                save_company_bom(company, BOM_TEMPLATE.copy())
            os.remove("data/subscriptions.json") if os.path.exists("data/subscriptions.json") else None
            st.success("✅ Reset Complete!")
            st.rerun()
        
        if st.button("🔐 Logout", type="secondary"):
            for key in ["admin_logged_in", "company_logged_in"]:
                st.session_state[key] = False
            st.rerun()

# ===================== COMPANY DASHBOARD =====================
else:  # Company logged in
    company = st.session_state.company_logged_in
    company_data = COMPANY_BOM[company]
    company_bom = load_company_bom(company)
    sub_data = subscriptions[company]
    
    is_active = sub_data["active"] and date.fromisoformat(sub_data["expiry"]) > date.today()
    days_left = max(0, (date.fromisoformat(sub_data["expiry"]) - date.today()).days)
    
    st.markdown(f"""
    <div class='enterprise-card'>
        <h1 class='title-gold'>स्वागत है {company_data['name']}! 👑</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Status
    if is_active:
        st.markdown(f"""
        <div class='company-card'>
            <h3>✅ ACTIVE - {days_left} Days Left</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='expired enterprise-card'>
            <h2>❌ SUBSCRIPTION EXPIRED</h2>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # BOM Management for Company
    tab1, tab2, tab3 = st.tabs(["💰 नया बिल", "📦 Manage BOM", "📊 बिल इतिहास"])
    
    with tab1:
        st.markdown("### 💰 बिल जेनरेट करें")
        with st.form("bill_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                customer = st.text_input("👨‍👩‍👧‍👦 ग्राहक का नाम", placeholder="Bikaji Foods...")
            with col2:
                people = st.number_input("👥 कुल व्यक्ति", 25, 5000, 150, 25)
            
            dishes = st.multiselect(
                "🍽️ डिशेज चुनें:",
                list(company_bom.keys()),
                default=list(company_bom.keys())[:3]
            )
            submitted = st.form_submit_button("📄 बिल बनाएं", type="primary")
        
        if submitted and customer and dishes:
            factor = people / BASE_PEOPLE
            bill_items = []
            for dish in dishes:
                for item_data in company_bom[dish]:
                    qty = item_data["qty"] * factor
                    bill_items.append({
                        "डिश": dish,
                        "सामग्री": item_data["item"],
                        "आवश्यक मात्रा": f"{round(qty, 1)} {item_data['unit']}"
                    })
            
            bill_df = pd.DataFrame(bill_items)
            st.markdown("### 📋 सामग्री आवश्यकता (BASE=100)")
            st.dataframe(bill_df, use_container_width=True)
            
            # HTML Invoice
            html_content = f"""
            <!DOCTYPE html>
            <html><head><meta charset="UTF-8">
            <title>{company_data['name']} बिल</title>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap');
            body {{font-family: 'Noto Sans Devanagari', Arial; margin: 20px;}}
            h1 {{color: #1e3a8a; text-align: center; font-size: 28px;}}
            table {{width: 100%; border-collapse: collapse; margin: 20px 0;}}
            th {{background: #1e3a8a; color: white; padding: 12px;}}
            td {{padding: 10px; border: 1px solid #ddd;}}
            </style></head><body>
            <h1>{company_data['name']}</h1>
            <p style='text-align:center'>{company_data['owners']}<br>{company_data['contact']}</p>
            <p><strong>ग्राहक:</strong> {customer} | <strong>व्यक्ति:</strong> {people} | <strong>तारीख:</strong> {date.today()}</p>
            {bill_df.to_html(index=False)}
            <p style='text-align:center; margin-top:40px'>Signature: ______________</p>
            </body></html>
            """
            st.download_button(
                "📥 बिल डाउनलोड",
                html_content.encode('utf-8'),
                f"{company}_{customer}_{date.today()}.html",
                "text/html"
            )
    
    with tab2:
        st.markdown(f"### 📦 {company_data['name']} BOM Management")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👇 Download Template**")
            st.download_button(
                "📥 Download My BOM Template",
                download_bom_template(company),
                f"{company}_BOM_TEMPLATE.json",
                "application/json",
                use_container_width=True
            )
        
        with col2:
            st.markdown("**📤 Upload My BOM**")
            uploaded_file = st.file_uploader("Choose JSON file", type="json")
            if uploaded_file and st.button("💾 Update My BOM", type="primary", use_container_width=True):
                try:
                    bom_data = json.load(uploaded_file)
                    save_company_bom(company, bom_data)
                    st.success("✅ BOM Updated Successfully!")
                    st.rerun()
                except:
                    st.error("❌ Invalid JSON! Use the template format.")
        
        st.markdown("---")
        st.info("**Steps:** 1️⃣ Download → 2️⃣ Edit → 3️⃣ Upload")
    
    if st.button("🔐 Logout"):
        st.session_state.company_logged_in = None
        st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>© 2026 रामलाल हलवाई एंटरप्राइजेज - Bikaner</p>", unsafe_allow_html=True)
