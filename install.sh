#!/bin/bash

# Define installation paths
INSTALL_DIR="/opt/llama.cpp-qt"
BIN_DIR="/usr/bin"
DESKTOP_DIR="/usr/share/applications"

# Ask for the sudo password
echo "Please enter your sudo password:"
sudo -v

# Check if llama.cpp-qt.py exists in /opt/llama.cpp-qt
if [ -f "/opt/llama.cpp-qt/llama.cpp-qt.py" ]; then
    sudo rm -r -f -d /opt/llama.cpp-qt
    sudo rm -r -f -d "$HOME/.llama.cpp-qt"
    sudo rm "$DESKTOP_DIR/llama-cpp-qt.desktop"
    sudo rm "$BIN_DIR/llama.cpp-qt"
fi

# Create the installation directory
echo "Creating installation directory..."
sudo mkdir -p "$INSTALL_DIR"
sudo chmod 755 "$INSTALL_DIR"

# Copy oai_api.py, server, and llama.cpp-qt.py to the installation directory
echo "Copying files to $INSTALL_DIR..."
sudo cp oai_api.py "$INSTALL_DIR"
sudo cp server "$INSTALL_DIR"
sudo cp llama.cpp-qt.py "$INSTALL_DIR"
sudo cp llama.png "$INSTALL_DIR"
sudo cp requirements.txt "$INSTALL_DIR"
sudo cp -r public "$INSTALL_DIR/public"
sudo cp llama.cpp-qt "$BIN_DIR"

# Set proper permissions
sudo chmod 755 "$INSTALL_DIR/api_like_OAI.py"
sudo chmod 755 "$INSTALL_DIR/server"
sudo chmod 755 "$INSTALL_DIR/llama.cpp-qt.py"
sudo chmod 755 "$BIN_DIR/llama.cpp-qt"

# Setup proper python venv
python3 -m venv --system-site-packages "$HOME/.llama.cpp-qt"
source "$HOME/.llama.cpp-qt/bin/activate"
pip install -r $INSTALL_DIR/requirements.txt
deactivate

# Create a desktop shortcut for llama.cpp-qt
echo "Creating desktop shortcut..."
cat <<EOF | sudo tee "$DESKTOP_DIR/llama-cpp-qt.desktop" > /dev/null
[Desktop Entry]
Path=$INSTALL_DIR
Name=LLama.cpp-Qt
Comment=LLama.cpp Server Wrapper
Exec=llama.cpp-qt
Icon=$INSTALL_DIR/llama.png
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=true
EOF

# Set proper permissions for the desktop shortcut
sudo chmod 644 "$DESKTOP_DIR/llama-cpp-qt.desktop"

echo "Installation completed successfully."

