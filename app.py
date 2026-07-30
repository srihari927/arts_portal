import streamlit as st
import pandas as pd
import base64
import os
import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(page_title="SKPS Youth Festival SUVARNAM2k26", page_icon="🎨", layout="centered")

# 2. Local Background Image & Viewport Layer Controls
try:
    with open("background.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    background_style = f"""
    <style>
    /* Force main app structural framework viewports to utilize background asset data */
    [data-testid="stAppViewContainer"], [data-testid="stAppViewMain"] {{
        background-image: url("data:image/png;base64,{encoded_string}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    /* Clear default canvas overlay backdrops */
    [data-testid="stHeader"], [data-testid="stAppViewBlockContainer"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    /* Render interactive forms cleanly on top of abstract backgrounds */
    .stTextInput, .stMultiSelect {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 8px !important;
        padding: 5px !important;
    }}
    </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)
except FileNotFoundError:
    pass

# 3. Logo Sizing & SUVARNAM2k26 Branding Header Setup
try:
    st.image("logo.png", width=220)
except Exception:
    st.write("📁 *[SKPS School Logo]*")

st.title("🎨 SKPS Youth Festival SUVARNAM2k26")
st.write("Please authenticate your student profile below to select your registered competition items.")

# 4. STEP 1: ENTER ADMISSION NUMBER
admission_no = st.text_input("🔑 Step 1: Enter Admission Number to begin:", value="").strip()

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

# Initialize local server tracking file database structures
DATA_FILE = "festival_registrations.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Admission Number", "Student Name", "Selected Items"]).to_csv(DATA_FILE, index=False)

# Establish connection matrix to pull Master student lookup directory (Sheet 1)
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def load_master_data(url):
    return conn.read(spreadsheet=url)

# 5. STEP 2: PROFILE VERIFICATION LOGIC
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
                student_name = str(match.iloc['ColB']).strip()
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
                    items_string = ", ".join(selected_items)
                    new_row = pd.DataFrame([{
                        "Admission Number": admission_no,
                        "Student Name": student_name,
                        "Selected Items": items_string
                    }])
                    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    
                    st.success(f"🎉 Success! {student_name}'s event selections have been safely locked for SUVARNAM2k26.")
                    st.balloons()
                except Exception as write_err:
                    st.error(f"Failed to record entry locally: {str(write_err)}")

# 🔐 ADMIN DASHBOARD COMPILING TOOL PANEL (Located securely at the foot margin)
st.write("---")
with st.expander("🛠️ Admin Portal: Export SUVARNAM2k26 Master Ledger Reports"):
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 50:
            current_df = pd.read_csv(DATA_FILE)
            st.write(f"Total Student Submissions Recorded: **{len(current_df)}**")
            st.dataframe(current_df, use_container_width=True)
            
            # --- REPORTLAB COMPILER ENGINE FOR SUMMARY LANDSCAPE TABLE ---
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
            story = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'AdminTitle',
                parent=styles['Heading1'],
                fontSize=22,
                leading=26,
                textColor=colors.HexColor('#1E3A8A'),
                alignment=1,
                spaceAfter=15
            )
            th_style = ParagraphStyle('TH', parent=styles['Normal'], fontSize=11, leading=14, textColor=colors.white, fontName='Helvetica-Bold')
            td_style = ParagraphStyle('TD', parent=styles['Normal'], fontSize=10, leading=13, textColor=colors.HexColor('#1F2937'))
            
            story.append(Paragraph("🏆 SKPS Youth Festival SUVARNAM2k26 - Master Ledger", title_style))
            story.append(Spacer(1, 10))
            
            # Formulate structured headings grid matrix
            table_data = [[
                Paragraph("Admission No.", th_style),
                Paragraph("Student Name", th_style),
                Paragraph("Registered Items Selection Directory", th_style)
            ]]
            
            # Pack current entries into cell blocks
            for _, r in current_df.iterrows():
                table_data.append([
                    Paragraph(str(r["Admission Number"]), td_style),
                    Paragraph(str(r["Student Name"]), td_style),
                    Paragraph(str(r["Selected Items"]), td_style)
                ])
            
            # Render layout matrix with clean text-wrapping bounds
            report_table = Table(table_data, colWidths=[100, 180, 440])
            report_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9FAFB')]),
                ('PADDING', (0,0), (-1,-1), 8),
            ]))
            
            story.append(report_table)
            doc.build(story)
            pdf_out = buffer.getvalue()
            buffer.close()
            
            st.download_button(
                label="📥 Download Tabular Master PDF Report Document",
                data=pdf_out,
                file_name="SUVARNAM2k26_Master_Registrations.pdf",
                mime="application/pdf",

