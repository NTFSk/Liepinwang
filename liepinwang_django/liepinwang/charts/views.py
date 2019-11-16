from django.shortcuts import render

from django.http import Http404
from django.http import HttpResponse

def index(request):
	return render(request, 'charts/index.html')

def mcharts(request):

	import pymysql
	from collections import Counter
	from pyecharts.faker import Faker  # pyecharts的示例数据来源
	from pyecharts import options as opts
	from pyecharts.charts import Bar, Tab, Pie, Line, WordCloud, Map, Bar, Page
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
			sql = 'select pay,count(*) pay_num from jobs where area="{}" and jobkey="{}" group by pay'.format(self.area,self.jobkey)
			data = pd.read_sql(sql,con=self.db)
			pay_list = data.pay.tolist()
			pay_num_list = data.pay_num.tolist()
			dict1 = dict(zip(pay_list,pay_num_list)) # 把工资列表和对应数量组成一个字典
			dict2 = {'0-10w':0,'10-20w':0, '20-30w':0, '30-50w':0, '50-100w':0}
			# 将数据整合到不同的工资区间
			for key, value in dict1.items():
				try:
					pay_num = int(re.match(r'(\d+)\D?',key).group(1))
					if(pay_num>=0 and pay_num<10):
						dict2['0-10w'] += value
					elif(pay_num>=10 and pay_num<20):
						dict2['10-20w'] += value
					elif(pay_num>=20 and pay_num<30):
						dict2['20-30w'] += value
					elif(pay_num>=30 and pay_num<50):
						dict2['30-50w'] += value
					else:
						dict2['50-100w'] += value
				except:
					pass
			range_list, pay_list = zip(*dict2.items())  # 用新字典的键值各自生成元组
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
			try:
				str_tem_list = data.temptation.tolist()  # 每一个岗位的福利信息组成的一个列表
				tem_list = []
				length = len(str_tem_list)
				for i in range(0,length):
					# 因为此时的福利信息还是一个比较长的字符串，把它按照逗号分隔开来，取出每一个关键词再添加到列表中
					tem_list += str_tem_list[i].split(',')  # 这就构造出了一个元素都是单个关键词的列表
				c = dict(Counter(tem_list))
				tem_list, tem_num_list = zip(*c.items())  # 用新字典的键值各自生成元组
				return tem_list, tem_num_list
			except:
				raise Http404("没有找到相关信息")


	class GetEduData(SqlConnect):
		""" 获取和整理数据库中关于教育程度的数据 """
		def __init__(self, area, jobkey):
			super().__init__()
			self.area = area
			self.jobkey = jobkey

		def get_data(self):
			sql = 'select education, count(*) num from jobs where area="{}" and jobkey="{}" group by education'.format(self.area,self.jobkey)
			data = pd.read_sql(sql,con=self.db)  # 获取到的数据是series类型
			edu_list = data.education.tolist()
			edu_num_list = data.num.tolist()
			return edu_list, edu_num_list


	class GetExpAndPayData(SqlConnect):
		""" 工作经验和工资的关系 """
		def __init__(self, area, jobkey):
			super().__init__()
			self.area = area
			self.jobkey = jobkey

		def del_min_data(self, ex_list, num_list, average_list):
			import heapq
			length = int(len(ex_list)/3)
			for i in range(0,length):
				min_num_index = list(map(num_list.index, heapq.nsmallest(1, num_list)))[0]
				ex_list.pop(min_num_index)
				num_list.pop(min_num_index)
				average_list.pop(min_num_index)
			return ex_list, num_list, average_list

		def get_data(self):
			sql = 'select experience, pay from jobs where area="{}" and jobkey="{}"'.format(self.area, self.jobkey)
			data = pd.read_sql(sql,con=self.db)
			grouped = data.groupby('experience')
			ex_list = list(grouped.groups.keys())  # 经验列表
			num_list = grouped.agg(np.size).pay.tolist() # 各经验对应的工作岗位数量
			average_list = [] # 各经验对应的平均工资

			for i in ex_list: # 遍历经验列表
				pay_list = grouped.get_group(i).pay.tolist()  # 获取 当前经验 所对应的工资列表
				for j in range(0,len(pay_list)):  # 遍历工资列表
					pay_list[j] = int(re.match(r'(\d+)\D?',pay_list[j]).group(1))  # 用正则表达式提取出需要的部分
				a = np.array(pay_list)  # 转换格式，方便求平均值
				average_list.append(int(np.mean(a, axis=0)))  # 求平均值，并转换成int格式

			ex_list, num_list, average_list = self.del_min_data(ex_list, num_list, average_list)

			return ex_list, num_list, average_list


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
			Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS,))  # 创建图形实例并设置主题
			.add(
				"",
				[list(z) for z in zip(ex_list, ex_num_list)],
				radius=["40%", "75%"],  # 内圆和外圆的大小
				center=["50%", "60%"]
			)
			# 全局配置项 - set_global_options
			.set_global_opts(  
				# 标题配置项
				title_opts=opts.TitleOpts(
					title="{}地区 {} 岗位的工作经验要求".format(area,jobkey),  # 主标题
					title_textstyle_opts=opts.TextStyleOpts(color="black",),
					subtitle="岗位数量：{}个".format(sum(ex_num_list)),  # 副标题
					subtitle_textstyle_opts=opts.TextStyleOpts(color="slateblue", font_size=16),
				),
				# 图例配置项
				legend_opts=opts.LegendOpts(  # 图例配置项（图例就是左边那一列）
					orient="vertical",  # 图里列表的布局朝向
					pos_bottom="20%",  # 图例组件离容器下侧的距离
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
			Bar(init_opts=opts.InitOpts(theme=ThemeType.ROMA,))
			.add_xaxis(range_list)
			.add_yaxis(
				" ",
				pay_list,
			)
			.set_global_opts(
				title_opts=opts.TitleOpts(title="{}地区{}岗位工资待遇".format(area, jobkey), subtitle=""),
				yaxis_opts=opts.AxisOpts(name="岗位数量"),
				xaxis_opts=opts.AxisOpts(name="工资水平(年薪)"),
				tooltip_opts = opts.TooltipOpts(formatter = "{b} : {c}")
			)
			# 系列配置项 - set_series_options
			.set_series_opts(
				label_opts=opts.LabelOpts(  # 标签配置项（标签就是图片旁边的文字）
					formatter="{c}",  # 标签内文本的格式
					font_size = 16,  # 标签文本的字号大小
				),
			)
		)
		return c

	# 词云图
	def wordcloud_base(tem_list,tem_num_list) -> WordCloud:
		c = (
			WordCloud(init_opts = opts.InitOpts(width = "900px", height = "550px", theme=ThemeType.ROMA))
			.add("", zip(tem_list,tem_num_list), word_size_range=[20, 120], shape=SymbolType.DIAMOND)
			.set_global_opts(title_opts=opts.TitleOpts(title="{}地区 {} 岗位工作福利".format(area,jobkey),))
		)
		return c

	# 富文本图
	def pie_rich_label(edu_list, edu_num_list) -> Pie:
		c = (
			Pie(init_opts = opts.InitOpts(height = "550px",))
			.add(
				"",
				[list(z) for z in zip(edu_list, edu_num_list)],
				radius=["40%", "55%"],
				label_opts=opts.LabelOpts(
					position="outside",
					formatter="{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
					background_color="#eee",
					border_color="#aaa",
					border_width=1,
					border_radius=4,
					rich={
						"a": {"color": "#999", "lineHeight": 22, "align": "center"},
						"abg": {
							"backgroundColor": "#e3e3e3",
							"width": "100%",
							"align": "right",
							"height": 22,
							"borderRadius": [4, 4, 0, 0],
						},
						"hr": {
							"borderColor": "#aaa",
							"width": "100%",
							"borderWidth": 0.5,
							"height": 0,
						},
						"b": {"fontSize": 16, "lineHeight": 33},
						"per": {
							"color": "#eee",
							"backgroundColor": "#334455",
							"padding": [2, 4],
							"borderRadius": 2,
						},
					},
				),
			)
			.set_global_opts(
				title_opts=opts.TitleOpts(title="{}地区{}岗位的教育程度要求".format(area, jobkey)),
				legend_opts = opts.LegendOpts(
					pos_top="bottom",
				),
			)
		)
		return c

	# 层叠多图(双Y轴) - 经验与平均工资
	def overlap_bar_line(ave_ex_list, ave_job_num_list, average_list) -> Bar:
		bar = (
			Bar()
			.add_xaxis(ave_ex_list)
			.add_yaxis("岗位数量", ave_job_num_list)
			.extend_axis(
				yaxis=opts.AxisOpts(
					axislabel_opts=opts.LabelOpts(formatter="{value} 万元"), split_number=5
				)
			)
			.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
			.set_global_opts(
				title_opts=opts.TitleOpts(title="{}地区{}岗位工作经验与平均薪资".format(area, jobkey)),
				yaxis_opts=opts.AxisOpts(
					axislabel_opts=opts.LabelOpts(formatter="{value} 个")
				),
			)
		)

		line = Line().add_xaxis(ave_ex_list).add_yaxis("平均工资", average_list, yaxis_index=1)
		bar.overlap(line)
		return bar

	# 地图（分段型）
	def map_visualmap(area_list, job_num_list) -> Map:
		c = (
			Map(init_opts=opts.InitOpts(theme=ThemeType.ROMA,))
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
				title_opts=opts.TitleOpts(title="{}岗位全国热度一览".format(jobkey)),
				legend_opts = opts.LegendOpts(pos_left = 'center',),
				visualmap_opts=opts.VisualMapOpts(  # 视觉映射配置项
					is_piecewise=True,  # 是否分段
					max_= max(job_num_list),  # 分段的最大值
					# 自定义分段信息
					pieces = [
						{"min": 0, "max": int(max(job_num_list)/5), "color": "steelblue"},
						{"min": int(max(job_num_list)/5), "max": int(max(job_num_list)/5)*2},
						{"min": int(max(job_num_list)/5)*2, "max": int(max(job_num_list)/5)*3},
						{"min": int(max(job_num_list)/5)*3, "max": int(max(job_num_list)/5)*4},
						{"min": int(max(job_num_list)/5)*4, "max": max(job_num_list)},
					]
				)
			)
		)
		return c


	
	# if __name__ == '__main__':
	# 	# area = input("please enter the area:")
	# 	# jobkey = input("please enter the jobkey:")
	
	user_text = request.GET['key_words']

	# print(user_text)
	# print(type(user_text))
	try:
		user_text_list = (user_text.strip()).split(' ')  # 将用户输入的字符串去首尾空格后，按照空格切片
		area = user_text_list[0]
		jobkey = user_text_list[1]
	except IndexError:
		raise Http404("请检查输入的信息是否符合规范")

	# 获取工作经验的数据
	data_exp = GetExpData(area, jobkey)
	ex_list, ex_num_list = data_exp.get_data()
	# 获取工资的数据
	data_pay = GetPayData(area,jobkey)
	pay_list, range_list = data_pay.get_data()
	# 获取工作福利的数据
	data_tem = GetTemData(area, jobkey)
	tem_list, tem_num_list = data_tem.get_data()
	# 获取教育程度的数据
	data_edu = GetEduData(area, jobkey)
	edu_list, edu_num_list = data_edu.get_data()
	# 获取工作经验和对应平均工资的数据
	data_average = GetExpAndPayData(area, jobkey)
	ave_ex_list, ave_job_num_list, average_list = data_average.get_data()
	# 获取工作数量的数据
	data_area = GetAreaData(jobkey)
	area_list, job_num_list = data_area.get_data()



	# 构造布局
	# layout：布局方式, page_title： 网页名, interval: 图例间隔
	page = Page(layout=Page.SimplePageLayout, page_title = "{}-{}岗位的分析".format(area,jobkey), interval=2)
	page.add(
		pie_radius(ex_list, ex_num_list),
		bar_base(pay_list, range_list),
		wordcloud_base(tem_list, tem_num_list),
		pie_rich_label(edu_list, edu_num_list),
		overlap_bar_line(ave_ex_list, ave_job_num_list, average_list),
		map_visualmap(area_list, job_num_list),
	)
	page.render('charts/templates/charts/render.html')

	return render(request, 'charts/render.html')

