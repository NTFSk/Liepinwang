# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class LiepinwangPipeline(object):
    def process_item(self, item, spider):
        # print(item)
        pass


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
    	# 对item中的特殊字符进行转义(', ", \, _)
        data = dict(item)
        keys = ', '.join(data.keys())  # 'area, education, experience, job_title, key, pay, temptation'
        values = ', '.join(['%s'] * len(data))  # '%s, %s, %s, %s, %s, %s, %s'
        # 构造动态sql语句
        sql = 'insert into %s (%s) values (%s)' % (item.table, keys, values)  # 'insert into jobs (area, education, experience, job_title, key, pay, temptation) values (%s, %s, %s, %s, %s, %s, %s)'
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()
        return item


