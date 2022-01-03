# FLO Token & Smart Contract System 

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
    
    # config.py
    committeeAddressList = ['oVwmQnQGtXjRpP7dxJeiRGd5azCrJiB6Ka']
    sseAPI_url = 'https://ranchimallflo-testnet.duckdns.org/'
    ```
    
   For mainnet 
   ```
   # config.ini
   [DEFAULT]
    NET = mainnet
    FLO_CLI_PATH = /usr/local/bin/flo-cli
    START_BLOCK = 3387900
    
    # config.py
    committeeAddressList = ['FRwwCqbP7DN4z5guffzzhCSgpD8Q33hUG8']
    sseAPI_url = 'https://ranchimallflo.duckdns.org/'
    ```
    
4. If running for the first time, run  `python3.7 tracktokens-smartcontracts.py --reset` otherwise run `python3.7 tracktokens-smartcontracts.py`
