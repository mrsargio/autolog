#!/data/data/com.termux/files/usr/bin/bash
echo "🔧 Setting up Termux..."

# Update packages
pkg update && pkg upgrade -y

# Install Python and required packages
pkg install python -y
pip install requests

# Setup storage
termux-setup-storage

# Create script directory
mkdir -p /sdcard/ScammerClasses

echo "✅ Setup complete!"
echo "🚀 Now run: python utk.py"
