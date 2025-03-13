import mysql.connector
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time

# Set up Selenium WebDriver options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def extract_mart_details(driver,category_name, product_url):
    """Extract details about the mart from its page (extendable)."""
    details = {
        "Product URL": product_url,"Category Name" : category_name
    }

    
    
    try:
        details["Product Name"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[1]/section/div[1]/div[2]/div[1]/div/h1').text.strip()
    except NoSuchElementException:
        details["Product Name"] = None

    try:
        details["Product Price"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[1]/section/div[1]/div[2]/div[2]/div[2]/div/span').text.strip()
    except NoSuchElementException:
        details["Product Prive"] = None

    try:
        details["Product Discount"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[1]/section/div[1]/div[2]/div[2]/div[2]/div/div/span[2]').text.strip()
    except NoSuchElementException:
        details["Product Discouunt"] = None

    try:
        details["MRP"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[1]/section/div[1]/div[2]/div[2]/div[2]/div/div/span[1]').text.strip()
    except NoSuchElementException:
        details["MRP"] = None

    try:
        details["Description"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[2]/div[2]/div[1]/div[2]').text.strip()
    except NoSuchElementException:
        details["Description"] = None

    try:
        details["Ratings"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[1]/section/div[1]/div[2]/div[2]/div[4]/div').text.strip()
    except NoSuchElementException:
        details["Ratings"] = None
    
    try:
        details["Reviews"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[1]/section/div[1]/div[2]/div[2]/div[4]/a').text.strip()
    except NoSuchElementException:
        details["Reviews"] = None

    
    # try:
    #     details["SKU"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[2]/div[2]/section[1]/div[2]/article[3]/div/ul/li[1]').text.strip()
    # except NoSuchElementException:
    #     details["SKU"] = None

    list_items = driver.find_elements(By.XPATH, '//*[@id="jm"]/main/div[2]/div[2]/section[1]/div[2]//li')

    # Iterate through each list item and check for "SKU"
    for item in list_items:
        text = item.text.strip()
        if 'SKU' in text:
            details["SKU"] = text.split(':')[-1].strip()  # Extract SKU after ':'
            break
    else:
        details["SKU"] = None

    try:
        details["Brand"] = driver.find_element(By.XPATH, '//*[@id="jm"]/main/div[1]/section/div[1]/div[2]/div[2]/div[1]/a[1]').text.strip()
    except NoSuchElementException:
        details["Brand"] = None
    

    return details


def scrape_location(driver, category_url, category_name):
    """Scrape product and mart details from a given category URL."""
    driver.get(category_url)
    time.sleep(3)

    data = []
    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.itm.col"))
            )

            products = driver.find_elements(By.CSS_SELECTOR, "div.itm.col")
            product_links = [product.find_element(By.CSS_SELECTOR, "a").get_attribute("href") for product in products]

            for product_link in product_links[:]:  # Iterate over mart links
                try:
                    driver.get(product_link)
                    
                    product_details = extract_mart_details(driver, category_name, product_link)
                    data.append(product_details)

                    time.sleep(2)

                    # similar_products= driver.find_elements(By.CSS_SELECTOR, "div.itm.col")
                    # similar_products_links = [similar_product.find_element(By.CSS_SELECTOR, "a").get_attribute("href") for similar_product in similar_products]
                    
                    # for similar_product_link in similar_products_links[:3]:
                    #     try:
                    #         driver.get(similar_product_link)
                    #         time.sleep(2)
                    #         similar_products_details = extract_mart_details(driver, category_name, similar_product_link)
                    #         data.append(similar_products_details)
                            

                        # except Exception as e:
                        #     print(e)


                except Exception as e:
                    print("Error extracting mart details:", e)

            # Check for next page and navigate if available
            try:
                next_page = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
                next_page.click()
                time.sleep(3)
            except NoSuchElementException:
                print("No more pages. Exiting pagination loop.")
                break

        except TimeoutException:
            print("Page load timeout. Exiting loop.")
            break

    return data

def main():
    """Main function to scrape multiple locations and save data to CSV."""
    categories = {
        "Health & Beauty":"https://www.jumia.com.ng/health-beauty/",
        "Groceries":"https://www.jumia.com.ng/groceries/",
        "Baby Products":"https://www.jumia.com.ng/baby-products/"
        
        
    }

    all_data = []

    try:
        for category_name, category_url in categories.items():
            print(f"Scraping: {category_url}")

            # Scrape data from the category page
            category_data = scrape_location(driver, category_url, category_name)

            all_data.extend(category_data)

        if all_data:
            df = pd.DataFrame(all_data, columns=["Category Name", "Product URL","Product Name","Product Price","Product Discount",
                                                 "MRP","Description", "Ratings", "Reviews","SKU", "Brand"])
            df.to_csv("jumia.csv", index=False)
            print("Scraping Completed Successfully!")
        else:
            print("No data scraped.")

    except Exception as e:
        print("Error during Scraping:", e)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
