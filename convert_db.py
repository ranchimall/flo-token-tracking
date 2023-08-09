from models import SystemData, ActiveTable, ConsumedTable, TransferLogs, TransactionHistory, RejectedTransactionHistory, Base, ContractStructure, ContractBase, ContractParticipants, SystemBase, ActiveContracts, ContractAddressMapping, LatestCacheBase, ContractTransactionHistory, RejectedContractTransactionHistory, TokenContractAssociation, ContinuosContractBase, ContractStructure1, ContractParticipants1, ContractDeposits1, ContractTransactionHistory1, LatestTransactions, LatestBlocks, DatabaseTypeMapping, TokenAddressMapping, LatestCacheBase1, LatestTransactions1, LatestBlocks1
import pdb 
from sqlalchemy import create_engine, func 
from sqlalchemy.orm import sessionmaker 


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


# connect to the database convert_db 
convert_db = create_database_session_orm('system_dbs', {'db_name': 'convertdb'}, LatestCacheBase1)
latest_blocks = convert_db.query(LatestBlocks1).all()
latest_txs = convert_db.query(LatestTransactions1).all()


# create a new database convert_db_new
convert_db_1 = create_database_session_orm('system_dbs', {'db_name': 'latestCache'}, LatestCacheBase)

for block in latest_blocks:
    convert_db_1.add(LatestBlocks(blockNumber=block.blockNumber, blockHash=block.blockHash, jsonData=block.jsonData))

for tx in latest_txs:
    convert_db_1.add(LatestTransactions(transactionHash=tx.transactionHash, blockNumber=tx.blockNumber, jsonData=tx.jsonData, transactionType=tx.transactionType, parsedFloData=tx.parsedFloData))

convert_db_1.commit()
convert_db_1.close()
convert_db.close()
