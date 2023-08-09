"""

DEFINITIONS:

Special character words - A word followed by either of the special character(#,*,@)
#-word - Token name 
@-word - Smart Contract name 
*-word - Smart Contract type 

"""

"""
FIND RULES 

1. Identify all Special character words in a text string >> and output as a list of those words
2. Apply rule 1, but only before a marker or keyword like ":" and output as a list of those words 
3. Find a number in the string 
5. Check for an occurance of exact order of pattern of special character words 
   eg. for one-time-event smart contract( identified using *-word), the existence of #-word should be checked before the ':' and output the #-word
       for continuos-event smart contract( identified using *-word)(with subtype tokenswap), the #-words should be checked after the ':' and output two hash words 
6. Given a string of the type contract conditions, format and output an object string by removing = and by removing number references 
7. Idenitfy all the special character words in a text string such that spaces are not taken into account, for eg. Input string => "contract-conditions :(2) accepting_token=rupee#(3) selling_token = bioscope# " | 
                                                                                                                  Output string => ["rupee#","bioscope#"]
"""

def findrule1(rawstring, special_character):
    wordList = []
    for word in rawstring.split(' '):
        if word.endswith(special_character) and len(word) != 1:
            wordList.append(word)
    return wordList

def findrule3(text):
    base_units = {'thousand': 10 ** 3, 'million': 10 ** 6, 'billion': 10 ** 9, 'trillion': 10 ** 12}
    textList = text.split(' ')
    counter = 0
    value = None
    for idx, word in enumerate(textList):
        try:
            result = float(word)
            if textList[idx + 1] in base_units:
                value = result * base_units[textList[idx + 1]]
                counter = counter + 1
            else:
                value = result
                counter = counter + 1
        except:
            for unit in base_units:
                result = word.split(unit)
                if len(result) == 2 and result[1] == '' and result[0] != '':
                    try:
                        value = float(result[0]) * base_units[unit]
                        counter = counter + 1
                    except:
                        continue

    if counter == 1:
        return value
    else:
        return None
    


"""
TRUE-FALSE RULES 

1. Check if subtype = tokenswap exists in a given string, 
2. Find if any one of special word in list is present, ie. [start, create, incorporate] and any of the words in second list is not present like [send,transfer, give]  

"""
import re

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

'''
findWholeWord('seek')('those who seek shall find')    # -> <match object>
findWholeWord('word')('swordsmith')
'''

def truefalse_rule1(rawstring, string_tobe_checked):
    nowhites_rawstring = rawstring.replace(" ","").lower()
    if string_tobe_checked.replace(" ","").lower() in nowhites_rawstring:
        return True
    else:
        return False

denied_list = ['transfer', 'send', 'give']  # keep everything lowercase
permitted_list = ['incorporate', 'create', 'start']  # keep everything lowercase

def truefalse_rule2(rawstring, permitted_list, denied_list):
    # Find transfer , send , give
    foundPermitted = None 
    foundDenied = None

    for word in permitted_list:
        if findWholeWord(word)(rawstring):
            foundPermitted = word
            break

    for word in denied_list:
        if findWholeWord(word)(rawstring):
            foundDenied = word
            break
    
    if (foundPermitted in not None) and (foundDenied is None):
        return True
    else:
        return False


def selectCateogry(rawstring, wordlist, category1, category2):


"""
CLASSIFY RULES 

1. Based on various combinations of the special character words and special words, create categorizations 
   eg. 1.1 if there is only one #-word, then the flodata is related purely to token system 
       1.2 if there is one #-word, one @-word .. then it is related to smart contract system, but cannot be a creation type since smart contract creaton needs to specify contract type with *-word
       1.3 if there is one 
2. Check if it is of the value 'one-time-event' or 'continuos-event'

"""

"""
REJECT RULES 

1. *-words have to be equal to 1 ie. You can specify only one contract type at once , otherwise noise 
2. *-word has to fall in the following type ['one-time-event*', 'continuous-event*'], otherwise noise 
3. @-word should exist only before the : , otherwise noise 
4. There should be only one @-word, otherwise noise 
5. for one-time-event smart contract( identified using one-time-event*), if there is a no #-word before : -> reject as noise 
6. for one-time-event smart contract( identified using one-time-event*) if there is more than one #-word before : -> reject as noise 
7. for one-time-event smart contract( identified using one-time-event*) if there is/are #-word(s) after colon -> reject as noise 
8. for continuos-event smart contract( identified using continuos-event*) if there is one or more #-word before : > reject as noise 
9. for continuos-event smart contract( identified using continuos-event*)( with subtype token-swap ) if there is one or more than two #-word after : > reject as noise 
10. 

"""

def rejectrule9(rawtext, starword):
    pass
    

extractContractConditions(cleanstring, contracttype, blocktime=blockinfo['time'], marker=hashList[0][:-1])

# Token incorporation operation 
## Existance of keyword 

""" 
APPLY RULES

1. After application of apply rule1, a parser rule will either return a value or will classify the result as noise 

""" 

def apply_rule1(*argv):
    a = argv[0](*argv[1:])
    if a is False:
        return "noise"
    elif a if True:
        return a

# If any of the parser rule returns a value, then queue it for further processing, otherwise send noise to the output engine 
apply_rule1(findrule_1, rawstring, special_character) 

def outputreturn(*argv):
    if argv[0] == 'noise':
        parsed_data = {'type': 'noise'}
    elif argv[0] == 'token_incorporation':
        parsed_data = {
            'type': 'tokenIncorporation',
            'flodata': argv[1], #string 
            'tokenIdentification': argv[2], #hashList[0][:-1] 
            'tokenAmount': argv[3] #initTokens
            }
    elif argv[0] == 'token_transfer':
        parsed_data = {
            'type': 'transfer', 
            'transferType': 'token', 
            'flodata': argv[1], #string
            'tokenIdentification': argv[2], #hashList[0][:-1]
            'tokenAmount': argv[3] #amount
            }
    elif argv[0] == 'one-time-event-userchoice-smartcontract-incorporation':
        parsed_data = {
            'type': 'smartContractIncorporation', 
            'contractType': 'one-time-event',
            'tokenIdentification': argv[1], #hashList[0][:-1] 
            'contractName': argv[2], #atList[0][:-1]
            'contractAddress': argv[3], #contractaddress[:-1] 
            'flodata': argv[4], #string
            'contractConditions': {
                'contractamount' : argv[5],
                'minimumsubscriptionamount' : argv[6],
                'maximumsubscriptionamount' : argv[7],
                'payeeaddress' : argv[8],
                'userchoice' : argv[9],
                'expiryTime' : argv[10]
            }
        }
    elif argv[0] == 'one-time-event-userchoice-smartcontract-participation':
        parsed_data = {
            'type': 'transfer', 
            'transferType': 'smartContract', 
            'flodata': argv[1], #string
            'tokenIdentification': argv[2], #hashList[0][:-1]
            'operation': 'transfer', 
            'tokenAmount': argv[3], #amount 
            'contractName': argv[4], #atList[0][:-1]
            'userChoice': argv[5] #userChoice
            }
    elif argv[0] == 'one-time-event-userchoice-smartcontract-trigger':
        parsed_data = {
            'type': 'smartContractPays', 
            'contractName': argv[1], #atList[0][:-1] 
            'triggerCondition': argv[2] #triggerCondition.group().strip()[1:-1]
            }
    elif argv[0] == 'one-time-event-time-smartcontract-incorporation':
        parsed_data = {
            'type': 'smartContractIncorporation', 
            'contractType': 'one-time-event',
            'tokenIdentification': argv[1], #hashList[0][:-1] 
            'contractName': argv[2], #atList[0][:-1]
            'contractAddress': argv[3], #contractaddress[:-1] 
            'flodata': argv[4], #string
            'contractConditions': {
                'contractamount' : argv[5],
                'minimumsubscriptionamount' : argv[6],
                'maximumsubscriptionamount' : argv[7],
                'payeeaddress' : argv[8],
                'expiryTime' : argv[9]
            }
        }
    elif argv[0] == 'one-time-event-time-smartcontract-participation':
        parsed_data = {
            'type': 'transfer', 
            'transferType': 'smartContract', 
            'flodata': argv[1], #string
            'tokenIdentification': argv[2], #hashList[0][:-1]
            'operation': 'transfer', 
            'tokenAmount': argv[3], #amount 
            'contractName': argv[4] #atList[0][:-1]
            }
    elif argv[0] == 'continuos-event-token-swap-incorporation':
        parsed_data = {
            'type': 'smartContractIncorporation', 
            'contractType': 'continuos-event',
            'tokenIdentification': argv[1], #hashList[0][:-1] 
            'contractName': argv[2], #atList[0][:-1]
            'contractAddress': argv[3], #contractaddress[:-1] 
            'flodata': argv[4], #string
            'contractConditions': {
                'subtype' : argv[5], #tokenswap
                'accepting_token' : argv[6],
                'selling_token' : argv[7],
                'pricetype' : argv[8],
                'price' : argv[9],
            }
        }
    elif argv[0] == 'continuos-event-token-swap-deposit':
        parsed_data = {
            'type': 'smartContractDeposit',
            'tokenIdentification': argv[1], #hashList[0][:-1]
            'depositAmount': argv[2], #depositAmount 
            'contractName': argv[3], #atList[0][:-1] 
            'flodata': argv[4], #string
            'depositConditions': {
                'expiryTime' : argv[5]
            }
        }
    elif argv[0] == 'continuos-event-token-swap-participation':
        parsed_data = {
            'type': 'smartContractParticipation',
            'tokenIdentification': argv[1], #hashList[0][:-1]
            'sendAmount': argv[2], #sendtAmount 
            'receiveAmount': argv[3], #receiveAmount 
            'contractName': argv[4], #atList[0][:-1] 
            'flodata': argv[5] #string
        }
