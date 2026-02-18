#!/bin/bash
# Quick start script for SignSpot

echo "🅿️ Starting SignSpot..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (fast Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed!"
    echo "⚠️  Please restart your terminal or run: source $HOME/.cargo/env"
    exit 0
fi

# Run the app with uv (auto-creates venv and installs dependencies)
echo "🚀 Launching app..."
uv run main.py
