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

            driver_path = r"C:\Users\91817\Desktop\AQI-Predictor\data_fetcher\chromedriver.exe"
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

            driver_path = r"C:\Users\91817\Desktop\AQI-Predictor\data_fetcher\geckodriver.exe"
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
            aqi_url = f"http://emis.wbpcb.gov.in/airquality/JSP/aq/fetch_val_ajax.jsp?district=010&date={ob_date.strftime('%d/%m/%Y')}&type=districtavg"
            response = requests.post(aqi_url)
            post_json = response.json()

            if post_json.get('status') != '0':
                for val in post_json.get('list', []):
                    if val['pname'] == 'PM10':
                        data_dict['PM10'] = [val['value'].strip()]
                    elif val['pname'] == 'NO2':
                        data_dict['NO2'] = [val['value'].strip()]
                    elif val['pname'] == 'SO2':
                        data_dict['SO2'] = [val['value'].strip()]

            # Fetch AQI data for the previous day
            prev_date = ob_date - timedelta(days=1)
            prev_aqi_url = f"http://emis.wbpcb.gov.in/airquality/JSP/aq/fetch_val_ajax.jsp?district=013&date={prev_date.strftime('%d/%m/%Y')}&type=districtavg"
            prev_response = requests.post(prev_aqi_url)
            prev_json = prev_response.json()

            if prev_json.get('status') != '0':
                for val in prev_json.get('list', []):
                    if val['pname'] == 'PM10':
                        data_dict['D-1 PM10'] = [val['value'].strip()]
                    elif val['pname'] == 'NO2':
                        data_dict['D-1 NO2'] = [val['value'].strip()]
                    elif val['pname'] == 'SO2':
                        data_dict['D-1 SO2'] = [val['value'].strip()]

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