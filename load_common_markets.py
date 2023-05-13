# load_markets_for_selected_exchanges() - don't call - call if have a list of exchanges
# exchange_selection() - call
# load_quote_assets_and_filter_common_assets() - call
# load_market_for_selected_quote_asset() - call
# find_common_markets() - don't call
# create_variables_for_selected_exchanges_assets() - don't call

'''
    this file will fetch data for common ticker from selected exchanges
    and save those into Excel file
'''

# Importing required libraried
from datetime import datetime
from time import sleep
from load_exchanges_filter_quote import loadFilterMarkets
import pandas as pd
import ccxt
import requests
import excel_read_write

# global variables to access all over the class
common_markets = exchanges = quote_asset = usdt_price_in_INR = []
Compared_Markets_Data = dict()  # Global variable to Store Market data after comparison
Markets_With_Problems = list()  # Will store USDT markets with problems like inactive/NoneType etc


class loadCommonMarkets:

    def __init__(self):
        pass

    # Comparing tickers/market with both exchanges
    def compare_tickers_with_both_markets(self, usdt_price_in_inr, first_market, second_market, market_, count,
                                          conversion_price=None):
        global Compared_Markets_Data
        global Markets_With_Problems, market_datetime

        try:
            if first_market['last'] is not None and second_market['last'] is not None:
                if first_market['bid'] is not None or first_market['ask'] is not None:
                    if second_market['bid'] is not None or second_market['ask'] is not None:
                        first_market_price = float('{:.10f}'.format(first_market.get('last')).rstrip('0').rstrip('.'))
                        second_market_price = float('{:.10f}'.format(second_market.get('last')).rstrip('0').rstrip('.'))

                        if first_market['datetime'] is None:
                            if second_market['datetime'] is not None:
                                market_datetime = second_market['datetime'].split(':')
                            else:
                                market_datetime = datetime.now()
                        else:
                            market_datetime = first_market['datetime'].split(':')
                        # first_market_price = float('{:.10f}'.format(first_market_price))
                        # second_market_price = float('{:.10f}'.format(second_market_price))

                        if conversion_price is not None:
                            first_market_price, second_market_price = first_market_price * conversion_price, second_market_price * conversion_price

                        difference_spread_usdt = round(second_market_price - first_market_price,
                                                       2) if second_market_price > first_market_price else round(
                            first_market_price - second_market_price, 2)
                        if difference_spread_usdt > 0.1:  # to continue, usdt diffr should be greater than 0.1 usdt
                            high_priced_exchange = str(
                                exchanges[1]) if second_market_price > first_market_price else str(exchanges[0])
                            difference_percentage_ = round((difference_spread_usdt / (
                                second_market_price if second_market_price > first_market_price else first_market_price)) * 100,
                                                           2)
                            if difference_percentage_ < 50: # market with diffr >= 50% will be ignored. those market may
                                # duplicate with same name
                                percentage_diff1 = (first_market['ask'] - first_market['bid']) / (
                                        (first_market['ask'] + first_market['bid']) / 2) * 100
                                if not percentage_diff1 > 2 or percentage_diff1 < -2: # ask/bid diffr must not be
                                    # greater than/less than 2%. otherwise ignore those market
                                    percentage_diff1 = (second_market['ask'] - second_market['bid']) / (
                                            (second_market['ask'] + second_market['bid']) / 2) * 100
                                    if not percentage_diff1 > 2 or percentage_diff1 < -2:
                                        market = {
                                            'market': market_,
                                            # 'date_time': market_datetime,
                                            'first_market_price': first_market_price,
                                            'second_market_price': second_market_price,
                                            'difference_spread_usdt': difference_spread_usdt,
                                            'difference_spread_usdt_inr': round(
                                                usdt_price_in_inr * difference_spread_usdt, 2),
                                            'difference_percentage_%': str(round(difference_percentage_, 2)) + '%',
                                            'high_priced_exchange': high_priced_exchange,
                                        }

                                        Compared_Markets_Data[market_] = market
                                        print(Compared_Markets_Data)
                                    else:
                                        print('Information: difference is huge b/w ask/bid price. Ignoring.')
                                else:
                                    print('Information: difference is huge b/w ask/bid price. Ignoring.')
                            else:
                                print('Information: difference is huge. Ignoring. Might be duplicate coin with same ID')
                        else:
                            print('Information: small difference in usdt. Ignoring.')
                    else:
                        print('Information: missing bid/ask price for second_market')
                else:
                    print('Information: missing bid/ask price for first_market')
            else:
                Markets_With_Problems.append(market_)
        except Exception as e:
            print('Error: falied to comapre tickers from both markets- ' + str(e))

        if count == len(common_markets) and len(Compared_Markets_Data) > 0:
            self.convert_into_dataframe(Compared_Markets_Data)
        else:
            print('Information: No market data found')

    # Fetching data for specific ticker from both exchanges and passing as argument to method
    def fetch_ticker_from_both_markets(self, usdt_price_in_inr, quote_asset, count=None):
        global conversion_price
        count = 0
        Compared_Markets_Data.clear()
        Markets_With_Problems.clear()
        try:
            try:
                for exchange in exchanges:
                    globals()[exchange] = getattr(ccxt, exchange)({'enableRateLimit': True, 'rateLimit': 500})
                    if not globals()[exchange].has.get('fetchTicker'):
                        print(f"{globals()[exchange]} doesn't have fetchticker. redirecting to select another pair of "
                              f"exchanges")
                        self.startmainmethod(True)
                delay = 1 if 'wazirx' in exchanges else 0

            except Exception as e:
                print('Error: failed to create varialbe for exchange ' + str(e))

            isQuoteAssetUSDT = True
            if not str(''.join(quote_asset)) == 'usdt':
                isQuoteAssetUSDT = False
                # for non-usdt quote, will convert that rate into usdt for better understading
                conversion_price = self.convert_quote_to_usdt(quote_asset)

            for market_num, MARKET in enumerate(common_markets): # comparing common markets one by one through loop
                print(f"Information: Started Comparing: {market_num + 1} --> {MARKET}")
                count = count + 1
                first_market = second_market = ''
                if market_num % 14 == 0:
                    sleep(5)
                for idx, exchange in enumerate(exchanges):
                    if exchange in globals():
                        if idx == 0:
                            first_market = globals()[exchange].fetch_ticker(MARKET)
                        if idx == 1:
                            second_market = globals()[exchange].fetch_ticker(MARKET)
                sleep(delay)  # delayed when wazirx is one of selected exchange
                '''first_market = globals()[exchanges[0]].fetch_ticker(MARKET)
                globals()[str(exchanges[0])]
                second_market = globals()[exchanges[1]].fetch_ticker(MARKET)'''
                if not isQuoteAssetUSDT: # execute for usdt quote
                    self.compare_tickers_with_both_markets(usdt_price_in_inr, first_market, second_market, MARKET,
                                                           count,
                                                           conversion_price)
                else: # execute for non-usdt quote like btc/usdc/busd etc
                    self.compare_tickers_with_both_markets(usdt_price_in_inr, first_market, second_market, MARKET,
                                                           count)

                # sleep(1)
                print('{}: {} completed'.format(count, str(MARKET)))
                print('----------------------------------------------------------------------------------------')
            print('Total Active Markets: {} \n Total Inactive markets: {}'.format(len(Compared_Markets_Data),
                                                                                  len(Markets_With_Problems)))
        except Exception as e:
            print("Error: failed to fetch ticker- " + str(e))

    '''
        if select quote asset instead of usdt then convert there price
        into usdt for easier understanding
    '''

    def convert_quote_to_usdt(self, selected_quote):
        try:
            # Define the API endpoint and parameters
            endpoint = 'https://api.binance.com/api/v3/ticker/price'
            params = {'symbol': str(''.join(selected_quote)).upper() + 'USDT'}
            # Send a GET request to the API endpoint
            response = requests.get(endpoint, params=params)

            # Extract the exchange rate from the response JSON
            if response.status_code == 200:
                json_data = response.json()
                return float(json_data['price'])
            else:
                print(f"warning: Failed to convert {str(selected_quote).split('/')[0].upper()} into USDT")
                return 0
        except Exception as e:
            print("Error: " + str(e))

    '''
     converting data into DataFrame
    '''

    def convert_into_dataframe(self, Compared_Markets_Data):
        df = pd.DataFrame(Compared_Markets_Data)
        df = df.transpose()
        # calling function to write file with dataframe
        excel_read_write.writexlsxfile(df, 'common_market.xlsx', exchanges)
    '''
        starting point of this class
    '''
    def startmainmethod(self, iscalledagain=None):
        global common_markets, exchanges, quote_asset, usdt_price_in_INR
        obj = loadFilterMarkets()
        common_markets, exchanges, quote_asset = obj.find_common_markets(iscalledagain)
        print(common_markets)
        print(exchanges)

        wazirx = ccxt.wazirx({'enableRateLimit': True})
        usdt_price_in_INR = wazirx.fetch_ticker('USDT/INR')
        usdt_price_in_INR = float('{:.10f}'.format(usdt_price_in_INR.get('last')).rstrip('0').rstrip('.'))
        sleep(1)

        if usdt_price_in_INR is not None:
            self.fetch_ticker_from_both_markets(usdt_price_in_INR, quote_asset)
        else:
            Markets_With_Problems.append('USDT/INR')


if __name__ == '__main__':
    obj = loadCommonMarkets()
    obj.startmainmethod()
