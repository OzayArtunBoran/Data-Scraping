from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import datetime

options = Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe" 
driver = webdriver.Firefox(options=options)  
wait = WebDriverWait(driver, 10)

def parse_product(product):
    product_description_elements = product.find_all('a', {'class': 'product-item-link product-item-detail-link'})
    
    product_description = ' '.join([desc.text for desc in product_description_elements]).strip()
    
    product_url = product_description_elements[0]['href'] if product_description_elements else None

    product_brand = product.find('strong', {'class': 'product brand product-item-name'}).text.strip()

    product_stock_check = bool(product.find('button',{'type':'submit'}))

    product_img = product.find('img', {'class': 'product-image-photo'})['src']
    
    product_price_standart = product_price_rossman = "YOK"

    price = product.find('p', {'class': 'regular-price'})
    if price:
        product_price_standart = price.find('span', {'class': 'price desktopPrice'}).text.strip()
        rossman_price = product.find('div', {'class': 'cart-campaign-wrapper color-lipstick-red'})
        if rossman_price:
            product_price_rossman = rossman_price.find('div', {'class': 'cart-campaign-price text-right'}).text.strip()

    stock_status = "VAR" if product_stock_check else "YOK"
    
    return [product_description, product_brand, product_price_standart, product_price_rossman, stock_status, product_url, product_img]

def get_page_data(page_number, category):
    base_url = f"https://www.rossmann.com.tr/{category}/?page="               
    data = []

    driver.get(base_url + str(page_number))
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'li')))

    soup = BeautifulSoup(driver.page_source, 'lxml')
    products = soup.find_all('li', {'class': 'item product product-item'})  
    
    for product in products:
        data.append(parse_product(product))

    return data

def makyaj_toplu():
    category_pages = {'makyaj': 188, 'cilt-bakimi': 93, 'kisisel-bakim': 254, 'sac-bakim': 87, 
                    'erkek-kisisel-bakim-urunleri': 32, 'temizlik': 41, 'anne-bebek': 31, 
                    'ev-yasam': 43, 'saglik-gida': 17}


    scrape_log = []
    all_data = []

    for category, max_pages in category_pages.items():
        start_time = datetime.datetime.now()
        data = []
        for i in range(1, max_pages + 2):
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
        df = pd.DataFrame(all_data, columns=['Kategori', 'Açıklama', 'Marka', 'Standart Fiyat', 'Rossmann Fiyat', 'Stok', 'URL', 'Resim'])
        df.to_excel(f'C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\KINA\\rrossman\\all_categories.xlsx', index=False)
    else:
        print("No data collected")
    
    log_df = pd.DataFrame(scrape_log, columns=['Category', 'Elapsed Time (ms)'])
    log_df.to_excel('C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\KINA\\rrossman\\scrape_log.xlsx', index=False)

makyaj_toplu()
