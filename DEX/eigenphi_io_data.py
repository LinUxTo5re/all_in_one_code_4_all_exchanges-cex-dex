import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


class hottokens:

    def __int__(self):
        pass

    url = soup = select_network = driver = ''

    def start_chrome_drivers(self):
        global driver
        # Set the path to the ChromeDriver executable
        chrome_driver_path = '~/Downloads/chromedriver'

        # Set Chrome options to run the browser in headless mode
        chrome_options = Options()

        chrome_options.add_argument('--headless')  # Comment this line to see the browser in action

        # Instantiate the Chrome web driver
        driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

        return self.selected_network()

    # select network from bsc/ethereum (eigenphi.io)
    def selected_network(self):
        global url, select_network
        select_network = int(input("""Press\n 1) bsc network\n 2) ethereum network\n"""))
        # Load the web page
        while True:
            if select_network == 1:
                url = 'https://eigenphi.io/mev/bsc/tokens/hot'
                # select_network = 'bsc'
                break
            elif select_network == 2:
                url = 'https://eigenphi.io/mev/ethereum/tokens/hot'
                # select_network = 'ethereum'
                break
            else:
                print('Incorrect choice, select again')
                select_network = int(input("""Press\n 1) bsc network\n 2) ethereum network\n"""))

        return self.read_page_prettify()

    # read page and prettify using bs4

    def read_page_prettify(self):
        global url, soup, driver
        driver.get(url)
        # Wait for the page to fully render
        # You can increase the sleep time if needed
        time.sleep(5)
        # Get the page source after JavaScript execution
        page_source = driver.page_source
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        # release driver
        driver.quit()

        return self.return_hot_tokens()

    # storing hot tokens into list

    def return_hot_tokens(self):
        span = soup.find_all('div', class_="mantine-Group-root mantine-17684dt")
        hot_tokens = {}
        tokens_list = []
        for p in span:
            tokens_list = p.text.split('#')
            del tokens_list[0]
            for token in tokens_list[:int(len(tokens_list) / 2)]:
                token_number = int(re.sub(r'\D', '', token))
                token_symbol = re.sub(r'\d+', '', token)
                hot_tokens.update({token_number: token_symbol})
            break
        print('Information: web scraping completed for hot tokens')
        return hot_tokens

    """
    it'll take more time as might've more than 2M risk token and 250K honeypot.
    so, ignoring this function for now.
        # getting list of malicious token related to previously selected network
        def malicious_tokens(self, network):
        global url
        # malicious tokens
        url = f'https://eigenphi.io/mev/{network}/tokens/malicious'

    """


class flashloan:
    pass
    """
    holding it for now, no more data available around this.
    data isn't available for bsc network
    """


if __name__ == '__main__':
    obj = hottokens()
    for hot_token in list(obj.start_chrome_drivers().items()):
        print(hot_token)
