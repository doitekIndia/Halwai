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

# ===================== FIXED CONFIG LOADING =====================
def load_config():
    config = None
    
    # Try Streamlit Secrets FIRST (Cloud deployment)
    try:
        if hasattr(st, 'secrets') and st.secrets:
            # Convert flat secrets to nested structure
            usernames = {}
            for key in st.secrets:
                if key.startswith('usernames.'):
                    parts = key.split('.', 2)
                    user = parts[1]
                    field = parts[2]
                    if user not in usernames:
                        usernames[user] = {}
                    usernames[user][field] = st.secrets[key]
            
            config = {
                "credentials": {"usernames": usernames},
                "cookie": {
                    "name": st.secrets.get("cookie.name", "halwai_auth"),
                    "key": st.secrets.get("cookie.key", "some_key"),
                    "expiry_days": st.secrets.get("cookie.expiry_days", 30)
                }
            }
    except:
        pass
    
    # Fallback to local config.yaml (Local testing)
    if config is None and os.path.exists("config.yaml"):
        try:
            with open("config.yaml", encoding='utf-8') as file:
                config = yaml.safe_load(file)
        except Exception as e:
            st.error(f"❌ Config error: {e}")
    
    return config

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

# ===================== LOAD & AUTHENTICATE =====================
config = load_config()
if config is None:
    st.error("❌ Configuration not found!")
    st.stop()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

authenticator.login(location="main")
authentication_status = st.session_state["authentication_status"]
name = st.session_state["name"]
username = st.session_state["username"]

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

def generate_invoice_html(bill_df, customer, people, company_profile):
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
            body {{ font-family: 'Noto Sans Devanagari', Arial, sans-serif; margin: 20px; font-size: 14px; }}
            .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid #1e3a8a; }}
            .header h1 {{ color: #1e3a8a; font-size: 28px; margin-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #1e3a8a; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border: 1px solid #ddd; }}
            .signature {{ margin-top: 40px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{company_profile['name']}</h1>
            <div>{company_profile['owners']}</div>
            <div>{company_profile['contact']}</div>
        </div>
        <p><strong>बिल तिथि:</strong> {date.today().strftime('%d-%m-%Y')} | <strong>ग्राहक:</strong> {customer} | <strong>व्यक्ति:</strong> {people}</p>
        <table><tr><th>डिश</th><th>सामग्री</th><th>यूनिट</th><th>मात्रा</th></tr>{rows}</table>
        <div class="signature">Authorized Signature: ______________________</div>
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

    if is_admin(username):
        st.warning("⚠️ Admin cannot generate bills. Use Admin Panel only!")
        tab1, tab2 = st.tabs(["🔧 Admin Panel", "👥 Users"])
        # Admin tabs code here (same as before)
        
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

                html_content = generate_invoice_html(bill_df, customer, people, company_profile)
                safe_filename = f"{username}_{customer.replace(' ', '_')}_{date.today().strftime('%d-%m-%Y')}.html"
                
                st.download_button(
                    label="📥 HTML बिल डाउनलोड (Print → PDF)",
                    data=html_content.encode('utf-8'),
                    file_name=safe_filename,
                    mime="text/html"
                )
                
                # Save history
                new_record = pd.DataFrame({
                    "Date": [date.today().strftime('%d-%m-%Y')],
                    "Customer": [customer], "People": [people], "Dishes": [", ".join(dishes)]
                })
                history_df = pd.read_csv(HISTORY_FILE)
                history_df = pd.concat([history_df, new_record], ignore_index=True)
                history_df.to_csv(HISTORY_FILE, index=False)
                st.success(f"✅ बिल '{customer}' तैयार!")

        with tab2:
            if os.path.exists(HISTORY_FILE):
                history = pd.read_csv(HISTORY_FILE)
                st.dataframe(history, use_container_width=True)

    with st.sidebar:
        authenticator.logout("🔐 Logout", "sidebar")

elif authentication_status is False:
    st.error("❌ गलत Username/Password")
else:
    st.info("कृपया लॉगिन करें")
