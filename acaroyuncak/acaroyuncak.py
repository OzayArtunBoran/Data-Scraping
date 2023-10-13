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
    product_description_elements = product.find_all('div', {'class': 'showcase-title'})
    product_description = ' '.join([desc.text for desc in product_description_elements])
    url_tag = product_description_elements[0].find('a')['href']
    product_url = "https://www.acaroyuncak.com.tr" + url_tag if product_description_elements else None
    product_brand = product_description
    product_brand = product.find('div', {'class': 'showcase-brand'}).text


    product_price_standart = product_price_acaroyuncak = "YOK"

    product_price_standart = product.find('div', {'class': 'showcase-price-new'}).text
    
    product_stock_check = product.find('a', {'class': 'add-to-cart-button'})
    
    stock_status = "VAR" if product_stock_check else "YOK"
    
    product_img = product.find('img',{'class':'lazyload'})['src']
    
    return [product_description, product_brand, product_price_standart, product_price_acaroyuncak, stock_status, product_url, product_img]

def get_page_data(page_number, category):
    base_url = f"https://www.acaroyuncak.com.tr/kategori/{category}?siralama=fiyat:desc&tp="               
    data = []

    driver.get(base_url + str(page_number))
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'showcase')))

    soup = BeautifulSoup(driver.page_source, 'lxml')
    products = soup.find_all('div', {'class': 'col-6 col-lg-4'})  
    
    for product in products:
        data.append(parse_product(product))

    return data

def scrape():
    category_pages = {'fisher-price': 6, 'okul-oncesi-oyuncaklari': 6, 'oyun-arkadaslari': 5, 'kutu-oyunlari': 5, 
                    'lego-oyuncaklar': 8, 'oyun-setleri': 13, 'puzzle-cesitleri': 8, 
                    'erkek-cocuk': 3, 'erkek-oyuncaklari': 7,'kiz-cocuk' : 4, 'kiz-oyuncaklari':12, 'bahce-oyuncaklari': 5,
                    'spor-oyuncaklari':9, 'pelus-oyuncak':6 , 'arabalar':10, 'araclar':12 , 'tasitlar': 6 , 'akulu-arabalar':1}

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
        df = pd.DataFrame(all_data, columns=['Kategori', 'Açıklama', 'Marka', 'Standart Fiyat', 'Kampanya Fiyat', 'Stok', 'URL', 'Resim'])
        df.to_excel(f'C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\acaroyuncak\\all_categories.xlsx', index=False)
    else:
        print("No data collected")

    log_df = pd.DataFrame(scrape_log, columns=['Category', 'Elapsed Time (ms)'])
    log_df.to_excel('C:\\Users\\artun\\OneDrive\\Masaüstü\\KINA\\acaroyuncak\\scrape_log.xlsx', index=False)

scrape()
