import streamlit as st
import sqlite3
from datetime import datetime
import folium
from streamlit_folium import st_folium
import pandas as pd
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="SignSpot - Parking Sign Reporter",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="collapsed"
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
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            flags INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migrate old votes column if it exists
    c.execute("PRAGMA table_info(reports)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'votes' in columns and 'upvotes' not in columns:
        c.execute('ALTER TABLE reports ADD COLUMN upvotes INTEGER DEFAULT 0')
        c.execute('ALTER TABLE reports ADD COLUMN downvotes INTEGER DEFAULT 0')
        # Migrate existing votes to upvotes
        c.execute('UPDATE reports SET upvotes = votes WHERE votes > 0')
        c.execute('UPDATE reports SET votes = 0')
    elif 'upvotes' not in columns:
        c.execute('ALTER TABLE reports ADD COLUMN upvotes INTEGER DEFAULT 0')
        c.execute('ALTER TABLE reports ADD COLUMN downvotes INTEGER DEFAULT 0')
    
    if 'flags' not in columns:
        c.execute('ALTER TABLE reports ADD COLUMN flags INTEGER DEFAULT 0')
    
    # Create page_views table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            view_count INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize page_views table with single row if empty
    c.execute('SELECT COUNT(*) FROM page_views')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO page_views (view_count) VALUES (0)')
    
    conn.commit()
    conn.close()

def get_all_reports():
    """Fetch all reports from database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, latitude, longitude, issue_type, description, upvotes, downvotes, flags, created_at FROM reports ORDER BY created_at DESC')
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
    """Upvote a report (agree with validity)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE reports SET upvotes = upvotes + 1 WHERE id = ?', (report_id,))
    conn.commit()
    conn.close()

def downvote_report(report_id):
    """Downvote a report (disagree with validity)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE reports SET downvotes = downvotes + 1 WHERE id = ?', (report_id,))
    conn.commit()
    conn.close()

def flag_report(report_id):
    """Flag a report as incorrect/spam"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE reports SET flags = flags + 1 WHERE id = ?', (report_id,))
    conn.commit()
    conn.close()

def increment_page_views():
    """Increment page view counter"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE page_views SET view_count = view_count + 1, last_updated = CURRENT_TIMESTAMP WHERE id = 1')
    conn.commit()
    conn.close()

def get_page_views():
    """Get total page views"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT view_count FROM page_views WHERE id = 1')
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

# Initialize database
init_db()

# Color mapping for markers
ISSUE_COLORS = {
    'Paid Parking (Problematic)': 'red',
    'Free Parking': 'green'
}

# Copenhagen coordinates (default)
COPENHAGEN_LAT = 55.6761
COPENHAGEN_LNG = 12.5683

# Major world cities
CITIES = {
    "Copenhagen, Denmark": (55.6761, 12.5683),
    "New York, USA": (40.7128, -74.0060),
    "London, UK": (51.5074, -0.1278),
    "Paris, France": (48.8566, 2.3522),
    "Berlin, Germany": (52.5200, 13.4050),
    "Amsterdam, Netherlands": (52.3676, 4.9041),
    "Barcelona, Spain": (41.3851, 2.1734),
    "Rome, Italy": (41.9028, 12.4964),
    "Tokyo, Japan": (35.6762, 139.6503),
    "Sydney, Australia": (-33.8688, 151.2093),
    "Singapore": (1.3521, 103.8198),
    "Dubai, UAE": (25.2048, 55.2708),
    "Toronto, Canada": (43.6532, -79.3832),
    "Los Angeles, USA": (34.0522, -118.2437),
    "San Francisco, USA": (37.7749, -122.4194),
    "Miami, USA": (25.7617, -80.1918),
    "Istanbul, Turkey": (41.0082, 28.9784),
    "Bangkok, Thailand": (13.7563, 100.5018),
    "Mexico City, Mexico": (19.4326, -99.1332),
    "São Paulo, Brazil": (-23.5505, -46.6333),
    "Tehran, Iran": (35.6892, 51.3890),
    "Moscow, Russia": (55.7558, 37.6173),
    "Beijing, China": (39.9042, 116.4074),
    "Shanghai, China": (31.2304, 121.4737),
    "Hong Kong": (22.3193, 114.1694),
    "Mumbai, India": (19.0760, 72.8777),
    "Delhi, India": (28.7041, 77.1025),
    "Seoul, South Korea": (37.5665, 126.9780),
    "Singapore": (1.3521, 103.8198),
    "Ho Chi Minh City, Vietnam": (10.7769, 106.7009),
    "Kuala Lumpur, Malaysia": (3.1390, 101.6869),
    "Jakarta, Indonesia": (-6.2088, 106.8456),
    "Manila, Philippines": (14.5995, 120.9842),
    "Athens, Greece": (37.9838, 23.7275),
    "Madrid, Spain": (40.4168, -3.7038),
    "Milan, Italy": (45.4642, 9.1900),
    "Vienna, Austria": (48.2082, 16.3738),
    "Prague, Czech Republic": (50.0755, 14.4378),
    "Budapest, Hungary": (47.4979, 19.0402),
    "Warsaw, Poland": (52.2297, 21.0122),
    "Lisbon, Portugal": (38.7223, -9.1393),
    "Dublin, Ireland": (53.3498, -6.2603),
    "Montreal, Canada": (45.5017, -73.5673),
    "Vancouver, Canada": (49.2827, -123.1207),
    "Mexico City, Mexico": (19.4326, -99.1332),
    "Buenos Aires, Argentina": (-34.6037, -58.3816),
    "Rio de Janeiro, Brazil": (-22.9068, -43.1729),
    "Santiago, Chile": (-33.8688, -51.2093),
    "Bogotá, Colombia": (4.7110, -74.0721),
    "Cairo, Egypt": (30.0444, 31.2357),
    "Lagos, Nigeria": (6.5244, 3.3792),
    "Cape Town, South Africa": (-33.9249, 18.4241),
    "Johannesburg, South Africa": (-26.2023, 28.0436),
    "Dubai, UAE": (25.2048, 55.2708),
    "Abu Dhabi, UAE": (24.4539, 54.3773),
}

# Initialize session state for map-based reporting
if 'report_lat' not in st.session_state:
    st.session_state.report_lat = COPENHAGEN_LAT
if 'report_lng' not in st.session_state:
    st.session_state.report_lng = COPENHAGEN_LNG
if 'report_type' not in st.session_state:
    st.session_state.report_type = "Hidden"
if 'report_desc' not in st.session_state:
    st.session_state.report_desc = "Parking sign hidden behind trees/bushes"

# Header with logo (centered)
left_spacer, center_header, right_spacer = st.columns([1, 2, 1])

with center_header:
    try:
        # Center the logo using columns with wider side margins
        _, logo_col, _ = st.columns([0.5, 1, 0.5])
        with logo_col:
            st.image('assets/signspotlogo_v1.png', width=220)
    except:
        st.markdown("<div style='text-align: center; font-size: 2rem;'>🅿️</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; padding-top: 10px;">
        <h1 style="margin: 0; color: #1f77b4; font-size: 2rem;">SignSpot</h1>
        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.95rem;"><i>Spot we trust</i> — Parking sign reporting made easy</p>
    </div>
    """, unsafe_allow_html=True)

    # Center the navigation menu
    _, nav_col, _ = st.columns([0.5, 1, 0.5])
    with nav_col:
        page = st.radio(
            "Navigation",
            ["🗺️ Map - Home", "📊 Reports"],
            horizontal=True,
            label_visibility="collapsed"
        )

# Increment page views on app load (use session state to count only once per session)
if 'view_counted' not in st.session_state:
    increment_page_views()
    st.session_state.view_counted = True

if page == "🗺️ Map - Home":
    st.markdown("<h2 style='text-align: center; font-size: 1.5rem;'>📍 Parking Areas Map</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem;'>Click anywhere on the map to select a location, then scroll down to submit your report</p>", unsafe_allow_html=True)
    
    # City selector - centered above map
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_city = st.selectbox(
            "Select City to Center Map",
            options=list(CITIES.keys()),
            index=0,
            key="city_selector"
        )
    
    # Get coordinates for selected city
    city_lat, city_lng = CITIES[selected_city]
    
    # Get all reports
    reports = get_all_reports()
    
    # Create map centered on selected city
    m = folium.Map(
        location=[city_lat, city_lng],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    # Add markers for each report
    for report in reports:
        report_id, lat, lng, issue_type, desc, upvotes, downvotes, flags, created = report
        color = ISSUE_COLORS.get(issue_type, 'blue')
        
        # Mark flagged reports with orange (if heavily flagged)
        if flags >= 3:
            color = 'red'
            icon_str = 'times-circle'
        else:
            icon_str = 'exclamation'
        
        net_votes = upvotes - downvotes
        
        popup_text = f"""
        <b>{issue_type} Sign</b><br>
        {desc if desc else 'No description'}<br>
        👍 {upvotes} | 👎 {downvotes} | Net: {net_votes:+d}<br>
        🚩 {flags} flags<br>
        <small>{created}</small>
        """
        
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_text, max_width=250),
            icon=folium.Icon(color=color, icon=icon_str, prefix='fa'),
            tooltip=f"{issue_type}: {desc[:30]}" if desc else issue_type
        ).add_to(m)
    
    # Add a marker for the current report location if in progress
    if 'report_in_progress' in st.session_state and st.session_state.report_in_progress:
        folium.Marker(
            location=[st.session_state.report_lat, st.session_state.report_lng],
            icon=folium.Icon(color='blue', icon='pencil', prefix='fa'),
            popup="📝 Report in progress"
        ).add_to(m)
    
    # Display map with click capture - centered with larger side margins for mobile scrolling
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        map_data = st_folium(m, width=850, height=560)
    
    # Handle map clicks
    if map_data and map_data['last_clicked']:
        st.session_state.report_lat = map_data['last_clicked']['lat']
        st.session_state.report_lng = map_data['last_clicked']['lng']
        st.session_state.report_in_progress = True
        st.info(f"📍 Location selected: {st.session_state.report_lat:.4f}, {st.session_state.report_lng:.4f}")
        st.info("👉 Scroll down to fill in the report details!", icon="👉")
    
    # Show reports near clicked location for voting
    if map_data and map_data['last_clicked']:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        
        # Find reports within ~50 meters of click
        nearby_reports = []
        for report in reports:
            report_id, lat, lng, issue_type, desc, upvotes, downvotes, flags, created = report
            # Rough distance calculation (not accurate but good enough for UI)
            distance = ((lat - clicked_lat)**2 + (lng - clicked_lng)**2)**0.5
            if distance < 0.001:  # Roughly 100 meters
                nearby_reports.append(report)
        
        if nearby_reports:
            st.divider()
            st.markdown("### 🗳️ Vote on Nearby Reports")
            st.info("Found reports near your clicked location. Vote to confirm accuracy!", icon="🗳️")
            
            for report in nearby_reports:
                report_id, lat, lng, issue_type, desc, upvotes, downvotes, flags, created = report
                net_votes = upvotes - downvotes
                
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                with col1:
                    st.write(f"**{issue_type}**")
                with col2:
                    st.write(f"{desc[:40]}..." if len(desc) > 40 else desc)
                with col3:
                    if st.button("👍", key=f"map_upvote_{report_id}", help="Agree with this report"):
                        upvote_report(report_id)
                        st.success(f"✅ Upvoted!")
                        st.rerun()
                with col4:
                    if st.button("👎", key=f"map_downvote_{report_id}", help="Disagree with this report"):
                        downvote_report(report_id)
                        st.warning(f"⚠️ Downvoted.")
                        st.rerun()
                with col5:
                    st.write(f"{upvotes}/{downvotes}")
                
                st.divider()
    
    # Report form (always visible for convenience)
    st.divider()
    st.markdown("<h3 style='font-size: 1.15rem;'>📝 Quick Report</h3>", unsafe_allow_html=True)
    
    st.markdown(f"**Selected Location:** {st.session_state.report_lat:.6f}, {st.session_state.report_lng:.6f}")
    # Area type selection outside form
    issue_type = st.selectbox(
        "What's the area?",
        ["Paid Parking (Problematic)", "Free Parking"],
        index=0,
        help="Paid Parking = Hidden, faded, damaged, or unclear paid parking signs. Free Parking = Free spots."
    )

    # Define presets based on area type
    if issue_type == "Paid Parking (Problematic)":
        presets = {
            "Hidden sign 🌳": "Parking sign hidden behind trees/bushes",
            "Faded sign ⚠️": "Sign is faded/hard to read",
            "No sign 🚫": "Should have a parking sign here",
            "Broken sign 💔": "Sign is damaged/broken",
            "Confusing sign ❓": "Sign is confusing or unclear"
        }
    else:  # Free Parking
        presets = {
            "Free spot! 💚": "Free parking available here",
            "Free street 🅿️": "Free street parking area",
            "Free lot 🏞️": "Free parking lot",
            "Free evening 🌙": "Free parking after hours",
            "Free weekend 📅": "Free parking on weekends"
        }
    
    st.markdown("**Choose a reason:**")
    preset_cols = st.columns(5)
    
    for idx, (preset_label, preset_text) in enumerate(presets.items()):
        if preset_cols[idx].button(preset_label, use_container_width=True, key=f"preset_{idx}"):
            st.session_state.report_desc = preset_text
            st.rerun()
    
    # Show currently selected preset
    st.info(f"**Selected:** {st.session_state.report_desc}")

    # Form with just the submit button
    with st.form("quick_report_form", border=True):
        st.caption("By submitting, you confirm your report is lawful, non-abusive, and does not include personal data.")
        
        submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True, type="primary")
        
        if submitted:
            add_report(st.session_state.report_lat, st.session_state.report_lng, issue_type, st.session_state.report_desc)
            st.success("✅ Report submitted! Thank you for helping the community.", icon="✅")
            st.balloons()
            st.session_state.report_in_progress = False
            st.session_state.report_desc = "Parking sign hidden behind trees/bushes"
            st.rerun()
    
    # Show summary stats
    if reports:
        st.divider()
        st.markdown("<h3 style='font-size: 1.15rem;'>📊 Quick Stats</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)

        total_reports = len(reports)
        problematic_paid = len([r for r in reports if r[3] == 'Paid Parking (Problematic)'])
        free_parking = len([r for r in reports if r[3] == 'Free Parking'])
        total_votes = sum([r[5] + r[6] for r in reports])
        page_views = get_page_views()

        with col1:
            st.metric("Total Reports", total_reports)
        with col2:
            st.metric("Problematic Paid", problematic_paid)
        with col3:
            st.metric("Free Spots", free_parking)
        with col4:
            st.metric("Community Votes", total_votes)
        with col5:
            st.metric("Page Views", page_views)
    else:
        st.info("📍 No reports yet. Click on the map or use the form below to report!", icon="ℹ️")

elif page == "📊 Reports":
    st.subheader("All Parking Areas")
    
    reports = get_all_reports()
    
    if reports:
        # Create DataFrame
        df_data = []
        for report in reports:
            report_id, lat, lng, issue_type, desc, upvotes, downvotes, flags, created = report
            total_votes = upvotes + downvotes
            net_votes = upvotes - downvotes
            agreement = round(100 * upvotes / total_votes) if total_votes > 0 else 0
            
            df_data.append({
                'ID': report_id,
                'Type': issue_type,
                'Location': f"{lat:.4f}, {lng:.4f}",
                'Description': desc[:50] + "..." if len(desc) > 50 else desc,
                '👍': upvotes,
                '👎': downvotes,
                'Net': net_votes,
                'Agreement': f"{agreement}%" if total_votes > 0 else "—",
                'Flags': flags,
                'Status': '🚨 Flagged' if flags >= 3 else '✅ OK' if flags == 0 else '⚠️ Disputed',
                'Reported': created
            })
        
        df = pd.DataFrame(df_data)
        
        # Tab view for different report types
        tab1, tab2, tab3, tab4 = st.tabs(["📋 All Reports", "📊 Vote on Reports", "⚠️ Disputed", "🚨 Flagged"])
        
        with tab1:
            st.markdown("#### All Community Reports")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_type = st.multiselect(
                    "Filter by Type",
                    options=df['Type'].unique(),
                    default=df['Type'].unique(),
                    key="tab1_type"
                )
            
            with col2:
                sort_by = st.selectbox("Sort by", ["Newest", "Most Agreement", "Most Votes", "Most Controversial"], key="tab1_sort")
            
            with col3:
                show_disputed = st.checkbox("Hide disputed", value=False, key="tab1_disputed")
            
            # Filter data
            filtered_df = df[(df['Type'].isin(selected_type))]
            if show_disputed:
                filtered_df = filtered_df[filtered_df['Flags'] < 3]
            
            # Sort
            if sort_by == "Most Agreement":
                filtered_df = filtered_df.sort_values('Agreement', ascending=False)
            elif sort_by == "Most Votes":
                filtered_df = filtered_df.copy()
                filtered_df['Total Votes'] = filtered_df['👍'] + filtered_df['👎']
                filtered_df = filtered_df.sort_values('Total Votes', ascending=False)
            elif sort_by == "Most Controversial":
                filtered_df = filtered_df.copy()
                filtered_df['Controversy'] = (filtered_df['👍'] + filtered_df['👎']).abs() * abs(filtered_df['Agreement'] - 50)
                filtered_df = filtered_df.sort_values('Controversy', ascending=False)
            
            # Display table with voting buttons
            st.markdown("**Click 👍 or 👎 to vote on report accuracy:**")
            
            for idx, row in filtered_df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{row['ID']}**")
                with col2:
                    st.write(f"{row['Type']}")
                with col3:
                    st.write(f"{row['Description']}")
                with col4:
                    if st.button("👍", key=f"upvote_{row['ID']}", help="Agree with this report"):
                        upvote_report(row['ID'])
                        st.success(f"✅ Upvoted report #{row['ID']}!")
                        st.rerun()
                with col5:
                    if st.button("👎", key=f"downvote_{row['ID']}", help="Disagree with this report"):
                        downvote_report(row['ID'])
                        st.warning(f"⚠️ Downvoted report #{row['ID']}.")
                        st.rerun()
                with col6:
                    st.write(f"{row['👍']}/{row['👎']}")
                
                st.divider()
        
        with tab2:
            st.markdown("#### 🗳️ Vote on Report Validity")
            st.info("👍 **Agree** = Report is accurate | 👎 **Disagree** = Report is inaccurate or outdated", icon="ℹ️")
            st.markdown("**Use the 'All Reports' tab above for easy voting, or enter a specific report ID below:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                vote_id = st.number_input("Report ID to vote on:", min_value=1, step=1, key="vote_id")
            
            with col2:
                st.write("")
                st.write("")
                col_agree, col_disagree = st.columns(2)
                
                with col_agree:
                    if st.button("👍 Agree", use_container_width=True, key="upvote_btn"):
                        if vote_id in df['ID'].values:
                            upvote_report(vote_id)
                            st.success(f"✅ Upvoted report #{vote_id}! Thank you for confirming.")
                            st.rerun()
                        else:
                            st.error("Report ID not found!")
                
                with col_disagree:
                    if st.button("👎 Disagree", use_container_width=True, key="downvote_btn"):
                        if vote_id in df['ID'].values:
                            downvote_report(vote_id)
                            st.warning(f"⚠️ Downvoted report #{vote_id}. Community will note the disagreement.")
                            st.rerun()
                        else:
                            st.error("Report ID not found!")
            
            # Show voting leaderboard
            st.divider()
            st.markdown("#### 🏆 Most Trusted Reports")
            trust_df = df[df['Flags'] < 3].copy()
            trust_df = trust_df.sort_values('Net', ascending=False).head(10)
            st.dataframe(trust_df[['ID', 'Type', '👍', '👎', 'Agreement']], use_container_width=True, hide_index=True)
        
        with tab3:
            st.markdown("#### ⚠️ Disputed Reports (1-2 flags)")
            disputed_df = df[(df['Flags'] > 0) & (df['Flags'] < 3)]
            
            if len(disputed_df) > 0:
                st.dataframe(
                    disputed_df[['ID', 'Type', 'Location', 'Description', '👍', '👎', 'Agreement', 'Flags']],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.info("💭 These reports have community concerns. Vote to help verify accuracy!", icon="🗳️")
            else:
                st.success("✅ No disputed reports!", icon="✅")
        
        with tab4:
            st.markdown("#### 🚨 Flagged Reports (3+ flags)")
            flagged_df = df[df['Flags'] >= 3]
            
            if len(flagged_df) > 0:
                st.warning(f"🚨 {len(flagged_df)} report(s) have multiple flags and may be inaccurate or spam.", icon="⚠️")
                st.dataframe(
                    flagged_df[['ID', 'Type', 'Location', 'Description', '👍', '👎', 'Agreement', 'Flags']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ No heavily flagged reports!", icon="✅")
        
        # Summary
        st.divider()
        st.markdown("### 📊 Community Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_upvotes = df['👍'].sum()
        total_downvotes = df['👎'].sum()
        total_votes_all = total_upvotes + total_downvotes
        
        with col1:
            st.metric("Total Reports", len(df))
        with col2:
            st.metric("Community Upvotes", total_upvotes)
        with col3:
            st.metric("Community Downvotes", total_downvotes)
        with col4:
            agreement_pct = round(100 * total_upvotes / total_votes_all) if total_votes_all > 0 else 0
            st.metric("Overall Agreement", f"{agreement_pct}%")
        with col5:
            flagged_count = len(df[df['Flags'] >= 3])
            st.metric("Heavily Flagged", flagged_count)
    else:
        st.info("📍 No reports yet. Be the first to report a parking sign issue!", icon="ℹ️")

# Footer
st.divider()
st.warning("⚠️ **Experimental App - No Liability**: This is an experimental crowdsourced app. We make no guarantees about the accuracy of reports and assume no liability for any parking tickets or issues. Always verify parking signs yourself.")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.85rem;'>© 2026 Ramtin Zargari Marandi. Experimental service - no warranty or liability.</p>",
    unsafe_allow_html=True
)
