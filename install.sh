#!/bin/bash

# Bitkub DCA Bot - Installation Script for Raspberry Pi
# สคริปต์ติดตั้ง DCA Bot สำหรับ Raspberry Pi

set -e

echo "=================================================="
echo "   Bitkub DCA Bot - Raspberry Pi Installation"
echo "=================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
INSTALL_DIR="/home/pi/bitkub-dca"
SERVICE_NAME="bitkub-dca"

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    echo -e "${YELLOW}Warning: Not running as 'pi' user. Service may need adjustment.${NC}"
fi

# Step 1: Update system
echo -e "\n${GREEN}[1/7] Updating system packages...${NC}"
sudo apt-get update

# Step 2: Install Python and pip
echo -e "\n${GREEN}[2/7] Installing Python dependencies...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv

# Step 3: Set timezone to Bangkok
echo -e "\n${GREEN}[3/7] Setting timezone to Asia/Bangkok...${NC}"
sudo timedatectl set-timezone Asia/Bangkok
echo "Current time: $(date)"

# Step 4: Create installation directory
echo -e "\n${GREEN}[4/7] Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"

# Copy files if running from different directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    cp "$SCRIPT_DIR/dca_bot.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/test_connection.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/"

    # Copy .env if exists
    if [ -f "$SCRIPT_DIR/.env" ]; then
        cp "$SCRIPT_DIR/.env" "$INSTALL_DIR/"
    fi
fi

# Step 5: Create virtual environment and install dependencies
echo -e "\n${GREEN}[5/7] Setting up Python virtual environment...${NC}"
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Step 6: Setup .env file
echo -e "\n${GREEN}[6/7] Setting up configuration...${NC}"
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo -e "${YELLOW}Please edit .env file with your API credentials:${NC}"
    echo "  nano $INSTALL_DIR/.env"
else
    echo ".env file already exists"
fi

# Step 7: Install systemd service
echo -e "\n${GREEN}[7/7] Installing systemd service...${NC}"
sudo cp "$SCRIPT_DIR/bitkub-dca.service" /etc/systemd/system/
sudo systemctl daemon-reload

echo ""
echo "=================================================="
echo -e "${GREEN}Installation completed!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit configuration file:"
echo "   nano $INSTALL_DIR/.env"
echo ""
echo "2. Test API connection:"
echo "   cd $INSTALL_DIR"
echo "   source venv/bin/activate"
echo "   python test_connection.py"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "4. Enable auto-start on boot:"
echo "   sudo systemctl enable $SERVICE_NAME"
echo ""
echo "5. Check service status:"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "6. View logs:"
echo "   tail -f $INSTALL_DIR/dca_bot.log"
echo "   journalctl -u $SERVICE_NAME -f"
echo ""
