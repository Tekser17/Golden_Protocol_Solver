import copy
import time
from urllib.request import urlopen, Request
# from googlesearch import search
from urllib import request
from bs4 import BeautifulSoup
from googletrans import Translator, constants
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from settings import GOLDEN_XYZ_AUTH, DRIVER_PATH
from socket import timeout


def surf(query, words):
    percent = 0.0
    count_sites = 0
    query = query.lower()
    words = words.lower()
    print(query)
    for url in [1]:  # search(query, tld="co.in", num=10, stop=10, pause=2):
        try:
            html = urlopen(url).read()

            soup = BeautifulSoup(html, features="html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()

            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text = text.lower()
            f = words.split()
            for i in range(len(f)):
                s = f[i]
                if s[len(s) - 1] in [',', '.', '!', '?']:
                    new_str = ""
                    for j in range(len(s) - 1):
                        new_str += s[j]
                    f[i] = new_str
            required = len(f)
            sum = 0
            for word in f:
                # print(word, ' ', text.count(word))
                sum += min(1, text.count(word))
            # print("GOOD")
            print(url)
            percent = max((sum / required) * 100, percent)
            count_sites += 1
        except Exception as e:
            print("Ошибка доступа", e)
    count_sites = max(1, count_sites)
    # percent /= count_sites
    return percent


def surf_result(title_, text_):
    title = copy.deepcopy(title_)
    text = copy.deepcopy(text_)
    x = surf(title, text)
    title = copy.deepcopy(title_)
    text = copy.deepcopy(text_)
    y = surf(title + ' ' + text, title + ' ' + text)
    title = copy.deepcopy(title_)
    text = copy.deepcopy(text_)
    z = surf(text, text + ' ' + title)
    return max(x, max(y, z))


def parse_page(title, text, url):
    try:
        req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = request.urlopen(req).read()
        soup = BeautifulSoup(html, features="html.parser")
        hrefs = soup.find_all('a', href=True)
        links = set()
        query = title.lower().split(" ") + text.lower().split(" ")
        q = 0
        while q < len(query):
            if len(query[q]) < 3 or query[q] in ['the', 'and', 'for']:
                query.pop(q)
                q -= 1
            q += 1
        print(query)
        for link in hrefs:
            if link.get('href').count('http') >= 1:
                links.add(link.get('href'))
        #print(links)
        pages = [soup.text.lower()]
        #pages.append(BeautifulSoup(request.urlopen(request.Request(r'https://fantoken.com/inter/', headers={'User-Agent': 'Mozilla/5.0'})).read(),
        #                           features="html.parser").text.lower())
        count = 0
        same_timeout = set()
        if len(links) >= 100:
            return False
        for link in links:
            count += 1
            print(link, round((count / len(links)) * 100, 2), '%')
            time_out = 20
            try:
                if 'apk' not in link:
                    try:
                        if link.split('//')[1].split('/')[0] in same_timeout:
                            time_out = 5
                        pages.append(BeautifulSoup(request.urlopen(request.Request(link, headers={'User-Agent': 'Mozilla/5.0'}), timeout=time_out).read(), features="html.parser").text.lower())
                    except timeout:
                        same_timeout.add(link.split('//')[1].split('/')[0])
                        print('Ошибка: ', timeout)
                #pass
            except Exception as e:
                print('Ошибка: ', e)
        #print(pages)
        mx_precent = 0
        for page in pages:
            words = 0
            for word in query:
                if page.find(word[1:]) != -1:
                    words += 1
                elif page.find(word[:-1]) != -1:
                    words += 1
                elif page.find(word) != -1:
                    words += 1
            precent = words / len(query) * 100
            mx_precent = max(mx_precent, precent)
            if mx_precent >= 74.95:
                return True
        print(mx_precent, '%')
        if len(query) <= 5:
            if mx_precent >= 74.95:
                return True
            else:
                return False
        elif mx_precent >= 59.95:
            return True
    except Exception as e:
        print('Ошибка: ', e)
        return False


def main():
    translator = Translator()
    golden_verification_url = 'https://dapp.golden.xyz/verification'
    chr_options = Options()
    chr_options.add_experimental_option("detach", True)
    _service = Service(DRIVER_PATH)
    driver = webdriver.Chrome(service=_service)
    driver.set_window_size(1440, 900)
    driver.get(golden_verification_url)
    driver.add_cookie({"name": GOLDEN_XYZ_AUTH[0], "value": GOLDEN_XYZ_AUTH[1]})
    driver.refresh()
    while True:
        link = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/div[1]/div[2]/div[3]/div/div/a').text
        accept_button = driver.find_element(By.XPATH, '/html/body/div/div[2]/main/div/div[2]/form/fieldset/div[1]/button')
        reject_button = driver.find_element(By.XPATH, '/html/body/div/div[2]/main/div/div[2]/form/fieldset/div[2]/button')
        title = driver.find_element(By.XPATH, '/html/body/div/div[2]/main/div/div[1]/div[2]/div[1]/div/div[1]/h2/a/div').text
        text = driver.find_element(By.XPATH, '/html/body/div/div[2]/main/div/div[1]/div[2]/div[1]/div/div[2]/div').text
        if len(title) > 0:
            try:
                title = translator.translate(title).text
            except Exception as ex:
                print('Ошибка: ', ex)
        if len(text) > 0:
            try:
                text = translator.translate(text).text
            except Exception as ex:
                print('Ошибка: ', ex)
        alert = None
        try:
            alert = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div[2]/button[2]')
            alert.click()
            print('Уведомления успешно выключены')
        except NoSuchElementException as e:
            pass
        print('Ссылка - ', link)
        response = parse_page(title, text, link)
        print(response)
        if response:
            try:
                accept_button.click()
            except Exception as e:
                try:
                    alert = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div[2]/button[2]')
                    alert.click()
                    print('Уведомления успешно выключены')
                except NoSuchElementException as e:
                    pass
        else:
            try:
                reject_button.click()
            except Exception as e:
                try:
                    alert = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div[2]/button[2]')
                    alert.click()
                    print('Уведомления успешно выключены')
                except NoSuchElementException as e:
                    pass
        time.sleep(5)

    #title = "Дмитрий Лукьяненко"
    #text = "Ректор Киевского национального экономического университета имени Вадима Гетьмана"
    #title = "Жетон болельщика миланского Интера"
    #text = "Токен болельщика Интера даст вам возможность помочь Нарадзурри принимать правильные решения, получать доступ к VIP-сервисам, зарабатывать официальные продукты и многое другое"
    #title = "Velo"
    #text = "Next Generation Financial Protocol for Businesses"
    #title = translator.translate(title).text
    #text = translator.translate(text).text
    #url = "https://www.socios.com"
    #url = "http://lukianenko.com.ua/en/"
    #url = "https://velo.org/"
    #parse_page(title, text, url)
    #print(text)

    # precent = surf_result(title, text) Гуглим и ищем сходства
    # print(precent, '%')


if __name__ == "__main__":
    main()

# Дмитрий Лукьяненко
# Ректор Киевского национального экономического университета имени Вадима Гетьмана
# http://lukianenko.com.ua/en/
