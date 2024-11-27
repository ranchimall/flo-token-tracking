# Howto start the MYSQL version
## MySQL commands to create a user
1. CREATE USER 'FUfB6cwSsGDbQpmA7Qs8zQJxU3HpwCdnjT'@'localhost' IDENTIFIED BY 'RAcifrTM2V75ipy5MeLYaDU3UNcUXtrit933TGM5o7Yj2fs8XdP5';
2. GRANT ALL PRIVILEGES ON `rm_%_db`.* TO 'FUfB6cwSsGDbQpmA7Qs8zQJxU3HpwCdnjT'@'localhost' WITH GRANT OPTION;

## Modify config.ini
   ```
   [MYSQL]
   USERNAME = FUfB6cwSsGDbQpmA7Qs8zQJxU3HpwCdnjT
   PASSWORD = RAcifrTM2V75ipy5MeLYaDU3UNcUXtrit933TGM5o7Yj2fs8XdP5
   HOST = localhost
   DATABASE_PREFIX = rm
   ```
## Setup setps

1. Setup the Python Virtual Environment first with atleast python3.7 at least. Look below for exact instructions
2. Install setup.sh to install all dependencies. Give it execute permissions first `chmod +x pyflosetup.sh`, and then `./setup.sh` 
3. Install MYSQL and create MySQL user and password
4. Add all the data in confg.ini
5. Then run the command as per one of the options below

## How to run
1. python3.7 tracktokens-smartcontracts.py 
2. python3.7 tracktokens-smartcontracts.py --reset
3. python3.7 tracktokens-smartcontracts.py --rebuild
4. python3.7 tracktokens-smartcontracts.py --rebuild usd# tokenroom#

1. python3.7 tracktokens-smartcontracts.py => To run normally
2. python3.7 tracktokens-smartcontracts.py --reset => To remove all data and start from scratch
3. python3.7 tracktokens-smartcontracts.py --rebuild => To reprocess existing blockchain data for ALL TOKENS as stored in latestBlocks table of rm_latestCache_db database
4. python3.7 tracktokens-smartcontracts.py --rebuild usd# tokenroom# => To reprocess existing blockchain data for USD# TOKENROOM# as stored in latestBlocks table of rm_latestCache_db database

# FLO Token & Smart Contract System 
[![Test flodata parsing](https://github.com/ranchimall/flo-token-tracking/actions/workflows/test_parsing.yml/badge.svg?branch=swap-statef-testing)](https://github.com/ranchimall/flo-token-tracking/actions/workflows/test_parsing.yml)

## Important versions and their hashes
The python script scans the FLO Blockchain for Token and Smart Contract activity and creates/updates local SQLite databases accordingly. 

`339dac6a50bcd973dda4caf43998fc61dd79ea68` 
The legacy token and smart contract system running currently on the server 

`41c4078db98e878ecef3452007893136c531ba05` ==> WORKING VERSION | Token swap branch 
The latest version with token swap smart contract and token transfer with the following problems:
1. Parsing module is not able to detect token creation and transfer floData 
2. The smart contract system is not moving forward because it is not able to detect token databases as they are created when run form scratch, however it is working with old created token databases

`89d96501b9fcdd3c91c8900e1fb3dd5a8d8684c1`
Docker-compatibility branch is needed right now because Docker image made for flo-token-tracking required some changes which have been made in that branch. 


## How to start the system 

1. Create a virtual environment with python3.7 and activate it 
   ```
   python3.7 -m venv py3.7 
   source py3.7/bin/activate
   ```
2. Install python packages required for the virtual environment from `pip3 install -r requirements.txt` 
3. Setup config files with the following information  
   For testnet 
   ```
   # config.ini
   [DEFAULT]
      NET = testnet
      FLO_CLI_PATH = /usr/local/bin/flo-cli
      START_BLOCK = 740400
      FLOSIGHT_NETURL = https://0.0.0.0:19166/
      TESTNET_FLOSIGHT_SERVER_LIST = https://0.0.0.0:19166/
      MAINNET_FLOSIGHT_SERVER_LIST = https://blockbook.ranchimall.net/
      TOKENAPI_SSE_URL = https://ranchimallflo-testnet-blockbook.ranchimall.net
      IGNORE_BLOCK_LIST = 902446
      IGNORE_TRANSACTION_LIST = b4ac4ddb51188b28b39bcb3aa31357d5bfe562c21e8aaf8dde0ec560fc893174
      DATA_PATH = /home/production/deployed/ftt-blockbook-migration-testnet-rescan
      APP_ADMIN = oWooGLbBELNnwq8Z5YmjoVjw8GhBGH3qSP
    ```
    
   For mainnet 
   ```
   # config.ini
   [DEFAULT]
      NET = mainnet
      FLO_CLI_PATH = /usr/local/bin/flo-cli
      START_BLOCK = 3387900
      FLOSIGHT_NETURL = https://blockbook.ranchimall.net/
      TESTNET_FLOSIGHT_SERVER_LIST = https://0.0.0.0:19166/
      MAINNET_FLOSIGHT_SERVER_LIST = https://blockbook.ranchimall.net/
      TOKENAPI_SSE_URL = https://ranchimallflo-blockbook.ranchimall.net
      IGNORE_BLOCK_LIST = 2
      IGNORE_TRANSACTION_LIST = b4
      DATA_PATH = /home/production/deployed/ftt-blockbook-migration-rescan
      APP_ADMIN = FNcvkz9PZNZM3HcxM1XTrVL4tgivmCkHp9
      API_VERIFY = False

   ```

4. Install pyflosetup.sh if dependency errors of any kind come. Give it execute permissions first `chmod +x pyflosetup.sh`, and then `./pyflosetup.sh`  
   
    
5. If running for the first time, run  `python3.7 tracktokens-smartcontracts.py --reset` otherwise run `python3.7 tracktokens-smartcontracts.py`


## How to setup a virtual environment

To set up a virtual environment that uses Python 3.7 while keeping Python 3.10 as the default system version, follow these steps:
Step 1: Make Sure Python 3.7 is Installed

Ensure Python 3.7 is installed on your system:

    Add the deadsnakes PPA (if not already done):

    bash

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

Install Python 3.7 and the venv module for Python 3.7:

bash

    sudo apt install python3.7 python3.7-venv

Step 2: Create a Virtual Environment with Python 3.7

Since you want your virtual environment to specifically use Python 3.7, you need to use Python 3.7 explicitly to create the venv, while keeping Python 3.10 as the system's default Python:

    Create the virtual environment using Python 3.7:

    bash

    /usr/bin/python3.7 -m venv myenv

    This command creates a virtual environment named myenv using Python 3.7 located at /usr/bin/python3.7. Replace myenv with your desired environment name.

Step 3: Activate the Virtual Environment

Activate the virtual environment to switch to Python 3.7 within the environment:

    On Linux or macOS:

    bash

source myenv/bin/activate

On Windows:

bash

    .\myenv\Scripts\activate

After activation, your shell prompt should indicate that the virtual environment is active.
Step 4: Verify the Python Version in the Virtual Environment

To confirm that the virtual environment is using Python 3.7, run:

bash

python --version

You should see output indicating that Python 3.7 is being used:

Python 3.7.x

Step 5: Deactivate the Virtual Environment When Done

When you are finished, deactivate the virtual environment to return to the base Python 3.10:

bash

deactivate

