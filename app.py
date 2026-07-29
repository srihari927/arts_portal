import streamlit as st
from streamlit_gsheets import GSheetsConnection
import base64

# 1. Set up the web page title and tab icon
st.set_page_config(page_title="Arts Festival Registration Portal", page_icon="🎨", layout="centered")

# 2. INTEGRATE LOCAL BACKGROUND IMAGE
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
    st.warning("⚠️ 'background.png' not found in your folder.")

# 3. INTEGRATE LOGO IMAGE 
try:
    st.image("logo.png", width=120)
except Exception:
    st.write("📁 *[School Logo]*")

# 4. HEADER & PORTAL DESCRIPTION
st.title("🎨 Cultural Arts Festival Portal")
st.write("Welcome to the registration tracking dashboard. Search by your admission number to verify your registered items.")

# 5. CORE DATABASE SEARCH & 5-ITEM RULE ENFORCEMENT
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="1m") # Auto-refreshes data every 60 seconds

    search_query = st.text_input("🔍 Check Your Registration (Enter Admission Number):")

    if search_query:
        df['AdmissionNumber'] = df['AdmissionNumber'].astype(str).str.strip()
        search_query = str(search_query).strip()
        
        # Filter spreadsheet data for this student
        result = df[df['AdmissionNumber'] == search_query]
        
        if not result.empty:
            # Calculate total registered items for this single person
            total_items = len(result)
            
            # Display status banner based on the strict 5-item limit rule
            if total_items > 5:
                st.error(f"❌ RULE VIOLATION: This student is registered for {total_items} items! Max allowed is 5. Please contact the arts committee immediately to remove {total_items - 5} event(s).")
            elif total_items == 5:
                st.warning(f"⚠️ Maximum Limit Reached: This student is registered for exactly {total_items}/5 items. No more items can be added.")
            else:
                st.success(f"✨ Registration Verified: Student is safely registered for {total_items}/5 items.")
            
            # Show the detailed data table
            st.dataframe(result, use_container_width=True)
        else:
            st.error("❌ No registration records found for this Admission Number.")
            
except Exception as e:
    st.error("Database standby. Complete your 'secrets.toml' file setup to link your live Google Sheet.")

st.divider()

# 6. OFFICIAL FESTIVAL ITEMS & COMPETITIONS LIST
st.header("📋 Official List of Competition Items")
st.write("Browse the 56 official competitive events hosted in this edition of the arts festival:")

# Categorized expanders for all 56 items
with st.expander("🗣️ Literary, Speaking & Stage Events", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.write("- Story telling (English)")
        st.write("- Speech (English)")
        st.write("- Speech (Malayalam)")
        st.write("- Elocution (English)")
        st.write("- Elocution (Malayalam)")
        st.write("- Elocution (Hindi)")
        st.write("- Extempore (English)")
        st.write("- Extempore (Malayalam)")
    with col2:
        st.write("- Extempore (Hindi)")
        st.write("- Mono Act")
        st.write("- Mimicry")
        st.write("- Anchoring")
        st.write("- Mime")
        st.write("- PowerPoint Presentation")

with st.expander("🎵 Music & Vocal Competitions"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("- Recitation (English)")
        st.write("- Recitation (Malayalam)")
        st.write("- Recitation (Hindi)")
        st.write("- Recitation (Arabic)")
        st.write("- Recitation (Sanskrit)")
        st.write("- Light Music (Lalithaganam)")
        st.write("- Classical Music (Carnatic)")
    with col2:
        st.write("- Mappilappattu")
        st.write("- Group Song")
        st.write("- Patriotic Song")
        st.write("- Western Music Concert")

with st.expander("💃 Classical & Folk Dance Forms"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("- Folk Dance")
        st.write("- Bharatanatyam")
        st.write("- Mohiniyattam")
        st.write("- Kuchipudi")
    with col2:
        st.write("- Kolkali")
        st.write("- Thiruvathirakali")
        st.write("- Oppana")
        st.write("- Margam Kali")

with st.expander("🎸 Instrumental Music"):
    st.write("- Band")
    st.write("- Tabla Eastern")
    st.write("- Mridangam Eastern")
    st.write("- Guitar Western")
    st.write("- Violin Eastern")

with st.expander("🎨 Fine Arts, Painting & Designing"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("- Pencil Drawing")
        st.write("- Painting (Crayons)")
        st.write("- Painting Watercolour")
        st.write("- Painting Oil Colour")
    with col2:
        st.write("- Digital Painting")
        st.write("- Poster Designing")
        st.write("- Cartoon")
        st.write("- Collage")

with st.expander("✍️ Creative Writing & Versification"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("- Essay Writing (English)")
        st.write("- Essay Writing (Malayalam)")
        st.write("- Essay Writing (Hindi)")
        st.write("- Story Writing (English)")
    with col2:
        st.write("- Story Writing (Malayalam)")
        st.write("- Story Writing (Hindi)")
        st.write("- Versification (English)")
        st.write("- Versification (Malayalam)")
        st.write("- Versification (Hindi)")

