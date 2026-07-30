import streamlit as st
import pandas as pd
import base64
import random
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

# Helper function to completely strip spaces and non-characters for bulletproof verification
def strict_clean(val):
    return ''.join(c for c in str(val).strip().lower().split('.')[0] if c.isalnum())

# 5. STEP 2: CACHE-BUSTING VERIFICATION ENGINE
if not admission_no:
    st.warning("⚠️ Access Locked: You must enter a valid Admission Number above to select your items.")
else:
    student_name = ""
    search_target = strict_clean(admission_no)
    
    try:
        # Establish connection with Google Sheets using Streamlit Secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Read the Master Student Sheet (Sheet 1) from secrets configuration
        # This automatically appends a cache buster under the hood to ensure live data
        raw_df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["master_sheet_url"], ttl=0)
        
        if not raw_df.empty:
            # Overwrite active headings to ignore manual cell mismatch typing issues entirely
            raw_df.columns = ['ColA', 'ColB'] + list(raw_df.columns[2:])
            raw_df['CleanA'] = raw_df['ColA'].fillna('').apply(strict_clean)
            
            # Execute verification search query
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
                try:
                    # 1. Fetch current submissions from your Entries Sheet (Sheet 2)
                    entries_df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["entries_sheet_url"], ttl=0)
                    
                    # 2. Formulate the new row registration entry
                    items_string = ", ".join(selected_items)
                    new_data = pd.DataFrame([{
                        "Admission Number": admission_no,
                        "Student Name": student_name,
                        "Selected Items": items_string
                    }])
                    
                    # 3. Concatenate and clear matching column formats
                    updated_df = pd.concat([entries_df, new_data], ignore_index=True)
                    
                    # 4. Push updated dataset back to Sheet 2
                    conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["entries_sheet_url"], data=updated_df)
                    
                    st.success(f"🎉 Excellent! {student_name}'s registration choices ({items_string}) have been logged successfully into Sheet 2.")
                    st.balloons()
                    
                except Exception as write_err:
                    st.error(f"Failed to record entry to database sheet: {str(write_err)}")



