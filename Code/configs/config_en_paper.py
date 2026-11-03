import os
import re

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

os_type = "linux"
if os_type == "linux":
    LTP_MODEL_DIR = R"resources/models/ltp4/base"
    EN_checkpoint_path = R"resources/models/bert-base-uncased"
    ZH_checkpoint_path = R"resources/models/bert-base-chinese"
else:
    LTP_MODEL_DIR = R"resources\models\ltp4\base"
    EN_checkpoint_path = R"resources\models\bert-base-uncased"
    ZH_checkpoint_path = R"resources\models\bert-base-chinese"

LANG = "en"  # en or zh
synonyms_thresh = 0.95
USE_userword = False   # True or False
literature_type = "paper" # patent or paper
abs_filedname = "摘要"
word_path = os.path.join(r"data\resources\words_dict.txt") 

"""无用"""
sub_project_dir = "data/01sub_projects/pej" 
user_indata_path = os.path.join(sub_project_dir, "input", "默认名称.xlsx")
user_ouput_dir = validateTitle("_".join(os.path.basename(user_indata_path).split(".")[:-1]))   # 关联名称
indata_path = os.path.join(sub_project_dir, "input", "indata.xlsx")  
xlsx_spo_path = os.path.join(sub_project_dir, "input", "indata-spo.xlsx")
