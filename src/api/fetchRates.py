import requests
import json
import sqlite3
import os
from config import *
import requests
import json
import sqlite3
import os
from config import *
import time

RETRY_TIMEOUT_DB = 60 # 60 sec
RETRY_TIMEOUT_REQUEST = 10 * 60 # 10 minsd

prices = {}
# 1. fetch old price data if its there, else create an empty db 
def connect_database():
    if not os.path.isfile("prices.db"):
        # create an empty db
        while True:
            try:
                conn = sqlite3.connect('prices.db')
                c = conn.cursor()
                c.execute('''CREATE TABLE ratepairs
                        (id integer primary key, ratepair text, price real)''')
                c.execute("INSERT INTO ratepairs(ratepair, price) VALUES ('BTCBTC', 1)")
                c.execute("INSERT INTO ratepairs(ratepair, price) VALUES ('BTCUSD', -1)")
                c.execute("INSERT INTO ratepairs(ratepair, price) VALUES ('BTCINR', -1)")
                c.execute("INSERT INTO ratepairs(ratepair, price) VALUES ('USDINR', -1)")
                c.execute("INSERT INTO ratepairs(ratepair, price) VALUES ('FLOUSD', -1)")
                conn.commit()
                conn.close()
            except:
                print(f"Unable to create prices.db, retrying in {RETRY_TIMEOUT_DB} sec")
                time.sleep(RETRY_TIMEOUT_DB)
            else:
                break
                

    # load old price data 
    # load older price data
    global prices
    while True:
        try:
            conn = sqlite3.connect('prices.db')
            c = conn.cursor()
            ratepairs = c.execute('select ratepair, price from ratepairs')
            ratepairs = ratepairs.fetchall()           
            for ratepair in ratepairs:
                ratepair = list(ratepair)
                prices[ratepair[0]] = ratepair[1]
        except:
            print(f"Unable to read prices.db, retrying in {RETRY_TIMEOUT_DB} sec")
            time.sleep(RETRY_TIMEOUT_DB)
        else:
            break

# 2. fetch new price data
def fetch_newprice():
    global prices
    while True:
        try:
            # apilayer
            response = requests.get(f"http://apilayer.net/api/live?access_key={apilayerAccesskey}")
            try:
                price = response.json()
                prices['USDINR'] = price['quotes']['USDINR']
                break
            except ValueError:
                print('Json parse error. retrying in {RETRY_TIMEOUT_REQUEST} sec')
                time.sleep(RETRY_TIMEOUT_REQUEST)
        except:
            print(f"Unable to fetch new price data, retrying in {RETRY_TIMEOUT_REQUEST} sec")
            time.sleep(RETRY_TIMEOUT_REQUEST)
          

def fetch_bitpay_or_coindesk():
    # bitpay
    global prices
    while True:
        print("Trying bitpay API")
        try:
            response = requests.get('https://bitpay.com/api/rates')
            bitcoinRates = response.json()
            for currency in bitcoinRates:
                if currency['code'] == 'USD':
                    prices['BTCUSD'] = currency['rate']
                elif currency['code'] == 'INR':
                    prices['BTCINR'] = currency['rate']
        except ValueError:
            print("Json parse error in bitpay")
        except:
            print(f"Unable to fetch bitpay")
        else:
            break # if data is accrued from bitpay, break from loop and procees to next process
        print("Trying coindesk API")
        # coindesk
        try:
            response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
            price = response.json()
            prices['BTCUSD'] = price['bpi']['USD']['rate']
        except ValueError:
            print(f'Json parse error in coindesk')
        except:
            print(f"Unable to fetch coindesk")
        else:
            break # if data is accrued from coindesk, break from loop and procees to next process

        print(f"Retrying in {RETRY_TIMEOUT_REQUEST} sec")
        time.sleep(RETRY_TIMEOUT_REQUEST)


# cryptocompare
def fetch_cryptocompare():
    while True:
        try:
            response = requests.get('https://min-api.cryptocompare.com/data/histoday?fsym=FLO&tsym=USD&limit=1&aggregate=3&e=CCCAGG')
            price = response.json()
            prices['FLOUSD'] = price['Data'][-1]['close']
        except ValueError:
            print(f'Json parse error in cryptocompare, retrying in {RETRY_TIMEOUT_REQUEST} sec')
        except:
            print(f"Unable to fetch cryptocompare, retrying in {RETRY_TIMEOUT_REQUEST} sec")
        else:
            break # if data is accrued from coindesk, break from loop and procees to next process

# 3. update latest price data
def update_latest_prices():
    while True:
        try:
            conn = sqlite3.connect('prices.db')
            c = conn.cursor()
            for pair in list(prices.items()):
                pair = list(pair)
                c.execute(f"UPDATE ratepairs SET price={pair[1]} WHERE ratepair='{pair[0]}'")
            conn.commit()
        except:
            print(f"Unable to write to prices.db, retrying in {RETRY_TIMEOUT_DB} sec")
            time.sleep(RETRY_TIMEOUT_DB)
        else:
            break

connect_database()
fetch_newprice()
fetch_bitpay_or_coindesk()
fetch_cryptocompare()
print('\n\n')
print(prices)
update_latest_prices()