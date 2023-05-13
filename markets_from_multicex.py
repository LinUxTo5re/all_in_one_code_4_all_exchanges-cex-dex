"""
this file will ask for list of exchanges or get all ccxt.exchanges() as
list. next, it'll ask for list of markets. user can pass list of markets
or it'll load existing markets from common_markets.xlsx Excel file.

"""

# Importing
import ccxt
import pandas as pd
from load_exchanges_filter_quote import loadFilterMarkets
from excel_read_write import readxlsxfile, writexlsxfile

# Global variables
exchanges_names = markets_names = list()
multicex = dict()
prices = []


# class hold all methods
class multicex_markets:
    # default constructor
    def __init__(self):
        pass

    # can pass list of exchanges or take ccxt.exchanges() as list
    def exchange_select(self):
        global exchanges_names
        obj = loadFilterMarkets()
        exchange_list = input('wanna pass exchanges? Y/N: ')
        if exchange_list == 'Y' or exchange_list == 'y':
            exchanges_names = obj.exchange_selection(islist=True)  # pass list of exchanges
        else:
            exchanges_names = obj.exchange_selection(islist=False)  # ccxt.exchanges() as list
        self.load_data()  # calling load_data() to pass list of markets

    def load_data(self):
        global markets_names, prices
        market_list = input('wanna pass markets? Y/N: ')
        if market_list == 'Y' or market_list == 'y':
            print("Enter markets: ")
            markets_names = input().split()  # user pass list of markets as list
        else:  # read existing file 'common_markets.xlsx' for markets list
            print('loading markets from existing excel file......')
            # df = pd.read_excel('common_market.xlsx', sheet_name='Common_markets_bt_cex')
            df = readxlsxfile()
            markets_names = df['market'].tolist()  # only getting market column as list

        self.loading_data_multicex()  # load data for exchanges/markets

        if len(prices) > 0:
            df = pd.DataFrame(prices)
            df = df.pivot(index='Exchange', columns='Market', values='Last Price')

            # filling empty rows with value = None
            df.fillna(value='None', inplace=True)
            writexlsxfile(df, 'multicex_markets.xlsx')  # delete existing if present and create new one to store data
        else:
            print('Information: No market data found')

    # load data for exchanges/markets
    def loading_data_multicex(self):
        global exchanges_names, markets_names, prices
        for exchange in exchanges_names:
            try:
                exchange_class = getattr(ccxt, exchange)()
                for market in markets_names:
                    try:
                        exchange_prices = exchange_class.fetch_ticker(market)  # fetching market
                        prices.append(
                            {'Exchange': exchange, 'Market': market, 'Last Price': exchange_prices['last']})
                        exchange_prices.clear()
                        print(f'Successfully fetched {market} from {exchange}')
                    except Exception as e:
                        print(f'Information: {market} market not available for {exchange}')
            except Exception as e:
                print(f"Error fetching data from {exchange}: {e}")


# Entry point of python (optional)
if __name__ == '__main__':
    multicex_obj = multicex_markets()
    multicex_obj.exchange_select()
