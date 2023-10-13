from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import json
import time as t

options = Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe" 
driver = webdriver.Firefox(options=options)  
wait = WebDriverWait(driver, 10)

def get_page_data(page_number, category):
    base_url = f"https://www.watsons.com.tr/makyaj/c/{category}?page={page_number}&size=30&sort=topRated"               
    data = []
    driver.get(base_url)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-tile-wrapper')))
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    products = soup.find_all('div', {'class': 'product-tile-wrapper'})  
    
    for product in products:
        if not product.parent.get('class', []):
            data.append(parse_product(product))
    return data

def parse_product(product):
    t.sleep(1*0.1)
    product_description_elements = product.find_all('a', {'class': 'product-tile__name'})
    product_description = ' '.join([desc.text for desc in product_description_elements])
    
    product_url = product_description_elements[0]['href'] if product_description_elements else None
    product_stock_check = bool(product.find('button',{'class':'button button--primary out-of-stock-button button--text-bold button--full-width disabled'}))

    product_price_standart = product_price_watsons = "YOK"
    product_img = product.find('img', {'class': 'product-tile__image'})['data-src']
    product_brand_main = product.find("e2-impression-tracker", {"class": "product-tile__content"})
    product_brand = product_brand_main['data-name'] if product_brand_main else print(product_url)

    prices = product.find_all('e2-price-badge', {'class': 'price-badge__price'})
    if prices:
        product_price_standart = prices[0]['price']
        watsons_price = product.find('e2-price-badge', {'price-source': 'MEMBER'})
        
        if watsons_price:
            watsons_price_json = json.loads(watsons_price['other-prices'].strip())
            product_price_watsons = watsons_price_json[0]['value']
            

    stock_status = "YOK" if product_stock_check else "VAR"
    return [product_description, product_brand, product_price_standart, product_price_watsons, stock_status, product_url, product_img]

def makyaj_toplu():
    # category_pages = {'100': 138, '101': 47, '102': 40, '103': 54, 
    #                 '104': 6, '105': 12, '106': 8, 
    #                 '108': 1, '109': 7}
    category_pages = {'100': 2, '101': 2, '102': 2, '103': 2, 
                    '104': 2, '105': 2, '106': 2, 
                    '108': 1, '109': 2}
    scrape_log = []
    all_data = []

    for category, max_pages in category_pages.items():
        start_time = datetime.datetime.now()
        data = []
        for i in range(0, max_pages + 1):
            print(f"Scraping {category} page {i}")
            page_data = get_page_data(i, category)
            for d in page_data:
                d.insert(0, category)
            data.extend(page_data)
        
        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000  # convert elapsed time to milliseconds
        scrape_log.append([category, elapsed_time])

        all_data.extend(data)

    if all_data:
        df = pd.DataFrame(all_data, columns=['Kategori', 'Açıklama', 'Marka', 'Standart Fiyat', 'Watsons Fiyat', 'Stok', 'URL', 'Resim'])
        df.to_excel(f'C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\KINA\\watsons\\all_categories.xlsx', index=False)
    else:
        print("No data collected")

    log_df = pd.DataFrame(scrape_log, columns=['Category', 'Elapsed Time (ms)'])
    log_df.to_excel('C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\KINA\\watsons\\scrape_log.xlsx', index=False)

makyaj_toplu()
