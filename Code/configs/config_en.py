# step1 文件预处理，规范字段

import os
import re

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


LTP_MODEL_DIR = "/Users/jiangman/resources/models/ltp4/base"
EN_checkpoint_path = "/Users/jiangman/resources/models/bert-base-uncased"
ZH_checkpoint_path = "/Users/jiangman/resources/models/bert-base-chinese"

LANG = "en"  # en or zh
synonyms_thresh = 0.95  #同义词合并时设定的余弦相似性阈值
USE_userword = False   # True or False
literature_type = "patent" # patent or paper

sub_project_dir = "data/Biosensor/直接抽取SAO"  # 修改根目录

user_indata_path = os.path.join(sub_project_dir, "input", "DM技术all.xlsx")  # 修改文件名
user_word_path = os.path.join(sub_project_dir, "input", "论文关键词Bio.xlsx")  # 修改文件名
user_ouput_dir = validateTitle("_".join(os.path.basename(user_indata_path).split(".")[:-1]))  
indata_path = os.path.join(sub_project_dir, "input", "indata.xlsx")   # 不动
word_path = os.path.join(sub_project_dir, "input", "words_dict.txt")  # 修改文件名

xlsx_spo_path = os.path.join(sub_project_dir, "input", "indata-spo.xlsx")

abs_filedname = "摘要spo"  #识别的摘要字段
