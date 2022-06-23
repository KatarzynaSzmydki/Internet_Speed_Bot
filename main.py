from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from time import sleep
from datetime import datetime
import pandas as pd
from os.path import exists
from twilio.rest import Client
import pygsheets


URL_SPEEDTEST = 'https://www.speedtest.net/'
URL_POST = 'https://www.speedtest.net/'
with open('credentials.txt') as f:
    credentials = json.loads(f.read())
chrome_driver_path = "C:/Users/kszmy/Desktop/chromedriver.exe"
GS_CREDENTIALS_PATH = "C:\\Users\\kszmy\\PycharmProjects\\Internet_Speed_Bot\\weather-email-sender-7143f7051a34.json"
PROMISED_DOWN = 160
PROMISED_UP = 10


class InternetSpeedTwitterBot:
    def __init__(self):
        self.driver = webdriver.Chrome(chrome_driver_path)
        self.test_time = None
        self.result_data = None
        self.result_link = None
        self.down = 0
        self.up = 0
        self.driver.get(URL_SPEEDTEST)
        self.gc = pygsheets.authorize(service_file=GS_CREDENTIALS_PATH)
        self.sh = self.gc.open('Python_Speed_Test_Stats')

        self.get_internet_speed()

    def get_internet_speed(self):

        sleep(10)
        self.driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
        sleep(5)
        self.test_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.driver.find_element(By.CLASS_NAME, 'start-text').click()
        sleep(50)
        self.result_data = self.driver.find_element(By.CLASS_NAME, 'result-data a')
        self.result_link = self.result_data.get_attribute('href')
        self.down = self.driver.find_element(By.XPATH,
                                   '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[3]/div/div/div[2]/div[1]/div[2]/div/div[2]/span').text
        self.up = self.driver.find_element(By.XPATH,
                                 '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[3]/div/div/div[2]/div[1]/div[3]/div/div[2]/span').text

        print(f'Test executed at: {self.test_time}.\nDownload speed: {self.down}\nUpload speed: {self.up}')


        # Writing to table
        stats_onetime = {
            'test_time':self.test_time,
            'result_link':self.result_link,
            'down':self.down,
            'up':self.up
        }


        # Google Sheets
        # select the first sheet
        self.wks = self.sh[0]
        self.wks.append_table(list(stats_onetime.values()), start='A1', end=None, dimension='ROWS', overwrite=True)

        # stats_onetime_tbl = pd.DataFrame(stats_onetime, index=[0])
        #
        # if exists('stats.csv'):
        #     stats = pd.read_csv('stats.csv', index_col=0)
        #     stats_fin = pd.concat([stats, stats_onetime_tbl], ignore_index=True)
        # else:
        #     stats_fin = stats_onetime_tbl
        # stats_fin.to_csv('stats.csv')

        self.driver.quit()
        self.sms_alert()


    def sms_alert(self):

        # Send SMS if speed lower than promised
        if float(self.down) < PROMISED_DOWN or float(self.up) < PROMISED_UP:
            account_sid = credentials['sid']
            auth_token = credentials['token']
            client = Client(account_sid, auth_token)

            message = client.messages \
                .create(
                body=f'Test executed at: {self.test_time}.\nDownload speed: {self.down}\nUpload speed: {self.up}',
                from_='(323)529-0516',
                to='+48512736849'
            )
            # print(message.sid)

        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


bot = InternetSpeedTwitterBot()


