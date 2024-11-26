import sys, os

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time






class fetcher:
    def __init__(self, browser_path='undefined'):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')

            driver_path = r"./data_fetcher/chromedriver.exe"
            if browser_path != 'undefined':
                options.binary_location = browser_path
            self.driver = webdriver.Chrome(service=webdriver.chrome.service.Service(driver_path), options=options)
            print("Chrome driver initialized successfully.")
            return
        except WebDriverException as e:
            print(f"Failed to initialize Chrome driver: {e}")

        try:
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')

            driver_path = r"./data_fetcher/geckodriver.exe"
            if browser_path != 'undefined':
                options.binary_location = browser_path
            self.driver = webdriver.Firefox(service=webdriver.firefox.service.Service(driver_path), options=options)
            print("Firefox driver initialized successfully.")
            return
        except WebDriverException as e:
            print(f"Failed to initialize Firefox driver: {e}")

        print("Only Google Chrome and Mozilla Firefox are supported.")
        raise RuntimeError("No supported browser drivers could be initialized.")

    def get(self, target_date):
        tdate = target_date
        driver = self.driver

        # Open the target website
        driver.get('https://rp5.ru/Weather_archive_in_New_Delhi,_Indira_Gandhi_(airport),_METAR')
        driver.implicitly_wait(30)
        time.sleep(3)

        try:
            # Click on the "Archive" tab
            driver.find_element(By.XPATH, '//*[@id="tabMetarArchive"]').click()

            # Enter the target date
            text_field = driver.find_element(By.XPATH, '//*[@id="calender_archive"]')
            text_field.clear()
            text_field.send_keys(tdate)

            # Click the "Show" button
            driver.find_element(By.XPATH, '//*[@id="toScreenMenu"]/form/table/tbody/tr/td[5]/div').click()
            time.sleep(5)

            # Fetch temperature-related data
            t1 = driver.find_elements(By.CLASS_NAME, 'cl_rd')
            t2 = driver.find_elements(By.CLASS_NAME, 'cl_rd_nt')
            temp = sum(float(e.text) for e in t1 + t2) / len(t1 + t2) if t1 or t2 else None

            # Fetch pressure and visibility data
            ph = []
            p1 = driver.find_elements(By.CLASS_NAME, 'cl')
            p2 = driver.find_elements(By.CLASS_NAME, 'cl_nt')
            for e in p1 + p2:
                try:
                    ph.append(float(e.text))
                except ValueError:
                    pass

            pressure = sum(ph[::2]) / (len(ph) // 2) if ph else None
            hv = sum(ph[1::2]) / (len(ph) // 2) if ph else None

            # Fetch humidity and dew point temperature
            rl1 = driver.find_elements(By.CLASS_NAME, 'cl_bl')
            rl2 = driver.find_elements(By.CLASS_NAME, 'cl_bl_nt')

            hum = sum(float(rl1[i].text) for i in range(0, len(rl1))) / (len(rl1) // 2) if rl1 else None
            dt = sum(float(rl2[i].text) for i in range(1, len(rl2))) / (len(rl2) // 2) if rl2 else None

            # Populate initial data dictionary
            data_dict = {
                'Air Temperature': [temp],
                'Pressure Station Level': [pressure],
                'Relative Humidity': [hum],
                'Horizontal Visibility': [hv],
                'Dew Point Temperature': [dt],
            }

            # Navigate to statistics tab and fetch wind speed
            driver.find_element(By.XPATH, '//*[@id="tabMetarStatist"]').click()
            time.sleep(3)

            tf1 = driver.find_element(By.XPATH, '//*[@id="calender_stat"]')
            tf1.clear()
            tf1.send_keys(tdate)

            tf2 = driver.find_element(By.XPATH, '//*[@id="calender_stat2"]')
            tf2.clear()
            tf2.send_keys(tdate)

            driver.find_element(By.XPATH, '//*[@id="t_statist_synop_wv"]').click()
            time.sleep(3)
            driver.find_element(By.XPATH, '//*[@id="statistMenu"]/form/table/tbody/tr[3]/td/div[2]/div').click()
            time.sleep(3)

            wind_speed = driver.find_element(By.XPATH, '//*[@id="statist_synop_data_6"]/table/tbody/tr[2]/td[2]/div[1]').text
            data_dict['Wind Speed'] = [wind_speed]

            # Additional calculations: Day No. and Year
            d_list = tdate.split('.')
            ob_date = datetime(int(d_list[2]), int(d_list[1]), int(d_list[0]))

            start_date = datetime(ob_date.year, 1, 1)
            day_no = (ob_date - start_date).days + 1
            data_dict['Day No.'] = [str(day_no)]
            data_dict['Year'] = [str(ob_date.year)]

            # Fetch AQI data
            api_key = '9fa87bf6e5a0b3d4b957d94a8388b30f'
            lat = 28.6139
            lon = 77.2090
            today =datetime.now()
            yesterday = today - timedelta(days=1)
            timestamp_today_start = int(today.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            timestamp_yesterday_start = int(yesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            timestamp_today_end = int((today + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            aqi_url_today= f"https://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={timestamp_today_start}&end={timestamp_today_end}&appid={api_key}"
            aqi_url_yesterday = f"https://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={timestamp_yesterday_start}&end={timestamp_today_start}&appid={api_key}"
            response_today = requests.get(aqi_url_today)
            response_yesterday = requests.get(aqi_url_yesterday)
            if response_today.status_code == 200 and response_yesterday.status_code == 200:
                data_today = response_today.json()
                data_yesterday = response_yesterday.json()
                
                def extract_pollutant_data(data):
                    pollutants = {'PM10': [], 'NO2': [], 'SO2': []}
                    if 'list' in data:
                        for entry in data['list']:
                            if 'components' in entry:
                                pollutants['PM10'].append(entry['components'].get('pm10', None))
                                pollutants['NO2'].append(entry['components'].get('no2', None))
                                pollutants['SO2'].append(entry['components'].get('so2', None))
                    return pollutants
                
                pollutants_today = extract_pollutant_data(data_today)
                pollutants_yesterday = extract_pollutant_data(data_yesterday)

                def calculate_average(values):
                    valid_values = [v for v in values if v is not None]
                    if valid_values:
                        return sum(valid_values) / len(valid_values)
                    else:
                        return None
                    
                avg_pm10_today = calculate_average(pollutants_today['PM10'])
                avg_no2_today = calculate_average(pollutants_today['NO2'])
                avg_so2_today = calculate_average(pollutants_today['SO2'])
                avg_pm10_yesterday = calculate_average(pollutants_yesterday['PM10'])
                avg_no2_yesterday = calculate_average(pollutants_yesterday['NO2'])
                avg_so2_yesterday = calculate_average(pollutants_yesterday['SO2'])
                data_dict['PM10'] = [avg_pm10_today]
                data_dict['NO2'] = [avg_no2_today]
                data_dict['SO2'] = [avg_so2_today]
                data_dict['D-1 PM10'] = [avg_pm10_yesterday]
                data_dict['D-1 NO2'] = [avg_no2_yesterday]
                data_dict['D-1 SO2'] = [avg_so2_yesterday]
        except Exception as e:
            print(f"Error while fetching data: {e}")
            return {}

        return data_dict
    
    def close(self):
        self.driver.close()

# {'Air Temperature': [16.979591836734695],
#  'Pressure Station Level': [763.0775510204081],
#  'Relative Humidity': [75.08163265306122],
#  'Horizontal Visibility': [2.8857142857142866],
#  'Dew Point Temperature': [12.244897959183673],
#  'Day No.': ['21'],
#  'Year': ['2020'],
#  'PM10': ['162.94'],
#  'NO2': ['42.81'],
#  'SO2': ['14.24'],
#  'D-1 PM10': ['180.89'],
#  'D-1 NO2': ['70.19'],
#  'D-1 SO2': ['19.14']}
