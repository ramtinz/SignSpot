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

# Initialize database
init_db()

# Color mapping for markers
ISSUE_COLORS = {
    'Paid Parking (Problematic)': 'red',
    'Free Parking': 'green'
}

# Copenhagen coordinates
COPENHAGEN_LAT = 55.6761
COPENHAGEN_LNG = 12.5683

# Initialize session state for map-based reporting
if 'report_lat' not in st.session_state:
    st.session_state.report_lat = COPENHAGEN_LAT
if 'report_lng' not in st.session_state:
    st.session_state.report_lng = COPENHAGEN_LNG
if 'report_type' not in st.session_state:
    st.session_state.report_type = "Hidden"
if 'report_desc' not in st.session_state:
    st.session_state.report_desc = ""

# Header with logo
logo_col, title_col = st.columns([1, 3])

with logo_col:
    try:
        st.image('assets/signspotlogo_v1.png', width=100, use_column_width=False)
    except:
        st.markdown("🅿️")

with title_col:
    st.markdown("""
    <div style="padding-top: 20px;">
        <h1 style="margin: 0; color: #1f77b4;">SignSpot</h1>
        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.95rem;"><i>Spot we trust</i> — Parking sign reporting made easy</p>
    </div>
    """, unsafe_allow_html=True)

# Disclaimer
st.warning("⚠️ **Experimental App - No Liability**: This is an experimental crowdsourced app. We make no guarantees about the accuracy of reports and assume no liability for any parking tickets or issues. Always verify parking signs yourself.")

# Sidebar navigation
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("Select View", ["🗺️ Map", "➕ Report", "📊 Reports"], label_visibility="collapsed")

if page == "🗺️ Map":
    st.subheader("📍 Parking Areas Map - Copenhagen")
    
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
    
    # Display map with click capture
    map_data = st_folium(m, width=1400, height=600)
    
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
    st.markdown("### 📝 Quick Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Selected Location:** {st.session_state.report_lat:.6f}, {st.session_state.report_lng:.6f}")
    
    with col2:
        if st.button("🔄 Use My Location", key="geolocate", use_container_width=True):
            # Create a simple HTML component for geolocation
            geolocation_html = """
            <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                <p style="margin: 0; font-weight: bold;">📍 Click "Get Location" below:</p>
                <button onclick="getLocation()" style="background-color: #ff4b4b; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-top: 5px;">Get My Location</button>
                <p id="location-status" style="margin: 5px 0; font-size: 14px; color: #666;">Click the button to get your current location</p>
            </div>
            
            <script>
            function getLocation() {
                const statusEl = document.getElementById('location-status');
                statusEl.textContent = 'Requesting location access...';
                statusEl.style.color = '#ffa500';
                
                if (!navigator.geolocation) {
                    statusEl.textContent = 'Geolocation not supported by this browser';
                    statusEl.style.color = '#ff4b4b';
                    return;
                }
                
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        const accuracy = Math.round(position.coords.accuracy);
                        
                        // Store in sessionStorage for Streamlit to access
                        sessionStorage.setItem('user_lat', lat.toString());
                        sessionStorage.setItem('user_lng', lng.toString());
                        sessionStorage.setItem('user_accuracy', accuracy.toString());
                        
                        statusEl.textContent = `✅ Location found: ${lat.toFixed(6)}, ${lng.toFixed(6)} (±${accuracy}m)`;
                        statusEl.style.color = '#28a745';
                        
                        // Reload the page to update Streamlit with new location
                        setTimeout(() => window.location.reload(), 1500);
                    },
                    function(error) {
                        let errorMsg = 'Location access failed';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                errorMsg = 'Location access denied. Please enable location permissions.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMsg = 'Location unavailable. Check GPS/network.';
                                break;
                            case error.TIMEOUT:
                                errorMsg = 'Location request timed out.';
                                break;
                        }
                        statusEl.textContent = '❌ ' + errorMsg;
                        statusEl.style.color = '#ff4b4b';
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 15000,
                        maximumAge: 300000
                    }
                );
            }
            </script>
            """
            
            components.html(geolocation_html, height=120)
            
            # Check if location was stored in sessionStorage
            if 'user_lat' in st.session_state and 'user_lng' in st.session_state:
                try:
                    lat = float(st.session_state.user_lat)
                    lng = float(st.session_state.user_lng)
                    accuracy = st.session_state.get('user_accuracy', 'unknown')
                    
                    st.session_state.report_lat = lat
                    st.session_state.report_lng = lng
                    
                    # Clear the stored location
                    del st.session_state.user_lat
                    del st.session_state.user_lng
                    if 'user_accuracy' in st.session_state:
                        del st.session_state.user_accuracy
                    
                    st.success(f"✅ Location set: {lat:.6f}, {lng:.6f} (±{accuracy}m)")
                    st.rerun()
                except (ValueError, TypeError):
                    st.error("❌ Error processing location data")
    st.markdown("**Quick presets:**")
    preset_cols = st.columns(5)
    presets = {
        "Hidden sign 🌳": "Parking sign hidden behind trees/bushes",
        "Faded sign ⚠️": "Sign is faded/hard to read",
        "No sign 🚫": "Should have a parking sign here",
        "Broken sign 💔": "Sign is damaged/broken",
        "FREE parking! 💚": "Free parking available here"
    }
    
    selected_preset = None
    for idx, (preset_label, preset_text) in enumerate(presets.items()):
        if preset_cols[idx].button(preset_label, use_container_width=True, key=f"preset_{idx}"):
            selected_preset = preset_text
            st.session_state.report_desc = preset_text
            st.rerun()
    
    with st.form("quick_report_form", border=True):
        issue_type = st.selectbox(
            "What's the area?",
            ["Paid Parking (Problematic)", "Free Parking"],
            index=0,
            help="Paid Parking = Hidden, faded, damaged, or unclear paid parking signs. Free Parking = Free spots."
        )
        
        description = st.text_area(
            "Details (optional)",
            placeholder="Add details or just click a preset above...",
            value=st.session_state.report_desc,
            height=80
        )
        
        submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True, type="primary")
        
        if submitted:
            add_report(st.session_state.report_lat, st.session_state.report_lng, issue_type, description)
            st.success("✅ Report submitted! Thank you for helping the community.", icon="✅")
            st.balloons()
            st.session_state.report_in_progress = False
            st.session_state.report_desc = ""
            st.rerun()
    
    # Show summary stats
    if reports:
        st.divider()
        st.markdown("### 📊 Quick Stats")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Reports</h3>
                <div class="value">{len(reports)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            hidden = len([r for r in reports if r[3] == 'Paid Parking (Problematic)'])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Problematic Paid</h3>
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
            total_upvotes = sum([r[5] for r in reports])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Community Votes</h3>
                <div class="value">{total_upvotes}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            free_parking = len([r for r in reports if r[3] == 'Free Parking'])
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                <h3>Free Spots</h3>
                <div class="value">{free_parking}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📍 No reports yet. Click on the map or use the form below to report!", icon="ℹ️")

elif page == "➕ Report":
    st.subheader("📝 Report a Parking Area")
    st.info("💡 **Tip:** For easier reporting, use the Map view to click a location and submit directly!", icon="💡")
    
    with st.form("detailed_report_form", border=True):
        st.markdown("#### Manual Coordinate Entry")
        
        col1, col2 = st.columns(2)
        
        with col1:
            latitude = st.number_input("Latitude", value=st.session_state.report_lat, format="%.6f")
        with col2:
            longitude = st.number_input("Longitude", value=st.session_state.report_lng, format="%.6f")
        
        issue_type = st.selectbox(
            "Parking Type",
            ["Paid Parking (Problematic)", "Free Parking"],
            help="Paid Parking = Hidden, faded, damaged, or unclear paid parking signs. Free Parking = Free spots."
        )
        
        description = st.text_area(
            "Description",
            placeholder="Add any details about this parking area...",
            height=100
        )
        
        submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True, type="primary")
        
        if submitted:
            add_report(latitude, longitude, issue_type, description)
            st.success("✅ Report submitted successfully! Thank you for helping the community.", icon="✅")
            st.balloons()
            st.session_state.report_in_progress = False

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
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.85rem;'>© 2026 SignSpot. Experimental service - no warranty or liability.</p>",
    unsafe_allow_html=True
)
