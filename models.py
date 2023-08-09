from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

TokenBase = declarative_base()
ContractBase = declarative_base()
ContinuosContractBase = declarative_base()
SystemBase = declarative_base()
LatestCacheBase = declarative_base()


class ActiveTable(TokenBase):
    __tablename__ = "activeTable"

    id = Column('id', Integer, primary_key=True)
    address = Column('address', String)
    parentid = Column('parentid', Integer)
    consumedpid = Column('consumedpid', String)
    transferBalance = Column('transferBalance', Float)
    addressBalance = Column('addressBalance', Float)
    orphaned_parentid = Column('orphaned_parentid', Integer)
    blockNumber = Column('blockNumber', Integer)


class ConsumedTable(TokenBase):
    __tablename__ = "consumedTable"

    primaryKey = Column('primaryKey', Integer, primary_key=True)
    id = Column('id', Integer)
    address = Column('address', String)
    parentid = Column('parentid', Integer)
    consumedpid = Column('consumedpid', String)
    transferBalance = Column('transferBalance', Float)
    addressBalance = Column('addressBalance', Float)
    orphaned_parentid = Column('orphaned_parentid', Integer)
    blockNumber = Column('blockNumber', Integer)


class TransferLogs(TokenBase):
    __tablename__ = "transferlogs"

    primary_key = Column('id', Integer, primary_key=True)
    sourceFloAddress = Column('sourceFloAddress', String)
    destFloAddress = Column('destFloAddress', String)
    transferAmount = Column('transferAmount', Float)
    sourceId = Column('sourceId', Integer)
    destinationId = Column('destinationId', Integer)
    blockNumber = Column('blockNumber', Integer)
    time = Column('time', Integer)
    transactionHash = Column('transactionHash', String)


class TransactionHistory(TokenBase):
    __tablename__ = "transactionHistory"

    primary_key = Column('id', Integer, primary_key=True)
    sourceFloAddress = Column('sourceFloAddress', String)
    destFloAddress = Column('destFloAddress', String)
    transferAmount = Column('transferAmount', Float)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    time = Column('time', Integer)
    transactionHash = Column('transactionHash', String)
    blockchainReference = Column('blockchainReference', String)
    jsonData = Column('jsonData', String)
    transactionType = Column('transactionType', String)
    parsedFloData = Column('parsedFloData', String)


class TokenContractAssociation(TokenBase):
    __tablename__ = "tokenContractAssociation"

    primary_key = Column('id', Integer, primary_key=True)
    tokenIdentification = Column('tokenIdentification', String)
    contractName = Column('contractName', String)
    contractAddress = Column('contractAddress', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    time = Column('time', Integer)
    transactionHash = Column('transactionHash', String)
    blockchainReference = Column('blockchainReference', String)
    jsonData = Column('jsonData', String)
    transactionType = Column('transactionType', String)
    parsedFloData = Column('parsedFloData', String)


class ContractStructure(ContractBase):
    __tablename__ = "contractstructure"

    id = Column('id', Integer, primary_key=True)
    attribute = Column('attribute', String)
    index = Column('index', Integer)
    value = Column('value', String)


class ContractParticipants(ContractBase):
    __tablename__ = "contractparticipants"

    id = Column('id', Integer, primary_key=True)
    participantAddress = Column('participantAddress', String)
    tokenAmount = Column('tokenAmount', Float)
    userChoice = Column('userChoice', String)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    winningAmount = Column('winningAmount', Float)


class ContractTransactionHistory(ContractBase):
    __tablename__ = "contractTransactionHistory"

    primary_key = Column('id', Integer, primary_key=True)
    transactionType = Column('transactionType', String)
    transactionSubType = Column('transactionSubType', String)
    sourceFloAddress = Column('sourceFloAddress', String)
    destFloAddress = Column('destFloAddress', String)
    transferAmount = Column('transferAmount', Float)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    time = Column('time', Integer)
    transactionHash = Column('transactionHash', String)
    blockchainReference = Column('blockchainReference', String)
    jsonData = Column('jsonData', String)
    parsedFloData = Column('parsedFloData', String)


class ContractDeposits(ContractBase):
    __tablename__ = "contractdeposits"

    id = Column('id', Integer, primary_key=True)
    depositorAddress = Column('depositorAddress', String)
    depositAmount = Column('depositAmount', Float)
    depositBalance = Column('depositBalance', Float)
    expiryTime = Column('expiryTime', String)
    unix_expiryTime = Column('unix_expiryTime', Integer)
    status = Column('status', String)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)


class ConsumedInfo(ContractBase):
    __tablename__ = "consumedinfo"
    
    id = Column('id', Integer, primary_key=True)
    id_deposittable = Column('id_deposittable', Integer)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)


class ContractWinners(ContractBase):
    __tablename__ = "contractwinners"

    id = Column('id', Integer, primary_key=True)
    participantAddress = Column('participantAddress', String)
    winningAmount = Column('winningAmount', Float)
    userChoice = Column('userChoice', String)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)


class ContractStructure2(ContinuosContractBase):
    __tablename__ = "contractstructure"

    id = Column('id', Integer, primary_key=True)
    attribute = Column('attribute', String)
    index = Column('index', Integer)
    value = Column('value', String)


class ContractParticipants2(ContinuosContractBase):
    __tablename__ = "contractparticipants"

    id = Column('id', Integer, primary_key=True)
    participantAddress = Column('participantAddress', String)
    tokenAmount = Column('tokenAmount', Float)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)


class ContractDeposits2(ContinuosContractBase):
    __tablename__ = "contractdeposits"

    id = Column('id', Integer, primary_key=True)
    depositorAddress = Column('depositorAddress', String)
    depositAmount = Column('depositAmount', Float)
    expiryTime = Column('expiryTime', String)
    status = Column('status', String)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)


class ContractTransactionHistory2(ContinuosContractBase):
    __tablename__ = "contractTransactionHistory"

    primary_key = Column('id', Integer, primary_key=True)
    transactionType = Column('transactionType', String)
    transactionSubType = Column('transactionSubType', String)
    sourceFloAddress = Column('sourceFloAddress', String)
    destFloAddress = Column('destFloAddress', String)
    transferAmount = Column('transferAmount', Float)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    time = Column('time', Integer)
    transactionHash = Column('transactionHash', String)
    blockchainReference = Column('blockchainReference', String)
    jsonData = Column('jsonData', String)
    parsedFloData = Column('parsedFloData', String)


class ActiveContracts(SystemBase):
    __tablename__ = "activecontracts"

    id = Column('id', Integer, primary_key=True)
    contractName = Column('contractName', String)
    contractAddress = Column('contractAddress', String)
    status = Column('status', String)
    tokenIdentification = Column('tokenIdentification', String)
    contractType = Column('contractType', String)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    incorporationDate = Column('incorporationDate', String)
    expiryDate = Column('expiryDate', String)
    closeDate = Column('closeDate', String)


class SystemData(SystemBase):
    __tablename__ = "systemData"

    id = Column('id', Integer, primary_key=True)
    attribute = Column('attribute', String)
    value = Column('value', String)


class ContractAddressMapping(SystemBase):
    __tablename__ = "contractAddressMapping"

    id = Column('id', Integer, primary_key=True)
    address = Column('address', String)
    addressType = Column('addressType', String)
    contractName = Column('contractName', String)
    contractAddress = Column('contractAddress', String)
    tokenAmount = Column('tokenAmount', Float)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)


class TokenAddressMapping(SystemBase):
    __tablename__ = "tokenAddressMapping"

    id = Column('id', Integer, primary_key=True)
    tokenAddress = Column('tokenAddress', String)
    token = Column('token', String)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)


class DatabaseTypeMapping(SystemBase):
    __tablename__ = "databaseTypeMapping"

    id = Column('id', Integer, primary_key=True)
    db_name = Column('db_name', String)
    db_type = Column('db_type', String)
    keyword = Column('keyword', String)
    object_format = Column ('object_format', String)
    blockNumber = Column('blockNumber', Integer)


class TimeActions(SystemBase):
    __tablename__ = "time_actions"

    id = Column('id', Integer, primary_key=True)
    time = Column('time', String)
    activity = Column('activity', String)
    status = Column('status', String)
    contractName = Column('contractName', String)
    contractAddress = Column('contractAddress', String)
    contractType = Column('contractType', String)
    tokens_db = Column('tokens_db', String)
    parsed_data = Column('parsed_data', String)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)


class RejectedContractTransactionHistory(SystemBase):
    __tablename__ = "rejectedContractTransactionHistory"

    primary_key = Column('id', Integer, primary_key=True)
    transactionType = Column('transactionType', String)
    transactionSubType = Column('transactionSubType', String)
    contractName = Column('contractName', String)
    contractAddress = Column('contractAddress', String)
    sourceFloAddress = Column('sourceFloAddress', String)
    destFloAddress = Column('destFloAddress', String)
    transferAmount = Column('transferAmount', Float)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    time = Column('time', Integer)
    transactionHash = Column('transactionHash', String)
    blockchainReference = Column('blockchainReference', String)
    jsonData = Column('jsonData', String)
    rejectComment = Column('rejectComment', String)
    parsedFloData = Column('parsedFloData', String)


class RejectedTransactionHistory(SystemBase):
    __tablename__ = "rejectedTransactionHistory"

    primary_key = Column('id', Integer, primary_key=True)
    tokenIdentification = Column('tokenIdentification', String)
    sourceFloAddress = Column('sourceFloAddress', String)
    destFloAddress = Column('destFloAddress', String)
    transferAmount = Column('transferAmount', Float)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    time = Column('time', Integer)
    transactionHash = Column('transactionHash', String)
    blockchainReference = Column('blockchainReference', String)
    jsonData = Column('jsonData', String)
    rejectComment = Column('rejectComment', String)
    transactionType = Column('transactionType', String)
    parsedFloData = Column('parsedFloData', String)


class LatestTransactions(LatestCacheBase):
    __tablename__ = "latestTransactions"
    
    id = Column('id', Integer, primary_key=True)
    transactionHash = Column('transactionHash', String)
    blockNumber = Column('blockNumber', Integer)
    jsonData = Column('jsonData', String)
    transactionType = Column('transactionType', String)
    parsedFloData = Column('parsedFloData', String)
    db_reference = Column('db_reference', String)


class LatestBlocks(LatestCacheBase):
    __tablename__ = "latestBlocks"

    id = Column('id', Integer, primary_key=True)
    blockNumber = Column('blockNumber', Integer)
    blockHash = Column('blockHash', String)
    jsonData = Column('jsonData', String)
