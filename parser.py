from selenium.webdriver import Chrome, ChromeOptions
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.by import By
from database.sqlite_db import get_data_win, get_data_draw, match_in_database, write_match_sql

options = ChromeOptions()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
options.add_argument("accept-encoding=gzip, deflate, br")
options.add_argument("Connection=keep-alive")
options.add_argument("Referer=https://www.google.com/")
options.add_argument("Cookie=foo=bar; baz=qux")
options.add_argument("Cache-Control=max-age=0")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--headless')
options.add_argument("--lang=en-US")
options.add_argument("--force-device-scale-factor=1.5")
options.add_argument('--disable-notifications')

driver = Chrome(options=options)


def get_now_time():
    now_utc = datetime.utcnow()
    utc_offset = timedelta(hours=3)
    now_utc3 = now_utc + utc_offset
    return now_utc3


def get_matches():
    now = get_now_time()
    day = str(now.day)
    month = str(now.month)
    if len(day) == 1:
        day = '0' + day
    if len(month) == 1:
        month = '0' + month
    now = f'{day}-{month}'
    url = 'https://vprognoze.ru/robobet/'
    driver.get(url)
    sleep(6)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    matches = soup.find('tbody').find_all('tr')
    check = len(matches)
    radio = driver.find_element(By.XPATH, '//*[@id="frm_filter"]/div/div/div/div[1]/div[2]/label[1]')
    radio.click()
    sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    new = soup.find('tbody').find_all('tr')
    matches.extend(new)
    return set(matches), check


def get_match_info(match):
    odds = match.find_all('a', class_='odd-badge')
    forecast = match.find('td', class_='robobet__percent-mob').find_all('div')
    time = list(map(int, match.find('td', class_='robobet__time').text.split(':')))
    teams = match.find_all('span', class_='robobet__team')
    first_team, second_team = [i.text for i in teams]
    first, draw, second = [[i.text, float(j.text)] for i, j in zip(forecast, odds)]
    url = match.find('a', class_='robobet__livecenter')
    if url:
        url = f'https://vprognoze.ru{url.get("href")}'
    else:
        url = f'https://vprognoze.ru/engine/ajax/controller.php?mod=fc_h2h&type=turnir&id={match.get("data-eventid")}'
    return time, first_team, second_team, url, first, draw, second


def is_valid_one(data):
    wins = get_data_win()
    for forecast, odds in data:
        for forecast_, odds_ in wins:
            if forecast == str(forecast_) + '%' and odds >= odds_:
                return True
    return False


def is_valid_draw(data):
    draws = get_data_draw()
    for forecast, odds in draws:
        if str(forecast) + '%' == data[0] and data[1] >= odds:
            return True
    return False


def main():
    matches, count = get_matches()
    now = get_now_time()
    result = []
    for i in matches:
        url = i.find('a', class_='robobet__livecenter')
        res = i.find('td', class_='robobet__result').get('data-res')
        if url:
            url = f'https://vprognoze.ru{url.get("href")}'
        else:
            url = f'https://vprognoze.ru/engine/ajax/controller.php?mod=fc_h2h&type=turnir&id={i.get("data-eventid")}'
        if match_in_database(url) or res != '- : -':
            continue
        time, first_team, second_team, url, first, draw, second, = get_match_info(i)
        time = now.replace(hour=time[0], minute=time[1], second=0, microsecond=0)
        if (now <= time or count <= 0) and (is_valid_one([first, second])) or (is_valid_draw(draw)):
            result.append([first_team, second_team, first, draw, second, url])
            write_match_sql(url)

        count -= 1
    return result


if __name__ == '__main__':
    count = 0
    from database.sqlite_db import sql_start

    sql_start()
    while True:
        count += 1
        result = main()
        for i in result:
            print(i)
        print(f'\n\n\n{count}\n\n\n')
        sleep(900)