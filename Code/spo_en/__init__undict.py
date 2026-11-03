# step2 构建/读取spo，英文
# 这一段代码无需更改，文件位置已经在config中指定路径
# 无词典过滤

import pandas as pd
import json
import ast
from tqdm import tqdm
from nltk import sent_tokenize
from .get_SAO_en import get_SAO_en


def normalize_spaces(text):
    text = " ".join(text.split()).strip()
    return text
    

# [[('cigarette raw materials', 'been treated with', 'alkali'), ('flavor components', 'were trapped in', 'closed space')]]
def clean(list_str):
    """清洗"""
    if type(list_str) == str:
        contents = ast.literal_eval(list_str)
    else:
        contents = list_str
    contents = [c for c in contents if c and c!='None']
    contents = sum(contents, [])
    contents = [(normalize_spaces(spo[0]), normalize_spaces(spo[1]), normalize_spaces(spo[2]), ) for spo in contents]  # 对每个元素的前三个值进行规范化处理，并将结果组成一个三元组
    contents = [spo for spo in contents if spo[0] and spo[1] and spo[2] and spo[0]!='None' and spo[1]!='None' and spo[2]!='None'] # 过滤掉任何元素中前三个值为 None 或空字符串的项
    return json.dumps(contents, ensure_ascii=False)


def clean_spo_en(config):
    """For en"""
    # 读取 xlsx 文件
    data = pd.read_excel(config.indata_path) # 输入的xlsx文件放在config.indata_path所指定的路径下
    print(data.columns)

    # 获取专利文本页
    ab_spos = data["摘要spo"]
    ab_spos = [clean(spos) for spos in ab_spos]
    data["摘要spo_clean"] = ab_spos

    # 输出到新的 xlsx 文件
    data.to_excel(config.xlsx_spo_path, index=False)  # 输出的xlsx文件被保存在config.xlsx_spo_path所指定的路径下


def generate_spo_en(config):

    # 读取 xlsx 文件
    # df = pd.read_excel(r'E:\01\coda\jiangman2\spo_code_gq\G06N03_new_head10.xlsx' ,
    #                         )  #
    
    abs_filedname = config.abs_filedname
    df = pd.read_excel(config.indata_path)

    print("输入文件：", config.indata_path)
    print("生成英文spo")

    abstract_spo_list = []
    count = 0
    for ind in tqdm(range(df.shape[0])):
        item = df.iloc[ind]
        #print("item:", item)

        #title = item[2].replace(" ","").replace("\n","")
        #abstract = item[5].replace(" ","").replace("\n","")
        #abstract = item[32].replace(" "," ").replace("\n"," ")

        generate_summary = item[abs_filedname]
        generate_summary = str(generate_summary)
        if generate_summary == "nan":
            abstract_spo_list.append(["None"])
            continue

        #title_spo_res = inference(title)

        sents = sent_tokenize(generate_summary, language="english")
        SAO_list=[] #定义一个空列表
        for sent in sents:
            saos = get_SAO_en(sent)
            if saos:
                SAO_list.append(saos)
            else:
                SAO_list.append('None')
        abstract_spo_list.append(SAO_list)
        # count += 1
        # if count ==10 :
        #     break 
        # print(title, abstract)

    #df["标题spo"] = title_spo_list
    abstract_spo_list = [clean(l) for l in abstract_spo_list]
    df["摘要spo_clean"] = abstract_spo_list
    df.to_excel(config.xlsx_spo_path, index=False)



