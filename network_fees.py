from credentials import bnb_secret_key, bnb_api_key
from excel_read_write import readxlsxfile
import ccxt

df = readxlsxfile()
df = df['market'].tolist()
markets_names = []
for market in df:
    markets_names.append(market.split('/')[0])  # will get btc if pair is btc/usdt

with open('network_fee.txt', 'w') as file:
    
    for market in markets_names:
        pass

