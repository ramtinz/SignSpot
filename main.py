import streamlit as st
import sqlite3
from datetime import datetime
import folium
from streamlit_folium import st_folium
import pandas as pd

# Page config
st.set_page_config(
    page_title="SignSpot - Parking Sign Reporter",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
DB_FILE = 'parking_reports.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            issue_type TEXT NOT NULL,
            description TEXT NOT NULL,
            votes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_all_reports():
    """Fetch all reports from database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, latitude, longitude, issue_type, description, votes, created_at FROM reports ORDER BY created_at DESC')
    reports = c.fetchall()
    conn.close()
    return reports

def add_report(lat, lng, issue_type, description):
    """Add a new report to database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (latitude, longitude, issue_type, description)
        VALUES (?, ?, ?, ?)
    ''', (lat, lng, issue_type, description))
    conn.commit()
    conn.close()

def upvote_report(report_id):
    """Increment vote count for a report"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE reports SET votes = votes + 1 WHERE id = ?', (report_id,))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Color mapping for markers
ISSUE_COLORS = {
    'Hidden': 'red',
    'Unclear': 'orange',
    'Missing': 'purple',
    'Damaged': 'gray'
}

# Header
st.markdown("# 🅿️ SignSpot")
st.markdown("### Spot problematic parking signs before you get ticketed")

# Disclaimer
st.warning("⚠️ **Experimental App - No Liability**: This is an experimental crowdsourced app. We make no guarantees about the accuracy of reports and assume no liability for any parking tickets or issues. Always verify parking signs yourself.")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["🗺️ Map View", "➕ Report Issue", "📊 All Reports"])

if page == "🗺️ Map View":
    st.subheader("📍 Parking Sign Issues Map")
    
    # Get all reports
    reports = get_all_reports()
    
    # Create map centered on San Francisco
    m = folium.Map(
        location=[37.7749, -122.4194],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    # Add markers for each report
    for report in reports:
        report_id, lat, lng, issue_type, desc, votes, created = report
        color = ISSUE_COLORS.get(issue_type, 'blue')
        
        popup_text = f"""
        <b>{issue_type} Sign</b><br>
        {desc if desc else 'No description'}<br>
        👍 {votes} votes<br>
        <small>{created}</small>
        """
        
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_text, max_width=250),
            icon=folium.Icon(color=color, icon='exclamation'),
            tooltip=f"{issue_type}: {desc[:30]}" if desc else issue_type
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1400, height=600)
    
    # Show summary
    if reports:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Reports", len(reports))
        with col2:
            hidden = len([r for r in reports if r[3] == 'Hidden'])
            st.metric("Hidden Signs", hidden)
        with col3:
            unclear = len([r for r in reports if r[3] == 'Unclear'])
            st.metric("Unclear Signs", unclear)
        with col4:
            st.metric("Total Votes", sum([r[5] for r in reports]))
    else:
        st.info("No reports yet. Be the first to report a parking sign issue!")

elif page == "➕ Report Issue":
    st.subheader("Report a Parking Sign Issue")
    
    col1, col2 = st.columns(2)
    
    with col1:
        latitude = st.number_input("Latitude", value=37.7749, format="%.6f")
    with col2:
        longitude = st.number_input("Longitude", value=-122.4194, format="%.6f")
    
    issue_type = st.selectbox(
        "Issue Type",
        ["Hidden", "Unclear", "Missing", "Damaged"],
        help="Select the type of parking sign issue"
    )
    
    description = st.text_area(
        "Description (optional)",
        placeholder="Describe the issue to help other drivers...",
        height=100
    )
    
    if st.button("Submit Report", type="primary"):
        add_report(latitude, longitude, issue_type, description)
        st.success("✅ Report submitted successfully!")
        st.balloons()

elif page == "📊 All Reports":
    st.subheader("All Parking Sign Reports")
    
    reports = get_all_reports()
    
    if reports:
        # Create DataFrame
        df_data = []
        for report in reports:
            report_id, lat, lng, issue_type, desc, votes, created = report
            df_data.append({
                'ID': report_id,
                'Type': issue_type,
                'Location': f"{lat:.4f}, {lng:.4f}",
                'Description': desc[:50] + "..." if len(desc) > 50 else desc,
                'Votes': votes,
                'Reported': created
            })
        
        df = pd.DataFrame(df_data)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            selected_type = st.multiselect(
                "Filter by Issue Type",
                options=df['Type'].unique(),
                default=df['Type'].unique()
            )
        
        with col2:
            min_votes = st.slider("Minimum Votes", 0, int(df['Votes'].max()) + 1, 0)
        
        # Filter data
        filtered_df = df[(df['Type'].isin(selected_type)) & (df['Votes'] >= min_votes)]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Sort options
        st.subheader("Top Issues")
        top_by = st.radio("Sort by:", ["Most Votes", "Most Recent"])
        
        if top_by == "Most Votes":
            top_df = df.nlargest(5, 'Votes')
        else:
            top_df = df.head(5)
        
        st.dataframe(top_df, use_container_width=True)
    else:
        st.info("No reports yet. Be the first to report a parking sign issue!")

# Footer
st.divider()
st.markdown("© 2026 SignSpot. Experimental service - no warranty or liability.")
