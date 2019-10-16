# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
import logging
import pymysql.cursors
from copy import deepcopy


class LiepinwangPipeline(object):
	def process_item(self, item, spider):
		# print(item)
		pass


# 去除重复数据
class DuplicatesPipeline(object):
	def __init__(self):
		self.job_list = list()

	def process_item(self, item, spider):
		if item['pay'] == '面议':
			raise DropItem("useless item:%s" % item)
			
		# 防止入库速度过慢导致数据重复
		item = deepcopy(item)
		jobtitle = item['jobtitle']
		company = item['company']
		area = item['area']

		if self.job_list.count([jobtitle,company,area]) != 	0:
			raise DropItem("Duplicate item found:%s" % item)

		if len(self.job_list)>10000:
			self.job_list = []

		self.job_list.append([jobtitle,company,area])
		return item






# class MysqlTwistedPipline(object):
# 	def __init__(self, dbpool):
# 		self.dbpool = dbpool
 
# 	@classmethod
# 	def from_settings(cls, settings):
# 		dbparms = dict(
# 			host = settings["MYSQL_HOST"],
# 			db = settings["MYSQL_DATABASE"],
# 			user = settings["MYSQL_USER"],
# 			passwd = settings["MYSQL_PASSWORD"],
# 			charset='utf8',
# 			cursorclass=pymysql.cursors.DictCursor,
# 			use_unicode=True,
# 		)
# 		dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
 
# 		return cls(dbpool)
 
# 	def process_item(self, item, spider):
		
# 		#使用twisted将mysql插入变成异步执行
# 		query = self.dbpool.runInteraction(self.do_insert, item)
# 		query.addErrback(self.handle_error, item, spider) #处理异常
 
# 	def handle_error(self, failure, item, spider):
# 		#处理异步插入的异常
# 		print(failure)
 
# 	def do_insert(self, cursor, item):
# 		#执行具体的插入
# 		#根据不同的item 构建不同的sql语句并插入到mysql中
		
# 		data = dict(item)
# 		keys = ', '.join(data.keys())  # 'area, education, experience, job_title, key, pay, temptation'
# 		values = ', '.join(['%s'] * len(data))  # '%s, %s, %s, %s, %s, %s, %s'
# 		# 构造动态sql语句
# 		sql = 'insert into %s (%s) values (%s)' % (item.table, keys, values)  # 'insert into jobs (area, education, experience, job_title, key, pay, temptation) values (%s, %s, %s, %s, %s, %s, %s)'
# 		cursor.execute(sql, tuple(data.values()))











class MysqlPipeline():
	def __init__(self, host, database, user, password, port):
		self.host = host
		self.database = database
		self.user = user
		self.password = password
		self.port = port
	
	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			host=crawler.settings.get('MYSQL_HOST'),
			database=crawler.settings.get('MYSQL_DATABASE'),
			user=crawler.settings.get('MYSQL_USER'),
			password=crawler.settings.get('MYSQL_PASSWORD'),
			port=crawler.settings.get('MYSQL_PORT'),
		)
	
	def open_spider(self, spider):
		# 爬虫开启时运行，连接数据库
		self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8',
								  port=self.port)
		self.cursor = self.db.cursor()
	
	def close_spider(self, spider):
		# 爬虫关闭时运行，关闭数据库连接
		self.db.close()
	
	def process_item(self, item, spider):
		if item['pay'] == '面议':
			raise DropItem("useless item:%s" % item)
		data = dict(item)
		keys = ', '.join(data.keys())  # 'area, education, experience, job_title, key, pay, temptation'
		values = ', '.join(['%s'] * len(data))  # '%s, %s, %s, %s, %s, %s, %s'
		# 构造动态sql语句
		sql = 'insert into %s (%s) values (%s)' % (item.table, keys, values)  # 'insert into jobs (area, education, experience, job_title, key, pay, temptation) values (%s, %s, %s, %s, %s, %s, %s)'
		self.cursor.execute(sql, tuple(data.values()))
		self.db.commit()
		return item


