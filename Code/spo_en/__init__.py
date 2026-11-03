# step2 构建/读取spo，英文
# 这一段代码无需更改，文件位置已经在config中指定路径

import pandas as pd
import json
import ast
from tqdm import tqdm
from nltk import sent_tokenize
from .get_SAO_en import get_SAO_en


def normalize_spaces(text):
    """规范化空格"""
    text = " ".join(text.split()).strip()
    return text


def load_user_terms_from_excel(path):
    """从Excel文件加载用户词表"""
    df = pd.read_excel(path)
    # 假设关键词在第一列
    terms = df[df.columns[0]].tolist()
    # 转换为小写以支持大小写不敏感的匹配
    terms = [term.lower() for term in terms if len(term)>2]
    return terms
    

def clean(list_str):
    """清洗SPO，但不进行用户词表过滤"""
    if type(list_str) == str:
        contents = ast.literal_eval(list_str)
    else:
        contents = list_str
    contents = [c for c in contents if c and c!='None']
    contents = sum(contents, [])
    contents = [(normalize_spaces(spo[0]), normalize_spaces(spo[1]), normalize_spaces(spo[2]), ) for spo in contents]  # 对每个元素的前三个值进行规范化处理，并将结果组成一个三元组
    contents = [spo for spo in contents if spo[0] and spo[1] and spo[2] and spo[0]!='None' and spo[1]!='None' and spo[2]!='None'] # 过滤掉任何元素中前三个值为 None 或空字符串的项
    # return json.dumps(contents, ensure_ascii=False)
    return contents

# [[('cigarette raw materials', 'been treated with', 'alkali'), ('flavor components', 'were trapped in', 'closed space')]]


def get_term_spo(terms, spos):
    """基于用户词表过滤SPO"""
    filtered_spos = []

    # 对terms进行排序，确保先匹配更长的词组
    terms = sorted(terms, key=len, reverse=True)
    
    for spo in spos:
                # 检查spo是否为长度为3的元组或列表
        if not isinstance(spo, (list, tuple)) or len(spo) != 3:
            print(f"Skipping invalid SPO format: {spo}")
            continue  # 跳过这个不符合格式的项
            
        s, p, o = spo
        ns, no = "", ""
                

        for term in terms:
            if term.lower() in s.lower() and not ns and s.lower() != "comprise":  # 确保s不为comprise
                ns = s.lower()
            if term.lower() in o.lower() and not no:  # 仅当no未赋值时进行匹配:
                no = o.lower()
            
            if (ns and no) and (ns != no):
                filtered_spos.append((ns, p, no))
                break
    # return filtered_spos
    return json.dumps(filtered_spos, ensure_ascii=False)


def deduplicate_spo_list(spo_list):
    """对SPO列表进行去重"""
    unique_spo_set = set(tuple(spo) for spo in spo_list)
    return [list(spo) for spo in unique_spo_set]
    

def generate_spo_en(config):

    # 读取 xlsx 文件
    # df = pd.read_excel(r'E:\01\coda\jiangman2\spo_code_gq\G06N03_new_head10.xlsx' ,
    #                         )  #
    user_terms = load_user_terms_from_excel(config.user_word_path)  # 从Excel文件加载用户词表
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


        sents = sent_tokenize(generate_summary, language="english")
        SAO_list=[] #定义一个空列表
        for sent in sents:
            saos = get_SAO_en(sent)
            if saos:
                SAO_list.append(saos)
            else:
                SAO_list.append('None')
        
        if SAO_list:
            unique_SAO_list = [sao for sao in SAO_list if sao != 'None']
        else:
            unique_SAO_list = []

        # 对unique_SAO_list进行简单清洗
        cleaned_sao_list = clean(unique_SAO_list)
        # 使用用户词表过滤清洗后的SPO
        filtered_sao_list = json.loads(get_term_spo(user_terms, cleaned_sao_list))
    
        # 这里加入去重步骤
        deduplicated_sao_list = deduplicate_spo_list(filtered_sao_list)
        # 在将数据转换为JSON字符串之前，确保没有'None'
        deduplicated_sao_list = [item for item in deduplicated_sao_list if item != 'None' and all(subitem != 'None' for subitem in item)]
         # 确保最终列表不为空；否则，可以选择插入一个占位符或留空
        if not deduplicated_sao_list:
            deduplicated_sao_list = []  # 或者使用其他适当的占位符
        json_deduplicated_sao_list = json.dumps(deduplicated_sao_list)

        abstract_spo_list.append(json_deduplicated_sao_list)

    df["摘要spo_clean"] = abstract_spo_list
    df.to_excel(config.xlsx_spo_path, index=False)




    


