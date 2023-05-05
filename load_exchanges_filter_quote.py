"""
this file will load exchanges and ask to select at least two exchanges.
based on these exchanges it'll show quote assets for these exchanges.
then it'll filter common quote assets from these exchanges.
again code will ask to select at least one quote asset. so, we can load
makrets for this/these quote assets from those exchanges.
final output will be common markets from those exchanges.
"""

# Importing Required libraries
import ccxt


# declaring global variables
exchanges_to_compare, exchanges_names = 0, []
unique_quote_assets = set()
quote_assets_specific_2_exchange = dict()
variable_name = ''
assets_names = assets_names_final = assets_copied = []

'''
    exchanges selection by user.
    exchanges number should be greater than 1 and less than 
    maximum length of ccxt.exchages length.
'''
class loadFilterMarkets:

    def __init__(self):
        pass

    def exchange_selection(self):
        while True:
            try:
                global exchanges_to_compare, exchanges_names
                exchanges_to_compare = int(
                    input(f"How many exchanges do you want to compare? (Total: {len(ccxt.exchanges)} exchanges): "))

                if exchanges_to_compare < 2 or exchanges_to_compare > len(ccxt.exchanges):
                    raise ValueError(f"Number of exchanges should be between 2 and {len(ccxt.exchanges)}.")

                print(f'{list(ccxt.exchanges)}')
                print("\nEnter exchanges names with space between: ")
                exchanges_names = input().split()[:exchanges_to_compare]

            except Exception as e:
                print(f"Error: {e}\n")

            else:
                self.create_variables_for_selected_exchanges_assets(
                    exchanges_names)  # calling function to create variables for selected exchanges
                print(f"Selected exchanges are: {exchanges_names}\n")
                break


    '''
    loading market data for selected exchanges
    '''


    def load_markets_for_selected_exchanges(self, exchange=None):
        if exchange is not None:
            exchange = getattr(ccxt, exchange)()
            return exchange.load_markets()
        else:
            for exchange_id, exchange in enumerate(exchanges_names):  # loading quote assets
                if exchange in globals():
                    exchange = getattr(ccxt, exchange)()
                    exchange = exchange.load_markets()
            return True


    '''
        loading quote assets for selected exchanges 
        and filtering unique assets from those exchanges
    '''


    def load_quote_assets_and_filter_common_assets(self):
        global unique_quote_assets, quote_assets_specific_2_exchange, exchanges_names

        if len(exchanges_names) == 0:
            self.exchange_selection()

        for exchange_id, exchange in enumerate(exchanges_names):  # loading quote assets
            quote_assets = set()
            try:
                if exchange in globals():
                    try:
                        globals()[exchange] = self.load_markets_for_selected_exchanges(exchange)
                    except Exception as e:
                        print("Error: loading market....")

                    for symbol in globals()[exchange]:
                        quote_assets.add(globals()[exchange][symbol]['quote'])

                    quote_assets_specific_2_exchange[str(exchanges_names[exchange_id])] = list(set(quote_assets))

                    if unique_quote_assets:  # if set isn't empty
                        unique_quote_assets.intersection_update(quote_assets)
                    else:  # if set is empty
                        unique_quote_assets = quote_assets

                else:
                    raise ValueError("Exchange not found")
            except Exception as e:
                print(f"Error: {str(e)}")

        quote_assets_specific_2_exchange['common quote assets'] = unique_quote_assets
        return unique_quote_assets


    '''
    load markets for selected quote assets based 
    on selected exchanges and store into 
    exchangeName_quoteAsset format
    '''


    def load_market_for_selected_quote_asset(self):
        global assets_names, assets_copied
        if len(unique_quote_assets) == 0:
            self.load_quote_assets_and_filter_common_assets()

        print(f'{list(unique_quote_assets)}')
        asset_to_load_market = input(
            f"select at least one asset to proceed <space> (Total: {len(unique_quote_assets)} assets): ")
        assets_names = asset_to_load_market.split(' ')
        assets_copied = assets_names.copy()

        if len(assets_names) == 0 or len(assets_names) > len(unique_quote_assets):
            raise ValueError(f"Number of assets should be between 1 and {len(unique_quote_assets)}.")

            # calling function to create variables for quote_assets (Format: exchange_quoteasset)
        self.create_variables_for_selected_exchanges_assets(exchanges_names, assets_names)
        assets_names.clear()
        assets_names = assets_names_final.copy()
        for asset_id, asset in enumerate(assets_copied):  # ex- asset = 'usdt', asset_id = 0
            for exchange_id, exchange in enumerate(exchanges_names):  # ex- exchange = 'bybit', exchange_id = 0
                for asset_var_id, asset_var in enumerate(assets_names):  # ex- asset_var = 'bybit_usdt', asset_var_id = 0
                    if asset_var.startswith(str(exchange)) and asset_var.endswith(str(asset)):
                        if (asset_var in globals()) and (exchange in globals()):
                            try:
                                temp_store = self.load_markets_for_selected_exchanges(exchange)
                                globals()[asset_var] = []
                                for market in temp_store:
                                    if market.endswith(str(asset).upper()):
                                        globals()[asset_var].append(market)
                            except Exception as e:
                                print("Error: while loading market")


    '''
        this function will find common markets like common USDT markets
        from selected exchanges
    '''


    def find_common_markets(self):
        global assets_names, assets_copied, variable_name

        for market in assets_copied:  # ex- market = 'usdt'
            filtered_markets_variables = list(filter(lambda k: k.endswith(str(market).lower()), globals().keys()))
            self.create_variables_for_selected_exchanges_assets(
                final_market=market)  # ex- final_market_usdt, final_market_btc etc

            if set(filtered_markets_variables).issubset(set(globals().keys())):
                common_markets = set()
                for common_market in range(len(filtered_markets_variables)):
                    common_market_1 = set(globals()[filtered_markets_variables[common_market]])

                    if common_market != len(filtered_markets_variables) - 1:
                        common_market_next = set(globals()[filtered_markets_variables[common_market + 1]])

                    if common_market == 0:
                        globals()[variable_name] = common_market_1.intersection(common_market_next)
                    else:
                        if common_market == len(filtered_markets_variables) - 1:
                            break
                        else:
                            globals()[variable_name] = globals()[variable_name].intersection(common_market_next)


    '''
    function will create variables for exchanges_names/unique_quote_assets/final markets
    so, we can use these variables later to assign values.
    also, all created varaibles can be found in globals().keys()
    '''


    def create_variables_for_selected_exchanges_assets(self, exchanges_names=None, unique_quote_assets=None, final_market=None):
        global variable_name

        if final_market is not None:
            variable_name = f"final_market_{final_market.lower()}"  # final_market_usdt
            globals()[variable_name] = []
        else:
            assets_names_final.clear()
            exchanges = {name: getattr(ccxt, name)() for name in exchanges_names}

            # create variables for entered exchanges
            for exchange_name, exchange_instance in exchanges.items():
                globals()[exchange_name] = exchange_instance
                
                if unique_quote_assets is not None:  # code will run when creating variables for quote_assets
                    for quote in unique_quote_assets:
                        variable_name = f"{exchange_name}_{quote.lower()}"
                        globals()[variable_name] = variable_name
                        assets_names_final.append(variable_name)


if __name__ == '__main__':
    my_market = loadFilterMarkets()
    my_market.load_market_for_selected_quote_asset()
    my_market.find_common_markets()

    """
    create_variables_for_selected_exchanges_assets() - this function will create variables for selected exchanges/
    unique quote assets/final markets

    find_common_markets() - this function will give final markets based on provided exchanges and quote assets
    such as for binance/wazirx/bybit if our unique quote assets are usdt and btc then this function will get common
    final markets for usdt and btc from selected exchanges

    load_quote_assets_and_filter_common_assets() - this function will load quote assets for selected exchanges and will 
    find common quote assets for those exchange

    load_market_for_selected_quote_asset() - this function will load market for selected quote assets based on selected 
    exchanges

    load_markets_for_selected_exchanges() - will run ccxt.exchange() function to load markets for selected exchanges
    for example- bybit = ccxt.bybit()

    exchange_selection() - this function will list the available exchanges in ccxt library and ask to select at lest
    two exchanges to proceed with other operation

    """
