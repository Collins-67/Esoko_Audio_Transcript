import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Esoko Audio Transcript", layout="wide")

# --- CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Using ttl=60 so it refreshes data once per minute
# Ensure your Google Sheet tab is named "Annotations"
df = conn.read(worksheet="Annotations", skiprows=1, ttl=60)

st.title("🎧 Esoko Audio Transcript")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Records")

# 1. Filter by Decision (Accepted, Review, Rejected)
if 'Decision' in df.columns:
    decisions = st.sidebar.multiselect("Filter by Decision", df['Decision'].unique())
    if decisions:
        df = df[df['Decision'].isin(decisions)]
else:
    st.sidebar.warning("⚠️ 'Decision' column not found.")

# 2. Filter by Language (Optional - kept from your previous version)
if 'Lang_Detected' in df.columns:
    langs = st.sidebar.multiselect("Language", df['Lang_Detected'].unique())
    if langs:
        df = df[df['Lang_Detected'].isin(langs)]

# --- DATA TABLE ---
selection = st.dataframe(
    df, 
    use_container_width=True, 
    on_select="rerun", 
    selection_mode="single-row"
)

# --- AUDIO & Q&A SECTION ---
if selection.selection.rows:
    selected_index = selection.selection.rows[0]
    row = df.iloc[selected_index]
    
    st.divider()
    
    # Create two columns: Left for Audio, Right for Q&A/Facts
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Play Recording")
        audio_link = row.get('File_Location')
        
        if pd.notna(audio_link) and str(audio_link).startswith("http"):
            st.audio(audio_link)
            st.caption(f"Recording ID: {row.get('Rec_ID', 'Unknown')}")
        else:
            st.warning("⚠️ No valid audio link found.")
            
        if 'Transcript_Excerpt' in row and pd.notna(row['Transcript_Excerpt']):
            st.info(f"**Transcript Excerpt:**\n\n{row['Transcript_Excerpt']}")

    with col2:
        st.subheader("Q&A & Fact Extraction")
        
        if 'Q1' in row and pd.notna(row['Q1']):
            # Display Question
            st.chat_message("user").write(row['Q1'])
            
            # Display Question Facts
            if 'Question_Facts' in row and pd.notna(row['Question_Facts']):
                with st.expander("📌 View Question Facts", expanded=True):
                    st.write(row['Question_Facts'])
            
            # Display Answer
            if 'A1' in row and pd.notna(row['A1']):
                st.chat_message("assistant").write(row['A1'])
                
                # Display Answer Facts
                if 'Answer_Facts' in row and pd.notna(row['Answer_Facts']):
                    with st.expander("💡 View Answer Facts", expanded=True):
                        st.write(row['Answer_Facts'])
        else:
            st.write("_No Q&A pairs recorded._")
        
        st.divider()
        
        # Display Decision and Quality Score
        st.write(f"**Current Status:** {row.get('Decision', 'N/A')}")
        st.write(f"**Quality Score:** {row.get('Composite_Score', 'N/A')}/5.0")
        
        if 'Rejection_Reason' in row and pd.notna(row['Rejection_Reason']):
            st.error(f"**Rejection Reason:** {row['Rejection_Reason']}")

else:
    st.info("💡 Click a row in the table above to listen to the recording and see details.")
