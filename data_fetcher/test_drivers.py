from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Paths to the WebDriver executables
chrome_path = r"C:\\Users\\91817\\Desktop\\AQI-Predictor\\data_fetcher\\chromedriver.exe"
firefox_path = r"C:\\Users\\91817\\Desktop\\AQI-Predictor\\data_fetcher\\geckodriver.exe"

try:
    # Testing ChromeDriver
    chrome_driver = webdriver.Chrome(service=ChromeService(executable_path=chrome_path))
    print("ChromeDriver is working correctly.")
    chrome_driver.quit()
except Exception as e:
    print(f"Error with ChromeDriver: {e}")

try:
    # Testing GeckoDriver (Firefox)
    firefox_options = FirefoxOptions()
    firefox_options.binary_location = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"  # Update if needed
    firefox_driver = webdriver.Firefox(
        service=FirefoxService(executable_path=firefox_path),
        options=firefox_options
    )
    print("FirefoxDriver is working correctly.")
    firefox_driver.quit()
except Exception as e:
    print(f"Error with FirefoxDriver: {e}")
