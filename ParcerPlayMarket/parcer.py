import xml.etree.ElementTree as ET
import requests
import gzip
import shutil
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
import time
from selenium.common.exceptions import NoSuchElementException
import tempfile
import csv
import os

# Ініціалізація WebDriver
def init_webdriver():
    driver_path = r"C:\Users\20002\Desktop\ParcerPlayMarket\chromedriver-win64\chromedriver.exe"
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=service, options=options)

# Отримання даних про книгу з URL
def extract_book_details(url, driver, writer):
    driver.get(url)
    time.sleep(1)

    parsed_url = urlparse(url)
    book_id = parse_qs(parsed_url.query).get('id', [None])[0]

    try:
        book_name = driver.find_element(By.CSS_SELECTOR, '[itemprop="name"]').text.strip()
    except NoSuchElementException:
        book_name = None

    try:
        author = driver.find_element(By.CSS_SELECTOR, '[itemprop="author"]').text.strip()
    except NoSuchElementException:
        author = None

    try:
        publication_date = driver.find_element(By.CSS_SELECTOR, '[itemprop="datePublished"]').text.strip()
    except NoSuchElementException:
        publication_date = None

    try:
        page_count = driver.find_element(By.XPATH, '//div[contains(text(), "Сторінок")]/following-sibling::span').text.strip()
    except NoSuchElementException:
        page_count = None

    try:
        is_audiobook = driver.find_element(By.XPATH, '//span[contains(text(), "Аудіокнига")]')
        book_type = "Аудіокнига"
    except NoSuchElementException:
        book_type = "Звичайна книга"

    success_status = "Успішно"

    if None in [book_id, book_name, author, publication_date, page_count, book_type]:
        success_status = "Помилка"

    if book_id and book_name:
        print(f"ID програми: {book_id}")
        print(f"Назва програми: {book_name}")
        print(f"Автор: {author}")
        print(f"Дата публікації: {publication_date}")
        print(f"Кількість сторінок: {page_count}")
        print(f"Тип книги: {book_type}")
        writer.writerow([book_id, book_name, author, publication_date, page_count, book_type, success_status])
        return True
    else:
        print("ID книги або назва відсутні, пропускаємо...")
        return False

# Обробка sitemap
def process_sitemap(sitemap_url, driver, writer, limit, global_count):
    response = requests.get(sitemap_url)
    response.raise_for_status()

    with gzip.open(BytesIO(response.content), 'rb') as f_in:
        with tempfile.NamedTemporaryFile(delete=False) as temp_xml:
            shutil.copyfileobj(f_in, temp_xml)
            temp_xml_path = temp_xml.name

    extracted_tree = ET.parse(temp_xml_path)
    extracted_root = extracted_tree.getroot()
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    count = 0

    for url_element in extracted_root.findall('ns:url/ns:loc', namespace):
        book_url = url_element.text
        print(f"------------------------------------")
        print(f"Обробка URL програми/книги/аудіокниги/фільму з Google Play: {book_url}")
        if extract_book_details(book_url, driver, writer):
            count += 1
            global_count += 1
        if count >= limit or global_count >= 100:
            break
    return global_count

# Основна функція
def main():
    sitemap_index_url = 'https://play.google.com/sitemaps/sitemaps-index-0.xml'
    response = requests.get(sitemap_index_url)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    driver = init_webdriver()
    output_file_path = os.path.join(os.path.dirname(__file__), 'data.csv')

    try:
        with open(output_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Ensure that the header is written only if the file is empty
            if os.stat(output_file_path).st_size == 0:
                writer.writerow(['ID програми', 'Назва програми', 'Автор', 'Дата публікації', 'Кількість сторінок', 'Тип книги', 'Статус'])

            global_count = 0  # Лічильник оброблених записів

            for loc_element in root.findall('ns:sitemap/ns:loc', namespace):
                gz_url = loc_element.text
                print(f"Обробка .xml.gz URL: {gz_url}")
                global_count = process_sitemap(gz_url, driver, writer, limit=100, global_count=global_count)
                if global_count >= 100:
                    break
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
