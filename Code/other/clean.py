import os
import pandas as pd
import ast
import json
import re

def text_clean(text):
    text = " ".join(text.split()).strip()
    return text
    

# [[('cigarette raw materials', 'been treated with', 'alkali'), ('flavor components', 'were trapped in', 'closed space')]]
def clean(list_str):
    """清洗"""

    contents = ast.literal_eval(list_str)
    contents = [c for c in contents if c and c!='None']
    contents = sum(contents, [])
    contents = [(text_clean(spo[0]), text_clean(spo[1]), text_clean(spo[2]), ) for spo in contents]
    contents = [spo for spo in contents if spo[0] and spo[1] and spo[2] and spo[0]!='None' and spo[1]!='None' and spo[2]!='None']
    return json.dumps(contents, ensure_ascii=False)

# 加载数据
data = pd.read_excel("/home/wjz/projects/others/jiangman/data/专利spo提取结果1.xlsx")

# 获取专利文本页
ab_spos = data["摘要spo"]
ab_spos = [clean(spos) for spos in ab_spos]
data["摘要spo_clean"] = ab_spos
print(data.columns)
data.to_excel("/home/wjz/projects/others/jiangman/data/专利spo提取结果1_cleanSPO.xlsx", index=False)