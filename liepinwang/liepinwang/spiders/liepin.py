# -*- coding: utf-8 -*-
import scrapy
import re
from liepinwang.items import LiepinwangItem


class LiepinSpider(scrapy.Spider):
	name = 'liepin'
	allowed_domains = ['liepin.com']
	start_urls = ['http://liepin.com/it/']

	# 返回各个职业标签的Request
	def parse(self, response):
		# base_url = "https://www.liepin.com/zhaopin/?imscid=R000000035&key={}&dqs=090050"
		# type_url_list = response.xpath('//div[contains(@class,"wrap")]//ul[contains(@class,"sidebar")]//dd/a/text()').getall()  # 包含所有标签的一个列表 [java,php,销售代表，交互代表...]
		# for i in type_url_list:
		# 	type_url = base_url.format(i)  # 把标签填入到base_url中，构造每个职业的链接
		# 	yield scrapy.Request(type_url, callback=self.parse_type_url)  # 返回全部链接

		# 测试用
		test_url = "https://www.liepin.com/zhaopin/?isAnalysis=&dqs=&pubTime=&salary=&subIndustry=&industryType=&compscale=&key=Java&init=-1&searchType=1&headckid=7085bbec3dcf7183&flushckid=1&compkind=&fromSearchBtn=2&sortFlag=15&ckid=2fdb4d066bb2b030&degradeFlag=0&curPage=0&jobKind=&industries=&clean_condition=&siTag=1SOHiA4eoigXpy03WSE4GQ%7EfA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_unknown&d_ckId=da84b6a5888a8090515d8f97558435e1&d_curPage=0&d_pageSize=40&d_headId=39073f967bf825fb9c6195ac1928379b"
		yield scrapy.Request(test_url, callback = self.parse_area_url)

	# 修改url地址中的"dps"参数,构造各职业标签下各地区url的Request
	def parse_area_url(self, response):
		# area_url_list = response.xpath('//div[@class="search-conditions"]//dl[3]//dd[@data-param="city"]/a/@href').getall()[1:-1]  # 12个热门城市的url（用不到了）
		area_url_list = [str(x) for x in range(10,311,10)]
		for num in range(0,9):
			area_url_list[num] = '0' + area_url_list[num]  # 让前9个元素变成‘010，020，030...’的形式
		for num in range(0,31):
			area_url_list[num] = 'dqs=' + area_url_list[num]  # 让元素变成‘dqs=010, dqs=020 ...’的形式

		for i in range(0,31):
			area_url_list[i] = re.sub(r'dqs=\d{0,3}', area_url_list[i], response.url)  # 替换参数，url构造完成
			if area_url_list[i] is not None:
				# print(area_url_list[i])
				yield scrapy.Request(area_url_list[i], callback = self.parse_pay_url)  # 各职业标签下的各个省级行政区的Request

	# 各地区的列表页，构造该地区下不同薪资的url
	# 不同的工资范围通过修改url中的参数salary的值就可以  如：'salary=10$20'就是10-20万年薪
	# 此函数中的response包含以上所有地区的response(31个：含4个直辖市)
	def parse_pay_url(self, response):
		pay_list = ['salary=0$10','salary=10$20','salary=20$30','salary=30$50','salary=50$100']  # 按照工资水平，将一个地区的数据分为五层爬取
		for pay in pay_list:
			pay_url = re.sub(r'salary=\d?\$?\d?', pay, response.url)  # 构造不同价格参数的url
			# print(pay_url)
			yield scrapy.Request(pay_url, callback=self.parse_type_url)

		# 测试用
		# pay_url_list.append(re.sub(r'\d+\$\d+', '10$20', response.url))
		# print(pay_url_list)  # 输出所有地区下所有工资分区的url

	# 处理列表页 获取职位，职业类型，薪水，学历，地点，经验要求
	# 翻页爬取
	def parse_type_url(self, response):  # 这里response包含上面所有链接的response
		# print("翻页啦！")
		# print("*"*50)
		# print("*"*50)
		# print("*"*50)
		li_list =  response.xpath('//ul[@class="sojob-list"]/li')
		# print(type(li_list))
		# print(len(li_list))
		
		for li in li_list:
			try:
				item = LiepinwangItem()
				item['job_title'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/h3/a/text()').get()).strip()  # 职位名称
				item['key'] = re.findall('key=(\w+)', response.url)  # 职位标签
				item['pay'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/p[1]/span[@class="text-warning"]/text()').get()).strip()
				# item['area'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/p[1]/child::*[@class="area"]/text()').get()).strip()  # 公司地址
				item['area'] = response.xpath('//div[@class="search-bar-wrap"]//div[@class="show-text"]//text()').get()  # 所属地区
				item['education'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/p[1]/span[@class="edu"]/text()').get()).strip()  # 教育程度
				item['experience'] = re.sub('[\r\n\t]','',li.xpath('.//div[@class="job-info"]/p[1]/span[last()]/text()').get()).strip()  # 工作经验
			except:
				return
			else:
				yield item

		next_url = "https://www.liepin.com" + response.xpath('//div[@class="job-content"]//div[@class="pagerbar"]/a[last()-1]/@href').get()
		if next_url is not None:
			yield scrapy.Request(next_url, callback=self.parse_type_url)


		

