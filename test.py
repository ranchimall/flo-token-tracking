import pdb

""" 
Find make lists of #, *, @ words 

If only 1 hash word and nothing else, then it is token related ( tokencreation or tokentransfer )

If @ is present, then we know it is smart contract related 
    @ (#)pre:       -  participation , deposit 
    @ * (#)pre:     -  one time event creation 
    @ * (# #)post:  -  token swap creation 
    @               -  trigger 

Check for 1 @ only 
Check for 1 # only 
Check for @ (#)pre: 
Check for @ * (#)pre: 
Check for @ * (# #)post: 

special_character_frequency = { 
    'precolon': { 
        '#':0, 
        '*':0,
        '@':0,
        ':':0
}

for word in allList:
    if word.endswith('#'):
        special_character_frequency['#'] = special_character_frequency['#'] + 1
    elif word.endswith('*'):
        special_character_frequency['*'] = special_character_frequency['*'] + 1
    elif word.endswith('@'):
        special_character_frequency['@'] = special_character_frequency['@'] + 1
    elif word.endswith(':'):
        special_character_frequency[':'] = special_character_frequency[':'] + 1

""" 

search_patterns = {
    'tokensystem-C':{
        1:['#']
    },
    'smart-contract-creation-C':{
        1:['@','*','#','$',':'],
        2:['@','*','#','$',':','#']
    },
    'smart-contract-participation-deposit-C':{
        1:['#','@',':'],
        2:['#','@','$',':']
    },
    'userchoice-trigger':{
        1:['@'] 
    },
    'smart-contract-participation-ote-ce-C':{
        1:['#','@'],
        2:['#','@','$']
    },
    'smart-contract-creation-ce-tokenswap':{
        1:['@','*','$',':','#','#']
    }
}

conflict_matrix = {
    'tokensystem-C':{
        # Check for send, check for create, if both are there noise, else conflict resolved
        'tokentransfer',
        'tokencreation'
    },
    'smart-contract-creation-C':{
        # Check contract-conditions for userchoice, if present then userchoice contract, else time based contract
        'creation-one-time-event-userchoice',
        'creation-one-time-event-timebased'
    },
    'smart-contract-participation-deposit-C':{
        # Check *-word, its either one-time-event or a continuos-event
        'participation-one-time-event-userchoice',
        'deposit-continuos-event-tokenswap'
    },
    'smart-contract-participation-ote-ce-C':{
        # Check *-word, its either one-time-event or a continuos-event
        'participation-one-time-event-timebased',
        'participation-continuos-event-tokenswap'
    }
}

def extract_specialcharacter_words(rawstring, special_characters):
    wordList = []
    for word in rawstring.strip().split(' '):
        if word[-1] in special_characters and (len(word) != 1 or word==":"):
            wordList.append(word)
    return wordList


def find_first_classification(parsed_list, search_patterns):
    for first_classification in search_patterns.keys():
        counter = 0
        for key in search_patterns[first_classification].keys():
            if checkSearchPattern(parsed_list, search_patterns[first_classification][key]):
                return {'categorization':f"{first_classification}",'key':f"{key}",'pattern':search_patterns[first_classification][key]}
    return {'categorization':"noise"}


def sort_specialcharacter_wordlist(inputlist):
    weight_values = {
        '@': 5,
        '*': 4,
        '#': 3,
        '$': 2
    }
    
    weightlist = []
    for word in inputlist:
        if word.endswith("@"):
            weightlist.append(5)
        elif word.endswith("*"):
            weightlist.append(4)
        elif word.endswith("#"):
            weightlist.append(4)
        elif word.endswith("$"):
            weightlist.append(4)


def classify_rawstring(rawstring):
    specialcharacter_wordlist = extract_specialcharacter_words(rawstring,['@','*','$','#',':'])
    print(specialcharacter_wordlist)
    first_classication = find_first_classification(specialcharacter_wordlist, search_patterns)

    if first_classication == 



def checkSearchPattern(parsed_list, searchpattern):
    if len(parsed_list)!=len(searchpattern):
        return False
    else:
        for idx,val in enumerate(parsed_list):
            if not parsed_list[idx].endswith(searchpattern[idx]):
                return False
        return True


def className(rawstring):
    # Create a list that contains @ , # , * and : ; in actual order of occurence with their words. Only : is allowed to exist without a word in front of it. 
    # Check for 1 @ only followed by :, and the class is trigger
    # Check for 1 # only, then the class is tokensystem
    # Check for @ in the first position, * in the second position, # in the third position and : in the fourth position, then class is one time event creation 
    # Check for @ in the first position, * in the second position and : in the third position, then hash is in 4th position, then hash in 5th position | Token swap creation 

    allList = findrules(rawstring,['#','*','@',':'])

    pattern_list1 = ['rmt@','rmt*',':',"rmt#","rmt#"]
    pattern_list2 = ['rmt#',':',"rmt@"]
    pattern_list3 = ['rmt#']
    pattern_list4 = ["rmt@","one-time-event*","floAddress$",':',"rupee#","bioscope#"]
    patternmatch = find_first_classification(pattern_list4, search_patterns)
    print(f"Patternmatch is {patternmatch}")


rawstring = "test rmt# rmt@ rmt* : rmt# rmt# test" 
#className(rawstring)
text_list = [
    "create 500 million rmt#",

    "transfer 200 rmt#",

    "Create Smart Contract with the name India-elections-2019@ of the type one-time-event* using the asset rmt# at the address F7osBpjDDV1mSSnMNrLudEQQ3cwDJ2dPR1$ with contract-conditions: (1) contractAmount=0.001rmt (2) userChoices=Narendra Modi wins| Narendra Modi loses (3) expiryTime= Wed May 22 2019 21:00:00 GMT+0530",

    "send 0.001 rmt# to india-elections-2019@ to FLO address F7osBpjDDV1mSSnMNrLudEQQ3cwDJ2dPR1 with the userchoice:'narendra modi wins'",

    "india-elections-2019@ winning-choice:'narendra modi wins'",

    "Create Smart Contract with the name India-elections-2019@ of the type one-time-event* using the asset rmt# at the address F7osBpjDDV1mSSnMNrLudEQQ3cwDJ2dPR1$ with contract-conditions: (1) contractAmount=0.001rmt (2) expiryTime= Wed May 22 2019 21:00:00 GMT+0530",

    "send 0.001 rmt# to india-elections-2019@ to FLO address F7osBpjDDV1mSSnMNrLudEQQ3cwDJ2dPR1",

    "Create Smart Contract with the name swap-rupee-bioscope@ of the type continuous-event* at the address oRRCHWouTpMSPuL6yZRwFCuh87ZhuHoL78$ with contract-conditions : (1) subtype = tokenswap (2) accepting_token = rupee# (3) selling_token = bioscope# (4) price = '15' (5) priceType = ‘predetermined’ (6) direction = oneway",
    
    "Deposit 15 bioscope# to swap-rupee-bioscope@ its FLO address being oRRCHWouTpMSPuL6yZRwFCuh87ZhuHoL78$ with deposit-conditions: (1) expiryTime= Wed Nov 17 2021 21:00:00 GMT+0530 ",

    "Send 15 rupee# to swap-rupee-article@ its FLO address being FJXw6QGVVaZVvqpyF422Aj4FWQ6jm8p2dL$"
]

for text in text_list:
    print(f"{classify_rawstring(text)} \n\n")