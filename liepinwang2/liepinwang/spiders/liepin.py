# -*- coding: utf-8 -*-
import scrapy
import re
from liepinwang.items import LiepinwangItem
from pprint import pprint
import traceback
from urllib import parse


class LiepinSpider(scrapy.Spider):
	name = 'liepin'
	allowed_domains = ['liepin.com']
	start_urls = ['http://liepin.com/it/']

	# 返回各个职业标签的Request
	def parse(self, response):
		base_url = "https://www.liepin.com"
		type_url_list = response.xpath('//div[contains(@class,"wrap")]//ul[contains(@class,"sidebar")]//dd/a/@href').getall()  # 包含所有标签的一个列表 [java,php,销售代表，交互代表...]
		for i in type_url_list:
			type_url = base_url + i  # 构造完整的各职业标签url
			# print(type_url)
			yield scrapy.Request(type_url, callback=self.parse_area_url)  # 返回全部链接

		# 测试用
		# test_url = "https://www.liepin.com/zhaopin/?imscid=R000000035&key=Java&dqs=090050&salary=0$10"
		# yield scrapy.Request(test_url, callback = self.parse_area_url)

	# 修改url地址中的"dps"参数,构造各职业标签下各地区url的Request
	def parse_area_url(self, response):
		area_url_list = [str(x) for x in range(10,311,10)]
		for num in range(0,9):
			area_url_list[num] = '0' + area_url_list[num]  # 让前9个元素变成‘010，020，030...’的形式
		for num in range(0,31):
			area_url_list[num] = 'dqs=' + area_url_list[num]  # 让元素变成‘dqs=010, dqs=020 ...’的形式
		for i in range(0,31):
			area_url_list[i] = re.sub(r'dqs=\d+', area_url_list[i], response.url)  # 替换参数，url构造完成
			yield scrapy.Request(area_url_list[i], callback = self.parse_pay_url)  # 各职业标签下的各个省级行政区的Request
		# pprint(area_url_list)  # 输出正确
		

	# 各地区的列表页，构造该地区下不同薪资的url
	# 不同的工资范围通过修改url中的参数salary的值就可以  如：'salary=10$20'就是10-20万年薪
	# 此函数中的response包含以上所有地区的response(31个：含4个直辖市)
	def parse_pay_url(self, response):
		pay_list = ['salary=0$10','salary=10$20','salary=20$30','salary=30$50','salary=50$100']  # 按照工资水平，将一个地区的数据分为五层爬取
		for pay in pay_list:
			# pay_url = re.sub(r'(salary=\d+\$?\d+&?)+', pay, response.url)  # 构造不同价格参数的url
			pay_url = response.url + '&' + pay
			# print(pay_url)  # 输出正确
			yield scrapy.Request(pay_url, callback=self.parse_type_url)

		# 测试用
		# pay_url_list.append(re.sub(r'\d+\$\d+', '10$20', response.url))
		# print(pay_url_list)  # 输出所有地区下所有工资分区的url

	# 处理列表页 获取职位，职业类型，薪水，学历，地点，经验要求
	# 翻页爬取
	def parse_type_url(self, response):  # 这里response包含上面所有链接的response
		li_list =  response.xpath('//ul[@class="sojob-list"]/li')
		
		for li in li_list:
			if li.xpath('./attribute::*').get() == 'downgrade-search':  # 如果当前li节点出现'downgrade-search' 就停止该函数
				return
			try:
				item = LiepinwangItem()
				item['jobtitle'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/h3/a/text()').get()).strip()  # 职位名称
				item['jobkey'] = re.search('key=(\w+)', parse.unquote(response.url)).group(1)  # 职位类别
				print(response.url)
				item['pay'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/p[1]/span[@class="text-warning"]/text()').get()).strip()
				# item['area'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/p[1]/child::*[@class="area"]/text()').get()).strip()  # 公司地址
				item['area'] = response.xpath('//div[@class="search-bar-wrap"]//div[@class="show-text"]//text()').get()  # 所属地区
				item['education'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/p[1]/span[@class="edu"]/text()').get()).strip()  # 教育程度
				item['experience'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/p[1]/span[last()]/text()').get()).strip()  # 工作经验
				temptation = li.xpath('.//div[contains(@class,"company-info")]/p[contains(@class,"temptation")]/span/text()').getall()
				if temptation:
					item['temptation'] = ','.join(temptation)  # 福利 列表转换成字符串
				else:
					item['temptation'] = ''
			except Exception as e:
				print(traceback.format_exc())
			else:
				yield item

		try:
			next_url = 'https://www.liepin.com' + response.xpath('//div[@class="job-content"]//div[@class="pagerbar"]/a[last()-1]/@href').get()
		except Exception as e:
			print(traceback.format_exc())
		else:
			if next_url != 'javascript:;':  # 如果不是最后一页的标志
				yield scrapy.Request(next_url, callback=self.parse_type_url)


		

