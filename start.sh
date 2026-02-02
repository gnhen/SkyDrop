#!/bin/bash
# Startup script for SkyDrop application

set -e

echo "🚀 Starting SkyDrop..."

# Check if .env.local exists, if not suggest creating it
if [ ! -f .env.local ]; then
    echo "💡 Tip: Create .env.local to override default settings without modifying .env"
    echo "   cp .env .env.local"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p received_files
mkdir -p data

# Initialize database
echo "💾 Initializing database..."
python -c "from receiver import init_db; init_db()"

# Start the application
echo "✨ Starting SkyDrop server..."
python receiver.py
