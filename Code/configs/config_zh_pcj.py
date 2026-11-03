import os
import re

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


LTP_MODEL_DIR = R"resources\models\ltp4\base"
EN_checkpoint_path = R"resources\models\bert-base-uncased"
ZH_checkpoint_path = R"resources\models\bert-base-chinese"

LANG = "zh"  # en or zh
synonyms_thresh = 0.95
USE_userword = True   # True or False
literature_type = "paper" # patent or paper


sub_project_dir = "data/01sub_projects/pcj" 

user_indata_path = os.path.join(sub_project_dir, "input", "中文期刊分词_1701498871580.xlsx")
# user_word_path = os.path.join(sub_project_dir, "input", "烟草病虫害词汇.xlsx")
user_ouput_dir = validateTitle("_".join(os.path.basename(user_indata_path).split(".")[:-1]))  
indata_path = os.path.join(sub_project_dir, "input", "indata.xlsx")  
word_path = os.path.join(r"data\resources\words_dict.txt") 
xlsx_spo_path = os.path.join(sub_project_dir, "input", "indata-spo.xlsx")

abs_filedname = "摘要分词"