import pymysql
from collections import Counter
from pyecharts.faker import Faker  # pyecharts的示例数据来源
from pyecharts import options as opts
from pyecharts.charts import Bar, Tab, Pie, Line, WordCloud, Map, Bar
from pyecharts.globals import ThemeType, SymbolType, ChartType
from pyecharts.components import Table
from pyecharts.commons import utils
from pyecharts.types import Tooltip
import numpy as np
import pandas as pd
import re

class SqlConnect(object):
	def __init__(self):
		self.db = pymysql.connect(host='localhost', user='root',password='123123',db='liepinwang',charset='utf8')  # 链接数据库
		

class GetExpData(SqlConnect):
	""" 获取和整理数据库中关于工作经验的数据 """
	def __init__(self, area, jobkey):
		super().__init__()
		self.area = area
		self.jobkey = jobkey

	def get_data(self):
		sql ='select experience,count(*) num from jobs where area="{}" and jobkey="{}" group by experience'.format(self.area,self.jobkey)
		data = pd.read_sql(sql,con=self.db)
		ex_list = list(data.experience)  # 经验列表
		num_list = list(data.num)  # 各经验对应的数值
		dict1 = dict(zip(ex_list,num_list))  # 把经验列表和数值组成一个字典
		dict2 = {'经验不限':0,'1-3年':0, '3-5年':0, '5-10年':0, '10年以上':0}
		# 将数据整合到不同的经验区间
		for key, value in dict1.items():
			try:
				key_num = int(re.match(r"\d+", key).group()) # 提取经验中的数字部分
				if(key_num>=1 and key_num<3):
					dict2['1-3年'] += value
				elif(key_num>=3 and key_num<5):
					dict2['3-5年'] +=value
				elif(key_num>=5 and key_num<10):
					dict2['5-10年'] += value
				else:
					dict2['10年以上'] += value
			except:  # 如果为None值
				dict2['经验不限'] +=value

		ex_list,ex_num_list = zip(*dict2.items())  # 用新字典的键值各自生成元组
		return ex_list,ex_num_list


class GetPayData(SqlConnect):
	""" 获取和整理数据库中关于薪资的数据 """
	def __init__(self, area, jobkey):
		super().__init__()
		self.area = area
		self.jobkey = jobkey

	def get_data(self):
		sql ='select pay from jobs where area="{}" and jobkey="{}"'.format(self.area,self.jobkey)
		data = pd.read_sql(sql,con=self.db)
		pay_list = data.pay.tolist()
		dict1 = {'0-10w':0,'10-20w':0, '20-30w':0, '30-50w':0, '50-100w':0}
		for i in range(0,len(pay_list)):
			try:
				pay_list[i] = int(re.match(r'(\d+)-',pay_list[i]).group(1))
				if(pay_list[i]>=0 and pay_list[i]<10):
					dict1['0-10w'] += 1
				elif(pay_list[i]>=10 and pay_list[i]<20):
					dict1['10-20w'] += 1
				elif(pay_list[i]>=20 and pay_list[i]<30):
					dict1['20-30w'] += 1
				elif(pay_list[i]>=30 and pay_list[i]<50):
					dict1['30-50w'] += 1
				else:
					dict1['50-100w'] += 1
			except:
				pass
		range_list, pay_list = zip(*dict1.items())  # 用新字典的键值各自生成元组
		return pay_list, range_list


class GetTemData(SqlConnect):
	""" 获取和整理数据库中关于工作福利的数据 """
	def __init__(self, area, jobkey):
		super().__init__()
		self.area = area
		self.jobkey = jobkey

	def get_data(self):
		sql ='select temptation from jobs where temptation is not null and temptation <> "" and area="{}" and jobkey="{}" '.format(self.area,self.jobkey)
		data = pd.read_sql(sql,con=self.db)  # 获取到的数据是series类型
		str_tem_list = data.temptation.tolist()  # 每一个岗位的福利信息组成的一个列表
		tem_list = []
		length = len(str_tem_list)
		for i in range(0,length):
			# 因为此时的福利信息还是一个比较长的字符串，把它按照逗号分隔开来，取出每一个关键词再添加到列表中
			tem_list += str_tem_list[i].split(',')  # 这就构造出了一个元素都是单个关键词的列表
		c = dict(Counter(tem_list))
		tem_list, tem_num_list = zip(*c.items())  # 用新字典的键值各自生成元组
		return tem_list, tem_num_list


class GetAreaData(SqlConnect):
	""" 获取和整理数据库中关于全国各地工作岗位数量的数据 """
	def __init__(self, jobkey):
		super().__init__()
		self.jobkey = jobkey

	def get_data(self):
		sql = 'select area,count(area) job_num from jobs where jobkey="{}" group by area'.format(self.jobkey)
		data = pd.read_sql(sql,con=self.db)  # 获取到的数据是series类型
		area_list = data.area.tolist()
		job_num_list = data.job_num.tolist()
		return area_list, job_num_list


#饼图
def pie_radius(ex_list,ex_num_list) -> Pie:
    c = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.ROMA))  # 创建图形实例并设置主题
        .add(
            "",
            [list(z) for z in zip(ex_list, ex_num_list)],
            radius=["40%", "75%"],  # 内圆和外圆的大小
            center=["55%", "60%"]
        )
        # 全局配置项 - set_global_options
        .set_global_opts(  
            title_opts=opts.TitleOpts(
            	title="{} {} 岗位的工作经验要求".format(area,jobkey),  # 主标题
             	subtitle="岗位数量：{}个".format(sum(ex_num_list)),  # 副标题
             	subtitle_textstyle_opts=opts.TextStyleOpts(font_size=16)
            ),  # 标题设置
            legend_opts=opts.LegendOpts(  # 图例配置项（图例就是左边那一列）
                orient="vertical",  # 图里列表的布局朝向
                pos_top="15%",  # 图例组件离容器上侧的距离
                pos_left="2%",  # 图例组件离容器左侧的距离
                textstyle_opts=opts.TextStyleOpts(font_size=16)  # 字体设置
            ),
        )
        # 系列配置项 - set_series_options
        .set_series_opts(
        	label_opts=opts.LabelOpts(  # 标签配置项（标签就是图片旁边的文字）
        		formatter="{b}: {c}（{d}%）",  # 标签内文本的格式
        		font_size = 16,  # 标签文本的字号大小
        	),
        	
        )
    )
    return c

# 柱状图
def bar_base(pay_list, range_list) -> Bar:
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(range_list)
        .add_yaxis("商家A", pay_list)
        .set_global_opts(
        	title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"),
        	yaxis_opts=opts.AxisOpts(name="所占比例"),
            xaxis_opts=opts.AxisOpts(name="工资水平"),
        )
        # 系列配置项 - set_series_options
        .set_series_opts(
        	label_opts=opts.LabelOpts(  # 标签配置项（标签就是图片旁边的文字）
        		formatter="{value}%）",  # 标签内文本的格式
        		font_size = 16,  # 标签文本的字号大小
        	),
        )
    )
    return c

# 词云图
def wordcloud_base(keys,values) -> WordCloud:
    c = (
        WordCloud(init_opts = opts.InitOpts(width = "1000px", height = "600px"))
        .add("", zip(keys,values), word_size_range=[20, 120], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(title="{} {} 岗位的工作福利".format(area,jobkey),))
    )
    return c


# 地图（分段型）
def map_visualmap(area_list, job_num_list) -> Map:
    c = (
        Map()
        .add(
        	"",
        	[list(z) for z in zip(area_list, job_num_list)],
        	"china",

        	tooltip_opts = opts.TooltipOpts(formatter=utils.JsCode(
        		"""function (params){
        			return params.name + ' : ' + params.value + '<br/>';
        		}"""
        		))
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Map-VisualMap（分段型）"),
            legend_opts = opts.LegendOpts(pos_left = 'center',),
            visualmap_opts=opts.VisualMapOpts(  # 视觉映射配置项
            	is_piecewise=True,  # 是否分段
            	max_= max(job_num_list),  # 分段的最大值
            	# 自定义分段信息
            	pieces = [
            		{"min": 0, "max": int(max(job_num_list)/5)},
            		{"min": int(max(job_num_list)/5), "max": int(max(job_num_list)/5)*2},
            		{"min": int(max(job_num_list)/5)*2, "max": int(max(job_num_list)/5)*3},
            		{"min": int(max(job_num_list)/5)*3, "max": int(max(job_num_list)/5)*4},
            		{"min": int(max(job_num_list)/5)*4, "max": max(job_num_list)},
            	]
            )
        )
    )
    return c


if __name__ == '__main__':
	# area = input("please enter the area:")
	# jobkey = input("please enter the jobkey:")
	area = "上海"
	jobkey = "Java"
	data_exp = GetExpData(area, jobkey)
	ex_list, ex_num_list = data_exp.get_data()
	data_tem = GetTemData(area, jobkey)
	tem_list, tem_num_list = data_tem.get_data()
	data_area = GetAreaData(jobkey)
	area_list, job_num_list = data_area.get_data()
	data_pay = GetPayData(area,jobkey)
	pay_list, range_list = data_pay.get_data()


	tab = Tab()
	tab.add(pie_radius(ex_list, ex_num_list),"工作经验")
	tab.add(bar_base(pay_list, range_list),"工资待遇")
	tab.add(wordcloud_base(tem_list, tem_num_list),"工作福利")
	tab.add(map_visualmap(area_list, job_num_list), "全国岗位数量")

	tab.render()
