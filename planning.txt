'''
TEMPLATE FOR SECOND STAGE AFTER INPUT CLASSIFIER 

IF BLOCK If the output of input classifier is tokensystem-C, 
JUST LINEARLY START BUILDING IT 

then first start building the known outputs 

// outputreturn('token_incorporation',f"{flodata}", f"{tokenname}", f"{tokenamount}") 

f"{flodata} = rawstring 
f"{tokenname}" = wordlist entry 
tokensystem-C-resolved = Output of second stage classification 
f"{tokenamount}" = find_number_function 
'''

'''
    The problem we are facing:

    * Token transactions don't have * or @ symbols 

    * Smart Contract transactions have * , @ , # symbols 

    * Smart Contract transaction of the type one time event have 1 # before colon 

    * Smart Contract transaction of the type continuous event has 2 # after colon 

    * So we are checking for hashes based on the type of smart contract(identified by *) 

    * But the above check disregards checking hashes in token transactions 
'''

# Write down all the possible flodata( with all combinations possible) for 
'''
    Token creation 
    create 500 million rmt#
    ['#']

    Token transfer 
    transfer 200 rmt#
    ['#']

    One time event userchoice creation 
    Create Smart Contract with the name India-elections-2019@ of the type one-time-event* using the asset rmt# at the address F7osBpjDDV1mSSnMNrLudEQQ3cwDJ2dPR1$ with contract-conditions: (1) contractAmount=0.001rmt (2) userChoices=Narendra Modi wins| Narendra Modi loses (3) expiryTime= Wed May 22 2019 21:00:00 GMT+0530
    ['@','*','#','$',':']
    ['@','*','#','$',':','#']
    
    One time event userchoice participation
    send 0.001 rmt# to india-elections-2019@ to FLO address F7osBpjDDV1mSSnMNrLudEQQ3cwDJ2dPR1 with the userchoice:'narendra modi wins'
    ['#','@',':']
    ['#','@','$',':']

    One time event userchoice trigger 
    india-elections-2019@ winning-choice:'narendra modi wins'
    ['@',':']

    One time event timeevent creation 
    Create Smart Contract with the name India-elections-2019@ of the type one-time-event* using the asset rmt# at the address F7osBpjDDV1mSSnMNrLudEQQ3cwDJ2dPR1$ with contract-conditions: (1) contractAmount=0.001rmt (2) expiryTime= Wed May 22 2019 21:00:00 GMT+0530
    ['@','*','#','$',':']
    ['@','*','#','$',':','#']

    One time event timeevent participation 
    send 0.001 rmt# to india-elections-2019@ to FLO address F7osBpjDDV1mSSnMNrLudEQQ3cwDJ2dPR1 
    ['#','@']
    ['#','@','$']

    Continuos event token swap creation 
    Create Smart Contract with the name swap-rupee-bioscope@ of the type continuous-event* at the address oRRCHWouTpMSPuL6yZRwFCuh87ZhuHoL78$ with contract-conditions :
    (1) subtype = tokenswap
    (2) accepting_token = rupee#
    (3) selling_token = bioscope#
    (4) price = '15'
    (5) priceType = ‘predetermined’
    (6) direction = oneway
    
    ['@','*','$',':','#','#']

    Continuos event tokenswap deposit 
    Deposit 15 bioscope# to swap-rupee-bioscope@ its FLO address being oRRCHWouTpMSPuL6yZRwFCuh87ZhuHoL78$ with deposit-conditions: (1) expiryTime= Wed Nov 17 2021 21:00:00 GMT+0530 
    ['#','@',':']
    ['#','@','$',':']

    Continuos event tokenswap participation 
    Send 15 rupee# to swap-rupee-article@ its FLO address being FJXw6QGVVaZVvqpyF422Aj4FWQ6jm8p2dL$ 
    ['#','@']
    ['#','@','$']
'''

'''

    ['#']                      -  Token creation 

    ['#']                      -  Token particiation


    ['@','*','#','$',':']      -  Smart contract creation user-choice  
    ['@','*','#','$',':','#']

    ['#','@',':']              -  Smart contract participation  user-choice
    ['#','@','$',':']

    ['@',':']                  -  Smart contract trigger user-choice 


    ['@','*','#','$',':']      -  Smart contract creation - ote-timebased
    ['@','*','#','$',':','#']

    ['#','@']                  -  Smart contract particiation - ote-timebased 
    ['#','@','$']


    ['@','*','$',':','#','#']  -  Smart contract creation - continuos event - tokenswap 

    ['#','@',':']              -  Smart contract deposit - continuos event - tokenswap 
    ['#','@','$',':']

    ['#','@']                  -  Smart contract participation - continuos event - tokenswap 
    ['#','@','$']              -  Smart contract participation - continuos event - tokenswap 

'''

'''

    ['#']                      -  Token creation 

    ['#']                      -  Token particiation


    ['@','*','#','$',':']      -  Smart contract creation ote-userchoice  
    ['@','*','#','$',':','#']

    ['@','*','#','$',':']      -  Smart contract creation - ote-timebased
    ['@','*','#','$',':','#']


    ['#','@',':']              -  Smart contract participation  user-choice
    ['#','@','$',':']

    ['#','@',':']              -  Smart contract deposit - continuos event - tokenswap 
    ['#','@','$',':']


    ['@',':']                  -  Smart contract trigger user-choice 


    ['#','@']                  -  Smart contract particiation - ote-timebased   
    ['#','@','$']

    ['#','@']                  -  Smart contract participation - continuos event - tokenswap 
    ['#','@','$']              -  Smart contract participation - continuos event - tokenswap 

    
    ['@','*','$',':','#','#']  -  Smart contract creation - continuos event - tokenswap 

'''

'''
Conflicts - 

1. Token creation | Token participation 
2. Smart contract CREATION of the type one-time-event-userchoice | one-time-event-timebased 
3. Smart contract PARTICIPATION user-choice | Smart contract DEPOSIT continuos-event token-swap 
4. Smart contract PARTICIPATION one-time-event-timebased | Smart contract participation - continuos event - tokenswap 

'''

'''

Emerging parser design 

Phase 1 - Input processing | Special character position based classification and noise detection (FINISHED)
Phase 2 - Conflict recognition (FINISHED)
Phase 3 - Category based keyword checks 
Phase 4 - Parser rules for finding data 
Phase 5 - Rules for applying parser rules 
Phase 6 - Category based data field extraction 
Phase 7 - Output formatting and return (FINISHED)

'''

'''
Allowed formats of Smart Contract and token names 

1. First character should always be an Alphabet, lower case or upper case 
2. The last character should always be an Alphabet, lower case or upper case 
3. The middle characters can be a - or _

Check for FLO Address 

Write checks for conditions inside contract conditions 
Serious error handling for contract-conditions 
* 2222:00 gives error 
* contractAmount = 0.022rt gives error | check if space is allowed between 0.022 rt 
'''


'''

    What we need for NFT contract code 

    1. NFT-address mapping table in system.db 
    2. New main transaction category class 
    3. New sub-category for transfer category class ie. NFT transfer 


    NFT Smart Contract end cases 
    1. NFT against an address 
    2. NFT against another NFT 
    3. 

    flodata format for NFT 
    Create 1000 NFT with bioscope# with nft-details: (1) name = 'bioscope' (2) hash = 

    Create 100 albumname# as NFT with 2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824 as asset hash 
    [#]

    Rules
    -----
    DIFFERENT BETWEEN TOKEN AND NFT
    System.db will have a differnent entry
    in creation nft word will be extra
    NFT Hash must be  present
    Creation and transfer amount .. only integer parts will be taken
    Keyword nft must be present in both creation and transfer

'''

'''

Need infinite tokens to create stable coins, so they can be created without worrying about the upper limit of the coins 

'''

'''
Create another table in system.db, it simply writes what is every database in one place 

Database_name               Database type

'''

'''
IDEA FOR NEW ROLLBACK SYSTEM - 24 Jan 2022 
-------------------------------------------

245436
[
    tx1 - rmt - 245436 - send 10 rmt# 
    tx2 - rmt - 245436 - send 4 rmt# 
    tx3 - rmt - 245436 - send 1 rmt# 
    tx4 - rmt - 245436 - send 100 rmt# 
    tx5 - rmt trigger(5) - 245436 - trigger 
]

banana - txhash 
orange - entries in activepid table 
mangoes - entries in transaction history table 

CURRENT SYSTEM 
given a block , find out all the oranges in the block 
given a block, find out all the bananas in the block and 
for each banana, find corresponding databases( found through parsing of banana flodata and banana txdata)
    -  if token database then rollback, if contractDatabase then delete entry 


NEW SYSTEM 
give a block , find out all the oranges in the block 
given a block, find out all the bananas in the block and their corresponding databases( found through parsing of banana flodata and banana txdata)
    - start opening all those databases one by one | if token database then rollback, if contractDatabase then delete entry 

send transaction -> receive the databases associated with it 
        
'''

'''
Step 1 
The block that we are rolling back into is earlier than the database creation blockNumber, then delete the whole database without rolling back. Do this for both token databases and smart contract databases 

Step 2 
If the rolling back block is later than database creation blockNumber, then invoke rollback a database function( rollback_database ) 

Step 3 
Create a list of databases to be opened, and creation date (creation date is block number). This will exclude the token and smart contract databases which are already deleted 

Step 4
For each of the database to be opened, rollback the database to rollback point 
rollback_database will take 2 inputs, a block number to which it has to rollback to and the name of the database 

Step 5 
Create a delete function, which will delete from transactionHistory, latestCache and contractDatabase 

To-do 
------
* Integrate all the functions in the following order: 
    1 , 2 , 3 , 4 , 5 | That will finish the operation of taking the block number as input and the roll back function will rollback upto the block number specified for all kinds of databases and all kinds of transactions 

'''