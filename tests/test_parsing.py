import unittest
import sys
sys.path.append("..")
import parsing

class TestParsing(unittest.TestCase):

    blockinfo_stub = {'time': 25634}

    def test_token_creation(self):
        text = 'create 100 rmt#'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'mainnet')
        expected_result = {
            'type': 'tokenIncorporation', 
            'flodata': 'create 100 rmt#', 
            'tokenIdentification': 'rmt', 
            'tokenAmount': 100.0, 
            'stateF': False
            }
        self.assertEqual(result, expected_result)
    
    def test_token_transfer(self):
        text = 'transfer 10.340 rmt#'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'mainnet')
        expected_result = {
            'type': 'transfer', 
            'transferType': 'token', 
            'flodata': 'transfer 10.340 rmt#', 
            'tokenIdentification': 'rmt', 
            'tokenAmount': 10.34, 
            'stateF': False
            }
        self.assertEqual(result, expected_result)

    def test_nft_creation(self):
        pass
    
    def test_nft_transfer(self):
        pass

    def test_infinite_token_incorporation(self):
        text = 'create usd# as infinite-token'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'mainnet')
        expected_result = {
            'type': 'infiniteTokenIncorporation', 
            'flodata': 'create usd# as infinite-token', 
            'tokenIdentification': 'usd', 
            'stateF': False
            }
        self.assertEqual(result, expected_result)

        text = 'create usd# as infinite-token send'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'mainnet')
        expected_result = {'type': 'noise'}
        self.assertEqual(result, expected_result)
    
    def test_infinite_token_transfer(self):
        pass

    def test_onetimeevent_timetrigger_creation(self):
        # contractamount
        text = '''Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions:(1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530  (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) contractAmount=0.1 end-contract-conditions'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {
            'type': 'smartContractIncorporation', 
            'contractType': 'one-time-event', 
            'subtype': 'time-trigger',
            'tokenIdentification': 'bioscope', 
            'contractName': 'all-crowd-fund-1', 
            'contractAddress': 'oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz', 
            'flodata': 'Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) contractAmount=0.1 end-contract-conditions', 
            'contractConditions': {
                'contractAmount': '0.1', 
                'payeeAddress': {
                    'oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7': 10.0, 'oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij': 20.0, 'oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5': 30.0, 'oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ': 40.0
                    }, 
                'expiryTime': 'sun nov 13 2022 19:35:00 gmt+0530',
                'unix_expiryTime': 1668387900.0
                }
            }
        self.assertEqual(result, expected_result)

        # minimumsubscriptionamount
        text = '''Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions:(1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530  (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1 end-contract-conditions'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype':'time-trigger','tokenIdentification': 'bioscope', 'contractName': 'all-crowd-fund-1', 'contractAddress': 'oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz', 'flodata': 'Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1 end-contract-conditions', 'contractConditions': {'minimumsubscriptionamount': '1.0', 'payeeAddress': {'oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7': 10.0, 'oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij': 20.0, 'oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5': 30.0, 'oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ': 40.0}, 'expiryTime': 'sun nov 13 2022 19:35:00 gmt+0530', 'unix_expiryTime': 1668387900.0}}
        self.assertEqual(result, expected_result)

        # maximumsubscriptionamount
        text = '''Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions:(1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530  (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) maximumsubscriptionamount=10 end-contract-conditions'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype': 'time-trigger','tokenIdentification': 'bioscope', 'contractName': 'all-crowd-fund-1', 'contractAddress': 'oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz', 'flodata': 'Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) maximumsubscriptionamount=10 end-contract-conditions', 'contractConditions': {'maximumsubscriptionamount': '10.0', 'payeeAddress': {'oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7': 10.0, 'oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij': 20.0, 'oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5': 30.0, 'oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ': 40.0}, 'expiryTime': 'sun nov 13 2022 19:35:00 gmt+0530', 'unix_expiryTime': 1668387900.0}}
        self.assertEqual(result, expected_result)

        # minimumsubscriptionamount | contractamount
        text = '''Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions:(1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530  (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1.600 (4) contractAmount=0.1 end-contract-conditions'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype': 'time-trigger', 'tokenIdentification': 'bioscope', 'contractName': 'all-crowd-fund-1', 'contractAddress': 'oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz', 'flodata': 'Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1.600 (4) contractAmount=0.1 end-contract-conditions', 'contractConditions': {'contractAmount': '0.1', 'minimumsubscriptionamount': '1.6', 'payeeAddress': {'oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7': 10.0, 'oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij': 20.0, 'oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5': 30.0, 'oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ': 40.0}, 'expiryTime': 'sun nov 13 2022 19:35:00 gmt+0530', 'unix_expiryTime': 1668387900.0}}
        self.assertEqual(result, expected_result)

        # maximumsubscriptionamount | contractamount
        text = '''Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions:(1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530  (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) maximumsubscriptionamount=10  (4) contractAmount=0.1 end-contract-conditions'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype': 'time-trigger', 'tokenIdentification': 'bioscope', 'contractName': 'all-crowd-fund-1', 'contractAddress': 'oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz', 'flodata': 'Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) maximumsubscriptionamount=10 (4) contractAmount=0.1 end-contract-conditions', 'contractConditions': {'contractAmount': '0.1', 'maximumsubscriptionamount': '10.0', 'payeeAddress': {'oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7': 10.0, 'oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij': 20.0, 'oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5': 30.0, 'oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ': 40.0}, 'expiryTime': 'sun nov 13 2022 19:35:00 gmt+0530', 'unix_expiryTime': 1668387900.0}}
        self.assertEqual(result, expected_result)
        
        # minimumsubscriptionamount | maximumsubscriptionamount
        text = '''Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions:(1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530  (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1 (4) maximumsubscriptionamount=10 end-contract-conditions'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype':'time-trigger','tokenIdentification': 'bioscope', 'contractName': 'all-crowd-fund-1', 'contractAddress': 'oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz', 'flodata': 'Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1 (4) maximumsubscriptionamount=10 end-contract-conditions', 'contractConditions': {'minimumsubscriptionamount': '1.0', 'maximumsubscriptionamount': '10.0', 'payeeAddress': {'oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7': 10.0, 'oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij': 20.0, 'oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5': 30.0, 'oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ': 40.0}, 'expiryTime': 'sun nov 13 2022 19:35:00 gmt+0530', 'unix_expiryTime': 1668387900.0}}
        self.assertEqual(result, expected_result)
        
        # minimumsubscriptionamount | maximumsubscriptionamount | contractamount
        text = '''Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions:(1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530  (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1 (4) maximumsubscriptionamount=10  (5) contractAmount=0.1 end-contract-conditions'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype': 'time-trigger', 'tokenIdentification': 'bioscope', 'contractName': 'all-crowd-fund-1', 'contractAddress': 'oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz', 'flodata': 'Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1 (4) maximumsubscriptionamount=10 (5) contractAmount=0.1 end-contract-conditions', 'contractConditions': {'contractAmount': '0.1', 'minimumsubscriptionamount': '1.0', 'maximumsubscriptionamount': '10.0', 'payeeAddress': {'oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7': 10.0, 'oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij': 20.0, 'oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5': 30.0, 'oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ': 40.0}, 'expiryTime': 'sun nov 13 2022 19:35:00 gmt+0530', 'unix_expiryTime': 1668387900.0}}
        self.assertEqual(result, expected_result)

        # With single payeeAddress with : format
        text = "Create a smart contract of the name album-fund@ of the type one-time-event* using asset bioscope# at the FLO address ocsiFSsjek3UXKdHpBWF79qrGN6qbpxeMt$ with contract-conditions: (1) expiryTime= Thu May 04 2023 18:57:00 GMT+0530 (India Standard Time) (2) payeeAddress= objfBRUX5zn4W56aHhRn4DgH6xqeRWk6Xc:100    end-contract-conditions"
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype': 'time-trigger', 'tokenIdentification': 'bioscope', 'contractName': 'album-fund', 'contractAddress': 'ocsiFSsjek3UXKdHpBWF79qrGN6qbpxeMt', 'flodata': 'Create a smart contract of the name album-fund@ of the type one-time-event* using asset bioscope# at the FLO address ocsiFSsjek3UXKdHpBWF79qrGN6qbpxeMt$ with contract-conditions: (1) expiryTime= Thu May 04 2023 18:57:00 GMT+0530 (India Standard Time) (2) payeeAddress= objfBRUX5zn4W56aHhRn4DgH6xqeRWk6Xc:100 end-contract-conditions', 'contractConditions': {'payeeAddress': {'objfBRUX5zn4W56aHhRn4DgH6xqeRWk6Xc': 100.0}, 'expiryTime': 'thu may 04 2023 18:57:00 gmt+0530 (india standard time)', 'unix_expiryTime': 1683246420.0}}
        self.assertEqual(result, expected_result)
        
        # With single payeeAddress with normal format
        text = "Create a smart contract of the name album-fund@ of the type one-time-event* using asset bioscope# at the FLO address ocsiFSsjek3UXKdHpBWF79qrGN6qbpxeMt$ with contract-conditions: (1) expiryTime= Thu May 04 2023 18:57:00 GMT+0530 (India Standard Time) (2) payeeAddress= objfBRUX5zn4W56aHhRn4DgH6xqeRWk6Xc   end-contract-conditions"
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype': 'time-trigger', 'tokenIdentification': 'bioscope', 'contractName': 'album-fund', 'contractAddress': 'ocsiFSsjek3UXKdHpBWF79qrGN6qbpxeMt', 'flodata': 'Create a smart contract of the name album-fund@ of the type one-time-event* using asset bioscope# at the FLO address ocsiFSsjek3UXKdHpBWF79qrGN6qbpxeMt$ with contract-conditions: (1) expiryTime= Thu May 04 2023 18:57:00 GMT+0530 (India Standard Time) (2) payeeAddress= objfBRUX5zn4W56aHhRn4DgH6xqeRWk6Xc end-contract-conditions', 'contractConditions': {'payeeAddress': {'objfBRUX5zn4W56aHhRn4DgH6xqeRWk6Xc': 100}, 'expiryTime': 'thu may 04 2023 18:57:00 gmt+0530 (india standard time)', 'unix_expiryTime': 1683246420.0}}
        self.assertEqual(result, expected_result)
        
        # With multiple payeeAddress with : format
        text = "Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1 (4) maximumsubscriptionamount=10 (5) contractAmount=0.1 end-contract-conditions"

        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'smartContractIncorporation', 'contractType': 'one-time-event', 'subtype': 'time-trigger', 'tokenIdentification': 'bioscope', 'contractName': 'all-crowd-fund-1', 'contractAddress': 'oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz', 'flodata': 'Create a smart contract of the name all-crowd-fund-1@ of the type one-time-event* using asset bioscope# at the FLO address oQkpZCBcAWc945viKqFmJVbVG4aKY4V3Gz$ with contract-conditions: (1) expiryTime= Sun Nov 13 2022 19:35:00 GMT+0530 (2) payeeAddress=oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7:10:oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij:20:oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5:30:oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ:40 (3) minimumsubscriptionamount=1 (4) maximumsubscriptionamount=10 (5) contractAmount=0.1 end-contract-conditions', 'contractConditions': {'contractAmount': '0.1', 'minimumsubscriptionamount': '1.0', 'maximumsubscriptionamount': '10.0', 'payeeAddress': {'oQotdnMBAP1wZ6Kiofx54S2jNjKGiFLYD7': 10.0, 'oMunmikKvxsMSTYzShm2X5tGrYDt9EYPij': 20.0, 'oRpvvGEVKwWiMnzZ528fPhiA2cZA3HgXY5': 30.0, 'oWpVCjPDGzaiVfEFHs6QVM56V1uY1HyCJJ': 40.0}, 'expiryTime': 'sun nov 13 2022 19:35:00 gmt+0530', 'unix_expiryTime': 1668387900.0}}
        self.assertEqual(result, expected_result)


    def test_onetimeevent_timetrigger_participation(self):
        text = '''send 2.2 bioscope# to all-crowd-fund@'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'transfer', 'transferType': 'smartContract', 'flodata': 'send 2.2 bioscope# to all-crowd-fund@', 'tokenIdentification': 'bioscope', 'tokenAmount': 2.2, 'contractName': 'all-crowd-fund'}
        self.assertEqual(result, expected_result)

        text = 'transfer 6.20000 bioscope# to all-crowd-fund-7@'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'transfer', 'transferType': 'smartContract', 'flodata': 'transfer 6.20000 bioscope# to all-crowd-fund-7@', 'tokenIdentification': 'bioscope', 'tokenAmount': 6.2, 'contractName': 'all-crowd-fund-7'}
        self.assertEqual(result, expected_result)

        text = 'transfer 6.20000 bioscope# to all-crowd-fund-7@ 24'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'noise'}
        self.assertEqual(result, expected_result)

        text = 'transfer 6.20000 bioscope# to all-crowd-fund-7@ 24 '
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'noise'}
        self.assertEqual(result, expected_result)

        text = '6.20.000 transfer bioscope# to all-crowd-fund-7@ 24'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'transfer', 'transferType': 'smartContract', 'flodata': '6.20.000 transfer bioscope# to all-crowd-fund-7@ 24', 'tokenIdentification': 'bioscope', 'tokenAmount': 24.0, 'contractName': 'all-crowd-fund-7'}
        self.assertEqual(result, expected_result)
    
    def test_onetimeevent_externaltrigger_creation(self):
        # contractamount
        text = '''Create a smart contract of the name twitter-survive@ of the type one-time-event* using asset bioscope# at the FLO address oVbebBNuERWbouDg65zLfdataWEMTnsL8r$ with contract-conditions:(1) expiryTime= Sun Nov 15 2022 14:55:00 GMT+0530  (2) userchoices= survives | dies (3) contractAmount=0.02 end-contract-conditions'''
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {
            'type': 'smartContractIncorporation', 
            'contractType': 'one-time-event', 
            'subtype': 'external-trigger',
            'tokenIdentification': 'bioscope', 
            'contractName': 'twitter-survive', 
            'contractAddress': 'oVbebBNuERWbouDg65zLfdataWEMTnsL8r', 
            'flodata': 'Create a smart contract of the name twitter-survive@ of the type one-time-event* using asset bioscope# at the FLO address oVbebBNuERWbouDg65zLfdataWEMTnsL8r$ with contract-conditions: (1) expiryTime= Sun Nov 15 2022 14:55:00 GMT+0530 (2) userchoices= survives | dies (3) contractAmount=0.02 end-contract-conditions', 
            'contractConditions': {
                'contractAmount': '0.02', 
                'userchoices': "{0: 'survives', 1: 'dies'}", 
                'expiryTime': 'sun nov 15 2022 14:55:00 gmt+0530',
                'unix_expiryTime': 1668543900.0
                }
            }
        self.assertEqual(result, expected_result)

    def test_tokenswap_deposits(self):
        text = 'Deposit 1 bioscope# to swap-rupee-bioscope-1@ its FLO address being oTzrcpLPRXsejSdYQ3XN6V4besrAPuJQrk$ with deposit-conditions: (1) expiryTime= Thu Apr 13 2023 21:45:00 GMT+0530'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {
            'type': 'smartContractDeposit', 
            'tokenIdentification': 'bioscope', 
            'depositAmount': 1.0, 
            'contractName': 'swap-rupee-bioscope-1', 
            'flodata': 'Deposit 1 bioscope# to swap-rupee-bioscope-1@ its FLO address being oTzrcpLPRXsejSdYQ3XN6V4besrAPuJQrk$ with deposit-conditions: (1) expiryTime= Thu Apr 13 2023 21:45:00 GMT+0530', 
            'depositConditions': {
                'expiryTime': 'thu apr 13 2023 21:45:00 gmt+0530'
                }, 
            'stateF': False}
        self.assertEqual(result, expected_result)

    def test_contract_trigger(self):
        text = 'contract@ triggerCondition:"twitter-survives"'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {
            'type': 'smartContractPays', 
            'contractName': 'contract', 
            'triggerCondition': 'twitter-survives', 
            'stateF': False}
        self.assertEqual(result, expected_result)

    def test_deposit_invalid(self):
        text = 'Deposit 1 bioscope# to swap-rupee-bioscope-1@ its FLO address being oTzrcpLPRXsejSdYQ3XN6V4besrAPuJQrk$ with deposit-conditions: (1) expiryTime= Tue, 25 Apr 2023 13:40:00 GMT'
        result = parsing.parse_flodata(text, TestParsing.blockinfo_stub, 'testnet')
        expected_result = {'type': 'noise'}
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()