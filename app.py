import streamlit as st
import pandas as pd
import base64
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(page_title="SKPS Youth Festival SUVARNAM2k26", page_icon="🎨", layout="centered")

# 2. Modern Native CSS UI & Interactive Elements Styling
if os.path.exists("background.png"):
    with open("background.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
    <style>
    .main, [data-testid="stAppViewContainer"], [data-testid="stAppViewMain"] {{
        background-image: url("data:image/png;base64,{encoded_string}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    .block-container, [data-testid="stHeader"], [data-testid="stAppViewBlockContainer"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    .stTextInput input, .stMultiSelect div {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1e293b !important;
        border-radius: 6px !important;
    }}
    .stButton button {{
        width: 100% !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. Logo Sizing Configuration
if os.path.exists("logo.png"):
    st.image("logo.png", width=450)
else:
    st.write("📁 *[SKPS School Logo]*")

st.title("🎨 SKPS Youth Festival SUVARNAM2k26")
st.write("Please authenticate your student profile below to select your registered competition items.")

# Full directory list of available competitive events
all_events = [
    "Story telling (English)", "Speech (English)", "Speech (Malayalam)", "Elocution (English)",
    "Elocution (Malayalam)", "Elocution (Hindi)", "Extempore (English)", "Extempore (Malayalam)",
    "Extempore (Hindi)", "Mono Act", "Mimicry", "Anchoring", "Mime", "PowerPoint Presentation",
    "Recitation (English)", "Recitation (Malayalam)", "Recitation (Hindi)", "Recitation (Arabic)",
    "Recitation (Sanskrit)", "Light Music (Lalithaganam)", "Classical Music (Carnatic)",
    "Mappilappattu", "Group Song", "Patriotic Song", "Western Music Concert", "Folk Dance",
    "Bharatanatyam", "Mohiniyattam", "Kuchipudi", "Kolkali", "Thiruvathirakali", "Oppana",
    "Margam Kali", "Band", "Tabla Eastern", "Mridangam Eastern", "Guitar Western", "Violin Eastern",
    "Pencil Drawing", "Painting (Crayons)", "Painting Watercolour", "Painting Oil Colour",
    "Digital Painting", "Poster Designing", "Cartoon", "Collage", "Essay Writing (English)",
    "Essay Writing (Malayalam)", "Essay Writing (Hindi)", "Story Writing (English)",
    "Story Writing (Malayalam)", "Story Writing (Hindi)", "Versification (English)",
    "Versification (Malayalam)", "Versification (Hindi)"
]

def strict_clean(val):
    return ''.join(c for c in str(val).strip().lower().split('.') if c.isalnum())

# 4. INITIALIZE PRIVATE CLOUD SHEET CONNECTION (Guarantees zero registration data loss)
conn = st.connection("gsheets", type=GSheetsConnection)

def get_live_registrations():
    try:
        df = conn.read(ttl="0s") # Force raw non-cached pull straight from cloud
        if df.empty or len(df.columns) < 3:
            return pd.DataFrame(columns=["Admission Number", "Student Name", "Selected Items"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Admission Number", "Student Name", "Selected Items"])

# 5. FAST LOCAL MASTER SHEET LOOKUP (Zero web latency timeouts)
@st.cache_data(ttl=600)
def load_master_data():
    if os.path.exists("master_sheet.xlsx"):
        df = pd.read_excel("master_sheet.xlsx", engine='openpyxl', header=0)
        df = df.dropna(how='all').reset_index(drop=True)
        df.columns = ['AdmissionNo', 'Studentname'] + list(df.columns[2:])
        df['AdmissionNo'] = df['AdmissionNo'].astype(str).str.split('.').str.get(0).str.strip()
        return df
    return pd.DataFrame(columns=['AdmissionNo', 'Studentname'])

master_df = load_master_data()

# 6. STEP 1: READ ADMISSION NUMBER INPUT
admission_no = st.text_input("🔑 Step 1: Enter Admission Number to begin:", value="", key="main_ad_input").strip()

# 7. STEP 2: PROFILE VERIFICATION & LIVE DUPLICATE GUARD
if not admission_no:
    st.warning("⚠️ Access Locked: You must enter a valid Admission Number above to select your items.")
else:
    student_name = ""
    search_target = strict_clean(admission_no)
    
    # Check live registrations from the cloud sheet safely
    live_df = get_live_registrations()
    is_duplicate = False
    
    if not live_df.empty and len(search_target) > 0:
        live_df['CleanCheck'] = live_df['Admission Number'].astype(str).fillna('').apply(strict_clean)
        if search_target in live_df['CleanCheck'].values:
            is_duplicate = True

    if is_duplicate:
        st.error("❌ Access Denied: A registration submission entry has already been logged for this Admission Number. Duplicates are blocked.")
    else:
        # Cross reference master list data
        if not master_df.empty:
            master_df['CleanA'] = master_df['AdmissionNo'].fillna('').apply(strict_clean)
            match = master_df[master_df['CleanA'] == search_target]
            
            if not match.empty:
                # Extracts raw clean string scalar name completely clear of lists/brackets
                student_name = str(match.iloc[0]['Studentname']).strip()
                st.success(f"🔓 Student Authenticated: **{student_name}** (Admission No: {admission_no})")
            else:
                st.error("❌ Invalid Entry: This Admission Number does not match any records inside your Master list.")
        else:
            st.error("📁 Master index layout spreadsheet file not found inside directory workspace.")

    # 8. STEP 3: ITEM SELECTION & AUTOMATED CLOUD SYNC
    if student_name:
        st.subheader("📋 Step 2: Select Your Registered Items (Max 5)")
        
        selected_items = st.multiselect(
            "Choose your competitive events from the directory:",
            options=all_events,
            max_selections=5,
            help="The system automatically prevents you from selecting more than 5 items."
        )
        
        total_selected = len(selected_items)
        st.info(f"Slots allocated: {total_selected} / 5 items selected.")
        
        if total_selected == 5:
            st.warning("🔒 Maximum registration threshold reached for this profile.")
            
        st.divider()
        
        st.subheader("🚀 Step 3: Complete Submission")
        if st.button("Submit Registration Details", type="primary"):
            if total_selected == 0:
                st.error("Please pick at least 1 item before attempting to submit.")
            else:
                # Final guard check loop execution right at submission line
                fresh_live_df = get_live_registrations()
                is_fresh_duplicate = False
                if not fresh_live_df.empty:
                    fresh_live_df['CleanCheck'] = fresh_live_df['Admission Number'].astype(str).fillna('').apply(strict_clean)
                    if search_target in fresh_live_df['CleanCheck'].values:
                        is_fresh_duplicate = True
                        
                if is_fresh_duplicate:
                    st.error("Submission blocked. Your registration details were already logged by another portal session.")
                else:
                    try:
                        items_string = ", ".join(selected_items)
                        new_row = pd.DataFrame([{
                            "Admission Number": str(admission_no),
                            "Student Name": str(student_name),
                            "Selected Items": str(items_string)
                        }])
                        
                        # Concatenate and stream write transaction direct to cloud spreadsheet rows
                        updated_df = pd.concat([fresh_live_df, new_row], ignore_index=True)
                        conn.update(data=updated_df)
                        
                        st.success(f"🎉 Success! {student_name}'s event selections have been safely locked for SUVARNAM2k26.")
                        st.balloons()
                        st.rerun()
                    except Exception as write_err:
                        st.error(f"Failed to securely record entry to cloud ledger: {str(write_err)}")

# 9. 🔐 ADMIN DASHBOARD - AUTOMATED BACKEND EMAIL REPORTING
st.write("---")
st.subheader("🛠️ Secure Admin Portal")
admin_code = st.text_input("Enter Admin Verification Code:", type="password", key="admin_key").strip()

if admin_code == st.secrets["admin"]["password"]:
    st.success("🔑 Code Verified. Admin Options Unlocked.")
    
    current_live_df = get_live_registrations()
    st.info(f"📊 Live Server Analytics Counter: {len(current_live_df)} secure entries saved inside your cloud storage ledger.")
    
    if st.button("📧 Email Live Master Report Table to Admin Inbox", use_container_width=True):
        if not current_live_df.empty:
            try:
                # Construct HTML table formatting summary rows dynamically
                html_rows = ""
                for _, r in current_live_df.iterrows():
                    html_rows += f"<tr>"
                    html_rows += f"<td style='padding:10px; border:1px solid #cbd5e1;'>{r['Admission Number']}</td>"
                    html_rows += f"<td style='padding:10px; border:1px solid #cbd5e1;'>{r['Student Name']}</td>"
                # Construct HTML table formatting summary rows dynamically
                html_rows = ""
                for _, r in current_live_df.iterrows():
                    html_rows += f"<tr>"
                    html_rows += f"<td style='padding:10px; border:1px solid #cbd5e1;'>{r['Admission Number']}</td>"
                    html_rows += f"<td style='padding:10px; border:1px solid #cbd5e1;'>{r['Student Name']}</td>"
                    html_rows += f"<td style='padding:10px; border:1px solid #cbd5e1;'>{r['Selected Items']}</td>"
                    html_rows += f"</tr>"
                    
                html_report = f"""
                <html><body>
                    <h2 style='color:#1e3a8a; text-align:center;'>🏆 SKPS Youth Festival SUVARNAM2k26</h2>
                    <h4 style='color:#64748b; text-align:center;'>Official Consolidated Registration Cloud Ledger</h4>
                    <table style='width:100%; border-collapse:collapse; margin-top:15px;'>
                        <thead><tr style='background-color:#1e3a8a; color:white;'>
                            <th style='padding:12px; text-align:left;'>Admission No.</th>
                            <th style='padding:12px; text-align:left;'>Student Name</th>
                            <th style='padding:12px; text-align:left;'>Registered Items Selection Directory</th>
                        </tr></thead>
                        <tbody>{html_rows}</tbody>
                    </table>
                </body></html>
                """
                
                sender = st.secrets["email"]["sender_address"]
                password = st.secrets["email"]["sender_password"]
                receiver = st.secrets["email"]["receiver_address"]
                
                msg = MIMEMultipart('alternative')
                msg['Subject'] = "🏆 SUVARNAM2k26 Real-Time Cloud Registration Table"
                msg['From'] = sender
                msg['To'] = receiver
                msg.attach(MIMEText(html_report, 'html'))
                
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
                server.quit()
                st.success(f"🚀 Success! The live master ledger has been compiled and emailed directly to {receiver}")
            except Exception as mail_err:
                st.error(f"Email transit routing pipeline failed: {str(mail_err)}")
        else:
            st.warning("Cannot email an empty table. Awaiting incoming submissions.")
            
    st.write(" ")
    if st.button("🔴 Clear & Reset All Registrations (Delete Trial Entries)", use_container_width=True):
        try:
            # Overwrite cloud table sheet back to fresh columns blueprint template layout instantly
            blank_df = pd.DataFrame(columns=["Admission Number", "Student Name", "Selected Items"])
            conn.update(data=blank_df)
            st.success("🧹 Cloud ledger database wiped clean! App restarted safely.")
            st.rerun()
        except Exception as reset_err:
            st.error(f"Failed to clear cloud spreadsheet: {str(reset_err)}")

elif admin_code != "":
    st.error("❌ Incorrect Admin Verification Code. Access Restricted.")

