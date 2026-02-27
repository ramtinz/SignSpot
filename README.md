# 🅿️ SignSpot

> **A crowdsourced web app to help drivers spot problematic parking signs before getting ticketed**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![NiceGUI](https://img.shields.io/badge/NiceGUI-latest-green.svg)](https://nicegui.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Demo Concept**: Community-driven platform for reporting and discovering parking signs that are hidden, unclear, missing, or damaged.

## 💡 The Problem

Private parking companies often place signs in hard-to-see locations, leading to unfair parking tickets. This app addresses that by crowdsourcing problematic sign locations.

## 🎯 Solution

- **Interactive map** using OpenStreetMap (no API keys needed)
- **Simple reporting** - click map location, select issue type, submit
- **Visual markers** - color-coded by issue severity
- **Lightweight** - Single Python file, SQLite database, no complex setup

## ✨ Features

- 🗺️ **Interactive OpenStreetMap** - Click to report issues
- 📍 **Location-based reports** - Pin exact problem locations  
- 📸 **Categorized issues** - Hidden, unclear, missing, damaged
- 👍 **Community voting** - Confirm problematic signs
- 💾 **SQLite database** - No external database needed
- 🚀 **Single Python file** - Simple and lightweight

## 🏃 Quick Start

### Prerequisites

- Python 3.8 or higher (check: `python3 --version`)
- uv (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Installation & Run

```bash
# Navigate to project (after cloning the `signspot` repo)
cd signspot

# Run with uv (automatically creates venv and installs dependencies)
uv run main.py
```

**That's it!** The app will open automatically at `http://localhost:8080`

uv handles everything automatically - virtual environment, dependencies, and running the app.

### Alternative (without uv)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 📖 How to Use

1. **View reports** - See all parking sign issues on the map (colored markers)
2. **Report an issue** - Click anywhere on the map
3. **Fill the form** - Select issue type and describe the problem
4. **Submit** - Your report appears immediately on the map
5. **Vote** - Click existing markers to view details and vote

## 🎨 Issue Types

- 🔴 **Hidden** - Behind bushes, trees, or obstacles
- 🟠 **Unclear** - Faded, confusing wording
- 🟣 **Missing** - Should be there but isn't
- 🟤 **Damaged** - Broken, vandalized, graffiti

## 📁 Project Structure

```
signspot/
├── main.py              # Complete application (~200 lines)
├── requirements.txt     # Just NiceGUI
├── parking_reports.db   # SQLite database (auto-created)
└── README.md
```

## 🛠️ Tech Stack

- **Framework**: [NiceGUI](https://nicegui.io/) - Python web UI framework
- **Maps**: Leaflet.js + OpenStreetMap (no API keys!)
- **Database**: SQLite (built into Python)
- **Frontend**: Automatic (handled by NiceGUI)

## 🌐 Deployment

Deploy for free on:
- **Railway** - `railway up`
- **Render** - Connect GitHub repo
- **PythonAnywhere** - Upload and run
- **Fly.io** - `fly launch`

## 💡 Why NiceGUI?

- ✅ No Node.js, no frontend/backend split
- ✅ One language (Python) for everything
- ✅ Built-in reactive UI components
- ✅ Native Leaflet map support
- ✅ Perfect for rapid prototyping
- ✅ Easy to extend and customize

## 🚀 Future Ideas

- [ ] Photo uploads
- [ ] User authentication
- [ ] Export to CSV/JSON
- [ ] Mobile app (same Python code!)
- [ ] Email notifications
- [ ] Dark mode
- [ ] Filter by issue type
- [ ] Search by location

## ⚠️ Disclaimer

**EXPERIMENTAL SERVICE - NO LIABILITY**

This is an experimental crowdsourced application. The information provided is submitted by community members and may be inaccurate, outdated, or incomplete.

**Important:**
- We make **NO WARRANTIES** about the accuracy, reliability, or completeness of any reports
- We assume **NO LIABILITY** for parking tickets, fines, or any other consequences
- **Always verify parking signs yourself** before parking
- Use this service at your own risk
- Report accuracy depends entirely on community contributions

## 📄 License & Copyright

© 2026 SignSpot. All rights reserved.

MIT License - Free to use and modify for non-commercial purposes.

## 🙏 Credits

- Maps: [OpenStreetMap](https://www.openstreetmap.org/)
- Framework: [NiceGUI](https://nicegui.io/)
- Icons: [Leaflet Color Markers](https://github.com/pointhi/leaflet-color-markers)

---

**SignSpot: Spot the signs before they cost you! 🅿️✅**
