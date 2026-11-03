# 扩展分析应用：年-技术簇矩阵，计算各技术簇的平均年龄和增长速度，专利权人数量

import numpy as np
import os
import sys
import pandas as pd
import ast
import json
import re
import shutil
import time
from tqdm import tqdm
from code_chinese_clean.utils.deduplicate import deduplicate_by_field, deduplicate_list
from code_chinese_clean.utils.fopener import json_open, json_open_write, jsonl_open_write,text_open_write

    
# 提取年份
def get_year(cell):
    cell = str(cell)
    try:
        year = int(cell[:4])
        if not year > 1900:
            year = 2013
    except:
        year = 2013
    return year

# 将单元格内容转换为整数
def get_int(cell, fillna_value=1):
    cell = str(cell)
    try:
        year = int(cell)
    except:
        year = fillna_value
    return year


def get_patent_authors(cell):
    if pd.isnull(cell):
        return []
    # 使用正则表达式来分割中文分号和英文分号
    authors = re.split(r';|；', cell)
    # 移除可能的空字符串，并去除首尾空格
    return [author.strip() for author in authors if author.strip()]


def cu_patentAvg_info(config):
    # 簇-专利平均信息
    print("计算簇-专利平均信息")


    data_patent = pd.read_csv(f"{config.sub_project_dir}/output/专利-spo-子图.csv")  # 读取专利数据集
    data_subnet = pd.read_csv(f"{config.sub_project_dir}/output/子图.csv")  # 读取簇（子图）的信息数据集


    # 预处理专利数据集以提取每个专利的作者列表
    patent2authors = {id: get_patent_authors(row[' AE ']) for id, row in data_patent.iterrows()}
    
    # 初始化列以存储去重后的专利作者列表和数量
    authors_list = []
    authors_num = []
    years = []

    patents_year = [get_year(cell) for cell in data_patent["AD_Year"]]  # 注意这里数据表头！
    
    for id, line in data_subnet.iterrows():
        pids = json.loads(line["专利"])  # 获取属于该簇的专利ID列表
        # 初始化一个集合，用于存储该簇的专利权人（去重）
        authors_set = set()  # 用于存储该簇的去重作者列表
    
        # 遍历簇中的每个专利ID
        for id in pids:
            authors_set.update(patent2authors.get(id, []))

        subnet_years = [patents_year[id] for id in pids] # 将专利转到年份索引，subnet_years为该簇所有专利的年份列表
        avg_year = sum(subnet_years) / len(pids)  # 簇的平均年份：簇年份总和/簇专利数量
        
        authors_list.append(list(authors_set))
        authors_num.append(len(authors_set))
        years.append(avg_year) # 所有簇的平均年份数据
    
    # 更新数据集
    data_subnet["author"] = authors_list
    data_subnet["authornum"] = authors_num
    data_subnet["簇年龄"] = years
    
    # 输出结果到新的CSV文件
    data_subnet.to_csv(f"{config.sub_project_dir}/output/子图.csv", index=False)


def calculate_growth_rate(data):
    yearly_growth = data.diff(axis=1)  # 计算每一列（年份）与前一列的差异，即年增长量 
    prev_year_data = data.shift(axis=1) # 获取前一年的专利数量，用于作为分母
    
    # 计算增长速度，这里先初始化一个和yearly_growth形状相同、但所有元素为0的DataFrame
    growth_rate = pd.DataFrame(0, index=data.index, columns=data.columns)
    # 对于分母不为0的情况，更新growth_rate的值
    non_zero_mask = prev_year_data != 0
    growth_rate[non_zero_mask] = yearly_growth[non_zero_mask].div(prev_year_data[non_zero_mask], axis=0)
    # 处理NaN（包括初始年份的增长速度，因为没有前一年的数据）
    growth_rate = growth_rate.fillna(0)
    # 计算平均增长速度
    average_growth_rate = growth_rate.mean(axis=1)
    return average_growth_rate


# 构建簇年份矩阵，显示每个簇中各年份的专利数量
def build_matrix_subnet_date(config):
    print("构建簇年份矩阵")

    # 簇年份矩阵
    data_patent = pd.read_csv(f"{config.sub_project_dir}/output/专利-spo-子图.csv")
    data_part = pd.read_csv(f"{config.sub_project_dir}/output/子图.csv")           # 输入，加载专利和簇信息

    patent_years = data_patent["AD_Year"]  # 注意这里数据表头！


    start_year = min([x for x in patent_years if x != 1111])
    year_list = [str(y) for y in list(range(start_year ,max(patent_years)+1)) ]# 列字段

    # 构建矩阵：每行代表一个簇，每列代表一个年份，元素值为该年份在簇中的专利数量。
    rows = []
    for id,line in data_part.iterrows():
        pids = json.loads(line["专利"])
        subnet_years_ids = [patent_years[id] - start_year for id in pids if patent_years[id]!=1111] # 将专利转到年份索引
        row = np.zeros(len(year_list))
        for id in subnet_years_ids:
            row[id] += 1
        rows.append(row)
    print("年份列名",len(rows[0]),len(year_list) )
    data = pd.DataFrame(rows, columns=year_list)
    data["簇"] = data_part["簇"]
    data = data[["簇"] + year_list]

    # 计算年均增长率
    growth_rates = calculate_growth_rate(data.drop("簇", axis=1))  # 计算增长速度，排除“簇”列
    data["平均增长速度"] = growth_rates  # 将平均增长速度添加到DataFrame中
    
    data.to_csv(f"{config.sub_project_dir}/output/簇年份矩阵_增长速度.csv",index=False)


def exec_all(config):  # 按顺序执行上述定义的函数
    cu_patentAvg_info(config)
    build_matrix_subnet_date(config)

