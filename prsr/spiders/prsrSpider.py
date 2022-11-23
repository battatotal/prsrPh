#WILDBARRIE VERSION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import scrapy
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


class NewSpider(scrapy.Spider):
    name = "prsr"
    handle_httpstatus_list = [403]
    nextpageval = 2
    CountLinks = 0
    DICT = {}

    count=0#

    def __init__(self):
        self.driver = webdriver.Chrome()


    def start_requests(self):
        # allowed_domains = ["https://www.ozon.ru/category/smartfony-15502/?sorting=rating"] ozon
        allowed_domains = ["https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony?sort=rate&page=1"]
        url = allowed_domains[0]

        yield scrapy.Request(url=url, callback=self.parse)


    def helppar(self, response): #Вспомогательный парсер
        #листаем к точке где прописана "версия системы"
        self.driver.get(response.url)
        time.sleep(1)
        # eltoscroll = self.driver.find_element(by=By.CLASS_NAME, value="l3x") ozon
        eltoscroll = self.driver.find_element(by=By.XPATH, value="//h2[@class='details-section__header']")#self.driver.find_element(by=By.ID, value="footer")
        ActionChains(self.driver).move_to_element(eltoscroll).perform()
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 1000)")
        time.sleep(1)

        # res = response.css("span.lx3::text").get()        ozon
        ######### Клик (Развернуть характеристики)
        expose = self.driver.find_element(By.XPATH, value="//div/button[@class='collapsible__toggle j-parameters-btn j-wba-card-item j-wba-card-item-show']").click()
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 1500)")
        time.sleep(1)
        #######
        self.driver.execute_script("window.scrollTo(0, 2000)") #Доп прокрутка (может поможет прочитать там где не читает)
        time.sleep(1)
        #######
        #Считываю все элементы таблицы характеристики и заношу их в текстовый файл(ибо конкретный выделить нельзя-одинаковые названия)
        tabledata = ""
        for i in self.driver.find_elements(By.XPATH, value="//table[@class='product-params__table']"):
            tabledata += i.get_attribute('innerHTML')
            with open("q.txt", "w", encoding="utf8") as f:
                f.write(tabledata)
        time.sleep(1)

        with open('q.txt', encoding='utf8') as q:
            rd = q.read()
        try:
            res = re.search("Android [\d.]+[()\w]*|i[oO][sS] [\d]+|Андроид [\d.]+[()\w]*|Android\s+[\[\]\w]*", rd)[0]
            if "Андроид" in res: res = "Android" + res[7:]
        except TypeError:
            res = "Undefined OS"
        #
        with open("test.txt", "a", encoding="utf8") as f:
            self.count += 1
            f.write(res+"    " + str(self.count) + '\n')
        #

        if res not in self.DICT:
            self.DICT[res] = 1
        else:
            self.DICT[res] += 1

        #Формируем файл с с результатом( на каждой итерации он перезаписывается)
        rresult = ''
        for i in sorted(self.DICT):
            rresult += i+" "+"-"+" "+str(self.DICT[i])+"\n"
        with open("finresult.txt", "w", encoding="utf8") as r:
            r.write(rresult)



        #########
            # Финальная часть     (Она тут совершенно необязательна, прописал её т.к в задании нужно использовать Pandas)
        if self.count >= 105:
            self.driver.close()
            for i in self.DICT:
                self.DICT[i] = [self.DICT[i]]  # -Преобразую значения в мини списки, чтобы пандас мог создать датафрейм
            hd = pd.DataFrame.from_dict(self.DICT)
            hd = hd.loc[0, sorted(hd)]
            with open("show.txt", "w", encoding="utf8") as s:
                for sys, val in hd.items():
                    s.write(sys + " " + "-" + " " + str(val) + "\n")
        #yield {}
        #########




        yield { 'res': self.DICT } #или просто DICT



    def parse(self, response):
        flag = True
        if flag == True:
            # filename = "result.txt"
            filename = "result.html"
            rlinks = "rlinks.txt" #для хранения полученных ссылок
            self.driver.get(response.url)
            #пролистываем страницу вниз с помощью силениума
            # eltoscroll = self.driver.find_element(by=By.CLASS_NAME, value="a2wa") ozon
            eltoscroll = self.driver.find_element(by=By.ID, value="footer")
            ActionChains(self.driver).move_to_element(eltoscroll).perform()
            time.sleep(2)
            #Извлекаю html из ВебЛемента(Объекта силениума)
            # elem = self.driver.find_element(by=By.CLASS_NAME, value="t8e").get_attribute("innerHTML") ozon
            elem = self.driver.find_element(by=By.CLASS_NAME, value="product-card-overflow").get_attribute("innerHTML")
            with open(filename, "a", encoding="utf8") as f:  #заменил a на w???
                f.write(elem)
            #читаю html чтобы найти ссылки с помощью re
            #ftoread = "" #строка в которую распаковывается текст
            with open(filename, "r", encoding="utf8") as f:
                # ftoread = f.readline() ozon
                ftoread = f.read()

            # r = re.findall("href=\"(/product/[^ >\"]+)", ftoread) #поиск ссылок ozon
            r = re.findall("href=\"(https://www.wildberries.ru/catalog/[\d]*/detail[^ >\"]+)", ftoread)  # поиск ссылок
            r = set(r)
            #CountLinks = 0
            with open(rlinks, "a", encoding="utf8") as f: #запись ссылок   (тут попробывал убрать а и поставил w чтобы не было перезаписи?????)
                for i in r:
                    # if CountLinks < 100:  ozon
                    if self.CountLinks == 105:
                        break
                    f.write(i + "\n")
                    self.CountLinks += 1
            #NextPaging
            # nextpageval = 2
            # for_next_page = self.driver.find_element(By.CLASS_NAME, value="maa0").get_attribute("innerHTML") ozon
            for_next_page = self.driver.find_element(By.XPATH, value="//div/a[7]").get_attribute("outerHTML")
            # next_page = re.findall(r"href=\"(/category/smartfony-15502/\?page=2[^\" ]+)", for_next_page) ozon
            next_page = re.findall(r"https://(www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony\?sort=rate[^`]*page=[\d][\d]*)", for_next_page)
            print(for_next_page)
            print(next_page)

            next_page = set(next_page).pop()
            #Замена символов html (amp;) в ссылке возле параметров get
            idx = 0

            ##
            while True:
                idx = next_page.find("amp;")
                if idx == -1: break
                next_page = next_page[:idx] + next_page[idx+4:]
            ##

            #замена номера следующей страницы в параметре ссылки
            next_pageN = []
            # for i, v in enumerate(next_page):
            #     if i != 32:
            #         next_pageN.append(str(v))                          ozon
            #     else: next_pageN.append(str(nextpageval))
            # next_page = "".join(next_pageN)


            next_page = next_page[:-1] + str(self.nextpageval)

            if self.CountLinks >= 105: next_page = None
            if next_page != None:
                # yield response.follow("https://www.ozon.ru"+next_page, callback=self.parse) #Убрал символ / после ру(тут и на следующей строке)
                self.nextpageval += 1
                yield response.follow("https://" + next_page, callback=self.parse)

            # print("https://www.ozon.ru"+next_page) ozon
            #print("https://www.wildberries.ru" + next_page) ################
            print(self.CountLinks)
            print(next_page)
        if self.CountLinks >= 105: flag = False #часть срабатывает уже в конце, когда все ссылки получены
        if flag == False:
            yield response.follow("https://wildberries.ru", callback=self.extraxt)


        ###############Выше - прошел по страницам и забрал ссылки на объекты, ниже идет проход по ссылкам и
        #получение итоговой информации и запись её в файл

    def extraxt(self, response):

        #DICT = {}
        readlinks = []
        with open("rlinks.txt",encoding="utf8") as f:
            for i in f.readlines():                         #читаю ссылки из файла
                readlinks.append(i)

        for i in readlinks:
            # lk = "www.ozon.ru" + i      ozon
            lk = i #"https://www.wildberries.ru" + i
            yield response.follow(lk, callback=self.helppar)#q = response.follow(lk, callback=self.helppar)