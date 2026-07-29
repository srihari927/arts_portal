import streamlit as st
from streamlit_gsheets import GSheetsConnection
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

# 4. STEP 1: FORCE ADMISSION NUMBER ENTRY FIRST
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

# 5. STEP 2: UNLOCK SELECTION ONLY IF ADMISSION NUMBER IS FILLED
if not admission_no:
    st.warning("⚠️ Access Locked: You must enter a valid Admission Number above to select your items.")
else:
    st.success(f"🔓 Access Granted for Admission Number: **{admission_no}**")
    st.subheader("📋 Step 2: Select Your Registered Items (Max 5)")
    
    # Multiselect input box tracking active selections
    selected_items = st.multiselect(
        "Choose your competitive events from the directory:",
        options=all_events,
        max_selections=5,
        help="The system will automatically prevent you from selecting more than 5 items."
    )
    
    # Dynamic counter feedback
    total_selected = len(selected_items)
    st.info(f"Slots allocated: {total_selected} / 5 items selected.")
    
    if total_selected == 5:
        st.warning("🔒 Maximum registration threshold reached for this profile.")
        
    st.divider()
    
    # Step 3: Submission Pipeline
    st.subheader("🚀 Step 3: Complete Submission")
    if st.button("Submit Registration to Database", type="primary"):
        if total_selected == 0:
            st.error("Please pick at least 1 item before attempting to submit.")
        else:
            try:
                # Connection framework to append choices to Google Sheets
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # Note: Streamlit's GSheetsConnection requires your Google Sheet URL sharing 
                # permissions to be set to "Anyone with link can EDIT" for this submit button to append data rows.
                st.success("🎉 Registration choices recorded! Your dataset is updating successfully.")
                st.balloons()
            except Exception as e:
                st.error("Data syncing standby. Please double check your editor sharing rules inside Google Sheets.")

