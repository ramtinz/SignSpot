# 🅿️ SignSpot

> **A crowdsourced web app to help drivers find free parking and avoid paid areas**

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SignSpot**: Community-driven platform for reporting and discovering paid parking areas and free parking spots in Copenhagen.

## 💡 The Problem

Drivers in Copenhagen waste time looking for parking and often unknowingly park in paid areas, resulting in expensive tickets. This app crowdsources this information to help everyone find parking quickly.

## 🎯 Solution

- **Interactive map** - Real-time reports of parking areas
- **Simple reporting** - Click map, choose type (Paid/Free), submit
- **Community voting** - Verify accuracy of reports
- **Lightweight** - Single Python file, SQLite database

## ✨ Features

- 🗺️ **Interactive Map** - Click to select location and submit reports instantly
- 📍 **Real-time Reports** - See all parking areas reported by the community
- 🔴🟢 **Clear Categories** - Paid Parking (red) | Free Parking (green)
- 👍👎 **Upvote/Downvote** - Vote on report accuracy
- 🚩 **Flag System** - Report incorrect or spam submissions
- 📊 **Community Stats** - View voting agreement and trust scores
- 💾 **SQLite Database** - Persistent data storage
- 🎨 **Modern UI** - Beautiful gradient design with Streamlit

## 🏃 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation & Run Locally

```bash
# Clone the repository
git clone https://github.com/ramtinz/SignSpot.git
cd SignSpot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run main.py
```

**That's it!** The app opens at `http://localhost:8501`

## 🌐 Live Deployment

**Live at:** [SignSpot on Streamlit Cloud](https://signspot.streamlit.app)

### Deploy Your Own (Free)

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repo
4. Deploy with one click!

The app auto-deploys on every git push. No servers to manage, always-on hosting.

## 📖 How to Use

### 🗺️ Map View
1. **Browse** - See all parking reports on the map
2. **Click location** - Select where you want to report
3. **Fill form** - Choose Paid/Free, add details, click preset or type
4. **Submit** - Report appears immediately

### 📊 Vote on Reports
1. Go to "Reports" tab
2. Click "Vote on Reports"
3. Enter report ID
4. Click 👍 (Agree) or 👎 (Disagree)
5. Help community verify accuracy!

### 🚩 Flag Incorrect Reports
1. Go to "Reports" tab
2. Find the report ID
3. Enter ID in "All Reports" tab
4. Flag if inaccurate (3+ flags = marked as disputed)

## 🎨 Parking Types

- 🔴 **Paid Parking** - Areas with paid parking (be aware of tickets!)
- 🟢 **Free Parking** - Free parking available (great find!)

## 📱 Quick Presets

One-click preset descriptions:
- "Hidden sign 🌳" - Sign behind trees/bushes
- "Faded sign ⚠️" - Sign is faded/hard to read
- "No sign 🚫" - Should have a sign here
- "Broken sign 💔" - Sign is damaged
- "FREE parking! 💚" - Free parking spot
- "Verified ✓" - Confirmed by community

## 📁 Project Structure

```
SignSpot/
├── main.py              # Complete Streamlit app
├── requirements.txt     # Dependencies
├── parking_reports.db   # SQLite database (auto-created)
├── README.md            # This file
└── .gitignore          # Git ignore rules
```

## 🛠️ Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/) - Python web framework
- **Maps**: [Folium](https://folium.readthedocs.io/) + [OpenStreetMap](https://www.openstreetmap.org/)
- **Database**: SQLite (built into Python)
- **Styling**: Custom CSS with Streamlit markdown
- **Hosting**: Streamlit Cloud (free tier)

## 📊 Features Explained

### Voting System
- **Upvotes 👍** - "This report is accurate"
- **Downvotes 👎** - "This report is inaccurate/outdated"
- **Agreement %** - Shows how much the community agrees
- **Net Score** - Upvotes minus downvotes

### Flagging System
- **0 flags** - ✅ OK
- **1-2 flags** - ⚠️ Disputed (community disagrees)
- **3+ flags** - 🚨 Flagged (likely inaccurate or spam)

### Statistics
- Total reports submitted
- Community voting stats
- Agreement percentage
- Flagged/disputed count

## 🚀 Future Ideas

- [ ] Photo uploads of parking signs
- [ ] User authentication & profiles
- [ ] Mobile-optimized interface
- [ ] Multiple cities support
- [ ] Email notifications for areas
- [ ] Export reports to CSV/JSON
- [ ] Time-based parking rules
- [ ] Search by address
- [ ] Dark mode

## ⚠️ Disclaimer

**EXPERIMENTAL SERVICE - USE AT YOUR OWN RISK**

SignSpot is an experimental crowdsourced application. Reports are submitted by community members and may be inaccurate, outdated, or incomplete.

**Important:**
- We make **NO WARRANTIES** about accuracy or reliability
- We assume **NO LIABILITY** for parking tickets or consequences
- **Always verify parking rules yourself** before parking
- This is a community tool - accuracy depends on users
- Report information responsibly

## 📄 License

MIT License - © 2026 SignSpot

Free to use, modify, and distribute for non-commercial purposes.

## 🙏 Credits

- Maps: [OpenStreetMap](https://www.openstreetmap.org/) contributors
- Framework: [Streamlit](https://streamlit.io/)
- Map visualization: [Folium](https://folium.readthedocs.io/)

---

**SignSpot: Find free parking, avoid tickets! 🅿️✅**
