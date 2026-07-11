#!/bin/bash

# Bitkub DCA Bot - Uninstallation Script
# สคริปต์ถอนการติดตั้ง DCA Bot

echo "=================================================="
echo "   Bitkub DCA Bot - Uninstallation"
echo "=================================================="

SERVICE_NAME="bitkub-dca"
INSTALL_DIR="/home/pi/bitkub-dca"

# Stop and disable service
echo "Stopping service..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true
sudo systemctl disable $SERVICE_NAME 2>/dev/null || true

# Remove service file
echo "Removing service file..."
sudo rm -f /etc/systemd/system/$SERVICE_NAME.service
sudo systemctl daemon-reload

# Ask before removing files
read -p "Remove all files in $INSTALL_DIR? (y/N): " confirm
if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    echo "Removing installation directory..."
    rm -rf "$INSTALL_DIR"
    echo "All files removed."
else
    echo "Files preserved in $INSTALL_DIR"
fi

echo ""
echo "Uninstallation completed!"
