from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as GeckoService
from selenium.webdriver.common.by import By

# Paths to the drivers
CHROME_DRIVER_PATH = r"C:\\Users\\91817\\Desktop\\AQI-Predictor\\data_fetcher\\chromedriver.exe"
GECKO_DRIVER_PATH = r"C:\\Users\\91817\\Desktop\\AQI-Predictor\\data_fetcher\\geckodriver.exe"

# Path to the Firefox binary
FIREFOX_BINARY_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"

def fetch_data_with_chrome(url):
    # Setup Chrome driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Run browser in headless mode
    chrome_service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    
    try:
        chrome_driver.get(url)
        print("Chrome Browser Title:", chrome_driver.title)  # Fetching the page title
    finally:
        chrome_driver.quit()

def fetch_data_with_gecko(url):
    # Setup Gecko (Firefox) driver
    gecko_options = webdriver.FirefoxOptions()
    gecko_options.binary_location = FIREFOX_BINARY_PATH  # Specify Firefox binary path
    gecko_options.add_argument('--headless')  # Run browser in headless mode
    gecko_service = GeckoService(executable_path=GECKO_DRIVER_PATH)
    gecko_driver = webdriver.Firefox(service=gecko_service, options=gecko_options)
    
    try:
        gecko_driver.get(url)
        print("Firefox Browser Title:", gecko_driver.title)  # Fetching the page title
    finally:
        gecko_driver.quit()

if __name__ == "__main__":
    # URL to fetch data from
    target_url = "https://www.youtube.com/"
    
    print("Fetching data using Chrome:")
    fetch_data_with_chrome(target_url)
    
    print("\nFetching data using Gecko (Firefox):")
    fetch_data_with_gecko(target_url)
