import streamlit as st
from streamlit_gsheets import GSheetsConnection
import base64
import pandas as pd

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

# 5. STEP 2: LOOKUP NAME FROM SHEET 1 AND UNLOCK SELECTION
if not admission_no:
    st.warning("⚠️ Access Locked: You must enter a valid Admission Number above to select your items.")
else:
    student_name = ""
    try:
        # Connect to master lookup sheet
        conn_lookup = st.connection("gsheets_lookup", type=GSheetsConnection)
        lookup_df = conn_lookup.read(ttl="5m")
        
        # Clean data to match text strings cleanly
        lookup_df['AdmissionNumber'] = lookup_df['AdmissionNumber'].astype(str).str.strip()
        match = lookup_df[lookup_df['AdmissionNumber'] == admission_no]
        
        if not match.empty:
            # FIXED: Extracts the name cleanly out of the data table row array
            student_name = str(match["Name"].values[0]).strip()
            st.success(f"🔓 Student Authenticated: **{student_name}** (Admission No: {admission_no})")
        else:
            st.error("❌ Invalid Entry: This Admission Number does not exist in our system. Please check your spelling.")
    except Exception as e:
        st.error("Database sync standby. Complete your Secrets panel setup to launch active student verification tracking.")

    # Continue layout expansion if student credentials resolve validly
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
        
        # Step 3: Submission Pipeline into Sheet 2
        st.subheader("🚀 Step 3: Complete Submission")
        if st.button("Submit Registration to Database", type="primary"):
            if total_selected == 0:
                st.error("Please pick at least 1 item before attempting to submit.")
            else:
                try:
                    # Connect to the blank registration tracking spreadsheet
                    conn_reg = st.connection("gsheets_registration", type=GSheetsConnection)
                    existing_reg_df = conn_reg.read(ttl="0s") # clear cache to prevent old data overlaps
                    
                    # Merge selections into a single text entry row segment
                    items_string = ", ".join(selected_items)
                    
                    # Package row structure
                    new_entry = {
                        "AdmissionNumber": [str(admission_no)], 
                        "Name": [str(student_name)], 
                        "Items": [items_string]
                    }
                    new_row_df = pd.DataFrame(new_entry)
                    
                    # Append data array and update live cloud asset
                    if existing_reg_df.empty:
                        updated_reg_df = new_row_df
                    else:
                        updated_reg_df = pd.concat([existing_reg_df, new_row_df], ignore_index=True)
                        
                    conn_reg.update(data=updated_reg_df)
                    
                    st.success(f"🎉 Excellent! {student_name}'s registration choices have been logged successfully.")
                    st.balloons()
                except Exception as e:
                    st.error("Submission failed. Ensure your registration spreadsheet is shared with EDITOR write permissions.")
