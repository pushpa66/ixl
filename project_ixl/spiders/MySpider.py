import json

import scrapy
from selenium import webdriver
from scrapy import signals
from pydispatch import dispatcher
from PIL import Image
import random
import csv


def save_to_json(file_name, data):
    with open(file_name, 'w') as f:
        # for data in self.allData:
        json.dump(data, f, indent=4)

        f.close()


def save_to_csv(file_name, data):
    with open(file_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)


class MySpider(scrapy.Spider):
    name = 'ixl'

    domain = "https://www.ixl.com"
    row_index = 1

    csv_file_name = "social-studies.csv"  # (1) set csv file name here

    start_urls = [
        # 'https://www.ixl.com/math/'
        'https://www.ixl.com/social-studies/'   # (2) set the subject url here
    ]

    allData = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.allData.append(['grade', 'category', 'skill', 'question'])

    def parse(self, response, **kwargs):

        grades_raw_data = response.xpath('//a[contains(@class, "node-name")]')

        grades = []
        urls = []
        for i in grades_raw_data:
        # for i in [grades_raw_data[self.row_index]]:
            grade = i.xpath('./text()').extract_first().strip()
            grades.append(grade)
            url = self.domain + i.xpath('./@href').get()
            urls.append(url)
            yield scrapy.Request(url, callback=self.parse_step1, meta={'data': grade})

        print("========================================= Start Reading ===============================================")
        print(grades)
        print(urls)

    def parse_step1(self, response):
        grade = response.meta['data']
        # print(response.url)
        # print(grade)

        raw_data = response.xpath('//div[contains(@class, "skill-tree-category")]')

        for i in raw_data:
        # for i in raw_data[0:1]:

            # category
            category_name = i.xpath('./div/h2/span[contains(@class, "category-name")]/text()').extract_first().strip()
            print(category_name)

            skills_raw_data = i.xpath('./ol/li/div/div/a')

            for j in skills_raw_data:
            # for j in [skills_raw_data[2]]:
                skill_url = self.domain + j.xpath('./@href').get()
                skill = j.xpath('./span/text()').extract_first().strip()

                print(skill_url)
                print(skill)

                data_step1 = {
                    'grade': grade,
                    'category': category_name,
                    'skill': skill,
                    'question': ''
                }
                yield self.get_selenium_response(skill_url, callback=self.parse_step2, meta={'data': data_step1})

    def get_selenium_response(self, url, callback=None, meta=None):

        driver = webdriver.Chrome("C:/chromedriver.exe")
        driver.get(url)
        element = driver.find_element_by_id("practice")

        # image_name = str(random.randint(1000, 9999)) + meta['data']['skill'] + ".png"
        # element = driver.find_element_by_id("practice")
        # location = element.location
        # size = element.size
        # driver.save_screenshot('image_full/' + image_name)
        #
        # # crop image
        # x = location['x']
        # y = location['y']
        # width = location['x']+size['width']
        # height = location['y']+size['height']
        # im = Image.open('image_full/' + image_name)
        # im = im.crop((int(x), int(y), int(width), int(height)))
        # im.save('image_cropped/' + image_name)

        # meta['data']['question'] = image_name

        text = str(element.text).strip().replace("Learn with an example", "").replace("Submit", "").replace('\n', '')
        print(text)

        meta['data']['question'] = text

        response = scrapy.Selector(text=driver.page_source.encode('utf-8'))

        callback([response, meta])

    def parse_step2(self, args):
        response = args[0]
        meta = args[1]
        print(meta['data'])

        # self.allData.append(meta['data'])

        data = [meta['data']['grade'], meta['data']['category'], meta['data']['skill'], meta['data']['question']]
        self.allData.append(data)

    def spider_closed(self, spider):
        print("=========================Done===============================")

        print(self.allData)

        save_to_csv(self.csv_file_name, self.allData)
