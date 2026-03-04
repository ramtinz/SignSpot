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

# Custom CSS for modern styling
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding: 2rem 1rem;
    }
    
    h1, h2, h3 {
        color: #1a1a2e;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 800;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        text-align: center;
    }
    
    .metric-card h3 {
        color: rgba(255, 255, 255, 0.8);
        margin: 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-card .value {
        font-size: 2rem;
        font-weight: 800;
        color: white;
        margin: 0.5rem 0 0 0;
    }
    
    [data-testid="stButton"] > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    [data-testid="stButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
        background-color: #f0f2f6;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

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

# Copenhagen coordinates
COPENHAGEN_LAT = 55.6761
COPENHAGEN_LNG = 12.5683

# Header
st.markdown("""
<div class="main-header">
    <h1>🅿️ SignSpot</h1>
    <p>Spot problematic parking signs before you get ticketed</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.warning("⚠️ **Experimental App - No Liability**: This is an experimental crowdsourced app. We make no guarantees about the accuracy of reports and assume no liability for any parking tickets or issues. Always verify parking signs yourself.")

# Sidebar navigation
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("Select View", ["🗺️ Map", "➕ Report", "📊 Reports"], label_visibility="collapsed")

if page == "🗺️ Map":
    st.subheader("📍 Parking Issues Map - Copenhagen")
    
    # Get all reports
    reports = get_all_reports()
    
    # Create map centered on Copenhagen
    m = folium.Map(
        location=[COPENHAGEN_LAT, COPENHAGEN_LNG],
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
    
    # Show summary stats
    if reports:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Reports</h3>
                <div class="value">{len(reports)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            hidden = len([r for r in reports if r[3] == 'Hidden'])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Hidden Signs</h3>
                <div class="value">{hidden}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            unclear = len([r for r in reports if r[3] == 'Unclear'])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Unclear Signs</h3>
                <div class="value">{unclear}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_votes = sum([r[5] for r in reports])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Votes</h3>
                <div class="value">{total_votes}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📍 No reports yet. Be the first to report a parking sign issue!", icon="ℹ️")

elif page == "➕ Report":
    st.subheader("Report a Parking Sign Issue")
    
    with st.form("report_form", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            latitude = st.number_input("Latitude", value=COPENHAGEN_LAT, format="%.6f")
        with col2:
            longitude = st.number_input("Longitude", value=COPENHAGEN_LNG, format="%.6f")
        
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
        
        submitted = st.form_submit_button("📤 Submit Report", use_container_width=True)
        
        if submitted:
            add_report(latitude, longitude, issue_type, description)
            st.success("✅ Report submitted successfully! Thank you for helping the community.", icon="✅")
            st.balloons()

elif page == "📊 Reports":
    st.subheader("All Parking Sign Reports")
    
    reports = get_all_reports()
    
    if reports:
        # Create DataFrame
        df_data = []
        for report in reports:
            report_id, lat, lng, issue_type, desc, votes, created = report
            df_data.append({
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
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        # Top issues section
        st.divider()
        st.subheader("🔝 Top Issues")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**By Votes**")
            top_votes = df.nlargest(5, 'Votes')[['Type', 'Description', 'Votes']]
            st.dataframe(top_votes, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**Most Recent**")
            recent = df.head(5)[['Type', 'Description', 'Votes']]
            st.dataframe(recent, use_container_width=True, hide_index=True)
        
        # Summary
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Reports", len(df))
        with col2:
            st.metric("Most Common Issue", df['Type'].mode()[0] if len(df) > 0 else "N/A")
        with col3:
            st.metric("Total Community Votes", df['Votes'].sum())
    else:
        st.info("📍 No reports yet. Be the first to report a parking sign issue!", icon="ℹ️")

# Footer
st.divider()
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.85rem;'>© 2026 SignSpot. Experimental service - no warranty or liability.</p>",
    unsafe_allow_html=True
)
