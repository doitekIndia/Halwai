import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import yaml
import os
from datetime import date

st.set_page_config(page_title="👑 कैटरिंग एंटरप्राइजेज", layout="wide")

# ===================== ENTERPRISE CSS =====================
st.markdown("""
<style>
.enterprise-card {background: linear-gradient(145deg, #1e3a8a, #3b82f6); border-radius: 20px; padding: 2.5rem; margin: 1rem 0; box-shadow: 0 20px 40px rgba(0,0,0,0.3); border: 2px solid gold;}
.title-gold {font-size: 3rem !important; background: linear-gradient(45deg, gold, orange); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; text-align: center;}
.admin-panel {background: linear-gradient(145deg, #dc2626, #ef4444); border: 2px solid #b91c1c; border-radius: 15px; padding: 1.5rem;}
.company-profile {background: linear-gradient(145deg, #10b981, #34d399); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;}
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

# ===================== ADMIN FUNCTIONS =====================
def load_config():
    # Try Streamlit secrets first, then local config.yaml
    try:
        if "credentials" in st.secrets:
            return {
                "credentials": st.secrets["credentials"],
                "cookie": st.secrets["cookie"]
            }
    except:
        pass
    
    # Fallback to local config.yaml
    if os.path.exists("config.yaml"):
        try:
            with open("config.yaml", encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            st.error(f"❌ Config error: {e}")
    return None

def save_config(config):
    with open("config.yaml", "w", encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
    st.success("✅ Config saved!")
    st.rerun()

def is_admin(username):
    return username == "admin"

def hash_password(password):
    from streamlit_authenticator.utilities.hasher import Hasher
    try:
        return Hasher.hash(password)
    except:
        return Hasher([password]).generate()[0]

# ===================== LOAD CONFIG & AUTH =====================
config = load_config()
if config is None:
    st.error("❌ config.yaml not found! Run generate_config.py first.")
    st.stop()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

authenticator.login(location="main")
authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")

# ===================== BOM =====================
BASE_PEOPLE = 100
BOM = {
    "पनीर टिक्का": [{"item": "पनीर", "qty": 12, "unit": "किलो"}, {"item": "दही", "qty": 6, "unit": "किलो"}],
    "शाही पनीर": [{"item": "पनीर", "qty": 10, "unit": "किलो"}, {"item": "टमाटर", "qty": 8, "unit": "किलो"}],
    "दाल मखनी": [{"item": "साबुत उड़द", "qty": 6, "unit": "किलो"}, {"item": "मक्खन", "qty": 2, "unit": "किलो"}],
    "जीरा राइस": [{"item": "बासमती चावल", "qty": 8, "unit": "किलो"}],
    "बटर नान": [{"item": "मैदा", "qty": 10, "unit": "किलो"}],
    "गुलाब जामुन": [{"item": "खोया", "qty": 6, "unit": "किलो"}]
}

def generate_bill(dishes, people):
    factor = people / BASE_PEOPLE
    rows = []
    for dish in dishes:
        for ing in BOM[dish]:
            rows.append({"Dish": dish, "Ingredient": ing["item"], "Unit": ing["unit"], "Required Qty": round(ing["qty"] * factor, 2)})
    return pd.DataFrame(rows)

# ===================== HTML INVOICE (REPLACES WEASYPRINT) =====================
def generate_invoice_html(bill_df, customer, people, company_profile):
    # Group by dish for better display
    rows = ""
    last_dish = None
    for _, row in bill_df.iterrows():
        dish = row["Dish"] if row["Dish"] != last_dish else ""
        rows += f"""
        <tr>
            <td style='padding: 8px; border: 1px solid #333;'>{dish}</td>
            <td style='padding: 8px; border: 1px solid #333;'>{row['Ingredient']}</td>
            <td style='padding: 8px; border: 1px solid #333;'>{row['Unit']}</td>
            <td style='padding: 8px; border: 1px solid #333; text-align: right;'>{row['Required Qty']}</td>
        </tr>
        """
        last_dish = row["Dish"]
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{company_profile['name']} - बिल</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap');
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Noto Sans Devanagari', Arial, sans-serif; 
                margin: 20px; 
                line-height: 1.6;
                font-size: 14px;
            }}
            .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid #1e3a8a; }}
            .header h1 {{ 
                color: #1e3a8a; 
                font-size: 28px; 
                margin-bottom: 10px; 
                font-weight: 700;
            }}
            .header .owners {{ font-size: 16px; color: #333; margin-bottom: 5px; }}
            .header .contact {{ font-size: 14px; color: #666; }}
            .bill-info {{ margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-left: 5px solid #1e3a8a; }}
            .bill-info strong {{ color: #1e3a8a; }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0; 
                font-size: 13px;
            }}
            th {{ 
                background: linear-gradient(145deg, #1e3a8a, #3b82f6); 
                color: white; 
                padding: 12px 8px; 
                text-align: left; 
                font-weight: 700;
            }}
            td {{ 
                padding: 10px 8px; 
                border: 1px solid #ddd; 
                vertical-align: top;
            }}
            tr:nth-child(even) {{ background-color: #f8f9fa; }}
            tr:hover {{ background-color: #e3f2fd; }}
            .signature {{ 
                margin-top: 40px; 
                text-align: center; 
                padding-top: 30px; 
                border-top: 2px dashed #1e3a8a;
            }}
            .footer {{ 
                margin-top: 30px; 
                text-align: center; 
                color: #666; 
                font-size: 12px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }}
            @media print {{ body {{ margin: 0; }} .no-print {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{company_profile['name']}</h1>
            <div class="owners">{company_profile['owners']}</div>
            <div class="contact">{company_profile['contact']}</div>
        </div>
        
        <div class="bill-info">
            <strong>बिल तिथि:</strong> {date.today().strftime('%d-%m-%Y')}<br>
            <strong>ग्राहक:</strong> {customer}<br>
            <strong>कुल व्यक्ति:</strong> {people}
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>डिश</th>
                    <th>सामग्री</th>
                    <th>यूनिट</th>
                    <th>आवश्यक मात्रा</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        
        <div class="signature">
            <p><strong>तैयार किया:</strong> {company_profile['name']}</p>
            <p style="margin-top: 30px; font-size: 16px;">Authorized Signature: ______________________</p>
        </div>
        
        <div class="footer">
            रामलाल हलवाई कैटरिंग एंटरप्राइजेज - बीकानेर | © 2026
        </div>
    </body>
    </html>
    """

# ===================== MAIN APP =====================
if authentication_status:
    st.markdown(f"""
    <div class='enterprise-card'>
        <h1 class='title-gold'>Welcome {name}! 👑</h1>
    </div>
    """, unsafe_allow_html=True)

    USER_DIR = f"data/{username}"
    os.makedirs(USER_DIR, exist_ok=True)
    HISTORY_FILE = f"{USER_DIR}/history.csv"
    if not os.path.exists(HISTORY_FILE):
        pd.DataFrame(columns=["Date", "Customer", "People", "Dishes"]).to_csv(HISTORY_FILE, index=False)

    # ===================== ADMIN SECTION =====================
    if is_admin(username):
        st.warning("⚠️ Admin cannot generate bills. Use Admin Panel only!")
        tab1, tab2 = st.tabs(["🔧 Admin Panel", "👥 Users"])
        
        with tab1:
            st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
            st.markdown("### 👑 User Editor")
            
            config = load_config()
            if config and "credentials" in config and "usernames" in config["credentials"]:
                users_df = pd.DataFrame([
                    {"Username": k, "Name": v["name"], "Email": v["email"]} 
                    for k, v in config["credentials"]["usernames"].items() if k != "admin"
                ])
                if not users_df.empty:
                    st.dataframe(users_df, use_container_width=True)
                else:
                    st.info("No users found")
            
            st.markdown("---")
            if config and "credentials" in config and "usernames" in config["credentials"]:
                user_list = [k for k in config["credentials"]["usernames"].keys() if k != "admin"]
                if user_list:
                    selected_user = st.selectbox("👤 Select User to Edit", user_list)
                    
                    current_user = config["credentials"]["usernames"][selected_user]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_name = st.text_input("📝 Name", value=current_user["name"])
                    with col2:
                        new_email = st.text_input("📧 Email", value=current_user["email"])
                    with col3:
                        new_password = st.text_input("🔐 New Password (leave empty to keep)", type="password", value="")
                    
                    col4, col5 = st.columns([2, 1])
                    with col4:
                        if st.button("💾 UPDATE USER", type="primary", use_container_width=True):
                            new_config = config.copy()
                            new_config["credentials"]["usernames"][selected_user] = {
                                "name": new_name if new_name else current_user["name"],
                                "email": new_email if new_email else current_user["email"],
                                "password": hash_password(new_password) if new_password else current_user["password"]
                            }
                            save_config(new_config)
                            st.success(f"✅ {selected_user} updated successfully!")
                            st.rerun()
                    
                    with col5:
                        if st.button("🗑️ DELETE", type="secondary", use_container_width=True):
                            new_config = config.copy()
                            del new_config["credentials"]["usernames"][selected_user]
                            save_config(new_config)
                            st.success(f"✅ {selected_user} deleted!")
                            st.rerun()
                else:
                    st.warning("No editable users found")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### 🏢 5 Halwai Companies")
            for username_key, profile in COMPANY_PROFILES.items():
                st.markdown(f"""
                <div class='company-profile'>
                    <h4>{profile['name']}</h4>
                    <p><strong>Owners:</strong> {profile['owners']}</p>
                    <p><strong>Contact:</strong> {profile['contact']}</p>
                </div>
                """, unsafe_allow_html=True)

    # ===================== HALWAI USER SECTION =====================
    elif username in COMPANY_PROFILES:
        company_profile = COMPANY_PROFILES[username]
        st.success(f"✅ Logged in as: **{company_profile['name']}**")
        
        tab1, tab2 = st.tabs(["💰 नया बिल", "📊 इतिहास"])
        
        with tab1:
            with st.form("bill_form"):
                customer = st.text_input("ग्राहक का नाम", placeholder="Bikaji Foods...")
                people = st.number_input("कुल व्यक्ति", 25, 5000, 150, 25)
                dishes = st.multiselect("डिशेज चुनें", list(BOM.keys()))
                submitted = st.form_submit_button("📄 बिल बनाएं")

            if submitted and customer and dishes:
                bill_df = generate_bill(dishes, people)
                st.markdown("### 📋 सामग्री आवश्यकता")
                st.dataframe(bill_df, use_container_width=True)

                # ✅ HTML DOWNLOAD (WORKS ON STREAMLIT CLOUD!)
                html_content = generate_invoice_html(bill_df, customer, people, company_profile)
                safe_filename = f"{username}_{customer.replace(' ', '_')}_{date.today().strftime('%d-%m-%Y')}.html"
                
                st.download_button(
                    label="📥 HTML बिल डाउनलोड (प्रिंट → PDF)",
                    data=html_content.encode('utf-8'),
                    file_name=safe_filename,
                    mime="text/html"
                )
                
                # Save history
                new_record = pd.DataFrame({
                    "Date": [date.today().strftime('%d-%m-%Y')],
                    "Customer": [customer], "People": [people], "Dishes": [", ".join(dishes)]
                })
                history = pd.read_csv(HISTORY_FILE)
                history = pd.concat([history, new_record], ignore_index=True)
                history.to_csv(HISTORY_FILE, index=False)
                st.success(f"✅ बिल '{customer}' के लिए तैयार! HTML डाउनलोड करें → Chrome में Print → Save as PDF!")

        with tab2:
            if os.path.exists(HISTORY_FILE):
                history = pd.read_csv(HISTORY_FILE)
                st.markdown("### 📊 आपका बिल इतिहास")
                st.dataframe(history, use_container_width=True)
            else:
                st.info("कोई बिल इतिहास नहीं मिला")
    
    else:
        st.error("❌ Unknown user type!")

    with st.sidebar:
        if is_admin(username):
            st.markdown("### 🔧 ADMIN")
        elif username in COMPANY_PROFILES:
            profile = COMPANY_PROFILES[username]
            st.markdown(f"### 🏢 {profile['name']}")
            st.markdown(f"**{profile['owners']}**")
            st.markdown(f"**{profile['contact']}**")
        authenticator.logout("🔐 Logout", "sidebar")

elif authentication_status is False:
    st.error("❌ गलत Username/Password")
else:
    st.info("कृपया लॉगिन करें")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>© 2026 कैटरिंग एंटरप्राइजेज - Bikaner</p>", unsafe_allow_html=True)
