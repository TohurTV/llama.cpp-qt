#!/bin/bash

# Define installation paths
INSTALL_DIR="/opt/llama.cpp-qt"
BIN_DIR="/usr/bin"
DESKTOP_DIR="/usr/share/applications"

# Check if the script is run as root (sudo)
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Please use sudo."
    exit 1
fi

# Ask for the sudo password
echo "Please enter your sudo password:"
sudo -v

# Create the installation directory
echo "Creating installation directory..."
sudo mkdir -p "$INSTALL_DIR"
sudo chmod 755 "$INSTALL_DIR"

# Copy api_like_OAI.py, server, and llama.cpp-qt.py to the installation directory
echo "Copying files to $INSTALL_DIR..."
sudo cp api_like_OAI.py "$INSTALL_DIR"
sudo cp server "$INSTALL_DIR"
sudo cp llama.cpp-qt.py "$INSTALL_DIR"
sudo cp llama.png "$INSTALL_DIR"
sudo cp llama.cpp-qt "$BIN_DIR"

# Set proper permissions
sudo chmod 755 "$INSTALL_DIR/api_like_OAI.py"
sudo chmod 755 "$INSTALL_DIR/server"
sudo chmod 755 "$INSTALL_DIR/llama.cpp-qt.py"
sudo chmod 755 "$BIN_DIR/llama.cpp-qt"

# Create a desktop shortcut for llama.cpp-qt
echo "Creating desktop shortcut..."
cat <<EOF | sudo tee "$DESKTOP_DIR/llama-cpp-qt.desktop" > /dev/null
[Desktop Entry]
Name=LLama.cpp-Qt
Comment=LLama.cpp Server Wrapper
Exec=llama.cpp-qt
Icon=$INSTALL_DIR/llama.png
Terminal=false
Type=Application
Categories=Utility;
EOF

# Set proper permissions for the desktop shortcut
sudo chmod 644 "$DESKTOP_DIR/llama-cpp-qt.desktop"

echo "Installation completed successfully."

