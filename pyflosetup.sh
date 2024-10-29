#!/bin/bash
# Run this setup file to install pyflo dependencies if pyflo is being installed
# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y build-essential libssl-dev pkg-config python3.7-dev python3-setuptools


# Inform the user
echo "System dependencies installed successfully."

# Install Python packages
pip install --upgrade pip  # Ensure pip is up-to-date
pip install --use-pep517 -r requirements.txt

git clone https://github.com/ranchimall/pyflo
sudo python3 pyflo/setup.py install

# Inform the user
echo "Python dependencies installed successfully."
