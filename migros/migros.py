from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time as t
import keyboard as key
profile = FirefoxProfile()
profile.set_preference("layout.css.devPixelsPerPx", "0.3")
options = Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe" 
options.set_preference("layout.css.devPixelsPerPx", "0.3")
driver = webdriver.Firefox(options=options)  
wait = WebDriverWait(driver, 10)
driver.maximize_window()
def get_page_data(page_number, category):
    base_url = f"https://www.migros.com.tr/{category}?sayfa={page_number}&sirala=once-en-dusuk-fiyat"               
    data = []
    driver.get(base_url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'sm-list-page-item')))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
    driver.execute_script("document.body.style.zoom='30%';")
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    products = soup.find_all('sm-list-page-item', {'class': 'mdc-layout-grid__cell--span-2-desktop mdc-layout-grid__cell--span-4-tablet mdc-layout-grid__cell--span-2-phone ng-star-inserted'})  
    
    for product in products:
        
        data.append(parse_product(product))
    return data

def parse_product(product):
    t.sleep(1*0.1)
    
    product_description_elements = product.find_all('a', {'class': 'mat-caption text-color-black product-name'})
    product_description = ' '.join([desc.text for desc in product_description_elements]).strip()
    
    product_url = product_description_elements[0]['href'] if product_description_elements else None
    
    product_price_standart = product_price_migros = "YOK"
    
    product_img_1 = product.find('img', {'class': 'ng-star-inserted'})
    product_img = product_img_1['src']
    if product_img == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAKCAYAAABrGwT5AAAAF0lEQVR42mN89uzxfwYyAeOo5lHNhAAA7jIk17T4Y6wAAAAASUVORK5CYII=":
        product_img = "YOK"
    print("----------------------------------------------------")
    print(product_img_1)
    
    print(product_img_1['src'])
    print("----------------------------------------------------")
    product_price_standart = product.find('span', {'class': 'amount'}).text.strip() + " TL"

    stock_status = "VAR"
    return [product_description, "YOK", product_price_standart, "YOK", stock_status, product_url, product_img]
    

def makyaj_toplu():
    #category_pages = {'elektronik-c-a6': 21, 'kisisel-bakim-kozmetik-saglik-c-8': 74}
    category_pages = {'elektronik-c-a6': 5, 'kisisel-bakim-kozmetik-saglik-c-8': 5}
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
        df = pd.DataFrame(all_data, columns=['Kategori', 'Açıklama', 'Marka', 'Standart Fiyat', 'Migros Fiyat', 'Stok', 'URL', 'Resim'])
        df.to_excel(f'C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\KINA\\migros\\all_categories.xlsx', index=False)
    else:
        print("No data collected")
    
    log_df = pd.DataFrame(scrape_log, columns=['Category', 'Elapsed Time (ms)'])
    log_df.to_excel('C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\KINA\\migros\\scrape_log.xlsx', index=False)
    
    
makyaj_toplu()
