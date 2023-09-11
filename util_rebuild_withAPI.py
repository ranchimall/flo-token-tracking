from sqlalchemy import create_engine, desc, func 
from sqlalchemy.orm import sessionmaker 
from models import SystemData, TokenBase, ActiveTable, ConsumedTable, TransferLogs, TransactionHistory, TokenContractAssociation, ContractBase, ContractStructure, ContractParticipants, ContractTransactionHistory, ContractDeposits, ConsumedInfo, ContractWinners, ContinuosContractBase, ContractStructure2, ContractParticipants2, ContractDeposits2, ContractTransactionHistory2, SystemBase, ActiveContracts, SystemData, ContractAddressMapping, TokenAddressMapping, DatabaseTypeMapping, TimeActions, RejectedContractTransactionHistory, RejectedTransactionHistory, LatestCacheBase, LatestTransactions, LatestBlocks 
import json 
from tracktokens_smartcontracts import processTransaction, checkLocal_expiry_trigger_deposit, newMultiRequest
import os 
import logging 
import argparse 
import configparser 
import shutil 
import sys 
import pdb


# helper functions
def check_database_existence(type, parameters):
    if type == 'token':
        return os.path.isfile(f"./tokens/{parameters['token_name']}.db")

    if type == 'smart_contract':
        return os.path.isfile(f"./smartContracts/{parameters['contract_name']}-{parameters['contract_address']}.db")


def create_database_connection(type, parameters):
    if type == 'token':
        engine = create_engine(f"sqlite:///tokens/{parameters['token_name']}.db", echo=True)
    elif type == 'smart_contract':
        engine = create_engine(f"sqlite:///smartContracts/{parameters['contract_name']}-{parameters['contract_address']}.db", echo=True)
    elif type == 'system_dbs':
        engine = create_engine(f"sqlite:///{parameters['db_name']}.db", echo=False)

    connection = engine.connect()
    return connection


def create_database_session_orm(type, parameters, base):
    if type == 'token':
        engine = create_engine(f"sqlite:///tokens/{parameters['token_name']}.db", echo=True)
        base.metadata.create_all(bind=engine)
        session = sessionmaker(bind=engine)()

    elif type == 'smart_contract':
        engine = create_engine(f"sqlite:///smartContracts/{parameters['contract_name']}-{parameters['contract_address']}.db", echo=True)
        base.metadata.create_all(bind=engine)
        session = sessionmaker(bind=engine)()
    
    elif type == 'system_dbs':
        engine = create_engine(f"sqlite:///{parameters['db_name']}.db", echo=False)
        base.metadata.create_all(bind=engine)
        session = sessionmaker(bind=engine)()
    
    return session


# MAIN EXECUTION STARTS
# Configuration of required variables 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('tracking.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


#  Rule 1 - Read command line arguments to reset the databases as blank
#  Rule 2     - Read config to set testnet/mainnet
#  Rule 3     - Set flo blockexplorer location depending on testnet or mainnet
#  Rule 4     - Set the local flo-cli path depending on testnet or mainnet ( removed this feature | Flosights are the only source )
#  Rule 5     - Set the block number to scan from


# Read command line arguments
parser = argparse.ArgumentParser(description='Script tracks RMT using FLO data on the FLO blockchain - https://flo.cash')
parser.add_argument('-rb', '--toblocknumer', nargs='?', type=int, help='Forward to the specified block number')
parser.add_argument('-r', '--blockcount', nargs='?', type=int, help='Forward to the specified block count') 
parser.add_argument('-to', '--to_blockNumber', nargs='?', type=int, help='Process until the specified block number')  # New argument
args = parser.parse_args()


if (args.blockcount and args.toblocknumber):
    print("You can only specify one of the options -b or -c")
    sys.exit(0)
elif args.blockcount:
    forward_block = lastscannedblock + args.blockcount
elif args.toblocknumer:
    forward_block = args.toblocknumer
else:
    latestCache_session = create_database_session_orm('system_dbs', {'db_name':'latestCache'}, LatestCacheBase)
    forward_block = int(latestCache_session.query(LatestBlocks.blockNumber).order_by(LatestBlocks.blockNumber.desc()).first()[0])
    latestCache_session.close()


args = parser.parse_args()

apppath = os.path.dirname(os.path.realpath(__file__))
dirpath = os.path.join(apppath, 'tokens')
if not os.path.isdir(dirpath):
    os.mkdir(dirpath)
dirpath = os.path.join(apppath, 'smartContracts')
if not os.path.isdir(dirpath):
    os.mkdir(dirpath)

# rename all the old databases 
# system.db , latestCache.db, smartContracts, tokens 
if os.path.isfile('./system.db'):
    os.rename('system.db', 'system1.db')
if os.path.isfile('./latestCache.db'):
    os.rename('latestCache.db', 'latestCache1.db')
if os.path.isfile('./smartContracts'):
    os.rename('smartContracts', 'smartContracts1')
if os.path.isfile('./tokens'):
    os.rename('tokens', 'tokens1')

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

# todo - write all assertions to make sure default configs are right 
if (config['DEFAULT']['NET'] != 'mainnet') and (config['DEFAULT']['NET'] != 'testnet'):
    logger.error("NET parameter in config.ini invalid. Options are either 'mainnet' or 'testnet'. Script is exiting now")
    sys.exit(0)

# Specify mainnet and testnet server list for API calls and websocket calls 
serverlist = None
if config['DEFAULT']['NET'] == 'mainnet':
    serverlist = config['DEFAULT']['MAINNET_FLOSIGHT_SERVER_LIST']
elif config['DEFAULT']['NET'] == 'testnet':
    serverlist = config['DEFAULT']['TESTNET_FLOSIGHT_SERVER_LIST']
serverlist = serverlist.split(',')
neturl = config['DEFAULT']['FLOSIGHT_NETURL']
tokenapi_sse_url = config['DEFAULT']['TOKENAPI_SSE_URL']

# Delete database and smartcontract directory if reset is set to 1
#if args.reset == 1:
logger.info("Resetting the database. ")
apppath = os.path.dirname(os.path.realpath(__file__))
dirpath = os.path.join(apppath, 'tokens')
shutil.rmtree(dirpath)
os.mkdir(dirpath)
dirpath = os.path.join(apppath, 'smartContracts')
shutil.rmtree(dirpath)
os.mkdir(dirpath)
dirpath = os.path.join(apppath, 'system.db')
if os.path.exists(dirpath):
    os.remove(dirpath)
dirpath = os.path.join(apppath, 'latestCache.db')
if os.path.exists(dirpath):
    os.remove(dirpath)

# Read start block no
startblock = int(config['DEFAULT']['START_BLOCK'])
session = create_database_session_orm('system_dbs', {'db_name': "system"}, SystemBase)
session.add(SystemData(attribute='lastblockscanned', value=startblock - 1))
session.commit()
session.close()

# Initialize latest cache DB
session = create_database_session_orm('system_dbs', {'db_name': "latestCache"}, LatestCacheBase)
session.commit()
session.close()

# get all blocks and transaction data 
latestCache_session = create_database_session_orm('system_dbs', {'db_name':'latestCache1'}, LatestCacheBase)
if forward_block:
    lblocks = latestCache_session.query(LatestBlocks).filter(LatestBlocks.blockNumber <= forward_block).all()
    ltransactions = latestCache_session.query(LatestTransactions).filter(LatestTransactions.blockNumber <= forward_block).all()
else:
    lblocks = latestCache_session.query(LatestBlocks).all()
    ltransactions = latestCache_session.query(LatestTransactions).all()
latestCache_session.close()

# make a list of all internal tx block numbers
systemDb_session = create_database_session_orm('system_dbs', {'db_name':'system1'}, SystemBase)
internal_action_blocks = systemDb_session.query(ActiveContracts.blockNumber).all()
internal_action_blocks = [block[0] for block in internal_action_blocks]
internal_action_blocks = sorted(internal_action_blocks)

lblocks_dict = {}
for block in lblocks:
    block_dict = block.__dict__
    print(block_dict['blockNumber'])
    lblocks_dict[block_dict['blockNumber']] = {'blockHash':f"{block_dict['blockHash']}", 'jsonData':f"{block_dict['jsonData']}"}

# process and rebuild all transactions 
prev_block = 0

for transaction in ltransactions:
    transaction_dict = transaction.__dict__
    current_block = transaction_dict['blockNumber']

    # Check if any internal action block lies between prev_block and current_block
    for internal_block in internal_action_blocks:

        if prev_block < internal_block <= current_block:
            logger.info(f'Processing block {internal_block}') 
            # Get block details 
            response = newMultiRequest(f"block-index/{internal_block}") 
            blockhash = response['blockHash'] 
            blockinfo = newMultiRequest(f"block/{blockhash}")
            # Call your function here, passing the internal block to it
            checkLocal_expiry_trigger_deposit(blockinfo)

    transaction_data = json.loads(transaction_dict['jsonData'])
    transaction_data = newMultiRequest(f"tx/{transaction_dict['transactionHash']}")
    parsed_flodata = json.loads(transaction_dict['parsedFloData'])
    try:
        block_info = json.loads(lblocks_dict[transaction_dict['blockNumber']]['jsonData'])
        processTransaction(transaction_data, parsed_flodata, block_info)
        prev_block = current_block
    except:
        prev_block = current_block
        continue

    # Check if the current block exceeds the specified "to_blockNumber"
    if current_block >= args.to_blockNumber:
        logger.info(f"Reached the specified block number {args.to_blockNumber}. Stopping processing.")
        break

# copy the old block data 
old_latest_cache = create_database_connection('system_dbs', {'db_name':'latestCache1'})
old_latest_cache.execute("ATTACH DATABASE 'latestCache.db' AS new_db")
old_latest_cache.execute("INSERT INTO new_db.latestBlocks SELECT * FROM latestBlocks WHERE blockNumber <= ?", (forward_block,))
old_latest_cache.close()

# delete 
# system.db , latestCache.db, smartContracts, tokens 
if os.path.isfile('./system1.db'):
    os.remove('system1.db')
if os.path.isfile('./latestCache1.db'):
    os.remove('latestCache1.db')
if os.path.isfile('./smartContracts1'):
    shutil.rmtree('smartContracts1')
if os.path.isfile('./tokens1'):
    shutil.rmtree('tokens1')

# Update system.db's last scanned block 
connection = create_database_connection('system_dbs', {'db_name': "system"})
connection.execute(f"UPDATE systemData SET value = {int(list(lblocks_dict.keys())[-1])} WHERE attribute = 'lastblockscanned';")
connection.close()