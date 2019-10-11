# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LiepinwangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    job_title = scrapy.Field()  # 职位名称
    key = scrapy.Field()  # 职位类型 如Java、PHP、C++、销售代表……
    area = scrapy.Field()  # 工作地点
    pay = scrapy.Field()  # 工资
    education = scrapy.Field()  # 教育经历
    experience = scrapy.Field()  # 工作经验
