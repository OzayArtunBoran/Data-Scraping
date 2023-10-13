from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time as t

options = Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe" 
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 10)

def get_page_data(page_number, category):
    base_url = f"https://www.gratis.com/{category}?sortCode=price-asc&page={page_number}"               
    data = []
    driver.get(base_url)
    
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'app-custom-product-grid-item')))
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    products = soup.find_all('app-custom-product-grid-item', {'class': 'col-xs-6 col-sm-4 col-md-4 ng-star-inserted'})  
    
    for product in products:
        data.append(parse_product(product))
    return data

def parse_product(product):
    t.sleep(1*0.05)
    product_description_elements = product.find_all('a', {'class': 'cx-product-name'})
    product_description = ' '.join([desc.text for desc in product_description_elements]).strip()
    
    product_url = product_description_elements[0]['href'] if product_description_elements else None
    product_stock_check =  bool(product.find('button', {'class': 'add-to-basket add-to-cart-for-product-grid-item'}))

    product_price_standart = product_price_gratis = "YOK"
    product_img = product.find('div', {'class': 'not-zoomable'}).find('img')['src']
    product_price_standart = product.find('div', {'class': 'product-price'}).text.strip()
    if product_price_standart:
        gratis_price = product.find('div', {'class': 'carded-price'})
        
        if gratis_price:
            product_price_gratis = gratis_price.text.strip()

    stock_status = "VAR" if product_stock_check else "YOK"
    return [product_description, "None", product_price_standart, product_price_gratis, stock_status, product_url, product_img]
    

def makyaj_toplu():
    category_pages = {'makyaj-c-501': 131, 'cilt-bakim-c-502': 80, 'sac-bakim-c-503': 63, 
                    'parfum-deodorant-c-504': 32, 'erkek-bakim-c-505': 3, 'kisisel-bakim-c-506': 52, 'anne-bebek-c-507': 9,
                    'ev-yasam-c-508': 27, 'moda-aksesuar-c-509': 7, 'supermarket-c-510': 29, 'elektrikli-urunler-c-511': 7}

    scrape_log = []
    all_data = []

    for category, max_pages in category_pages.items():
        start_time = datetime.datetime.now()
        data = []
        for i in range(0, max_pages + 2):
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
        df = pd.DataFrame(all_data, columns=['Kategori', 'Açıklama', 'Marka', 'Standart Fiyat', 'Gratis Fiyat', 'Stok', 'URL', 'Resim'])
        df.to_excel(f'C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\gratis\\all_categories.xlsx', index=False)
    else:
        print("No data collected")
    
    log_df = pd.DataFrame(scrape_log, columns=['Category', 'Elapsed Time (ms)'])
    log_df.to_excel('C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\gratis\\scrape_log.xlsx', index=False)
    
    
makyaj_toplu()
