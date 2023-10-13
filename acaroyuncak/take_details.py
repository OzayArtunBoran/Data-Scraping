import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from openpyxl import load_workbook

# Excel dosyasını pandas ile oku
df = pd.read_excel('all_categories.xlsx')

# Selenium için tarayıcıyı başlat
options = Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe" 
driver = webdriver.Firefox(options=options)  
wait = WebDriverWait(driver, 10)

barkod_list = []
stok_list = []

for url in df['URL']:
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    # sayfadaki belirli başlı yazıları çek (örnekte barkod etiketi kullanılıyor)
    elemanlar = soup.find_all('div',{'class':'product-list-content'})
    barkod_list.append(elemanlar[3].text) # barkod
    stok_list.append(elemanlar[2].text) # stok kodu
    

# driver'ı kapat
driver.quit()

# Yeni sütunu ekle ve veriyi kaydet
df['Barkod_Kodu'] = barkod_list
df['Stok_Kodu'] = stok_list
df.to_excel('all_categories.xlsx', index=False)
