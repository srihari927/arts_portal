import streamlit as st
import pandas as pd
import base64
import requests
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(page_title="Arts Festival Registration Portal", page_icon="🎨", layout="centered")

# 2. Local Background Image Integration
try:
    with open("background.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    background_style = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)
except FileNotFoundError:
    pass

# 3. Header Logo
try:
    st.image("logo.png", width=120)
except Exception:
    st.write("📁 *[School Logo]*")

st.title("🎨 Cultural Arts Festival Registration")
st.write("Please authenticate your profile below to unlock event selection.")

# 4. STEP 1: ENTER ADMISSION NUMBER
admission_no = st.text_input("🔑 Step 1: Enter Admission Number to begin:", value="").strip()

# Full list of 55 available events
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

# Initialize the Sheets engine
conn = st.connection("gsheets", type=GSheetsConnection)

# Cache student data for 10 minutes so validation is instant
@st.cache_data(ttl=600)
def load_master_data(url):
    return conn.read(spreadsheet=url)

# 5. STEP 2: VERIFICATION ENGINE
if not admission_no:
    st.warning("⚠️ Access Locked: You must enter a valid Admission Number above to select your items.")
else:
    student_name = ""
    search_target = strict_clean(admission_no)
    
    try:
        raw_df = load_master_data(st.secrets["connections"]["gsheets"]["master_sheet_url"])
        
        if not raw_df.empty:
            raw_df.columns = ['ColA', 'ColB'] + list(raw_df.columns[2:])
            raw_df['CleanA'] = raw_df['ColA'].fillna('').apply(strict_clean)
            
            match = raw_df[raw_df['CleanA'] == search_target]
            
            if not match.empty:
                student_name = str(match.iloc[0]['ColB']).strip()
                st.success(f"🔓 Student Authenticated: **{student_name}** (Admission No: {admission_no})")
            else:
                st.error("❌ Invalid Entry: This Admission Number does not match any records inside your Master list.")
    except Exception as e:
        st.error(f"🔌 Critical Link Pipeline Interrupted: {str(e)}")

    # 6. LAYOUT EXPANSION ONCE PROFILE LOADS
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
        
        # Step 3: Registration Confirmation Display Box
        st.subheader("🚀 Step 3: Complete Submission")
        if st.button("Submit Registration to Database", type="primary"):
            if total_selected == 0:
                st.error("Please pick at least 1 item before attempting to submit.")
            else:
                items_string = ", ".join(selected_items)
                
                try:
                    # Dynamically maps values straight from your saved Secrets panel configuration
                    form_url = st.secrets["connections"]["gsheets"]["form_url"]
                    form_data = {
                        st.secrets["connections"]["gsheets"]["form_entry_admission"]: admission_no,
                        st.secrets["connections"]["gsheets"]["form_entry_name"]: student_name,
                        st.secrets["connections"]["gsheets"]["form_entry_items"]: items_string
                    }
                    
                    # Fire entry straight to Google forms database background endpoint
                    response = requests.post(form_url, data=form_data)
                    
                    if response.status_code == 200 or response.ok:
                        st.success(f"🎉 Excellent! {student_name}'s registration choices ({items_string}) have been logged successfully into Sheet 2.")
                        st.balloons()
                    else:
                        st.error("Submission delivered, but backend returned an unexpected network confirmation code.")
                except Exception as form_err:
                    st.error(f"Failed to post via automated form engine: {str(form_err)}")


