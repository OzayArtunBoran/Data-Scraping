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
    product_description_elements = product.find_all('a', {'class': 'product-item-link'})
    product_description = ' '.join([desc.text.strip() for desc in product_description_elements])
    
    product_url = product_description_elements[0]['href'] if product_description_elements else None
    product_brand = product_description.strip()

    product_price_standart = product_price_rossman = "YOK"
    product_img = product.find('img',{'class':'product-image-photo'})['src']
    
    price_span = product.find('span', {'class': 'price'})
    if price_span:
        product_price_standart = price_span.text.strip()

    stock_status = "VAR" 
    
    return [product_description, product_brand, product_price_standart, product_price_rossman, stock_status, product_url, product_img]

def get_page_data(page_number, category):
    base_url = f"https://www.armaganoyuncak.com.tr/{category}?page={page_number}&order=price&dir=desc"
    data = []

    driver.get(base_url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'li')))

    soup = BeautifulSoup(driver.page_source, 'lxml')
    products = soup.find_all('li', {'class': 'item product product-item'})  
    
    for product in products:
        data.append(parse_product(product))

    return data

def makyaj_toplu():
    category_pages = {'oyuncak-arabalar': 43, 'figur-oyuncaklar': 40, 'elektronik-urunler': 2, 'oyun-setleri': 24, 
                    'oyuncak-silah-ve-kilic-setleri': 2, 'egitici-oyuncaklar': 8, 'muzik-aletleri': 1, 
                    'oyunlar': 11, 'hobi-oyuncaklari': 18,'bebekler' : 31, 'kozmetik-ve-takilar':5,'anne-bebek-oyuncaklari': 13,
                    'yapi-oyuncaklari':21, 'parti-ve-ozel-gunler':7 , 'acik-hava-spor-deniz-urunleri':12, 'kirtasiye-okul':13 , 'peluslar': 16}

    scrape_log = []
    all_data = []

    for category, max_pages in category_pages.items():
        start_time = datetime.datetime.now()
        data = []
        for i in range(1, max_pages + 1):
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
        df = pd.DataFrame(all_data, columns=['Kategori', 'Açıklama', 'Marka', 'Standart Fiyat', 'Kampanya', 'Stok', 'URL', 'Resim'])
        df.to_excel(f'C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\armagan\\all_categories.xlsx', index=False)
    else:
        print("No data collected")

    log_df = pd.DataFrame(scrape_log, columns=['Category', 'Elapsed Time (ms)'])
    log_df.to_excel('C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\armagan\\scrape_log.xlsx', index=False)

makyaj_toplu()
