# 用于构建词表，是将提取的s,o构建词表
# step3-1 构建词表，中英文有区别
#后面有个文件路径注意一下

"""主函数"""

import os
import sys
import pandas as pd
import ast
import json
import re
from tqdm import tqdm
import spacy
nlp = spacy.load('en_core_web_sm')

from .utils.fopener import json_open
from .utils.deduplicate import deduplicate_by_field, deduplicate_list

# 获取当前脚本所在的目录
current_directory = os.getcwd()

# 构建数据文件的目录
data_dir = os.path.join(current_directory, '..', 'data')


def tokenize_EN(text):
    """分词"""
    text = text.lower()
    doc = nlp(text)
    tokens = []
    for token in doc:
        token = token.lemma_
        chars = re.findall("[a-z]" , token)
        if len(chars) < 2:
            continue
        tokens.append(token)
    new_text = " ".join(tokens)
    if not new_text: new_text = "default"
    return new_text

def tokenize_EN2(text):
    """分词"""
    tokens = []
    text = text.lower()
    for token in text.split():
        chars = re.findall("[a-z]" , token)
        if len(chars) < 2:
            continue
        tokens.append(token)
    new_text = " ".join(tokens)
    if not new_text: new_text = "default"
    return new_text


# [[('cigarette raw materials', 'been treated with', 'alkali'), ('flavor components', 'were trapped in', 'closed space')]]

#清洗文本
def text_clean(text, lang):
    text = text.lower()
    if lang=="en":
        return tokenize_EN2(text)
    else:
        text = text.lower()
        return text


import ast

def build_voc(config):
    # spo之后，获得词表
    print("substep:构建词表")
    data = pd.read_excel(config.xlsx_spo_path) # 输入
    ab_spos = data["摘要spo_clean"]  # 注意该字段
    
    ab_spos = [json.loads(l) for l in ab_spos]
    ab_spos_c = sum(ab_spos,[])
    

    # 提取所有的s,o
    voc_dict = {}
    vocs = [c[0] for c in  ab_spos_c]
    vocs = vocs + [c[2] for c in  ab_spos_c]
    raw_vocs = list(set(vocs))

    # 词汇表 - clean
    vocs2clean = {}
    for voc in tqdm(raw_vocs[:]):
        vocs2clean[voc] = text_clean(voc,config.LANG)
    clean_vocs = list(set(vocs2clean.values()))
    print(len(raw_vocs), len(clean_vocs))
    clean_vocs = ["default"] + [w for w in clean_vocs if w!="default"]
    clean_vocs2id = {voc:id for id,voc in enumerate(clean_vocs)}
    for k in vocs2clean:
        vocs2clean[k] = clean_vocs2id[vocs2clean[k]]

    print(config.sub_project_dir)
    with open(f"{config.sub_project_dir}/output/sim/voc.txt","w",encoding="utf8") as fw:
        fw.write("\n".join(clean_vocs))
    with open(f"{config.sub_project_dir}/output/sim/voc_raw2clean.json","w",encoding="utf8") as fw:
        fw.write(json.dumps(vocs2clean))


def rename_xlsx_fields():
    df = pd.read_excel("jupyterdata/spotech/data/1130_test_en/input/DM_14-23.xlsx")  #注意这里文件
    df =  df.rename(columns={"Term_SPO字段": "摘要spo_clean"})
    df.to_excel('jupyterdata/spotech/data/1130_test_en/output//病虫害-中文期刊数据-spo.xlsx', index=False)



def build_vocp():
    # useless
    data = pd.read_excel("jupyterdata/spotech/data/1130_test_en/output/专利spo提取结果_cleanSPO.xlsx")
    ab_spos = data["摘要spo_clean"]
    ab_spos = [json.loads(l) for l in ab_spos]
    ab_spos_c = sum(ab_spos,[])

    # 提取所有的s
    voc_dict = {}
    vocs = [c[1] for c in  ab_spos_c]
    raw_vocs = list(set(vocs))
    raw_vocs = [w.lower() for w in raw_vocs]


    with open("jupyterdata/spotech/data/1130_test_en/output/sim/vocp.json","w") as fw:
        fw.write("\n".join(raw_vocs))


if __name__ == '__main__':
    core_tech_sort()
