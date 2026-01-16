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
@keyframes pulse {0% {opacity: 1;} 50% {opacity: 0.7;} 100% {opacity: 1;}}
</style>
""", unsafe_allow_html=True)

# ===================== FULL ENTERPRISE BOM =====================
BASE_PEOPLE = 100

FULL_BOM_TEMPLATE = {
    "पनीर टिक्का": [{"item": "पनीर", "qty": 12, "unit": "किलो"}, {"item": "दही", "qty": 6, "unit": "किलो"}, {"item": "मसाले", "qty": 1, "unit": "किलो"}, {"item": "तेल", "qty": 2, "unit": "लीटर"}],
    "हरा भरा कबाब": [{"item": "पालक", "qty": 5, "unit": "किलो"}, {"item": "हरी मटर", "qty": 4, "unit": "किलो"}, {"item": "आलू", "qty": 6, "unit": "किलो"}, {"item": "ब्रेड क्रम्ब्स", "qty": 2, "unit": "किलो"}],
    "वेज मंचूरियन": [{"item": "पत्ता गोभी", "qty": 6, "unit": "किलो"}, {"item": "गाजर", "qty": 4, "unit": "किलो"}, {"item": "मैदा", "qty": 3, "unit": "किलो"}, {"item": "तेल", "qty": 3, "unit": "लीटर"}],
    "शाही पनीर": [{"item": "पनीर", "qty": 10, "unit": "किलो"}, {"item": "टमाटर", "qty": 8, "unit": "किलो"}, {"item": "काजू", "qty": 2, "unit": "किलो"}, {"item": "क्रीम", "qty": 3, "unit": "लीटर"}],
    "पनीर बटर मसाला": [{"item": "पनीर", "qty": 10, "unit": "किलो"}, {"item": "मक्खन", "qty": 2, "unit": "किलो"}, {"item": "टमाटर", "qty": 7, "unit": "किलो"}],
    "मटर पनीर": [{"item": "पनीर", "qty": 8, "unit": "किलो"}, {"item": "हरी मटर", "qty": 6, "unit": "किलो"}, {"item": "टमाटर", "qty": 5, "unit": "किलो"}],
    "दाल मखनी": [{"item": "साबुत उड़द", "qty": 6, "unit": "किलो"}, {"item": "राजमा", "qty": 2, "unit": "किलो"}, {"item": "मक्खन", "qty": 2, "unit": "किलो"}],
    "तड़का दाल": [{"item": "अरहर दाल", "qty": 6, "unit": "किलो"}, {"item": "घी", "qty": 1, "unit": "किलो"}, {"item": "मसाले", "qty": 0.5, "unit": "किलो"}],
    "राजमा": [{"item": "राजमा", "qty": 7, "unit": "किलो"}, {"item": "टमाटर", "qty": 6, "unit": "किलो"}, {"item": "तेल", "qty": 2, "unit": "लीटर"}],
    "छोले": [{"item": "काबुली चना", "qty": 8, "unit": "किलो"}, {"item": "प्याज़", "qty": 5, "unit": "किलो"}, {"item": "मसाले", "qty": 1, "unit": "किलो"}],
    "कटलेट": [{"item": "आलू", "qty": 8, "unit": "किलो"}, {"item": "मिक्स सब्ज़ियाँ", "qty": 5, "unit": "किलो"}, {"item": "ब्रेड क्रम्ब्स", "qty": 2, "unit": "किलो"}],
    "आलू दम": [{"item": "आलू", "qty": 12, "unit": "किलो"}, {"item": "दही", "qty": 3, "unit": "किलो"}, {"item": "मसाले", "qty": 1, "unit": "किलो"}],
    "मिक्स वेज": [{"item": "मिक्स सब्ज़ियाँ", "qty": 14, "unit": "किलो"}, {"item": "प्याज़", "qty": 5, "unit": "किलो"}, {"item": "तेल", "qty": 2, "unit": "लीटर"}],
    "कढ़ी पकौड़ा": [{"item": "दही", "qty": 8, "unit": "किलो"}, {"item": "बेसन", "qty": 4, "unit": "किलो"}, {"item": "तेल", "qty": 2, "unit": "लीटर"}],
    "जीरा राइस": [{"item": "बासमती चावल", "qty": 8, "unit": "किलो"}, {"item": "घी", "qty": 1, "unit": "किलो"}],
    "वेज पुलाव": [{"item": "बासमती चावल", "qty": 9, "unit": "किलो"}, {"item": "मिक्स सब्ज़ियाँ", "qty": 5, "unit": "किलो"}],
    "वेज बिरयानी": [{"item": "बासमती चावल", "qty": 10, "unit": "किलो"}, {"item": "दही", "qty": 4, "unit": "किलो"}],
    "बटर नान": [{"item": "मैदा", "qty": 10, "unit": "किलो"}, {"item": "मक्खन", "qty": 2, "unit": "किलो"}],
    "गुलाब जामुन": [{"item": "खोया", "qty": 6, "unit": "किलो"}, {"item": "चीनी", "qty": 5, "unit": "किलो"}]
}

# ===================== FUNCTIONS =====================
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

COMPANY_INFO = {
    "ramlal_halwai": {"name": "रामलाल हलवाई कैटरिंग एंटरप्राइजेज", "owners": "श्री सुरेश चौधरी जी | सुनीता चौधरी जी", "contact": "9928406444 | 9782266444 | 9414736444"},
    "bhanwarlal_halwai": {"name": "भंवरलाल कैटरिंग सर्विसेज", "owners": "श्री भंवरलाल जी | सीमा देवी जी", "contact": "9414141414 | 9784141414 | 9928141414"},
    "motilal_sweet": {"name": "मोतिलाल स्वीट्स एंड कैटरर्स", "owners": "श्री मोतीलाल जी | राधा देवी जी", "contact": "9829242424 | 9784242424 | 9414242424"}
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
        st.markdown("### Admin")
        admin_user = st.text_input("Username", placeholder="admin")
        admin_pass = st.text_input("Password", type="password", placeholder="admin123")
        if st.button("🔐 Admin Login", type="primary"):
            if admin_user == "admin" and admin_pass == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
    with col2:
        st.markdown("### Company")
        company_list = list(COMPANY_INFO.keys())
        selected_company = st.selectbox("Company", company_list)
        password = st.text_input("Password", type="password", placeholder="company123")
        if st.button("🏢 Company Login", type="primary"):
            if password == "company123":
                st.session_state.company_logged_in = selected_company
                st.rerun()

# ===================== ADMIN =====================
elif st.session_state.admin_logged_in:
    st.markdown(f"<div class='enterprise-card'><h1 class='title-gold'>Admin Panel 👑</h1></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💳 Subscriptions", "📦 BOM"])
    with tab1:
        sub_df = pd.DataFrame([
            {"Company": COMPANY_INFO[c]["name"], "Status": "✅ Active" if sub["active"] and date.fromisoformat(sub["expiry"]) > date.today() else "❌ Expired", 
             "Expiry": sub["expiry"], "Paid": f"₹{sub['paid']}", "Days": max(0, (date.fromisoformat(sub["expiry"]) - date.today()).days)}
            for c, sub in subscriptions.items()
        ])
        st.dataframe(sub_df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1: company_to_renew = st.selectbox("Renew", list(subscriptions.keys()))
        with col2: days = st.number_input("Days", 1, 365, 30)
        if st.button("💰 Renew ₹5000", type="primary", use_container_width=True):
            subscriptions[company_to_renew]["expiry"] = (date.today() + timedelta(days=days)).isoformat()
            subscriptions[company_to_renew]["active"] = True
            subscriptions[company_to_renew]["paid"] += 5000
            save_subscriptions(subscriptions)
            st.success(f"✅ Renewed!")
            st.rerun()
    
    with tab2:
        company = st.selectbox("Company", list(COMPANY_INFO.keys()))
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 BOM Template", download_bom_template(), f"{company}_BOM.json", "application/json")
        with col2:
            uploaded = st.file_uploader("Upload BOM", type="json")
            if uploaded and st.button(f"Save {COMPANY_INFO[company]['name']}", key=f"save_{company}"):
                save_company_bom(company, json.load(uploaded))
                st.success("✅ Saved!")
    
    st.button("🔐 Logout", on_click=lambda: [setattr(st.session_state, k, False) for k in ["admin_logged_in"]]+[st.rerun()])

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
        if st.button("🔄 Renew ₹5000", type="primary"): 
            subscriptions[company]["expiry"] = (date.today() + timedelta(days=30)).isoformat()
            subscriptions[company]["active"] = True
            subscriptions[company]["paid"] += 5000
            save_subscriptions(subscriptions)
            st.rerun()
        st.stop()
    
    tab1, tab2 = st.tabs(["💰 Bill", "📦 BOM"])
    
    # 🔥 PERFECT BILL GENERATION - Dish name ONCE + Indented ingredients
    with tab1:
        st.markdown("### 💰 बिल बनाएं")
        col1, col2 = st.columns([2,1])
        with col1: 
            customer = st.text_input("👨‍👩‍👧‍👦 ग्राहक का नाम", placeholder="Bikaji Foods")
        with col2: 
            people = st.number_input("👥 व्यक्ति", 25, 5000, 150)
        
        dishes = st.multiselect("🍽️ डिशेज", list(company_bom.keys()), default=list(company_bom.keys())[:5])
        generate = st.button("📄 बिल बनाएं", type="primary")
        
        if generate and customer and dishes:
            factor = people / BASE_PEOPLE
            bill_items = []
            
            # 🔥 DISH-WISE (Dish name ONCE per dish)
            for dish in dishes:
                bill_items.append({
                    "डिश": dish,
                    "सामग्री": "",
                    "मात्रा": ""
                })
                for item_data in company_bom[dish]:
                    qty = round(item_data["qty"] * factor, 1)
                    bill_items.append({
                        "डिश": "",
                        "सामग्री": item_data["item"],
                        "मात्रा": f"{qty} {item_data['unit']}"
                    })
            
            bill_df = pd.DataFrame(bill_items)
            st.markdown("### 📋 **डिश अनुसार सामग्री**")
            st.dataframe(bill_df, use_container_width=True, hide_index=True)
            
            # 🔥 PROFESSIONAL HTML - Dish name ONCE + Indented ingredients
            html_content = f"""
            <!DOCTYPE html>
            <html><head><meta charset="UTF-8">
            <title>{company_info['name']} बिल</title>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap');
            body {{font-family: 'Noto Sans Devanagari', Arial; margin: 0; padding: 20px; background: #f8f9fa;}}
            .header {{background: linear-gradient(145deg, #1e3a8a, #3b82f6); color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px;}}
            .info {{background: white; padding: 20px; border-radius: 12px; margin: 15px 0; box-shadow: 0 8px 25px rgba(0,0,0,0.1);}}
            table {{width: 100%; border-collapse: collapse; margin: 20px 0; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.1);}}
            th {{background: #1e3a8a !important; color: white; padding: 15px; font-weight: bold; font-size: 16px;}}
            .dish-name {{background: #dbeafe !important; font-weight: bold; font-size: 16px; border-left: 6px solid #1e3a8a; padding-left: 20px !important;}}
            .ingredient {{padding-left: 40px !important; border-left: 3px solid #60a5fa;}}
            td {{padding: 14px 15px; border-bottom: 1px solid #eee; font-size: 15px;}}
            tr:nth-child(even) {{background: #f8f9fa;}}
            tr:hover {{background: #e3f2fd !important;}}
            .signature {{text-align: center; margin-top: 40px; font-size: 18px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);}}
            @media print {{body {{background: white; margin: 0;}} .no-print {{display: none;}}}}
            </style>
            </head><body>
            <div class='header'>
                <h1 style='margin: 0; font-size: 32px;'>{company_info['name']}</h1>
                <p style='margin: 8px 0 0 0; font-size: 18px;'>{company_info['owners']}</p>
                <p style='margin: 0; font-size: 16px;'>{company_info['contact']}</p>
            </div>
            <div class='info'>
                <strong>ग्राहक:</strong> {customer} | <strong>कुल व्यक्ति:</strong> {people} | 
                <strong>तारीख:</strong> {date.today().strftime('%d/%m/%Y')} | 
                <strong>चयनित डिशेज:</strong> {len(dishes)}
            </div>
            
            <table>
            <thead><tr><th>डिश</th><th>सामग्री</th><th>मात्रा</th></tr></thead>
            <tbody>
            """
            
            # Add dish name ONCE + ingredients indented
            for dish in dishes:
                html_content += f"<tr class='dish-name'><td colspan='3'>{dish}</td></tr>"
                for item_data in company_bom[dish]:
                    qty = round(item_data["qty"] * factor, 1)
                    html_content += f"<tr class='ingredient'><td></td><td>{item_data['item']}</td><td>{qty} {item_data['unit']}</td></tr>"
            
            html_content += """
            </tbody></table>
            <div class='signature'>
                <strong>हस्ताक्षर:</strong> <span style='border-bottom: 3px solid #1e3a8a; width: 250px; display: inline-block; padding: 0 10px;'>__________________________</span>
                <br><small>ग्राहक हस्ताक्षर | Customer Signature</small>
            </div>
            </body></html>
            """
            
            st.download_button(
                label="📥 बिल डाउनलोड (Print → PDF)",
                data=html_content.encode('utf-8'),
                file_name=f"{company}_{customer}_{people}people_{date.today().strftime('%d%m%Y')}.html",
                mime="text/html",
                use_container_width=True
            )
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📥 Template डाउनलोड करें**")
            st.download_button("Download BOM", download_bom_template(), f"{company}_BOM_TEMPLATE.json", "application/json", use_container_width=True)
        with col2:
            st.markdown("**📤 BOM अपलोड करें**")
            uploaded = st.file_uploader("JSON File", type="json")
            if uploaded and st.button("💾 BOM अपडेट करें", type="primary", use_container_width=True):
                try:
                    bom_data = json.load(uploaded)
                    save_company_bom(company, bom_data)
                    st.success("✅ BOM अपडेट हो गया!")
                    st.rerun()
                except:
                    st.error("❌ गलत JSON फॉर्मेट!")
    
    st.button("🔐 Logout", on_click=lambda: [st.session_state.pop('company_logged_in'), st.rerun()])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>© 2026 रामलाल हलवाई - Bikaner</p>", unsafe_allow_html=True)
