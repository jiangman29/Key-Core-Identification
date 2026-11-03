# step5 后处理获取所需文件
# 数据处理和分析功能：计算簇-专利平均信息、计算簇核心性、构建专利簇矩阵、构建簇年份矩阵

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
def copy_some_file(config):
    user_ouput_dir = f"{config.sub_project_dir}/to_user/{config.user_ouput_dir}"
    os.makedirs(user_ouput_dir, exist_ok=True)

    # inf = f"{config.sub_project_dir}/output/专利-spo-子图.xlsx"
    # shutil.copy(inf, user_ouput_dir)

    # inf = f"{config.sub_project_dir}/output/子图.xlsx"
    # shutil.copy(inf, user_ouput_dir)

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

# 计算论文/专利的作者数量
def get_paper_author_num(cell):
    return len(re.split("[；;]", str(cell))) # 作者之间用分号（中文或英文）分隔

# 定义归一化函数
def min_max_normalize(values):
    min_val = min(values)
    max_val = max(values)
    return [(x - min_val) / (max_val - min_val) for x in values]

def cu_patentAvg_info(config):
    # 簇-专利平均信息
    print("计算簇-专利平均信息")

    user_ouput_dir = f"{config.sub_project_dir}/to_user/{config.user_ouput_dir}"

    os.makedirs(user_ouput_dir, exist_ok=True)

    data_patent = pd.read_csv(f"{config.sub_project_dir}/output/专利-spo-子图.csv")  # 读取专利数据集
    data_subnet = pd.read_csv(f"{config.sub_project_dir}/output/子图.csv")  # 读取簇（子图）的信息数据集

    years = []
    cites = []
    authors =[]

    if config.literature_type == "paper":  # 论文
        patents_year = data_patent["年"]  # 注意这里数据表头！
        patents_authornum = [len(re.split("[；;]", str(cell))) for cell in data_patent["作者"]]
        patents_citenum = [1]*len(data_patent)  # 默认值 设为了1

    else:
        patents_year = [get_year(cell) for cell in data_patent["AD_Year"]]  # 注意这里数据表头！
        data_patent["年"] = patents_year
        # patents_authornum = [get_int(cell) for cell in data_patent["发明人数量"]] #注意这里数据表头
        # patents_citenum = [get_int(cell) for cell in data_patent["引用专利数量"]]  #注意这里数据表头

    # 计算簇的平均信息
    for id,line in data_subnet.iterrows():

        pids = json.loads(line["专利"])  # 获取属于该簇的专利ID列表

        # 对于每个簇，根据专利ID列表提取对应的年份、作者数量和引用次数，计算这些值的总和，再计算平均年份（对年份求和后除以专利数量
        subnet_years = [patents_year[id] for id in pids] # 将专利转到年份索引，subnet_years为该簇所有专利的年份列表
        avg_year = sum(subnet_years) / len(pids)  # 簇的平均年份：簇年份总和/簇专利数量

        # authornum = sum([patents_authornum[id] for id in pids]) # 将专利转到年份索引，该簇所有专利的作者数量总和
        # citenum = sum([patents_citenum[id] for id in pids]) # 将专利转到年份索引，该簇所有专利的引用次数总和

        years.append(avg_year) # 所有簇的平均年份数据
        # authors.append(authornum)  # 所有簇的作者数量总和数据
        # cites.append(citenum)  # 所有簇的引用次数总和数据

    # 更新数据集，将计算得到的平均年份、总作者数量、总引用次数分别添加到data_subnet数据集的"TN"、"SI"、"IN"列。
    data_subnet["TN"] = years
    # data_subnet["SI"] = authors
    # data_subnet["IN"] = cites

    # 如果文献类型是"paper"，则删除"IN"列，因为对于论文数据，引用次数不适用
    if config.literature_type == "paper": 
        data_subnet.drop(columns="IN")
        
    # data_patent.to_excel(f"{user_ouput_dir}/专利-spo-子图-年.xlsx",index=False)
    # data_subnet.to_excel(f"{user_ouput_dir}/子图-info.xlsx",index=False)
    data_patent.to_csv(f"{user_ouput_dir}/专利-spo-子图-年.csv",index=False)
    data_subnet.to_csv(f"{user_ouput_dir}/子图-info.csv",index=False)


def core_tech_sort(config):
    """计算簇核心性"""
    print("计算簇核心性")
    user_ouput_dir = f"{config.sub_project_dir}/to_user/{config.user_ouput_dir}"
    os.makedirs(user_ouput_dir, exist_ok=True)

    subgraph_degrees = json_open(f"{config.sub_project_dir}/output/graph/subgraph_degrees.json")
    func_repair_intk = lambda dictx: {int(k):v for k,v in dictx.items()}
    subgraph_degrees = {int(k):func_repair_intk(v) for k,v in subgraph_degrees.items()}

    # 加载全局节点的度信息
    # with open(f"{config.sub_project_dir}/output/graph/degreesOfNodes.json","r",) as fr:
    #     degreesOfNodes = json.loads(fr.read())
    #     degreesOfNodes = {int(k):v for k,v in degreesOfNodes.items()}

    # 加载簇与专利的映射关系
    # data_part = pd.read_excel(f"{user_ouput_dir}/子图-info.xlsx")           # 输入，如果前面是xlsx则用该条
    data_part = pd.read_csv(f"{user_ouput_dir}/子图-info.csv")           # 输入

    data_part["簇节点"] = [json.loads(l) for l in data_part["簇节点"]]
    

    # 计算每个簇的节点长度、最大和最小节点数，定义一个归一化函数
    subnet_nodes_len = [len(l) for l in data_part["簇节点"]]
    max_subnet_nodes_num = max(subnet_nodes_len)
    min_subnet_nodes_num = min(subnet_nodes_len)
    func_Normalization_subnet = lambda x: (x-min_subnet_nodes_num)/(max_subnet_nodes_num-min_subnet_nodes_num)
    
    # 挑选最大的簇的代表节点
    scoreOfSubnets = []
    # 总节点数
    for id,line in data_part.iterrows():
        subnet_nodes = line["簇节点"]
        degreesOfNodes = subgraph_degrees[id]
        # if len(subnet_nodes) < 10:continue
        top_node = subnet_nodes[0]
        cu_patent_num = len(json.loads(line["专利"]))
        scoreOfSubnets.append([cu_patent_num, line["簇总链接强度"]/max(1,len(subnet_nodes)),  sum(degreesOfNodes[node] for node in subnet_nodes)])   #上面这里 计算的是簇平均链接强度

    # 添加簇专利数量的计算
    data_part["簇专利数量"] = data_part["专利"].apply(lambda x: len(x.split(";")))
    # 标准化三个指标
    s0 = min_max_normalize([s[0] for s in scoreOfSubnets])
    s1 = min_max_normalize([s[1] for s in scoreOfSubnets])
    s2 = min_max_normalize([s[2] for s in scoreOfSubnets])
    scoreOfSubnets = [[v1,v2,v3] for v1,v2,v3 in zip(s0,s1,s2)]
    
    # 提取簇专利数量、簇大小和簇中心性的原始值
    data_part["簇专利数量归一化值"] = [s[0] for s in scoreOfSubnets]
    data_part["簇平均链接强度"] = [s[1] for s in scoreOfSubnets]
    data_part["簇中心性"] = [s[2] for s in scoreOfSubnets]
    print(sum(data_part["簇中心性"])/len(data_part))
    print(sum(data_part["簇平均链接强度"])/len(data_part))
    print(sum(data_part["簇专利数量归一化值"])/len(data_part))
    data_part["簇核心性得分"] = [s[0] + s[1] + s[2] for s in scoreOfSubnets]

    # scoreOfTopnodes_sort = sorted(scoreOfTopnodes.items(), key=lambda x:x[1], reverse=True)
    #     # 加载词表
    # with open("/home/wjz/projects/others/jiangman/data/chinese_data_1112/output/sim/voc_raw2clean.json") as fr:
    #     voc2id = json.loads(fr.read())
    #     id2voc = {v:k for k,v in voc2id.items()}

    # rows = []
    # for id,s in scoreOfTopnodes_sort:
    #     if id not in id2voc:continue
    #     rows.append([id,s, id2voc[id]])
    data_part_columns = [c for c in data_part.columns if c not in ["簇专利数量归一化值", "簇中心性","簇平均链接强度", "簇核心性得分"]] + ["簇专利数量归一化值", "簇中心性","簇平均链接强度", "簇核心性得分"]
    data_part = data_part[data_part_columns]
    data_part["代表三元组"] = [l[:32760] for l in data_part["代表三元组"]]

    # data_part.to_excel(f"{user_ouput_dir}/簇_核心度.xlsx",index=False)
    data_part_part_columns = [c for c in data_part.columns if c not in ["簇节点", "专利","三元组"]]  #排除这三列，因为太长了
    data_part[data_part_part_columns].to_csv(f"{user_ouput_dir}/簇_核心度.csv",index=False)
    
    # 保存到json的数据
    data_part["专利"] = [";".join(str(i) for i in json.loads(l)) for l in data_part["专利"]]
    data_part["簇节点"] = [";".join(str(i) for i in l) for l in data_part["簇节点"]]
    dd = data_part[["簇","三元组"]].to_dict(orient="records")
    # dd = data_part[["簇", "簇节点", "专利","三元组"]].to_dict(orient="records") 更多信息可以用这行
    ss = json.dumps(dd, ensure_ascii=False, indent=2)
    text_open_write(f"{user_ouput_dir}/簇-专利-节点.json", ss)


# 构建一个专利簇矩阵，反映专利与簇的关系
def build_matrix(config):
    """专利簇矩阵"""
    print("构建专利簇矩阵")
    user_ouput_dir = f"{config.sub_project_dir}/to_user/{config.user_ouput_dir}"
    os.makedirs(user_ouput_dir, exist_ok=True)

    # data_patent = pd.read_excel(f"{user_ouput_dir}/专利-spo-子图-年.xlsx")
    # data_part = pd.read_excel(f"{user_ouput_dir}/子图-info.xlsx")           # 输入

    data_patent = pd.read_csv(f"{user_ouput_dir}/专利-spo-子图-年.csv")
    data_part = pd.read_csv(f"{user_ouput_dir}/子图-info.csv")           # 输入

    # 创建一个矩阵，每行代表一个簇，每列代表一个专利，如果专利属于簇，则相应的元素为1。
    patent_ids = list(range(len(data_patent)))
    rows = []
    for id,line in tqdm(data_part.iterrows(),total=len(data_part)):
        pids = json.loads(line["专利"])
        row = np.zeros(len(data_patent))
        row[pids] = 1
        rows.append(row)
    data = pd.DataFrame(rows, columns=patent_ids)
    data["簇"] = data_part["簇"]
    data = data[["簇"] + patent_ids]
    print("保存到csv", time.asctime())
    data.to_csv(f"{user_ouput_dir}/专利簇矩阵.csv",index=False)
    print("已保存到csv", time.asctime())


# 构建簇年份矩阵，显示每个簇中各年份的专利数量
def build_matrix_subnet_date(config):
    print("构建簇年份矩阵")

    # 簇年份矩阵
    user_ouput_dir = f"{config.sub_project_dir}/to_user/{config.user_ouput_dir}"
    os.makedirs(user_ouput_dir, exist_ok=True)

    # data_patent = pd.read_excel(f"{user_ouput_dir}/专利-spo-子图-年.xlsx")
    # data_part = pd.read_excel(f"{user_ouput_dir}/子图-info.xlsx")           # 输入

    data_patent = pd.read_csv(f"{user_ouput_dir}/专利-spo-子图-年.csv")
    data_part = pd.read_csv(f"{user_ouput_dir}/子图-info.csv")           # 输入，加载专利和簇信息

    patent_years = data_patent["年"]


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
    # data.to_excel(f"{user_ouput_dir}/簇年份矩阵.xlsx",index=False)
    data.to_csv(f"{user_ouput_dir}/簇年份矩阵.csv",index=False)

def __tmp__get_all_pspos():
    """获得各簇的所有三元组，无用"""
    representativeWord2spo = json_open("/home/wjz/projects/others/jiangman/data/chinese_data_1112/output/graph/representativeWord2spo.json")
    spoid2word = json_open("/home/wjz/projects/others/jiangman/data/chinese_data_1112/output/graph/spoid2word.json")

    # 新表 簇 - 专利 - 节点 - 代表节点 - 簇属性
    partion_data = pd.read_excel("/home/wjz/projects/others/jiangman/data/chinese_data_1112/output/子图.xlsx")
    partition_nodes = partion_data["簇节点"].to_list()
    partition_nodes = [json.loads(l) for l in partition_nodes]

    partition_symb_nodes = []
    partition_symb_spo = []
    partition_symb_spo_word = []
    for nids in partition_nodes:
        symb_nodes = nids
        
        symb_spo =  [representativeWord2spo[str(id)] for id in symb_nodes] # 节点id - spo,id
        symb_spo_word = [spoid2word[str((spo[0], spo[1]))] for spo in symb_spo] # spoid-word
        partition_symb_nodes.append(symb_nodes)
        partition_symb_spo.append(symb_spo)
        partition_symb_spo_word.append(";".join(deduplicate_list(symb_spo_word)))
    # 全部节点
    partition_symb_spo_word = partition_symb_spo_word
    partion_data["全部三元组"] = partition_symb_spo_word
    partion_data.to_excel("/home/wjz/projects/others/jiangman/data/chinese_data_1112/output/子图2.xlsx", index=False)

def exec_all(config):  # 按顺序执行上述定义的函数
    # core_tech_sort(config)
    # return

    copy_some_file(config)
    cu_patentAvg_info(config)
    # return
    core_tech_sort(config)
    build_matrix(config)
    build_matrix_subnet_date(config)
