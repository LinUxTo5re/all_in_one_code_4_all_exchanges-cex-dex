# Importing Libraries
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from time import sleep
import pandas as pd
from read_write_hottokens import writexlsxfile

class hotTokens:
    def __init__(self):
        pass

    driver = chrome_driver_path = chrome_options = ''
    eth_bsc_hot_tokens = pd.DataFrame()

    def start_chrome_drivers(self):
        global driver, chrome_options, chrome_driver_path
        # Optional: Set the path to the ChromeDriver executable
        chrome_driver_path = '~/Downloads/chromedriver'
        # Set Chrome options to run the browser in headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Comment this line to see the browser in action
        # Instantiate the Chrome web driver
        driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
        return self.load_hot_tokens_selected_network()

    # select network from bsc/ethereum (eigenphi.io)
    def load_hot_tokens_selected_network(self):
        global eth_bsc_hot_tokens
        urls = ['https://eigenphi.io/mev/ethereum/tokens/hot', 'https://eigenphi.io/mev/bsc/tokens/hot']
        # Load the web page
        for index, main_url in enumerate(urls):
            driver.get(main_url)
            wait = WebDriverWait(driver, 10)  # Set an explicit wait time (in seconds)
            element_24h = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='24H']")))
            element_24h.click()
            self.scrapping_tokens(wait, index)
        return eth_bsc_hot_tokens

    def scrapping_tokens(self, wait, index):
        global eth_bsc_hot_tokens, chrome_options, chrome_driver_path
        try:
            # Wait for the elements to be present on the page
            elements = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@class='mantine-Text-root mantine-iz66j5']")))
            all_matches = []
            network = 'ethereum' if index == 0 else 'bsc'
            for element in elements[:30]:
                address = element.get_attribute("href").split('/')[-1]
                text = element.text
                if text == '':
                    dex_url = f'https://api.dexscreener.com/latest/dex/tokens/{address}'
                    response = requests.get(dex_url)
                    token_data = response.json()
                    pairs = token_data.get('pairs', [])
                    if pairs:
                        if address.lower() == pairs[0]['baseToken']['address'].lower():
                            text = pairs[0]['baseToken']['symbol']
                        else:
                            text = pairs[0]['quoteToken']['symbol']
                    else:
                        url = f'https://eigenphi.io/mev/{network}/token/{address}'
                        driver2 = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
                        driver2.get(url)
                        sleep(10)
                        elements = driver2.find_elements(By.XPATH,
                                                         "//table[@class='mantine-Table-root mantine-1n4st5i']")
                        if elements:
                            table_element = elements[0]  # Assuming only one matching table element
                            tr_elements = table_element.find_elements(By.XPATH, ".//tr")
                            if len(tr_elements) > 1:
                                second_tr_element = tr_elements[1]  # Assuming at least two <tr> elements
                                td_elements = second_tr_element.find_elements(By.XPATH, ".//td")
                                if len(td_elements) > 1:
                                    second_td_element = td_elements[1]  # Assuming at least two <td> elements
                                    title = second_td_element.get_attribute("title")
                                    text = title
                        driver2.quit()
                all_matches.append((address, text))
        except TimeoutException:
            print("Timeout: Elements not found within the specified time.")
        finally:
            df = pd.DataFrame(all_matches, columns=['Address', 'Token'])
            if len(all_matches) == 30:
                if network == 'ethereum':
                    eth_bsc_hot_tokens = df.copy()
                else:
                    eth_bsc_hot_tokens = pd.concat([eth_bsc_hot_tokens, df], axis=0)
                    # Reset the index of the dataframe
                    eth_bsc_hot_tokens = eth_bsc_hot_tokens.reset_index(drop=True).reindex(range(len(eth_bsc_hot_tokens)))
                    # Reindex the dataframe using the range of numbers
                    # eth_bsc_hot_tokens = eth_bsc_hot_tokens.reindex(range(len(eth_bsc_hot_tokens)))

                # print(f"'total {network} tokens:' {len(all_matches)}, 'tokens:' ")
                # print(df)
                return eth_bsc_hot_tokens
            else:
                print(f"error: {network} got less hot tokens")
                eth_bsc_hot_tokens.clear()
                return False


if __name__ == '__main__':
    obj = hotTokens()
    writexlsxfile(obj.start_chrome_drivers())
