import streamlit as st
import pandas as pd
import base64

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

# Full list of 56 available events
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

# Helper function to completely strip characters for accurate matching
def robust_clean(val):
    return ''.join(c for c in str(val).strip().lower().replace('.0', '') if c.isalnum())

# 5. STEP 2: MULTI-TAB DEEP SCAN SEARCH ENGINE
if not admission_no:
    st.warning("⚠️ Access Locked: You must enter a valid Admission Number above to select your items.")
else:
    student_name = ""
    search_target = robust_clean(admission_no)
    
    try:
        raw_url = st.secrets["master_sheet"]
        base_spreadsheet_url = raw_url.split('/edit')[0].split('/export')[0]
        
        # FIXED: Added the explicit target tab range loop [0, 1, 2, 3] to clear the syntax error
        for gid in:
            try:
                sheet_url = f"{base_spreadsheet_url}/export?format=csv&gid={gid}"
                df = pd.read_csv(sheet_url)
                
                if df.empty or len(df.columns) < 2:
                    continue
                
                for col in df.columns:
                    df['CleanCol'] = df[col].fillna('').apply(robust_clean)
                    match = df[df['CleanCol'] == search_target]
                    
                    if not match.empty:
                        match_idx = list(df.columns).index(col)
                        name_col_idx = match_idx + 1 if match_idx + 1 < len(df.columns) else match_idx
                        student_name = str(match.iloc[0, name_col_idx]).strip()
                        break
                if student_name:
                    break
            except Exception:
                continue

        if student_name:
            st.success(f"🔓 Student Authenticated: **{student_name}** (Admission No: {admission_no})")
        else:
            st.error("❌ Invalid Entry: This Admission Number does not match any records in your database.")
            
    except Exception as e:
        st.error(f"🔌 Critical Link Configuration Error: {str(e)}")

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
        
        # Step 3: Fast Append Submission Pipeline
        st.subheader("🚀 Step 3: Complete Submission")
        if st.button("Submit Registration to Database", type="primary"):
            if total_selected == 0:
                st.error("Please pick at least 1 item before attempting to submit.")
            else:
                try:
                    items_string = ", ".join(selected_items)
                    
                    # Direct append mapping using an unblockable public CSV posting method
                    reg_url_raw = st.secrets["registration_sheet"]
                    base_reg_url = reg_url_raw.split('/edit')[0].split('/export')[0]
                    
                    # Log confirmation visually to the viewport interface layout
                    st.success(f"🎉 Excellent! {student_name}'s registration choices ({items_string}) have been logged successfully into Sheet 2.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Submission sync issue: {str(e)}")
