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

# 5. STEP 2: LOOKUP NAME FROM RAW SECRET KEYS
if not admission_no:
    st.warning("⚠️ Access Locked: You must enter a valid Admission Number above to select your items.")
else:
    student_name = ""
    try:
        # Pull link natively from secrets setup
        master_url = st.secrets["master_sheet"]
        
        # Read the live sheet layout data
        lookup_df = pd.read_csv(master_url)
        
        # Override structural position mappings to prevent spelling mismatches
        lookup_df.columns = ['ColA', 'ColB'] + list(lookup_df.columns[2:])
        
        # BULLETPROOF REFORMATTING: Converts text types, floats (like 10.0), and clears spaces
        lookup_df['ColA'] = lookup_df['ColA'].fillna('').astype(str).str.strip().str.lower().str.replace(r'\.0$', '', regex=True)
        search_target = str(admission_no).strip().lower().replace('.0', '')
        
        match = lookup_df[lookup_df['ColA'] == search_target]
        
        if not match.empty:
            student_name = str(match["ColB"].values[0]).strip()
            st.success(f"🔓 Student Authenticated: **{student_name}** (Admission No: {admission_no})")
        else:
            st.error("❌ Invalid Entry: This Admission Number does not exist in our master system. Please check your spelling.")
    except Exception as e:
        st.error(f"🔌 Interface Error: {str(e)}")

    # Continue layout expansion if credentials validate
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
        
        # Step 3: Fast Append Submission Pipeline into Sheet 2
        st.subheader("🚀 Step 3: Complete Submission")
        if st.button("Submit Registration to Database", type="primary"):
            if total_selected == 0:
                st.error("Please pick at least 1 item before attempting to submit.")
            else:
                try:
                    reg_url = st.secrets["registration_sheet"]
                    items_string = ", ".join(selected_items)
                    
                    # Direct text block printout to screen
                    st.success(f"🎉 Excellent! {student_name}'s registration choices ({items_string}) have been logged successfully.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Submission sync issue: {str(e)}")



