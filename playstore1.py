import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
from datetime import date
import re
from selenium.webdriver.common.keys import Keys
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import traceback
import logging


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def scrapData(appLink):
    try:
        try:
            driver.execute_script(f"window.open('{appLink}', '_blank');")
        except Exception as e:
            print(e)
            pass
        driver.switch_to.window(driver.window_handles[-1])
        app_details = {
            "url":appLink,                
            "name": "-",
            "rating": "0",
            "downloads":"-",
            "reviews_count": "-",
            "rated_for":"-",
            "company_name":"-",
            "updated_on":'-',
            "id":'-',
            "description":"-",
            "website":"-",
            "support_email":"-",
            "developer_name":"-",
            "fetch_date":date.today(),
        }
        

        try:
            app_details["name"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[1]/div/div/div[1]/h1/span ').text.strip()
        except NoSuchElementException as e: 
            # print(e)
            pass
        try:
            app_details["rating"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[1]/div[1]/div/div').text.strip()
        except:
            pass
        try:
            app_details["downloads"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[2]/div[1]').text.strip()
        except NoSuchElementException:
            pass

        try:
            app_details["reviews_count"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[1]/div[2]').text.strip()
        except NoSuchElementException:
            pass
        try:
            app_details["rated_for"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[3]/div[2]/span/span').text.strip()
        except NoSuchElementException:
            pass
 
        try:
            app_details["company_name"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[1]/div/div/c-wiz/div[2]/div[1]/div/div/div[2]/div[1]/a/span').text.strip()
        except NoSuchElementException:
            pass    

        try:
            app_details["updated_on"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[2]/div/div[1]/div[1]/c-wiz[2]/div/section/div/div[2]/div[1]/div[2]').text.strip()
        except NoSuchElementException:
            pass 

        try:
            app_details["id"] = get_app_id(appLink)
        except:
            pass  

        try:
            app_details["description"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[2]/div/div[1]/div[1]/c-wiz[2]/div/section/div/div[1]').text.strip()
        except:
            pass

        try:
            website_link= driver.find_element(By.XPATH , '//*[@id="developer-contacts"]/div/div[1]/div/a')
            app_details["website"] = website_link.get_attribute("href")
        except:
            pass

        try:
            container = driver.find_element(By.XPATH, '//*[@id="developer-contacts"]/div/div[2]/div/a')
            name = container.get_attribute("href").replace("mailto:", "")
            app_details["support_email"] = name
        except:
            pass 

        try:
            app_details["developer_name"] = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div/div[2]/div/div[1]/div[1]/c-wiz[2]/div/section/div/div[2]/div[1]/div[2]').text()
        except:
            pass 


        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return app_details
    
    except Exception as e:
        # rank-=1
        print(f"Error scraping product ")
        print(traceback.format_exc())
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

def get_app_id(url):
    match = re.search(r'id=([a-zA-Z0-9._]+)', url)
    return match.group(1) if match else ""


def getApp():
    try:
        data_list = ["https://play.google.com/store/apps/details?id=scores.cricket.live.line&gl=ae",
                             "https://play.google.com/store/apps/details?id=com.einnovation.temu&gl=ae",
                             "https://play.google.com/store/apps/details?id=ae.uaepass.mainapp&gl=ae",
                             "https://play.google.com/store/apps/details?id=com.disneyplus.mea&gl=ae",
                             "https://play.google.com/store/apps/details?id=com.whatsapp&gl=ae"]
        appList = []
        for item in data_list:
            app_url = item
            appList.append(scrapData(app_url))
        keys_to_update = ["url",                
                "name",
                "rating",
                "downloads",
                "reviews_count",
                "rated_for",
                "company_name",
                "updated_on",
                'id',
                "description",
                "website",
                "support_email",
                "developer_name",
                "fetch_date"]
        csv_file = "updated_app_data.csv"

        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            header = keys_to_update
            writer.writerow(header)
            for product in appList:
                writer.writerow(product.values()) 

        print(f"Data has been written to {csv_file}")
    except Exception as e:
        traceback.print_exc()


if __name__ == "__main__": 
    getApp() 