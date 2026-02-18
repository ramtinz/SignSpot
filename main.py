from nicegui import ui, app
import sqlite3
from datetime import datetime
from pathlib import Path
import json

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
            photo_path TEXT,
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
    c.execute('SELECT id, latitude, longitude, issue_type, description, photo_path, votes, created_at FROM reports ORDER BY created_at DESC')
    reports = c.fetchall()
    conn.close()
    return reports

def add_report(lat, lng, issue_type, description, photo_path=None):
    """Add a new report to database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (latitude, longitude, issue_type, description, photo_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (lat, lng, issue_type, description, photo_path))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Issue type colors for map markers
ISSUE_COLORS = {
    'hidden': 'red',
    'unclear': 'orange', 
    'missing': 'purple',
    'damaged': 'brown'
}

@ui.page('/')
async def main_page():
    """Main application page"""
    
    def create_markers_js():
        """Generate JavaScript for map markers"""
        reports = get_all_reports()
        markers_data = []
        
        for report in reports:
            report_id, lat, lng, issue_type, desc, photo, votes, created = report
            color = ISSUE_COLORS.get(issue_type, 'blue')
            
            popup_html = f'''
                <div style="min-width: 200px;">
                    <h4 style="margin: 0 0 8px 0;">{issue_type.title()} Sign</h4>
                    <p style="margin: 0 0 8px 0;">{desc if desc else 'No description'}</p>
                    <div style="padding-top: 8px; border-top: 1px solid #ddd;">
                        <span>👍 {votes} votes</span>
                    </div>
                </div>
            '''
            
            markers_data.append({
                'lat': lat,
                'lng': lng,
                'color': color,
                'popup': popup_html
            })
        
        return json.dumps(markers_data)
    
    # Header
    with ui.header().classes('items-center justify-between bg-blue-grey-9'):
        ui.label('🅿️ SignSpot').classes('text-h5')
        ui.label('Spot problematic parking signs before you get ticketed').classes('text-subtitle2 opacity-70')
    
    # Disclaimer banner
    with ui.card().classes('w-full bg-orange-1 border-l-4 border-orange-5'):
        ui.label('⚠️ Experimental App - No Liability').classes('text-subtitle2 font-bold text-orange-9')
        ui.label('This is an experimental crowdsourced app. We make no guarantees about the accuracy of reports and assume no liability for any parking tickets or issues. Always verify parking signs yourself.').classes('text-caption text-grey-8')
    
    # Map
    ui.add_head_html('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />')
    ui.add_head_html('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>')
    
    map_div = ui.html('<div id="map" style="height: 60vh; width: 100%;"></div>').classes('w-full')
    
    def update_map():
        """Update the map with current reports"""
        markers_json = create_markers_js()
        
        map_script = f'''
            var map = L.map('map').setView([37.7749, -122.4194], 13);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }}).addTo(map);
            
            const iconUrls = {{
                red: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                orange: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png',
                purple: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png',
                brown: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png',
                blue: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png'
            }};
            
            const markers = {markers_json};
            markers.forEach(marker => {{
                const icon = L.icon({{
                    iconUrl: iconUrls[marker.color] || iconUrls.blue,
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }});
                
                L.marker([marker.lat, marker.lng], {{icon: icon}})
                    .bindPopup(marker.popup)
                    .addTo(map);
            }});
            
            map.on('click', function(e) {{
                window.location.href = '/report?lat=' + e.latlng.lat + '&lng=' + e.latlng.lng;
            }});
        '''
        
        ui.run_javascript(map_script)
    
    ui.timer(0.1, update_map, once=True)
    
    # Instructions
    with ui.card().classes('w-full mt-4'):
        ui.label('📍 Click anywhere on the map to report a parking sign issue').classes('text-subtitle1')
    
    # Footer info card
    with ui.card().classes('w-full mt-2 bg-grey-1'):
        ui.label('© 2026 SignSpot. Experimental service - no warranty or liability.').classes('text-caption text-grey-7')

@ui.page('/report')
async def report_page(lat: float, lng: float):
    """Report submission page"""
    
    with ui.header().classes('items-center bg-blue-grey-9'):
        ui.link('← Back to SignSpot', '/').classes('text-white')
        ui.label('Report Issue').classes('text-h5 ml-4')
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-4'):
        
        ui.label(f'Location: {lat:.6f}, {lng:.6f}').classes('text-body2 text-grey-7 mb-4')
        
        with ui.card().classes('w-full'):
            ui.label('Report Parking Sign Issue').classes('text-h6 mb-4')
            
            issue_type = ui.select(
                label='Issue Type',
                options={
                    'hidden': 'Hidden (behind bushes, trees, etc.)',
                    'unclear': 'Unclear (faded, confusing)',
                    'missing': 'Missing (should be there)',
                    'damaged': 'Damaged (broken, graffiti)'
                },
                value='hidden'
            ).classes('w-full mb-4')
            
            description = ui.textarea(
                label='Description (optional)',
                placeholder='Describe the issue to help other drivers...'
            ).classes('w-full mb-4')
            
            async def submit_report():
                desc_text = description.value if description.value else ''
                add_report(lat, lng, issue_type.value, desc_text)
                ui.notify('Report submitted successfully!', type='positive')
                await ui.navigate.to('/')
            
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=lambda: ui.navigate.to('/')).props('flat')
                ui.button('Submit Report', on_click=submit_report).props('color=primary')

# Run the app
if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title='SignSpot - Parking Sign Reporter',
        port=8081,
        reload=True,
        show=True
    )
