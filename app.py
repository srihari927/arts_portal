import streamlit as st
import pandas as pd
import base64
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. Page Configuration
st.set_page_config(page_title="SKPS Youth Festival SUVARNAM2k26", page_icon="🎨", layout="centered")

# 2. FIXED: Universal CSS Background Image Integration
try:
    if os.path.exists("background.png"):
        with open("background.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        background_style = f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], .main {{
            background-image: url("data:image/png;base64,{encoded_string}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
            background-color: transparent !important;
        }}
        [data-testid="stHeader"], [data-testid="stAppViewBlockContainer"] {{
            background: transparent !important;
            background-color: transparent !important;
        }}
        .stTextInput input, .stMultiSelect div {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #1e293b !important;
            border-radius: 6px !important;
        }}
        </style>
        """
        st.markdown(background_style, unsafe_allow_html=True)
except Exception:
    pass

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

# Initialize local tracking file database structures
DATA_FILE = "festival_registrations.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Admission Number", "Student Name", "Selected Items"]).to_csv(DATA_FILE, index=False)

# FIXED INDEPENDENT BACKEND HELPER
def send_report_email():
    current_df = pd.read_csv(DATA_FILE)
    
    html_report = "<html><head><style>"
    html_report += "body { font-family: Arial, sans-serif; margin: 20px; color: #1e293b; }"
    html_report += "h1 { text-align: center; color: #1e3a8a; }"
    html_report += "table { width: 100%; border-collapse: collapse; margin-top: 20px; }"
    html_report += "th { background-color: #1e3a8a; color: white; padding: 12px; text-align: left; }"
    html_report += "tr:nth-child(even) { background-color: #f8fafc; }"
    html_report += "</style></head><body>"
    html_report += "<h1>🏆 SKPS Youth Festival SUVARNAM2k26</h1>"
    html_report += "<h3 style='text-align: center; color: #64748b;'>Official Consolidated Registration Ledger</h3>"
    html_report += "<table><thead><tr><th>Admission No.</th><th>Student Name</th><th>Registered Items Selection Directory</th></tr></thead><tbody>"
    
    for _, r in current_df.iterrows():
        html_report += "<tr>"
        html_report += "<td style='padding: 10px; border: 1px solid #cbd5e1;'>" + str(r["Admission Number"]) + "</td>"
        html_report += "<td style='padding: 10px; border: 1px solid #cbd5e1;'>" + str(r["Student Name"]) + "</td>"
        html_report += "<td style='padding: 10px; border: 1px solid #cbd5e1;'>" + str(r["Selected Items"]) + "</td>"
        html_report += "</tr>"
        
    html_report += "</tbody></table></body></html>"
    
    sender = st.secrets["email"]["sender_address"]
    password = st.secrets["email"]["sender_password"]
    receiver = st.secrets["email"]["receiver_address"]
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "🏆 SUVARNAM2k26 Live Registration Report Table"
    msg['From'] = sender
    msg['To'] = receiver
    msg.attach(MIMEText(html_report, 'html'))
    
    server = smtplib.SMTP("://gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()
    st.success(f"🚀 Success! The live registrations ledger has been emailed directly to {receiver}")

# Establish connection matrix to pull Master student lookup directory from Secrets Tab URL
master_url = ""
try:
    master_url = st.secrets["connections"]["gsheets"]["master_sheet_url"]
    if "edit" in master_url:
        master_url = master_url.split("/edit")[0] + "/export?format=csv"
except Exception:
    pass

@st.cache_data(ttl=10)
def load_master_data(url):
    # FIXED: Skips any formatting rows and reads data directly from positional data grids
    df = pd.read_csv(url, header=None)
    # Automatically drops completely empty rows or layout borders at the top
    df = df.dropna(how='all').reset_index(drop=True)
    # Assign standard working headers dynamically to bypass naming typos
    df.columns = ['AdmissionNo', 'StudentName'] + list(df.columns[2:])
    return df

# 4. STEP 1: READ ADMISSION NUMBER INPUT
admission_no = st.text_input("🔑 Step 1: Enter Admission Number to begin:", value="", key="main_ad_input").strip()

# 5. STEP 2: UNIQUE LOGON & PROFILE VERIFICATION ENGINE
if not admission_no:
    st.warning("⚠️ Access Locked: You must enter a valid Admission Number above to select your items.")
else:
    student_name = ""
    search_target = strict_clean(admission_no)
    
    existing_records = pd.read_csv(DATA_FILE)
    existing_records['CleanCheck'] = existing_records['Admission Number'].fillna('').apply(strict_clean)
    
    if search_target in existing_records['CleanCheck'].values:
        st.error("❌ Access Denied: A registration submission entry has already been logged for this Admission Number. Duplicates are blocked.")
    else:
        try:
            raw_df = load_master_data(master_url)
            
            if not raw_df.empty:
                # Apply validation parameters cleanly to positional vectors
                raw_df['CleanA'] = raw_df['AdmissionNo'].fillna('').apply(strict_clean)
                match = raw_df[raw_df['CleanA'] == search_target]
                
                if not match.empty:
                    student_name = str(match.iloc[0]['StudentName']).strip()
                    st.success(f"🔓 Student Authenticated: **{student_name}** (Admission No: {admission_no})")
                else:
                    st.error("❌ Invalid Entry: This Admission Number does not match any records inside your Master list.")
        except Exception as e:
            st.error(f"🔌 Critical Link Pipeline Interrupted: {str(e)}")

    # 6. STEP 3: ITEM SELECTION & LOCAL DATABASE STORAGE 
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
                try:
                    fresh_check = pd.read_csv(DATA_FILE)
                    fresh_check['CleanCheck'] = fresh_check['Admission Number'].fillna('').apply(strict_clean)
                    
                    if search_target in fresh_check['CleanCheck'].values:
                        st.error("Submission blocked. Your registration details were already logged by another portal session.")
                    else:
                        items_string = ", ".join(selected_items)
                        new_row = pd.DataFrame([{
                            "Admission Number": admission_no,
                            "Student Name": student_name,
                            "Selected Items": items_string
                        }])
                        new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                        
                        st.success(f"🎉 Success! {student_name}'s event selections have been safely locked for SUVARNAM2k26.")
                        st.balloons()


