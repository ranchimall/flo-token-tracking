#!/bin/bash

# =====================
# Setup Script for PyFLO, MySQL, and FLO Token Tracking
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

# Step 3: Install MySQL
echo "Installing MySQL server, client, and development libraries..."
sudo apt install -y mysql-server mysql-client libmysqlclient-dev

# Start and enable MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Inform the user
echo "MySQL server and client installed successfully. MySQL service is running."

# Step 4: Configure MySQL Default User and Privileges
echo "Configuring MySQL user and privileges..."
MYSQL_USER="FUfB6cwSsGDbQpmA7Qs8zQJxU3HpwCdnjT"
MYSQL_PASSWORD="RAcifrTM2V75ipy5MeLYaDU3UNcUXtrit933TGM5o7Yj2fs8XdP5"

sudo mysql -e "CREATE USER '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';"
sudo mysql -e "GRANT ALL PRIVILEGES ON rm_%_db.* TO '${MYSQL_USER}'@'localhost' WITH GRANT OPTION;"
sudo mysql -e "FLUSH PRIVILEGES;"

echo "MySQL user '${MYSQL_USER}' created and granted privileges on databases matching 'rm_%_db'."

# Step 5: Clone the PyFLO Repository
if [ ! -d "pyflo" ]; then
    echo "Cloning the PyFLO repository..."
    git clone https://github.com/ranchimall/pyflo
else
    echo "PyFLO repository already exists. Skipping clone."
fi

# Step 6: Install Python Dependencies
echo "Installing Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    # Generate a requirements.txt file if missing
    echo "arduino" > requirements.txt
    echo "pybtc" >> requirements.txt
    echo "config" >> requirements.txt
    echo "pymysql" >> requirements.txt
    echo "Generated requirements.txt with default dependencies."
else
    echo "requirements.txt file exists. Adding pymysql to the list."
    echo "pymysql" >> requirements.txt
fi

# Ensure pip is up-to-date
pip install --upgrade pip

# Install Python packages
pip install --use-pep517 -r requirements.txt

# Step 7: Install PyFLO
echo "Installing PyFLO..."
sudo python3 pyflo/setup.py install

# Inform the user
echo "Python dependencies and PyFLO installed successfully."

# Step 8: Clone the FLO Token Tracking Repository
if [ ! -d "flo-token-tracking" ]; then
    echo "Cloning the FLO Token Tracking repository (mysql-migration branch)..."
    git clone --branch mysql-migration https://github.com/ranchimall/flo-token-tracking
else
    echo "FLO Token Tracking repository already exists. Skipping clone."
fi

# Step 9: Navigate into the FLO Token Tracking Directory
echo "Navigating into the FLO Token Tracking directory..."
cd flo-token-tracking

# Inform the user
echo "You are now in the FLO Token Tracking directory. Setup complete!"

# Final Instructions
echo "========================================================"
echo "Setup is complete. MySQL server is installed and running."
echo "MySQL user '${MYSQL_USER}' has been created with privileges on databases matching 'rm_%_db'."
echo "========================================================"
