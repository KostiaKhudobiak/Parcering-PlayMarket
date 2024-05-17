import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def parse_games_page(url):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    games = soup.find_all('div', {'class': 'wXUyZd'})

    for game in games:
        try:
            app_name = game.find('div', {'class': 'Fd93Bb ynrBgc xwcR9d'}).text.strip()
            app_url = "https://play.google.com" + game.find('a', href=True)['href']
            vendor_name = game.find('div', {'class': 'KoLSrc'}).text.strip()
            installations = game.find_all('div', {'class': 'b8cIId f5NCO'})[1].text.strip()
            rate = game.find('div', {'class': 'b8cIId f5NCO'}).text.strip()
            last_update = game.find('div', {'class': 'vU6FJ p63iDd'}).find_all('span', {'class': 'htlgb'})[-1].text.strip()
            age_restriction = game.find_all('div', {'class': 'vU6FJ p63iDd'})[1].find('div', {'class': 'KoLSrc'}).text.strip()
            description = game.find_all('div', {'class': 'vU6FJ p63iDd'})[2].find('span', {'jsname': 'sngebd'}).text.strip()

            print("App Name:", app_name)
            print("App URL:", app_url)
            print("Vendor Name:", vendor_name)
            print("Installations:", installations)
            print("Rate:", rate)
            print("Last Update:", last_update)
            print("Age Restriction:", age_restriction)
            print("Description:", description)
            print("-----------------------------")

            data = [app_name, app_url, vendor_name, installations, rate, last_update, age_restriction, description]
            write_to_csv(data)
        except Exception as e:
            print("Error:", e)

    driver.quit()

def write_to_csv(data):
    try:
        with open('games.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            print("Data written to CSV:", data)
    except Exception as e:
        print("Error writing to CSV file:", e)

def main():
    url = 'https://play.google.com/store/games'
    try:
        with open('games.csv', mode='w', newline='', encoding='utf-8') as file:
            pass
    except Exception as e:
        print("Error creating CSV file:", e)
        return

    parse_games_page(url)

if __name__ == "__main__":
    main()
