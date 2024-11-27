#!/bin/bash

# =====================
# Setup Script for PyFLO
# =====================

# Exit on any error
set -e

# Step 1: Update Package List
echo "Updating package list..."
sudo apt update

# Step 2: Install System Dependencies
echo "Installing system dependencies..."
sudo apt install -y build-essential libssl-dev pkg-config python3.7-dev python3-setuptools git

# Inform the user
echo "System dependencies installed successfully."

# Step 3: Clone the PyFLO Repository
if [ ! -d "pyflo" ]; then
    echo "Cloning the PyFLO repository..."
    git clone https://github.com/ranchimall/pyflo
else
    echo "PyFLO repository already exists. Skipping clone."
fi

# Step 4: Install Python Dependencies
echo "Installing Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    # Generate a requirements.txt file if missing
    echo "arduino" > requirements.txt
    # echo "pybtc" >> requirements.txt
    echo "config" >> requirements.txt
    echo "Generated requirements.txt with default dependencies."
else
    echo "requirements.txt file exists. Using it for installation."
fi

# Ensure pip is up-to-date
pip install --upgrade pip

# Install Python packages
pip install --use-pep517 -r requirements.txt

# Step 5: Install PyFLO
echo "Installing PyFLO..."
sudo python3 pyflo/setup.py install

# Inform the user
echo "Python dependencies and PyFLO installed successfully."

# Step 6: Final Instructions
echo "Setup complete! You're ready to use PyFLO."
