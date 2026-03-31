import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Esoko Audio Transcript", layout="wide")

# --- CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Using ttl=60 so it refreshes data once per minute
# Replace "Annotations" with your actual tab name if different
df = conn.read(worksheet="Annotations", skiprows=1, ttl=60)

st.title("🎧 Esoko Audio Transcript")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Records")
if 'Lang_Detected' in df.columns:
    langs = st.sidebar.multiselect("Language", df['Lang_Detected'].unique())
    if langs:
        df = df[df['Lang_Detected'].isin(langs)]

# --- DATA TABLE ---
# Show all columns, but allow single-row selection
selection = st.dataframe(
    df, 
    use_container_width=True, 
    on_select="rerun", 
    selection_mode="single-row"
)

# --- AUDIO PLAYER LOGIC ---
if selection.selection.rows:
    selected_idx = selection.selection.rows[0]
    row = df.iloc[selected_idx]
    
    st.divider()
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Play Recording")
        # Extract the S3 link from your 'File_Location' column
        audio_url = row['File_Location']
        
        if pd.notna(audio_url):
            st.audio(audio_url)
            st.write(f"**ID:** {row['Rec_ID']}")
        else:
            st.warning("No audio link found for this record.")

with col_right:
        st.subheader("Transcription & Q&A")
        
        # 1. Show the main transcript excerpt
        if 'Transcript_Excerpt' in row and pd.notna(row['Transcript_Excerpt']):
            st.info(f"**Main Transcript:**\n\n{row['Transcript_Excerpt']}")
        
        # 2. Show the Q&A Pairs (Q1/A1)
        if 'Q1' in row and pd.notna(row['Q1']):
            st.markdown("---")
            st.write("#### ❓ Call Q&A")
            # Using Chat Messages for a nice UI look
            st.chat_message("user").write(row['Q1'])
            if 'A1' in row and pd.notna(row['A1']):
                st.chat_message("assistant").write(row['A1'])
                
        # 3. Add Q2/A2 if they exist in your sheet
        if 'Q2' in row and pd.notna(row['Q2']):
            st.chat_message("user").write(row['Q2'])
            if 'A2' in row and pd.notna(row['A2']):
                st.chat_message("assistant").write(row['A2'])

        # 4. Metadata footer
        st.divider()
        st.write(f"**Annotator:** {row.get('Annotator', 'N/A')}")
        st.write(f"**Quality Score:** {row.get('Composite_Score', 'N/A')}/5")
        
        if 'Rejection_Reason' in row and pd.notna(row['Rejection_Reason']):
            st.error(f"**Rejection Reason:** {row['Rejection_Reason']}")

