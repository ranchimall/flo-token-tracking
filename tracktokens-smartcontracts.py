import requests
import json
import sqlite3
import argparse
import configparser
import subprocess
import sys
import parsing
import time
import os
import shutil
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, func, desc
from models import SystemData, ActiveTable, ConsumedTable, TransferLogs, TransactionHistory, RejectedTransactionHistory, Base, ContractStructure, ContractBase, ContractParticipants, SystemBase, ActiveContracts, ContractAddressMapping, LatestTransactions, LatestCacheBase, LatestBlocks, ContractTransactionHistory, RejectedContractTransactionHistory
from config import *
import pybtc
import socketio

# Setup logging
import logging
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


def retryRequest(tempserverlist, apicall):
    if len(tempserverlist)!=0:
        try:
            response = requests.get('{}api/{}'.format(tempserverlist[0], apicall))
        except:
            tempserverlist.pop(0)
            return retryRequest(tempserverlist, apicall)
        else:
            if response.status_code == 200:
                return json.loads(response.content)
            else:
                tempserverlist.pop(0)
                return retryRequest(tempserverlist, apicall)
    else:
        logger.error("None of the APIs are responding for the call {}".format(apicall))
        sys.exit(0)


def multiRequest(apicall, net):
    testserverlist = ['http://0.0.0.0:9000/','https://testnet.flocha.in/', 'https://testnet-flosight.duckdns.org/']
    mainserverlist = ['http://0.0.0.0:9001/', 'https://livenet.flocha.in/', 'https://testnet-flosight.duckdns.org/']
    if net == 'mainnet':
        return retryRequest(mainserverlist, apicall)
    elif net == 'testnet':
        return retryRequest(testserverlist, apicall)


def pushData_SSEapi(message):
    signature = pybtc.sign_message(message.encode(), privKey)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Signature': signature}
    try:
        r = requests.post(sseAPI_url, json={'message': '{}'.format(message)}, headers=headers)
    except:
        logger.error("couldn't push the following message to SSE api {}".format(message))


def processBlock(blockindex):
    logger.info(f"Processing block {blockindex}")
    # Scan every block
    response = multiRequest(f"block-index/{blockindex}", config['DEFAULT']['NET'])
    blockhash = response['blockHash']
    blockinfo = multiRequest(f"block/{blockhash}", config['DEFAULT']['NET'])

    # todo Rule 8 - read every transaction from every block to find and parse flodata

    # Scan every transaction
    for transaction in blockinfo["tx"]:
        transaction_data = multiRequest(f"tx/{transaction}", config['DEFAULT']['NET'])
        text = transaction_data["floData"]
        text = text.replace("\n", " \n ")

        # todo Rule 9 - Reject all noise transactions. Further rules are in parsing.py

        parsed_data = parsing.parse_flodata(text, blockinfo, config['DEFAULT']['NET'])
        if parsed_data['type'] != 'noise':
            logger.info(f"Processing transaction {transaction}")
            logger.debug(f"flodata {text} is parsed to {parsed_data}")
            returnval = processTransaction(transaction_data, parsed_data)
            if returnval != 0:
                updateLatestBlock(blockinfo)
            else:
                logger.debug("Transfer for the transaction %s is illegitimate. Moving on" % transaction)

    engine = create_engine('sqlite:///system.db')
    SystemBase.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    entry = session.query(SystemData).filter(SystemData.attribute == 'lastblockscanned').all()[0]
    entry.value = str(blockindex)
    session.commit()
    session.close()

    # Check smartContracts which will be triggered locally, and not by the contract committee
    checkLocaltriggerContracts(blockinfo)


def processApiBlock(blockhash):

    blockinfo = multiRequest('block/{}'.format(str(blockhash)), config['DEFAULT']['NET'])

    # todo Rule 8 - read every transaction from every block to find and parse flodata

    # Scan every transaction
    for transaction in blockinfo["tx"]:

        transaction_data = multiRequest('tx/{}'.format(str(transaction)), config['DEFAULT']['NET'])
        text = transaction_data["floData"]
        text = text.replace("\n", " \n ")

        # todo Rule 9 - Reject all noise transactions. Further rules are in parsing.py

        parsed_data = parsing.parse_flodata(text, blockinfo, config['DEFAULT']['NET'])
        if parsed_data['type'] != 'noise':
            print(blockindex)
            print(parsed_data['type'])
            processTransaction(transaction_data, parsed_data)

    engine = create_engine('sqlite:///system.db')
    SystemBase.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    entry = session.query(SystemData).filter(SystemData.attribute == 'lastblockscanned').all()[0]
    entry.value = str(blockindex)
    session.commit()
    session.close()

    # Check smartContracts which will be triggered locally, and not by the contract committee
    checkLocaltriggerContracts(blockinfo)


def updateLatestTransaction(transactionData, parsed_data):
    # connect to latest transaction db
    conn = sqlite3.connect('latestCache.db')
    conn.execute("INSERT INTO latestTransactions(transactionHash, blockNumber, jsonData, transactionType, parsedFloData) VALUES (?,?,?,?,?)", (transactionData['txid'], transactionData['blockheight'], json.dumps(transactionData), parsed_data['type'], json.dumps(parsed_data)))
    conn.commit()
    conn.close()


def updateLatestBlock(blockData):
    # connect to latest block db
    conn = sqlite3.connect('latestCache.db')
    conn.execute('INSERT INTO latestBlocks(blockNumber, blockHash, jsonData) VALUES (?,?,?)',(blockData['height'], blockData['hash'], json.dumps(blockData)))
    conn.commit()
    conn.close()


def transferToken(tokenIdentification, tokenAmount, inputAddress, outputAddress, transaction_data=None):
    engine = create_engine('sqlite:///tokens/{}.db'.format(tokenIdentification), echo=True)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    availableTokens = session.query(func.sum(ActiveTable.transferBalance)).filter_by(address=inputAddress).all()[0][0]
    commentTransferAmount = float(tokenAmount)
    if availableTokens is None:
        logger.info(f"The sender address {inputAddress} doesn't own any {tokenIdentification.upper()} tokens")
        session.close()
        return 0

    elif availableTokens < commentTransferAmount:
        logger.info("The transfer amount passed in the comments is more than the user owns\nThis transaction will be discarded\n")
        session.close()
        return 0

    elif availableTokens >= commentTransferAmount:
        table = session.query(ActiveTable).filter(ActiveTable.address==inputAddress).all()
        block_data = multiRequest('block/{}'.format(transaction_data['blockhash']), config['DEFAULT']['NET'])

        pidlst = []
        checksum = 0
        for row in table:
            if checksum >= commentTransferAmount:
                break
            pidlst.append([row.id, row.transferBalance])
            checksum = checksum + row.transferBalance

        if checksum == commentTransferAmount:
            consumedpid_string = ''

            # Update all pids in pidlist's transferBalance to 0
            lastid = session.query(ActiveTable)[-1].id
            for piditem in pidlst:
                entry = session.query(ActiveTable).filter(ActiveTable.id == piditem[0]).all()
                consumedpid_string = consumedpid_string + '{},'.format(piditem[0])
                session.add(TransferLogs(sourceFloAddress=inputAddress, destFloAddress=outputAddress,
                                         transferAmount=entry[0].transferBalance, sourceId=piditem[0], destinationId=lastid+1,
                                         blockNumber=block_data['height'], time=block_data['time'],
                                         transactionHash=transaction_data['txid']))
                entry[0].transferBalance = 0

            if len(consumedpid_string)>1:
                consumedpid_string = consumedpid_string[:-1]

            # Make new entry
            session.add(ActiveTable(address=outputAddress, consumedpid=consumedpid_string,
                                    transferBalance=commentTransferAmount))

            # Migration
            # shift pid of used utxos from active to consumed
            for piditem in pidlst:
                # move the parentids consumed to consumedpid column in both activeTable and consumedTable
                entries = session.query(ActiveTable).filter(ActiveTable.parentid == piditem[0]).all()
                for entry in entries:
                    entry.consumedpid = entry.consumedpid + ',{}'.format(piditem[0])
                    entry.parentid = None

                entries = session.query(ConsumedTable).filter(ConsumedTable.parentid == piditem[0]).all()
                for entry in entries:
                    entry.consumedpid = entry.consumedpid + ',{}'.format(piditem[0])
                    entry.parentid = None

                # move the pids consumed in the transaction to consumedTable and delete them from activeTable
                session.execute(
                    'INSERT INTO consumedTable (id, address, parentid, consumedpid, transferBalance) SELECT id, address, parentid, consumedpid, transferBalance FROM activeTable WHERE id={}'.format(
                        piditem[0]))
                session.execute('DELETE FROM activeTable WHERE id={}'.format(piditem[0]))
                session.commit()
            session.commit()

        if checksum > commentTransferAmount:
            consumedpid_string = ''
            # Update all pids in pidlist's transferBalance
            lastid = session.query(ActiveTable)[-1].id
            for idx, piditem in enumerate(pidlst):
                entry = session.query(ActiveTable).filter(ActiveTable.id == piditem[0]).all()
                if idx != len(pidlst) - 1:
                    session.add(TransferLogs(sourceFloAddress=inputAddress, destFloAddress=outputAddress,
                                             transferAmount=entry[0].transferBalance, sourceId=piditem[0],
                                             destinationId=lastid + 1,
                                             blockNumber=block_data['height'], time=block_data['time'],
                                             transactionHash=transaction_data['txid']))
                    entry[0].transferBalance = 0
                    consumedpid_string = consumedpid_string + '{},'.format(piditem[0])
                else:
                    session.add(TransferLogs(sourceFloAddress=inputAddress, destFloAddress=outputAddress,
                                             transferAmount=piditem[1]-(checksum - commentTransferAmount), sourceId=piditem[0],
                                             destinationId=lastid + 1,
                                             blockNumber=block_data['height'], time=block_data['time'],
                                             transactionHash=transaction_data['txid']))
                    entry[0].transferBalance = checksum - commentTransferAmount


            if len(consumedpid_string) > 1:
                consumedpid_string = consumedpid_string[:-1]

            # Make new entry
            session.add(ActiveTable(address=outputAddress, parentid= pidlst[-1][0], consumedpid=consumedpid_string,
                                    transferBalance=commentTransferAmount))

            # Migration
            # shift pid of used utxos from active to consumed
            for piditem in pidlst[:-1]:
                # move the parentids consumed to consumedpid column in both activeTable and consumedTable
                entries = session.query(ActiveTable).filter(ActiveTable.parentid == piditem[0]).all()
                for entry in entries:
                    entry.consumedpid = entry.consumedpid + ',{}'.format(piditem[0])
                    entry.parentid = None

                entries = session.query(ConsumedTable).filter(ConsumedTable.parentid == piditem[0]).all()
                for entry in entries:
                    entry.consumedpid = entry.consumedpid + ',{}'.format(piditem[0])
                    entry.parentid = None

                # move the pids consumed in the transaction to consumedTable and delete them from activeTable
                session.execute(
                    'INSERT INTO consumedTable (id, address, parentid, consumedpid, transferBalance) SELECT id, address, parentid, consumedpid, transferBalance FROM activeTable WHERE id={}'.format(
                        piditem[0]))
                session.execute('DELETE FROM activeTable WHERE id={}'.format(piditem[0]))
                session.commit()
            session.commit()


        block_data = multiRequest('block/{}'.format(transaction_data['blockhash']), config['DEFAULT']['NET'])

        blockchainReference = neturl + 'tx/' + transaction_data['txid']
        session.add(TransactionHistory(sourceFloAddress=inputAddress, destFloAddress=outputAddress,
                                 transferAmount=tokenAmount, blockNumber=block_data['height'], blockHash=block_data['hash'], time=block_data['time'],
                                 transactionHash=transaction_data['txid'], blockchainReference=blockchainReference, jsonData=json.dumps(transaction_data)))
        session.commit()
        session.close()
        return 1


def checkLocaltriggerContracts(blockinfo):
    engine = create_engine('sqlite:///system.db', echo=False)
    connection = engine.connect()
    # todo : filter activeContracts which only have local triggers
    activeContracts = connection.execute('select contractName, contractAddress from activecontracts where status=="active" ').fetchall()
    connection.close()

    for contract in activeContracts:
        # Check if the contract has blockchain trigger or committee trigger
        engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(contract[0],contract[1]), echo=False)
        connection = engine.connect()
        # todo : filter activeContracts which only have local triggers
        contractStructure = connection.execute('select * from contractstructure').fetchall()
        contractStructure_T = list(zip(*contractStructure))

        if 'exitconditions' in list(contractStructure_T[1]):
            # This is a committee trigger contract
            expiryTime = connection.execute('select value from contractstructure where attribute=="expiryTime"').fetchall()[0][0]
            expirytime_split = expiryTime.split(' ')
            parse_string = '{}/{}/{} {}'.format(expirytime_split[3], parsing.months[expirytime_split[1]],
                                                expirytime_split[2], expirytime_split[4])
            expirytime_object = parsing.arrow.get(parse_string, 'YYYY/M/D HH:mm:ss').replace(tzinfo=expirytime_split[5][3:])
            blocktime_object = parsing.arrow.get(blockinfo['time']).to('Asia/Kolkata')

            if blocktime_object > expirytime_object:
                if 'minimumsubscriptionamount' in list(contractStructure_T[1]):
                    minimumsubscriptionamount = connection.execute('select value from contractstructure where attribute=="minimumsubscriptionamount"').fetchall()[0][0]
                    tokenAmount_sum = connection.execute('select sum(tokenAmount) from contractparticipants').fetchall()[0][0]
                    if tokenAmount_sum < minimumsubscriptionamount:
                        # Initialize payback to contract participants
                        contractParticipants = connection.execute('select participantAddress, tokenAmount, transactionHash from contractparticipants').fetchall()[0][0]

                        for participant in contractParticipants:
                            tokenIdentification = connection.execute('select * from contractstructure where attribute="tokenIdentification"').fetchall()[0][0]
                            contractAddress = connection.execute('select * from contractstructure where attribute="contractAddress"').fetchall()[0][0]
                            returnval = transferToken(tokenIdentification, participant[1], contractAddress, participant[0])
                            if returnval is None:
                                logger.critical("Something went wrong in the token transfer method while doing local Smart Contract Trigger. THIS IS CRITICAL ERROR")
                                return
                            connection.execute(
                                'update contractparticipants set winningAmount="{}" where participantAddress="{}" and transactionHash="{}"'.format(
                                    (participant[1], participant[0], participant[2])))
                        engine = create_engine('sqlite:///system.db', echo=True)
                        connection = engine.connect()
                        connection.execute(
                            'update activecontracts set status="closed" where contractName="{}" and contractAddress="{}"'.format(contract[0], contract[1]))
                        connection.execute(
                            'update activecontracts set closeDate="{}" where contractName="{}" and contractAddress="{}"'.format(blockinfo['time'],
                                contract[0], contract[1]))
                        connection.close()

                engine = create_engine('sqlite:///system.db', echo=True)
                connection = engine.connect()
                connection.execute(
                    'update activecontracts set status="expired" where contractName="{}" and contractAddress="{}"'.format(
                        contract[0], contract[1]))
                connection.execute(
                    'update activecontracts set expirydate="{}" where contractName="{}" and contractAddress="{}"'.format(blockinfo['time'],
                        contract[0], contract[1]))
                connection.close()


        else:
            # This is a blockchain trigger contract
            if 'maximumsubscriptionamount' in list(contractStructure_T[1]):
                maximumsubscriptionamount = connection.execute('select value from contractstructure where attribute=="maximumsubscriptionamount"').fetchall()[0][0]
                tokenAmount_sum = connection.execute('select sum(tokenAmount) from contractparticipants').fetchall()[0][0]
                if tokenAmount_sum >= maximumsubscriptionamount:
                    # Trigger the contract
                    payeeAddress = connection.execute('select * from contractstructure where attribute="payeeAddress"').fetchall()[0][0]
                    tokenIdentification = connection.execute('select * from contractstructure where attribute="tokenIdentification"').fetchall()[0][0]
                    contractAddress = connection.execute('select * from contractstructure where attribute="contractAddress"').fetchall()[0][0]
                    returnval = transferToken(tokenIdentification, tokenAmount_sum, contractAddress, payeeAddress)
                    if returnval is None:
                        logger.critical("Something went wrong in the token transfer method while doing local Smart Contract Trigger")
                        return
                    connection.execute(
                        'update contractparticipants set winningAmount="{}"'.format(
                            (0)))
                    engine = create_engine('sqlite:///system.db', echo=False)
                    connection = engine.connect()
                    connection.execute(
                        'update activecontracts set status="closed" where contractName="{}" and contractAddress="{}"'.format(contract[0], contract[1]))
                    connection.execute(
                        'update activecontracts set closeDate="{}" where contractName="{}" and contractAddress="{}"'.format(
                            blockinfo['time'], contract[0], contract[1]))
                    connection.close()

            expiryTime = connection.execute('select value from contractstructure where attribute=="expiryTime"').fetchall()[0][0]
            expirytime_split = expiryTime.split(' ')
            parse_string = '{}/{}/{} {}'.format(expirytime_split[3], parsing.months[expirytime_split[1]], expirytime_split[2], expirytime_split[4])
            expirytime_object = parsing.arrow.get(parse_string, 'YYYY/M/D HH:mm:ss').replace(
                tzinfo=expirytime_split[5][3:])
            blocktime_object = parsing.arrow.get(blockinfo['time']).to('Asia/Kolkata')

            if blocktime_object > expirytime_object:
                if 'minimumsubscriptionamount' in list(contractStructure_T[1]):
                    minimumsubscriptionamount = connection.execute('select value from contractstructure where attribute=="minimumsubscriptionamount"').fetchall()[0][0]
                    tokenAmount_sum = connection.execute('select sum(tokenAmount) from contractparticipants').fetchall()[0][0]
                    if tokenAmount_sum < minimumsubscriptionamount:
                        # Initialize payback to contract participants
                        contractParticipants = connection.execute(
                            'select participantAddress, tokenAmount, transactionHash from contractparticipants').fetchall()[0][0]

                        for participant in contractParticipants:
                            tokenIdentification = connection.execute(
                                'select * from contractstructure where attribute="tokenIdentification"').fetchall()[0][
                                0]
                            contractAddress = connection.execute(
                                'select * from contractstructure where attribute="contractAddress"').fetchall()[0][0]
                            returnval = transferToken(tokenIdentification, participant[1], contractAddress,
                                                      participant[0])
                            if returnval is None:
                                logger.critical(
                                    "Something went wrong in the token transfer method while doing local Smart Contract Trigger")
                                return
                            connection.execute('update contractparticipants set winningAmount="{}" where participantAddress="{}" and transactionHash="{}"'.format((participant[1], participant[0], participant[2])))
                        engine = create_engine('sqlite:///system.db', echo=False)
                        connection = engine.connect()
                        connection.execute(
                            'update activecontracts set status="closed" where contractName="{}" and contractAddress="{}"'.format(
                                contract[0], contract[1]))
                        connection.execute(
                            'update activecontracts set closeDate="{}" where contractName="{}" and contractAddress="{}"'.format(
                                blockinfo['time'],contract[0], contract[1]))
                        connection.close()

                # Trigger the contract
                payeeAddress = connection.execute('select * from contractstructure where attribute="payeeAddress"').fetchall()[0][0]
                tokenIdentification = connection.execute('select * from contractstructure where attribute="tokenIdentification"').fetchall()[0][0]
                contractAddress = connection.execute('select * from contractstructure where attribute="contractAddress"').fetchall()[0][0]
                returnval = transferToken(tokenIdentification, tokenAmount_sum, contractAddress, payeeAddress)
                if returnval is None:
                    logger.critical("Something went wrong in the token transfer method while doing local Smart Contract Trigger")
                    return
                connection.execute('update contractparticipants set winningAmount="{}"'.format(0))
                engine = create_engine('sqlite:///system.db', echo=False)
                connection = engine.connect()
                connection.execute(
                    'update activecontracts set status="closed" where contractName="{}" and contractAddress="{}"'.format(
                        contract[0], contract[1]))
                connection.execute(
                    'update activecontracts set closeDate="{}" where contractName="{}" and contractAddress="{}"'.format(
                        blockinfo['time'], contract[0], contract[1]))
                connection.close()


def processTransaction(transaction_data, parsed_data):

    # Do the necessary checks for the inputs and outputs

    # todo Rule 38 - Here we are doing FLO processing. We attach asset amounts to a FLO address, so every FLO address
    #        will have multiple feed ins of the asset. Each of those feedins will be an input to the address.
    #        an address can also spend the asset. Each of those spends is an output of that address feeding the asset into some
    #        other address an as input

    # Rule 38 reframe - For checking any asset transfer on the flo blockchain it is possible that some transactions may use more than one
    # vins. However in any single transaction the system considers valid, they can be only one source address from which the flodata is
    # originting. To ensure consistency, we will have to check that even if there are more than one vins in a transaction, there should be
    # excatly one FLO address on the originating side and that FLO address should be the owner of the asset tokens being transferred

    # Create vinlist and outputlist
    vinlist = []
    querylist = []

    # todo Rule 39 - Create a list of vins for a given transaction id
    for obj in transaction_data["vin"]:
        querylist.append([obj["txid"], obj["vout"]])

    totalinputval = 0
    inputadd = ''

    # todo Rule 40 - For each vin, find the feeding address and the fed value. Make an inputlist containing [inputaddress, n value]
    for query in querylist:
        content = multiRequest('tx/{}'.format(str(query[0])), config['DEFAULT']['NET'])
        for objec in content["vout"]:
            if objec["n"] == query[1]:
                inputadd = objec["scriptPubKey"]["addresses"][0]
                totalinputval = totalinputval + float(objec["value"])
                vinlist.append([inputadd, objec["value"]])

    # todo Rule 41 - Check if all the addresses in a transaction on the input side are the same
    for idx, item in enumerate(vinlist):
        if idx == 0:
            temp = item[0]
            continue
        if item[0] != temp:
            logger.info(f"System has found more than one address as part of vin. Transaction {transaction_data['txid']} is rejected")
            return 0

    inputlist = [vinlist[0][0], totalinputval]


    # todo Rule 42 - If the number of vout is more than 2, reject the transaction
    if len(transaction_data["vout"]) > 2:
        logger.info(f"System has found more than 2 address as part of vout. Transaction {transaction_data['txid']} is rejected")
        return 0

    # todo Rule 43 - A transaction accepted by the system has two vouts, 1. The FLO address of the receiver
    #      2. Flo address of the sender as change address.  If the vout address is change address, then the other adddress
    #     is the recevier address

    outputlist = []
    for obj in transaction_data["vout"]:
        if obj["scriptPubKey"]["type"] == "pubkeyhash":
            if inputlist[0] == obj["scriptPubKey"]["addresses"][0]:
                continue
            outputlist.append([obj["scriptPubKey"]["addresses"][0], obj["value"]])

    if len(outputlist) != 1:
        logger.info(
            f"Transaction's change is not coming back to the input address. Transaction {transaction_data['txid']} is rejected")
        return 0

    outputlist = outputlist[0]

    logger.debug(
        f"Input address list : {inputlist}")
    logger.debug(
        f"Output address list : {outputlist}")

    # All FLO checks completed at this point.
    # Semantic rules for parsed data begins

    # todo Rule 44 - Process as per the type of transaction
    if parsed_data['type'] == 'transfer':
        logger.debug(f"Transaction {transaction_data['txid']} is of the type transfer")

        # todo Rule 45 - If the transfer type is token, then call the function transferToken to adjust the balances
        if parsed_data['transferType'] == 'token':
            # check if the token exists in the database
            if os.path.isfile(f"./tokens/{parsed_data['tokenIdentification']}.db"):
                # Check if the transaction hash already exists in the token db
                engine = create_engine(f"sqlite:///tokens/{parsed_data['tokenIdentification']}.db", echo=True)
                connection = engine.connect()
                blockno_txhash = connection.execute('select blockNumber, transactionHash from transactionHistory').fetchall()
                connection.close()
                blockno_txhash_T = list(zip(*blockno_txhash))

                if transaction_data['txid'] in list(blockno_txhash_T[1]):
                    logger.warning(f"Transaction {transaction_data['txid']} already exists in the token db. This is unusual, please check your code")
                    pushData_SSEapi(f"Error | Transaction {transaction_data['txid']} already exists in the token db. This is unusual, please check your code")
                    return 0

                returnval = transferToken(parsed_data['tokenIdentification'], parsed_data['tokenAmount'], inputlist[0], outputlist[0], transaction_data)
                if returnval is None:
                    logger.info("Something went wrong in the token transfer method")
                    pushData_SSEapi(f"Error | Something went wrong while doing the internal db transactions for {transaction_data['txid']}")
                    return 0
                else:
                    updateLatestTransaction(transaction_data, parsed_data, transaction_data['blockheight'])

                # If this is the first interaction of the outputlist's address with the given token name, add it to token mapping
                engine = create_engine('sqlite:///system.db', echo=True)
                connection = engine.connect()
                firstInteractionCheck = connection.execute(f"select * from tokenAddressMapping where tokenAddress='{outputlist[0]}' and token='{parsed_data['tokenIdentification']}'").fetchall()

                if len(firstInteractionCheck) == 0:
                    connection.execute(f"INSERT INTO tokenAddressMapping (tokenAddress, token, transactionHash, blockNumber, blockHash) VALUES ('{outputlist[0]}', '{parsed_data['tokenIdentification']}', '{transaction_data['txid']}', '{transaction_data['blockheight']}', '{transaction_data['blockhash']}')")

                connection.close()


                # Pass information to SSE channel
                url = 'https://ranchimallflo.duckdns.org/'
                headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
                r = requests.post(url, json={f"message': 'Token Transfer | name:{parsed_data['tokenIdentification']} | transactionHash:{transaction_data['txid']}"}, headers=headers)
            else:
                logger.info(
                    f"Token transfer at transaction {transaction_data['txid']} rejected as a token with the name {parsed_data['tokenIdentification']} doesnt not exist")
                engine = create_engine(f"sqlite:///tokens/{parsed_data['tokenIdentification']}.db", echo=True)
                Base.metadata.create_all(bind=engine)
                session = sessionmaker(bind=engine)()
                blockchainReference = neturl + 'tx/' + transaction_data['txid']
                session.add(RejectedTransactionHistory(sourceFloAddress=inputadd, destFloAddress=outputlist[0],
                                                       transferAmount=parsed_data['tokenAmount'],
                                                       blockNumber=transaction_data['blockheight'],
                                                       blockHash=transaction_data['blockhash'],
                                                       time=transaction_data['blocktime'],
                                                       transactionHash=transaction_data['txid'],
                                                       blockchainReference=blockchainReference,
                                                       jsonData=json.dumps(transaction_data),
                                                       rejectComment=f"Token transfer at transaction {transaction_data['txid']} rejected as a token with the name {parsed_data['tokenIdentification']} doesnt not exist"))
                session.commit()
                session.close()
                pushData_SSEapi(
                    f"Error | Token transfer at transaction {transaction_data['txid']} rejected as a token with the name {parsed_data['tokenIdentification']} doesnt not exist")
                return 0

        # todo Rule 46 - If the transfer type is smart contract, then call the function transferToken to do sanity checks & lock the balance
        elif parsed_data['transferType'] == 'smartContract':
            if os.path.isfile(f"./smartContracts/{parsed_data['contractName']}-{parsed_data['contractAddress']}.db"):
                # Check if the transaction hash already exists in the contract db (Safety check)
                engine = create_engine(
                    'sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]), echo=True)
                connection = engine.connect()
                participantAdd_txhash = connection.execute(
                    'select participantAddress, transactionHash from contractparticipants').fetchall()
                participantAdd_txhash_T = list(zip(*participantAdd_txhash))

                if len(participantAdd_txhash) != 0 and transaction_data['txid'] in list(participantAdd_txhash_T[1]):
                    logger.warning(
                        f"Transaction {transaction_data['txid']} rejected as it already exists in the Smart Contract db. This is unusual, please check your code")
                    pushData_SSEapi(
                        f"Error | Transaction {transaction_data['txid']} rejected as it already exists in the Smart Contract db. This is unusual, please check your code" )
                    return 0

                #if contractAddress was passed check if it matches the output address of this contract
                if 'contractAddress' in parsed_data:
                    if parsed_data['contractAddress'] != outputlist[0]:
                        logger.info(
                            f"Contract participation at transaction {transaction_data['txid']} rejected as contractAddress specified in flodata, {parsed_data['contractAddress']}, doesnt not match with transaction's output address {outputlist[0]}")
                        # Store transfer as part of RejectedContractTransactionHistory
                        engine = create_engine(
                            f"sqlite:///smartContracts/{parsed_data['contractName']}-{parsed_data['contractAddress']}.db",
                            echo=True)
                        ContractBase.metadata.create_all(bind=engine)
                        session = sessionmaker(bind=engine)()
                        blockchainReference = neturl + 'tx/' + transaction_data['txid']
                        session.add(
                            RejectedContractTransactionHistory(transactionType='participation',
                                                               sourceFloAddress=inputadd,
                                                               destFloAddress=outputlist[0],
                                                               transferAmount=None,
                                                               blockNumber=transaction_data['blockheight'],
                                                               blockHash=transaction_data['blockhash'],
                                                               time=transaction_data['blocktime'],
                                                               transactionHash=transaction_data['txid'],
                                                               blockchainReference=blockchainReference,
                                                               jsonData=json.dumps(transaction_data),
                                                               rejectComment=f"Contract participation at transaction {transaction_data['txid']} rejected as contractAddress specified in flodata, {parsed_data['contractAddress']}, doesnt not match with transaction's output address {outputlist[0]}"))
                        session.commit()
                        session.close()

                        url = 'https://ranchimallflo.duckdns.org/'
                        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
                        r = requests.post(url, json={
                            'message': f"Error | Contract participation at transaction {transaction_data['txid']} rejected as contractAddress specified in flodata, {parsed_data['contractAddress']}, doesnt not match with transaction's output address {outputlist[0]}"},
                                          headers=headers)
                        return 0

                        # Pass information to SSE channel
                        pushData_SSEapi('Error| Mismatch in contract address specified in flodata and the output address of the transaction {}'.format(transaction_data['txid']))
                        return 0


                # check the status of the contract
                engine = create_engine('sqlite:///system.db', echo=True)
                connection = engine.connect()
                contractStatus = connection.execute(
                    f"select status from activecontracts where contractName=='{parsed_data['contractName']}' and contractAddress='{outputlist[0]}'").fetchall()[0][0]
                connection.close()
                contractList = []

                if contractStatus == 'closed':
                    logger.info(f"Transaction {parsed_data['txid']} closed as Smart contract {parsed_data['contractName']} at the {outputlist[0]} is closed")
                    # Store transfer as part of RejectedContractTransactionHistory
                    engine = create_engine(
                        f"sqlite:///smartContracts/{parsed_data['contractName']}-{outputlist[0]}.db",
                        echo=True)
                    ContractBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    blockchainReference = neturl + 'tx/' + transaction_data['txid']
                    session.add(
                        RejectedContractTransactionHistory(transactionType='participation',
                                                           sourceFloAddress=inputadd,
                                                           destFloAddress=outputlist[0],
                                                           transferAmount=None,
                                                           blockNumber=transaction_data['blockheight'],
                                                           blockHash=transaction_data['blockhash'],
                                                           time=transaction_data['blocktime'],
                                                           transactionHash=transaction_data['txid'],
                                                           blockchainReference=blockchainReference,
                                                           jsonData=json.dumps(transaction_data),
                                                           rejectComment=f"Transaction {parsed_data['txid']} closed as Smart contract {parsed_data['contractName']} at the {outputlist[0]} is closed"))
                    session.commit()
                    session.close()

                    url = 'https://ranchimallflo.duckdns.org/'
                    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
                    r = requests.post(url, json={
                        'message': f"Error | Transaction {parsed_data['txid']} closed as Smart contract {parsed_data['contractName']} at the {outputlist[0]} is closed"},
                                      headers=headers)
                    return 0

                else:
                    engine = create_engine(
                        'sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]),
                        echo=True)
                    ContractBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    result = session.query(ContractStructure).filter_by(attribute='expiryTime').all()
                    session.close()
                    if result:
                        # now parse the expiry time in python
                        expirytime = result[0].value.strip()
                        expirytime_split = expirytime.split(' ')
                        parse_string = '{}/{}/{} {}'.format(expirytime_split[3], parsing.months[expirytime_split[1]],
                                                            expirytime_split[2], expirytime_split[4])
                        expirytime_object = parsing.arrow.get(parse_string, 'YYYY/M/D HH:mm:ss').replace(
                            tzinfo=expirytime_split[5][3:])
                        blocktime_object = parsing.arrow.get(transaction_data['blocktime']).to('Asia/Kolkata')

                        if blocktime_object > expirytime_object:
                            logger.info(
                                f"Transaction {parsed_data['txid']} rejected as Smart contract {parsed_data['contractName']}-{outputlist[0]} has expired and will not accept any user participation")
                            # Store transfer as part of RejectedContractTransactionHistory
                            engine = create_engine(
                                f"sqlite:///smartContracts/{parsed_data['contractName']}-{outputlist[0]}.db",
                                echo=True)
                            ContractBase.metadata.create_all(bind=engine)
                            session = sessionmaker(bind=engine)()
                            blockchainReference = neturl + 'tx/' + transaction_data['txid']
                            session.add(
                                RejectedContractTransactionHistory(transactionType='participation',
                                                                   sourceFloAddress=inputadd,
                                                                   destFloAddress=outputlist[0],
                                                                   transferAmount=None,
                                                                   blockNumber=transaction_data['blockheight'],
                                                                   blockHash=transaction_data['blockhash'],
                                                                   time=transaction_data['blocktime'],
                                                                   transactionHash=transaction_data['txid'],
                                                                   blockchainReference=blockchainReference,
                                                                   jsonData=json.dumps(transaction_data),
                                                                   rejectComment=f"Transaction {parsed_data['txid']} rejected as Smart contract {parsed_data['contractName']}-{outputlist[0]} has expired and will not accept any user participation"))
                            session.commit()
                            session.close()
                            pushData_SSEapi(
                                f"Error| Transaction {parsed_data['txid']} rejected as Smart contract {parsed_data['contractName']}-{outputlist[0]} has expired and will not accept any user participation"
                            return 0


                # Check if contractAmount is part of the contract structure, and enforce it if it is
                engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]), echo=True)
                connection = engine.connect()
                contractAmount = connection.execute(
                    'select value from contractstructure where attribute=="contractAmount"').fetchall()
                connection.close()

                if len(contractAmount) != 0:
                    if float(contractAmount[0][0]) != float(parsed_data['tokenAmount']):
                        logger.info(
                            f"Transaction {parsed_data['txid']} rejected as contractAmount being transferred is not part of the structure of Smart Contract named {parsed_data['contractName']} at the address {outputlist[0]}")
                        # Store transfer as part of RejectedContractTransactionHistory
                        engine = create_engine(
                            f"sqlite:///smartContracts/{parsed_data['contractName']}-{outputlist[0]}.db",
                            echo=True)
                        ContractBase.metadata.create_all(bind=engine)
                        session = sessionmaker(bind=engine)()
                        blockchainReference = neturl + 'tx/' + transaction_data['txid']
                        session.add(
                            RejectedContractTransactionHistory(transactionType='participation',
                                                               sourceFloAddress=inputadd,
                                                               destFloAddress=outputlist[0],
                                                               transferAmount=None,
                                                               blockNumber=transaction_data['blockheight'],
                                                               blockHash=transaction_data['blockhash'],
                                                               time=transaction_data['blocktime'],
                                                               transactionHash=transaction_data['txid'],
                                                               blockchainReference=blockchainReference,
                                                               jsonData=json.dumps(transaction_data),
                                                               rejectComment=f"Transaction {parsed_data['txid']} rejected as contractAmount being transferred is not part of the structure of Smart Contract named {parsed_data['contractName']} at the address {outputlist[0]}"))
                        session.commit()
                        session.close()
                        pushData_SSEapi(
                            f"Error| Transaction {parsed_data['txid']} rejected as contractAmount being transferred is not part of the structure of Smart Contract named {parsed_data['contractName']} at the address {outputlist[0]}")
                        return 0


                # Check if exitcondition exists as part of contractstructure and is given in right format
                engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]), echo=True)
                connection = engine.connect()

                contractAttributes = connection.execute('select attribute, value from contractstructure').fetchall()
                contractAttributes_T = list(zip(*contractAttributes))

                if 'exitconditions' in contractAttributes_T[0]:
                    exitconditions = connection.execute('select id,value from contractstructure where attribute=="exitconditions"').fetchall()
                    exitconditions_T = list(zip(*exitconditions))
                    if parsed_data['userChoice'] not in list(exitconditions_T[1]):
                        logger.info(f"Transaction {parsed_data['txid']} rejected as wrong userchoice entered for the Smart Contract named {parsed_data['contractName']} at the address {outputlist[0]}")
                        # Store transfer as part of RejectedContractTransactionHistory
                        engine = create_engine(
                            f"sqlite:///smartContracts/{parsed_data['contractName']}-{outputlist[0]}.db",
                            echo=True)
                        ContractBase.metadata.create_all(bind=engine)
                        session = sessionmaker(bind=engine)()
                        blockchainReference = neturl + 'tx/' + transaction_data['txid']
                        session.add(
                            RejectedContractTransactionHistory(transactionType='participation',
                                                               sourceFloAddress=inputadd,
                                                               destFloAddress=outputlist[0],
                                                               transferAmount=None,
                                                               blockNumber=transaction_data['blockheight'],
                                                               blockHash=transaction_data['blockhash'],
                                                               time=transaction_data['blocktime'],
                                                               transactionHash=transaction_data['txid'],
                                                               blockchainReference=blockchainReference,
                                                               jsonData=json.dumps(transaction_data),
                                                               rejectComment=f"Transaction {parsed_data['txid']} rejected as wrong userchoice entered for the Smart Contract named {parsed_data['contractName']} at the address {outputlist[0]}"))
                        session.commit()
                        session.close()
                        pushData_SSEapi(f"Error| Transaction {parsed_data['txid']} rejected as wrong userchoice entered for the Smart Contract named {parsed_data['contractName']} at the address {outputlist[0]}")
                        return 0


                # Check if maximum subscription amount has reached
                engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]), echo=True)
                ContractBase.metadata.create_all(bind=engine)
                session = sessionmaker(bind=engine)()
                result = session.query(ContractStructure).filter_by(attribute='maximumsubscriptionamount').all()
                if result:
                    # now parse the expiry time in python
                    maximumsubscriptionamount = float(result[0].value.strip())
                    amountDeposited = session.query(func.sum(ContractParticipants.tokenAmount)).all()[0][0]

                    if amountDeposited is None:
                        amountDeposited = 0

                    if amountDeposited >= maximumsubscriptionamount:
                        logger.info("Maximum subscription amount reached\n Money will be refunded")
                        pushData_SSEapi('Error | Maximum subscription amount reached for contract {}-{} at transaction {}. Token will not be transferred'.format(parsed_data['contractName'], outputlist[0],
                                transaction_data['txid']))
                        return 0
                    else:
                        if parsed_data['tokenAmount'] + amountDeposited <= maximumsubscriptionamount:
                            # Check if the tokenAmount being transferred exists in the address & do the token transfer
                            returnval = transferToken(parsed_data['tokenIdentification'], parsed_data['tokenAmount'], inputlist[0], outputlist[0], transaction_data)
                            if returnval is not None:
                                # Store participant details in the smart contract's db
                                session.add(ContractParticipants(participantAddress=inputadd, tokenAmount=parsed_data['tokenAmount'], userChoice=parsed_data['userChoice'], transactionHash=transaction_data['txid'], blockNumber=transaction_data['blockheight'], blockHash=transaction_data['blockhash']))
                                session.commit()

                                # Store transfer as part of ContractTransactionHistory
                                blockchainReference = neturl + 'tx/' + transaction_data['txid']
                                session.add(ContractTransactionHistory(transactionType='participation', sourceFloAddress=inputadd, destFloAddress=outputlist[0],
                                                               transferAmount=parsed_data['tokenAmount'],
                                                               blockNumber=transaction_data['blockheight'],
                                                               blockHash=transaction_data['blockhash'],
                                                               time=transaction_data['blocktime'],
                                                               transactionHash=transaction_data['txid'],
                                                               blockchainReference=blockchainReference,
                                                               jsonData=json.dumps(transaction_data)))

                                session.commit()
                                session.close()

                                # Store a mapping of participant address -> Contract participated in
                                engine = create_engine('sqlite:///system.db', echo=True)
                                SystemBase.metadata.create_all(bind=engine)
                                session = sessionmaker(bind=engine)()
                                session.add(ContractAddressMapping(address=inputadd, addressType='participant', tokenAmount=parsed_data['tokenAmount'],
                                                                 contractName = parsed_data['contractName'], contractAddress = outputlist[0], transactionHash=transaction_data['txid'], blockNumber=transaction_data['blockheight'], blockHash=transaction_data['blockhash']))
                                session.commit()

                                updateLatestTransaction(transaction_data, parsed_data)
                                return

                            else:
                                logger.info("Something went wrong in the smartcontract token transfer method")
                                return 0
                        else:
                            # Transfer only part of the tokens users specified, till the time it reaches maximumamount
                            returnval = transferToken(parsed_data['tokenIdentification'], maximumsubscriptionamount-amountDeposited,
                                                      inputlist[0], outputlist[0], transaction_data)
                            if returnval is not None:
                                # Store participant details in the smart contract's db
                                session.add(ContractParticipants(participantAddress=inputadd,
                                                                 tokenAmount=maximumsubscriptionamount-amountDeposited,
                                                                 userChoice=parsed_data['userChoice'], transactionHash=transaction_data['txid'], blockNumber=transaction_data['blockheight'],
                                                               blockHash=transaction_data['blockhash']))
                                session.commit()
                                session.close()

                                # Store a mapping of participant address -> Contract participated in
                                engine = create_engine('sqlite:///system.db', echo=True)
                                SystemBase.metadata.create_all(bind=engine)
                                session = sessionmaker(bind=engine)()
                                session.add(ContractAddressMapping(address=inputadd, addressType='participant',
                                                                       tokenAmount=maximumsubscriptionamount-amountDeposited,
                                                                       contractName=parsed_data['contractName'], contractAddress = outputlist[0], transactionHash=transaction_data['txid'], blockNumber=transaction_data['blockheight'], blockHash=transaction_data['blockhash']))
                                session.commit()
                                session.close()
                                updateLatestTransaction(transaction_data, parsed_data)
                                return

                            else:
                                logger.info("Something went wrong in the smartcontract token transfer method")
                                return 0

                ###############################
                # Check if the tokenAmount being transferred exists in the address & do the token transfer
                returnval = transferToken(parsed_data['tokenIdentification'], parsed_data['tokenAmount'],
                                          inputlist[0], outputlist[0], transaction_data)
                if returnval is not None:
                    # Store participant details in the smart contract's db
                    session.add(ContractParticipants(participantAddress=inputadd,
                                                     tokenAmount=parsed_data['tokenAmount'],
                                                     userChoice=parsed_data['userChoice'], transactionHash=transaction_data['txid'], blockNumber=transaction_data['blockheight'],
                                                     blockHash=transaction_data['blockhash']))
                    session.commit()
                    # Store transfer as part of ContractTransactionHistory
                    blockchainReference = neturl + 'tx/' + transaction_data['txid']
                    session.add(ContractTransactionHistory(transactionType='participation', sourceFloAddress=inputadd, destFloAddress=outputlist[0],
                                                               transferAmount=parsed_data['tokenAmount'],
                                                               blockNumber=transaction_data['blockheight'],
                                                               blockHash=transaction_data['blockhash'],
                                                               time=transaction_data['blocktime'],
                                                               transactionHash=transaction_data['txid'],
                                                               blockchainReference=blockchainReference,
                                                               jsonData=json.dumps(transaction_data)))
                    session.commit()
                    session.close()

                    # Store a mapping of participant address -> Contract participated in
                    engine = create_engine('sqlite:///system.db', echo=True)
                    SystemBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    session.add(ContractAddressMapping(address=inputadd, addressType='participant',
                                                           tokenAmount=parsed_data['tokenAmount'],
                                                           contractName=parsed_data['contractName'],
                                                           contractAddress=outputlist[0], transactionHash=transaction_data['txid'], blockNumber=transaction_data['blockheight'], blockHash=transaction_data['blockhash']))
                    session.commit()
                    session.close()

                    updateLatestTransaction(transaction_data, parsed_data)

                    pushData_SSEapi('Participation | Succesfully participated in the contract {}-{} at transaction {}'.format(
                            parsed_data['contractName'], outputlist[0],
                            transaction_data['txid']))

                return
            else:
                logger.info(
                    f"Transaction {transaction_data['txid']} rejected as a Smart Contract with the name {parsed_data['contractName']} at address {parsed_data['contractAddress']} doesnt exist")
                # Store transfer as part of RejectedContractTransactionHistory
                engine = create_engine(
                    f"sqlite:///smartContracts/{parsed_data['contractName']}-{parsed_data['contractAddress']}.db",
                    echo=True)
                ContractBase.metadata.create_all(bind=engine)
                session = sessionmaker(bind=engine)()
                blockchainReference = neturl + 'tx/' + transaction_data['txid']
                session.add(
                    RejectedContractTransactionHistory(transactionType='participation', sourceFloAddress=inputadd,
                                                       destFloAddress=outputlist[0],
                                                       transferAmount=None,
                                                       blockNumber=transaction_data['blockheight'],
                                                       blockHash=transaction_data['blockhash'],
                                                       time=transaction_data['blocktime'],
                                                       transactionHash=transaction_data['txid'],
                                                       blockchainReference=blockchainReference,
                                                       jsonData=json.dumps(transaction_data),
                                                       rejectComment=f"Transaction {transaction_data['txid']} rejected as a Smart Contract with the name {parsed_data['contractName']} at address {parsed_data['contractAddress']} doesnt exist"))
                session.commit()
                session.close()

                url = 'https://ranchimallflo.duckdns.org/'
                headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
                r = requests.post(url, json={
                    'message': f"Error | Contract transaction {transaction_data['txid']} rejected as a smartcontract with same name {parsed_data['contractName']}-{parsed_data['contractAddress']} dosent exist "},
                                  headers=headers)
                return 0

    # todo Rule 47 - If the parsed data type is token incorporation, then check if the name hasn't been taken already
    #  if it has been taken then reject the incorporation. Else incorporate it
    elif parsed_data['type'] == 'tokenIncorporation':
        if not os.path.isfile(f"./tokens/{parsed_data['tokenIdentification']}.db"):
            engine = create_engine(f"sqlite:///tokens/{parsed_data['tokenIdentification']}.db", echo=True)
            Base.metadata.create_all(bind=engine)
            session = sessionmaker(bind=engine)()
            session.add(ActiveTable(address=inputlist[0], parentid=0, transferBalance=parsed_data['tokenAmount']))
            session.add(TransferLogs(sourceFloAddress=inputadd, destFloAddress=outputlist[0], transferAmount=parsed_data['tokenAmount'], sourceId=0, destinationId=1, blockNumber=transaction_data['blockheight'], time=transaction_data['blocktime'], transactionHash=transaction_data['txid']))
            blockchainReference = neturl + 'tx/' + transaction_data['txid']
            session.add(TransactionHistory(sourceFloAddress=inputadd, destFloAddress=outputlist[0],
                                           transferAmount=parsed_data['tokenAmount'], blockNumber=transaction_data['blockheight'], blockHash=transaction_data['blockhash'],
                                           time=transaction_data['blocktime'],
                                           transactionHash=transaction_data['txid'],
                                           blockchainReference=blockchainReference, jsonData=json.dumps(transaction_data)))
            session.commit()
            session.close()

            # add it to token address to token mapping db table
            engine = create_engine('sqlite:///system.db'.format(parsed_data['tokenIdentification']), echo=True)
            connection = engine.connect()
            connection.execute(
                    f"INSERT INTO tokenAddressMapping (tokenAddress, token, transactionHash, blockNumber, blockHash) VALUES ('{inputadd}', '{parsed_data['tokenIdentification']}', '{transaction_data['txid']}', '{transaction_data['blockheight']}', '{transaction_data['blockhash']}');")
            connection.close()

            updateLatestTransaction(transaction_data, parsed_data)

            pushData_SSEapi(f"Token | Succesfully incorporated token {parsed_data['tokenIdentification']} at transaction {transaction_data['txid']}")
        else:
            logger.info(f"Transaction {transaction_data['txid']} rejected as a token with the name {parsed_data['tokenIdentification']} has already been incorporated")
            engine = create_engine(f"sqlite:///tokens/{parsed_data['tokenIdentification']}.db", echo=True)
            Base.metadata.create_all(bind=engine)
            session = sessionmaker(bind=engine)()
            blockchainReference = neturl + 'tx/' + transaction_data['txid']
            session.add(RejectedTransactionHistory(sourceFloAddress=inputadd, destFloAddress=outputlist[0],
                                           transferAmount=parsed_data['tokenAmount'],
                                           blockNumber=transaction_data['blockheight'],
                                           blockHash=transaction_data['blockhash'],
                                           time=transaction_data['blocktime'],
                                           transactionHash=transaction_data['txid'],
                                           blockchainReference=blockchainReference,
                                           jsonData=json.dumps(transaction_data),
                                           rejectComment=f"Transaction {transaction_data['txid']} rejected as a token with the name {parsed_data['tokenIdentification']} has already been incorporated"))
            session.commit()
            session.close()
            pushData_SSEapi(f"Error | Token incorporation rejected at transaction {transaction_data['txid']} as token {parsed_data['tokenIdentification']} already exists")
            return 0

    # todo Rule 48 - If the parsed data type if smart contract incorporation, then check if the name hasn't been taken already
    #      if it has been taken then reject the incorporation.
    elif parsed_data['type'] == 'smartContractIncorporation':
        if not os.path.isfile(f"./smartContracts/{parsed_data['contractName']}-{parsed_data['contractAddress']}.db"):
            # todo Rule 49 - If the contract name hasn't been taken before, check if the contract type is an authorized type by the system
            if parsed_data['contractType'] == 'one-time-event':
                logger.debug("Smart contract is of the type one-time-event")

                # either userchoice or payeeAddress condition should be present. Check for it
                if 'userchoices' not in parsed_data['contractConditions'] and 'payeeAddress' not in parsed_data['contractConditions']:
                    logger.info(
                        f"Either userchoice or payeeAddress should be part of the Contract conditions.\nSmart contract incorporation on transaction {transaction_data['txid']} rejected")
                    # Store transfer as part of RejectedContractTransactionHistory
                    engine = create_engine(
                        f"sqlite:///smartContracts/{parsed_data['contractName']}-{parsed_data['contractAddress']}.db",
                        echo=True)
                    ContractBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    blockchainReference = neturl + 'tx/' + transaction_data['txid']
                    session.add(
                        RejectedContractTransactionHistory(transactionType='incorporation', sourceFloAddress=inputadd,
                                                           destFloAddress=outputlist[0],
                                                           transferAmount=None,
                                                           blockNumber=transaction_data['blockheight'],
                                                           blockHash=transaction_data['blockhash'],
                                                           time=transaction_data['blocktime'],
                                                           transactionHash=transaction_data['txid'],
                                                           blockchainReference=blockchainReference,
                                                           jsonData=json.dumps(transaction_data),
                                                           rejectComment=f"Either userchoice or payeeAddress should be part of the Contract conditions.\nSmart contract incorporation on transaction {transaction_data['txid']} rejected"))
                    session.commit()
                    session.close()
                    return 0

                # userchoice and payeeAddress conditions cannot come together. Check for it
                if 'userchoices' in parsed_data['contractConditions'] and 'payeeAddress' in parsed_data['contractConditions']:
                    logger.info(f"Both userchoice and payeeAddress provided as part of the Contract conditions.\nSmart contract incorporation on transaction {transaction_data['txid']} rejected")
                    # Store transfer as part of RejectedContractTransactionHistory
                    engine = create_engine(
                        f"sqlite:///smartContracts/{parsed_data['contractName']}-{parsed_data['contractAddress']}.db",
                        echo=True)
                    ContractBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    blockchainReference = neturl + 'tx/' + transaction_data['txid']
                    session.add(
                        RejectedContractTransactionHistory(transactionType='incorporation', sourceFloAddress=inputadd,
                                                           destFloAddress=outputlist[0],
                                                           transferAmount=None,
                                                           blockNumber=transaction_data['blockheight'],
                                                           blockHash=transaction_data['blockhash'],
                                                           time=transaction_data['blocktime'],
                                                           transactionHash=transaction_data['txid'],
                                                           blockchainReference=blockchainReference,
                                                           jsonData=json.dumps(transaction_data),
                                                           rejectComment=f"Both userchoice and payeeAddress provided as part of the Contract conditions.\nSmart contract incorporation on transaction {transaction_data['txid']} rejected"))
                    session.commit()
                    session.close()
                    return 0

                # todo Rule 50 - Contract address mentioned in flodata field should be same as the receiver FLO address on the output side
                #    henceforth we will not consider any flo private key initiated comment as valid from this address
                #    Unlocking can only be done through smart contract system address
                if parsed_data['contractAddress'] == inputadd:
                    dbName = '{}-{}'.format(parsed_data['contractName'], parsed_data['contractAddress'])
                    engine = create_engine('sqlite:///smartContracts/{}.db'.format(dbName), echo=True)
                    ContractBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    session.add(ContractStructure(attribute='contractType', index=0, value=parsed_data['contractType']))
                    session.add(ContractStructure(attribute='contractName', index=0, value=parsed_data['contractName']))
                    session.add(
                        ContractStructure(attribute='tokenIdentification', index=0, value=parsed_data['tokenIdentification']))
                    session.add(
                        ContractStructure(attribute='contractAddress', index=0, value=parsed_data['contractAddress']))
                    session.add(
                        ContractStructure(attribute='flodata', index=0,
                                          value=parsed_data['flodata']))
                    session.add(
                        ContractStructure(attribute='expiryTime', index=0,
                                          value=parsed_data['contractConditions']['expiryTime']))
                    if 'contractAmount' in parsed_data['contractConditions']:
                        session.add(
                            ContractStructure(attribute='contractAmount', index=0,
                                              value=parsed_data['contractConditions']['contractAmount']))

                    if 'minimumsubscriptionamount' in parsed_data['contractConditions']:
                        session.add(
                        ContractStructure(attribute='minimumsubscriptionamount', index=0,
                                          value=parsed_data['contractConditions']['minimumsubscriptionamount']))
                    if 'maximumsubscriptionamount' in parsed_data['contractConditions']:
                        session.add(
                        ContractStructure(attribute='maximumsubscriptionamount', index=0,
                                          value=parsed_data['contractConditions']['maximumsubscriptionamount']))
                    if 'userchoices' in parsed_data['contractConditions']:
                        for key, value in parsed_data['contractConditions']['userchoices'].items():
                            session.add(ContractStructure(attribute='exitconditions', index=key, value=value))

                    if 'payeeAddress' in parsed_data['contractConditions']:
                        # in this case, expirydate( or maximumamount) is the trigger internally. Keep a track of expiry dates
                        session.add(
                            ContractStructure(attribute='payeeAddress', index=0,
                                              value=parsed_data['contractConditions']['payeeAddress']))

                    session.commit()


                    # Store transfer as part of ContractTransactionHistory
                    blockchainReference = neturl + 'tx/' + transaction_data['txid']
                    session.add(ContractTransactionHistory(transactionType='incorporation', sourceFloAddress=inputadd,
                                                destFloAddress=outputlist[0],
                                                transferAmount=None,
                                                blockNumber=transaction_data['blockheight'],
                                                blockHash=transaction_data['blockhash'],
                                                time=transaction_data['blocktime'],
                                                transactionHash=transaction_data['txid'],
                                                blockchainReference=blockchainReference,
                                                jsonData=json.dumps(transaction_data)))
                    session.commit()
                    session.close()

                    # Store smart contract address in system's db, to be ignored during future transfers
                    engine = create_engine('sqlite:///system.db', echo=True)
                    SystemBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    session.add(ActiveContracts(contractName=parsed_data['contractName'],
                                                contractAddress=parsed_data['contractAddress'], status='active', tokenIdentification=parsed_data['tokenIdentification'], contractType=parsed_data['contractType'], transactionHash=transaction_data['txid'], blockNumber=transaction_data['blockheight'], blockHash=transaction_data['blockhash'], incorporationDate=transaction_data['blocktime']))
                    session.commit()

                    session.add(ContractAddressMapping(address=inputadd, addressType='incorporation',
                                                       tokenAmount=None,
                                                       contractName=parsed_data['contractName'],
                                                       contractAddress=inputadd,
                                                       transactionHash=transaction_data['txid'],
                                                       blockNumber=transaction_data['blockheight'], blockHash=transaction_data['blockhash']))
                    session.commit()

                    session.close()

                    updateLatestTransaction(transaction_data, parsed_data)

                    pushData_SSEapi('Contract | Contract incorporated at transaction {} with name {}-{}'.format(
                            transaction_data['txid'], parsed_data['contractName'], parsed_data['contractAddress']))
                else:
                    logger.info(f"Contract Incorporation on transaction {transaction_data['txid']} rejected as contract address in Flodata and input address are different")
                    # Store transfer as part of RejectedContractTransactionHistory
                    engine = create_engine(
                        f"sqlite:///smartContracts/{parsed_data['contractName']}-{parsed_data['contractAddress']}.db",
                        echo=True)
                    ContractBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    blockchainReference = neturl + 'tx/' + transaction_data['txid']
                    session.add(
                        RejectedContractTransactionHistory(transactionType='incorporation', sourceFloAddress=inputadd,
                                                           destFloAddress=outputlist[0],
                                                           transferAmount=None,
                                                           blockNumber=transaction_data['blockheight'],
                                                           blockHash=transaction_data['blockhash'],
                                                           time=transaction_data['blocktime'],
                                                           transactionHash=transaction_data['txid'],
                                                           blockchainReference=blockchainReference,
                                                           jsonData=json.dumps(transaction_data),
                                                           rejectComment=f"Contract Incorporation on transaction {transaction_data['txid']} rejected as contract address in flodata and input address are different"))
                    session.commit()
                    session.close()
                    pushData_SSEapi('Error | Contract Incorporation rejected as address in Flodata and input address are different at transaction {}'.format(
                            transaction_data['txid']))
                    return 0
        else:
            logger.info(f"Transaction {transaction_data['txid']} rejected as a Smart Contract with the name {parsed_data['contractName']} at address {parsed_data['contractAddress']} already exists")
            # Store transfer as part of RejectedContractTransactionHistory
            engine = create_engine(f"sqlite:///smartContracts/{parsed_data['contractName']}-{parsed_data['contractAddress']}.db", echo=True)
            ContractBase.metadata.create_all(bind=engine)
            session = sessionmaker(bind=engine)()
            blockchainReference = neturl + 'tx/' + transaction_data['txid']
            session.add(RejectedContractTransactionHistory(transactionType='incorporation', sourceFloAddress=inputadd,
                                                   destFloAddress=outputlist[0],
                                                   transferAmount=None,
                                                   blockNumber=transaction_data['blockheight'],
                                                   blockHash=transaction_data['blockhash'],
                                                   time=transaction_data['blocktime'],
                                                   transactionHash=transaction_data['txid'],
                                                   blockchainReference=blockchainReference,
                                                   jsonData=json.dumps(transaction_data),
                                                   rejectComment=f"Transaction {transaction_data['txid']} rejected as a Smart Contract with the name {parsed_data['contractName']} at address {parsed_data['contractAddress']} already exists"))
            session.commit()
            session.close()

            url = 'https://ranchimallflo.duckdns.org/'
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            r = requests.post(url, json={
                'message': 'Error | Contract Incorporation rejected as a smartcontract with same name {}-{} is active currentlyt at transaction {}'.format(parsed_data['contractName'], parsed_data['contractAddress'], transaction_data['txid'])}, headers=headers)
            return 0

    elif parsed_data['type'] == 'smartContractPays':
        logger.debug('Found a transaction of the type smartContractPays')

        # Check if input address is a committee address
        if inputlist[0] in committeeAddressList:

            # Check if the output address is an active Smart contract address
            engine = create_engine('sqlite:///system.db', echo=True)
            connection = engine.connect()
            # todo : Get only activeContracts which have non-local trigger ie. committee triggers them

            contractDetails = connection.execute('select contractName, contractAddress from activecontracts where status=="expired"').fetchall()
            connection.close()
            contractList = []

            counter = 0
            for contract in contractDetails:
                if contract[0] == parsed_data['contractName'] and contract[1] == outputlist[0]:
                    counter = counter + 1

            if counter != 1:
                logger.info('Active Smart contract with the given name doesn\'t exist\n This committee trigger will be rejected')
                return 0

            # Check if the contract has maximumsubscriptionamount and if it has reached it
            engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]), echo=True)
            connection = engine.connect()
            ContractBase.metadata.create_all(bind=engine)
            session = sessionmaker(bind=engine)()
            # todo : filter activeContracts which only have local triggers
            contractStructure = connection.execute('select * from contractstructure').fetchall()
            contractStructure_T = list(zip(*contractStructure))

            if 'maximumsubscriptionamount' in list(contractStructure_T[1]):
                maximumsubscriptionamount = connection.execute('select value from contractstructure where attribute=="maximumsubscriptionamount"').fetchall()[0][0]
                tokenAmount_sum = connection.execute('select sum(tokenAmount) from contractparticipants').fetchall()[0][0]
                if tokenAmount_sum >= maximumsubscriptionamount:
                    # Trigger the contract
                    contractWinners = connection.execute(
                        'select * from contractparticipants where userChoice="{}"'.format(
                            parsed_data['triggerCondition'])).fetchall()
                    tokenSum = connection.execute('select sum(tokenAmount) from contractparticipants').fetchall()[0][0]
                    winnerSum = connection.execute(
                        'select sum(tokenAmount) from contractparticipants where userChoice="{}"'.format(
                            parsed_data['triggerCondition'])).fetchall()[0][0]
                    tokenIdentification = connection.execute(
                        'select value from contractstructure where attribute="tokenIdentification"').fetchall()[0][0]

                    for winner in contractWinners:
                        winnerAmount = "%.8f" % ((winner[2] / winnerSum) * tokenSum)
                        returnval = transferToken(tokenIdentification, winnerAmount,
                                                  outputlist[0], winner[1], transaction_data)
                        if returnval is None:
                            logger.critical("Something went wrong in the token transfer method while doing local Smart Contract Trigger")
                            return 0
                        connection.execute(
                            'update contractparticipants set winningAmount="{}" where participantAddress="{}" and transactionHash="{}"'.format(
                                (winnerAmount, winner[1], winner[4])))


                    # add transaction to ContractTransactionHistory
                    blockchainReference = neturl + 'tx/' + transaction_data['txid']
                    session.add(ContractTransactionHistory(transactionType='trigger', sourceFloAddress=inputadd,
                                                           destFloAddress=outputlist[0],
                                                           transferAmount=None,
                                                           blockNumber=transaction_data['blockheight'],
                                                           blockHash=transaction_data['blockhash'],
                                                           time=transaction_data['blocktime'],
                                                           transactionHash=transaction_data['txid'],
                                                           blockchainReference=blockchainReference,
                                                           jsonData=json.dumps(transaction_data)))

                    engine = create_engine('sqlite:///system.db', echo=True)
                    connection = engine.connect()
                    connection.execute(
                        'update activecontracts set status="closed" where contractName="{}" and contractAddress="{}"'.format(parsed_data['contractName'], outputlist[0]))
                    connection.execute(
                        'update activecontracts set closeDate="{}" where contractName="{}" and contractAddress="{}"'.format(transaction_data['blocktime'],
                            parsed_data['contractName'], outputlist[0]))
                    connection.close()

                    updateLatestTransaction(transaction_data, parsed_data)

                    pushData_SSEapi('Trigger | Contract triggered of the name {}-{} is active currently at transaction {}'.format(parsed_data['contractName'], outputlist[0], transaction_data['txid']))
                    return


            # Check if contract has passed expiry time
            expiryTime = connection.execute('select value from contractstructure where attribute=="expiryTime"').fetchall()[0][0]
            expirytime_split = expiryTime.split(' ')
            parse_string = '{}/{}/{} {}'.format(expirytime_split[3], parsing.months[expirytime_split[1]],
                                                expirytime_split[2], expirytime_split[4])
            expirytime_object = parsing.arrow.get(parse_string, 'YYYY/M/D HH:mm:ss').replace(
                tzinfo=expirytime_split[5][3:])
            blocktime_object = parsing.arrow.get(transaction_data['blocktime']).to('Asia/Kolkata')
            connection.close()

            if blocktime_object > expirytime_object:
                # Check if the minimum subscription amount has been reached if it exists as part of the structure
                engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]), echo=True)
                ContractBase.metadata.create_all(bind=engine)
                session = sessionmaker(bind=engine)()
                result = session.query(ContractStructure).filter_by(attribute='minimumsubscriptionamount').all()
                session.close()
                if result:
                    minimumsubscriptionamount = float(result[0].value.strip())
                    engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]),
                                           echo=True)
                    ContractBase.metadata.create_all(bind=engine)
                    session = sessionmaker(bind=engine)()
                    result = session.query(ContractStructure).filter_by(attribute='minimumsubscriptionamount').all()
                    amountDeposited = session.query(func.sum(ContractParticipants.tokenAmount)).all()[0][0]
                    session.close()

                    if amountDeposited is None:
                        amountDeposited = 0

                    if amountDeposited < minimumsubscriptionamount:
                        logger.info('Minimum subscription amount hasn\'t been reached\n The token will be returned back')
                        # Initialize payback to contract participants
                        engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]),
                                               echo=True)
                        connection = engine.connect()
                        contractParticipants = connection.execute(
                            'select participantAddress, tokenAmount, transactionHash from contractparticipants').fetchall()[0][0]

                        for participant in contractParticipants:
                            tokenIdentification = connection.execute(
                                'select * from contractstructure where attribute="tokenIdentification"').fetchall()[0][
                                0]
                            contractAddress = connection.execute(
                                'select * from contractstructure where attribute="contractAddress"').fetchall()[0][0]
                            returnval = transferToken(tokenIdentification, participant[1], contractAddress,
                                                      participant[0], transaction_data)
                            if returnval is None:
                                logger.info(
                                    "CRITICAL ERROR | Something went wrong in the token transfer method while doing local Smart Contract Trigger")
                                return 0

                            connection.execute(
                                'update contractparticipants set winningAmount="{}" where participantAddress="{}" and transactionHash="{}"'.format(
                                    (participant[1], participant[0], participant[4])))


                        # add transaction to ContractTransactionHistory
                        blockchainReference = neturl + 'tx/' + transaction_data['txid']
                        session.add(ContractTransactionHistory(transactionType='trigger', sourceFloAddress=inputadd,
                                                               destFloAddress=outputlist[0],
                                                               transferAmount=None,
                                                               blockNumber=transaction_data['blockheight'],
                                                               blockHash=transaction_data['blockhash'],
                                                               time=transaction_data['blocktime'],
                                                               transactionHash=transaction_data['txid'],
                                                               blockchainReference=blockchainReference,
                                                               jsonData=json.dumps(transaction_data)))

                        engine = create_engine('sqlite:///system.db', echo=True)
                        connection = engine.connect()
                        connection.execute(
                            'update activecontracts set status="closed" where contractName="{}" and contractAddress="{}"'.format(
                                parsed_data['contractName'], outputlist[0]))
                        connection.execute(
                            'update activecontracts set status="{}" where contractName="{}" and contractAddress="{}"'.format(transaction_data['blocktime'],
                                parsed_data['contractName'], outputlist[0]))
                        connection.close()

                        pushData_SSEapi('Trigger | Minimum subscription amount not reached at contract {}-{} at transaction {}. Tokens will be refunded'.format(
                                parsed_data['contractName'], outputlist[0], transaction_data['txid']))
                        return

                engine = create_engine('sqlite:///smartContracts/{}-{}.db'.format(parsed_data['contractName'], outputlist[0]), echo=True)
                connection = engine.connect()
                contractWinners = connection.execute('select * from contractparticipants where userChoice="{}"'.format(parsed_data['triggerCondition'])).fetchall()
                tokenSum = connection.execute('select sum(tokenAmount) from contractparticipants').fetchall()[0][0]
                winnerSum = connection.execute('select sum(tokenAmount) from contractparticipants where userChoice="{}"'.format(parsed_data['triggerCondition'])).fetchall()[0][0]
                tokenIdentification = connection.execute('select value from contractstructure where attribute="tokenIdentification"').fetchall()[0][0]

                for winner in contractWinners:
                    winner = list(winner)
                    winnerAmount = "%.8f" % ((winner[2]/winnerSum)*tokenSum)
                    returnval = transferToken(tokenIdentification, winnerAmount, outputlist[0], winner[1], transaction_data)
                    if returnval is None:
                        logger.info(
                            "CRITICAL ERROR | Something went wrong in the token transfer method while doing local Smart Contract Trigger")
                        return 0
                    connection.execute('update contractparticipants set winningAmount="{}" where participantAddress="{}" and transactionHash="{}"'.format(winnerAmount, winner[1], winner[4]))
                connection.close()

                # add transaction to ContractTransactionHistory
                blockchainReference = neturl + 'tx/' + transaction_data['txid']
                session.add(ContractTransactionHistory(transactionType='trigger', sourceFloAddress=inputadd,
                                                       destFloAddress=outputlist[0],
                                                       transferAmount=None,
                                                       blockNumber=transaction_data['blockheight'],
                                                       blockHash=transaction_data['blockhash'],
                                                       time=transaction_data['blocktime'],
                                                       transactionHash=transaction_data['txid'],
                                                       blockchainReference=blockchainReference,
                                                       jsonData=json.dumps(transaction_data)))

                engine = create_engine('sqlite:///system.db', echo=True)
                connection = engine.connect()
                connection.execute(
                    'update activecontracts set status="closed" where contractName="{}" and contractAddress="{}"'.format(
                        parsed_data['contractName'], outputlist[0]))
                connection.execute(
                    'update activecontracts set closeDate="{}" where contractName="{}" and contractAddress="{}"'.format(transaction_data['blocktime'],
                        parsed_data['contractName'], outputlist[0]))
                connection.close()

                updateLatestTransaction(transaction_data, parsed_data, transaction_data['blockheight'])

                pushData_SSEapi('Trigger | Contract triggered of the name {}-{} is active currentlyt at transaction {}'.format(
                        parsed_data['contractName'], outputlist[0], transaction_data['txid']))

        else:
            logger.info('Input address is not part of the committee address list. This trigger is rejected')
            pushData_SSEapi('Error | Smart contract pay\'s input address is not part of the committee address. Contract will be rejected'.format(parsed_data['contractName'], outputlist[0], transaction_data['txid']))



# todo Rule 1 - Read command line arguments to reset the databases as blank
#  Rule 2     - Read config to set testnet/mainnet
#  Rule 3     - Set flo blockexplorer location depending on testnet or mainnet
#  Rule 4     - Set the local flo-cli path depending on testnet or mainnet
#  Rule 5     - Set the block number to scan from


# Read command line arguments
parser = argparse.ArgumentParser(description='Script tracks RMT using FLO data on the FLO blockchain - https://flo.cash')
parser.add_argument('-r', '--reset', nargs='?', const=1, type=int, help='Purge existing db and rebuild it')
args = parser.parse_args()

apppath = os.path.dirname(os.path.realpath(__file__))
dirpath = os.path.join(apppath, 'tokens')
if not os.path.isdir(dirpath):
    os.mkdir(dirpath)
dirpath = os.path.join(apppath, 'smartContracts')
if not os.path.isdir(dirpath):
    os.mkdir(dirpath)

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Assignment the flo-cli command
if config['DEFAULT']['NET'] == 'mainnet':
    neturl = 'https://livenet.flocha.in/'
    localapi = config['DEFAULT']['FLO_CLI_PATH']
elif config['DEFAULT']['NET'] == 'testnet':
    neturl = 'https://testnet.flocha.in/'
    localapi = '{} --testnet'.format(config['DEFAULT']['FLO_CLI_PATH'])
else:
    logger.error("NET parameter in config.ini invalid. Options are either 'mainnet' or 'testnet'. Script is exiting now")

# Delete database and smartcontract directory if reset is set to 1
if args.reset == 1:
    logger.debug("Resetting the database. ")
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
    engine = create_engine('sqlite:///system.db', echo=True)
    SystemBase.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    session.add( SystemData(attribute='lastblockscanned', value=startblock-1))
    session.commit()
    session.close()

    # initialize latest cache DB
    engine = create_engine('sqlite:///latestCache.db', echo=True)
    LatestCacheBase.metadata.create_all(bind=engine)
    session.commit()
    session.close()




# Read start block no
engine = create_engine('sqlite:///system.db', echo=True)
SystemBase.metadata.create_all(bind=engine)
session = sessionmaker(bind=engine)()
startblock = int(session.query(SystemData).filter_by(attribute='lastblockscanned').all()[0].value) + 1
session.commit()
session.close()



# todo Rule 6 - Find current block height
#     Rule 7 - Start analysing the block contents from starting block to current height

# Find current block height
response = multiRequest('blocks?limit=1', config['DEFAULT']['NET'])
current_index = response['blocks'][0]['height']
logger.debug("Current block height is %s" % str(current_index))

for blockindex in range( startblock, current_index ):
    if blockindex==869163:
        print('heyo')
    processBlock(blockindex)

# At this point the script has updated to the latest block
# Now we connect to flosight's websocket API to get information about the latest blocks

sio = socketio.Client()
sio.connect(neturl + "socket.io/socket.io.js")


@sio.on('connect')
def on_connect():
    print('I connected to the websocket')
    sio.emit('subscribe', 'inv')


@sio.on('block')
def on_block(data):
    print('New block received')
    print(str(data))
    processApiBlock(data)
