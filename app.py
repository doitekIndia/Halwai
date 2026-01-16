import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import json

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
</style>
""", unsafe_allow_html=True)

# ===================== COMPANY SPECIFIC BOM =====================
COMPANY_BOM = {
    "ramlal_halwai": {
        "name": "रामलाल हलवाई कैटरिंग एंटरप्राइजेज",
        "owners": "श्री सुरेश चौधरी जी | सुनीता चौधरी जी",
        "contact": "9928406444 | 9782266444 | 9414736444",
        "dishes": {
            "पनीर टिक्का": {"पनीर": 12, "दही": 6},
            "शाही पनीर": {"पनीर": 10, "टमाटर": 8},
            "दाल मखनी": {"साबुत उड़द": 6, "मक्खन": 2},
            "जीरा राइस": {"बासमती चावल": 8},
            "बटर नान": {"मैदा": 10}
        }
    },
    "bhanwarlal_halwai": {
        "name": "भंवरलाल कैटरिंग सर्विसेज",
        "owners": "श्री भंवरलाल जी | सीमा देवी जी",
        "contact": "9414141414 | 9784141414 | 9928141414",
        "dishes": {
            "पनीर लबाबदार": {"पनीर": 11, "क्रीम": 4},
            "मलाई कोफ्ता": {"कोफ्ता": 8, "मलाई": 5},
            "प्लेन राइस": {"चावल": 9},
            "लच्छा पराठा": {"मैदा": 12}
        }
    },
    "motilal_sweet": {
        "name": "मोतिलाल स्वीट्स एंड कैटरर्स",
        "owners": "श्री मोतीलाल जी | राधा देवी जी",
        "contact": "9829242424 | 9784242424 | 9414242424",
        "dishes": {
            "गुलाब जामुन": {"खोया": 6},
            "रस मलाई": {"चैना": 7, "दूध": 10},
            "मालपुआ": {"मैदा": 6, "चीनी": 8},
            "पनीर टिक्का": {"पनीर": 12, "दही": 6}
        }
    }
}

# ===================== FIXED DATA LOADING - NO CACHE =====================
def load_data():
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

def save_data(data):
    with open("data/subscriptions.json", 'w') as f:
        json.dump(data, f)

# Load fresh data every time
subscriptions = load_data()

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
        st.markdown("### 🔥 **Admin: admin / admin123**")
        
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
        st.markdown("### 🔥 **Company: company123**")
        
        col1, col2 = st.columns(2)
        with col1:
            company_list = ["ramlal_halwai", "bhanwarlal_halwai", "motilal_sweet"]
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

# ===================== ADMIN DASHBOARD - FIXED RENEWAL =====================
elif st.session_state.admin_logged_in:
    st.markdown(f"""
    <div class='enterprise-card'>
        <h1 class='title-gold'>Admin Panel 👑</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💳 Subscriptions", "🔐 Manage"])
    
    with tab1:
        # ✅ FRESH DATAFRAME - Updates instantly after renewal
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
        
        # ✅ RENEWAL FORM
        col1, col2 = st.columns(2)
        with col1:
            company_to_extend = st.selectbox("🔄 Renew Company", list(subscriptions.keys()))
        with col2:
            days = st.number_input("Days", 1, 365, 30, key="admin_days")
        
        if st.button("💰 RENEW (₹5000)", type="primary", use_container_width=True):
            old_status = "✅ Active" if subscriptions[company_to_extend]["active"] and date.fromisoformat(subscriptions[company_to_extend]["expiry"]) > date.today() else "❌ Expired"
            
            # Update subscription
            subscriptions[company_to_extend]["expiry"] = (date.today() + timedelta(days=days)).isoformat()
            subscriptions[company_to_extend]["active"] = True
            subscriptions[company_to_extend]["paid"] += 5000
            save_data(subscriptions)
            
            new_status = "✅ Active" if subscriptions[company_to_extend]["active"] and date.fromisoformat(subscriptions[company_to_extend]["expiry"]) > date.today() else "❌ Expired"
            
            st.success(f"✅ **{COMPANY_BOM[company_to_extend]['name']}**")
            st.success(f"   {old_status} → {new_status}")
            st.success(f"   New expiry: {subscriptions[company_to_extend]['expiry']}")
            st.balloons()
            st.rerun()
    
    with tab2:
        st.success("✅ **Company Password:** company123")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset All Data", type="secondary"):
                os.remove("data/subscriptions.json") if os.path.exists("data/subscriptions.json") else None
                st.success("✅ Reset!")
                st.rerun()
        with col2:
            if st.button("🔐 Logout", type="secondary"):
                for key in ["admin_logged_in", "company_logged_in"]:
                    st.session_state[key] = False
                st.rerun()

# ===================== COMPANY DASHBOARD =====================
else:  # Company logged in
    company = st.session_state.company_logged_in
    company_data = COMPANY_BOM[company]
    sub_data = subscriptions[company]
    
    is_active = sub_data["active"] and date.fromisoformat(sub_data["expiry"]) > date.today()
    days_left = max(0, (date.fromisoformat(sub_data["expiry"]) - date.today()).days)
    
    st.markdown(f"""
    <div class='enterprise-card'>
        <h1 class='title-gold'>स्वागत है {company_data['name']}! 👑</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if is_active:
        st.markdown(f"""
        <div class='company-card'>
            <h3>✅ ACTIVE - {days_left} Days Left</h3>
            <p>Total Paid: ₹{sub_data['paid']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='expired enterprise-card'>
            <h2>❌ SUBSCRIPTION EXPIRED</h2>
        </div>
        """, unsafe_allow_html=True)
    
    if not is_active:
        if st.button("🔄 RENEW NOW (₹5000/30 days)", type="primary", use_container_width=True):
            subscriptions[company]["expiry"] = (date.today() + timedelta(days=30)).isoformat()
            subscriptions[company]["active"] = True
            subscriptions[company]["paid"] += 5000
            save_data(subscriptions)
            st.success("✅ Renewed! 🎉")
            st.balloons()
            st.rerun()
        st.stop()
    
    # Bill generation
    tab1, tab2 = st.tabs(["💰 नया बिल", "📊 बिल इतिहास"])
    
    with tab1:
        with st.form("bill_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                customer = st.text_input("👨‍👩‍👧‍👦 ग्राहक का नाम", placeholder="Bikaji Foods...")
            with col2:
                people = st.number_input("👥 कुल व्यक्ति", 25, 5000, 150, 25)
            
            dishes = st.multiselect(
                "🍽️ डिशेज चुनें:",
                list(company_data["dishes"].keys()),
                default=list(company_data["dishes"].keys())[:2]
            )
            submitted = st.form_submit_button("📄 बिल बनाएं", type="primary")
        
        if submitted and customer and dishes:
            factor = people / 100
            bill_items = []
            for dish in dishes:
                for item, base_qty in company_data["dishes"][dish].items():
                    bill_items.append({
                        "डिश": dish,
                        "सामग्री": item,
                        "आवश्यक मात्रा": f"{round(base_qty * factor, 1)} किलो"
                    })
            
            bill_df = pd.DataFrame(bill_items)
            st.markdown("### 📋 सामग्री आवश्यकता")
            st.dataframe(bill_df, use_container_width=True)
            
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
    
    if st.button("🔐 Logout"):
        for key in ["company_logged_in"]:
            st.session_state[key] = None
        st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>© 2026 रामलाल हलवाई एंटरप्राइजेज - Bikaner</p>", unsafe_allow_html=True)
