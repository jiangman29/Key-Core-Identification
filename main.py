"""主函数"""


# 获取三元组

import os
import shutil
from code_chinese_clean import config_en as config

from code_chinese_clean.other import get_userdict
from code_chinese_clean.spo_chinese import generate_spo
from code_chinese_clean.spo_en import clean_spo_en
from code_chinese_clean.voc import build_voc
from code_chinese_clean.vector_by_bert import generate_bert_vector
from code_chinese_clean.kmeans_merge_synonyms import build_voc2RepresentativeWord
from code_chinese_clean.build_graph import build_net
from code_chinese_clean import post_out

# 获取当前脚本所在的目录
current_directory = os.path.dirname(os.path.abspath(__file__))

# 构建数据文件的目录
data_dir = os.path.join(current_directory, '..', 'data')


def init_dir():
    sub_project_dir = config.sub_project_dir
    os.makedirs(f"{sub_project_dir}/input", exist_ok=True)
    os.makedirs(f"{sub_project_dir}/output", exist_ok=True)
    os.makedirs(f"{sub_project_dir}/output/sim", exist_ok=True)
    os.makedirs(f"{sub_project_dir}/output/graph", exist_ok=True)
    os.makedirs(f"{sub_project_dir}/to_user", exist_ok=True)

def main(steps=[3]):
    # step1 文件预处理，规范字段
    if 1 in steps:
        if 0:
            get_userdict.get_userdict(config.user_word_path, config.word_path) # 如果有的话
        shutil.copy(config.user_indata_path, config.indata_path)

    # step2 构建/读取spo，中英文有区别
    if 2 in steps:
        if config.LANG.lower() == "en":
            clean_spo_en(config)
        else:
            generate_spo(config)

    # step3-1 构建词表，中英文有区别
    # step3-2 构建bert向量，中英文有区别
    # step3-3 构建同义词
    if 3 in steps:
        build_voc(config)
        generate_bert_vector(config)
        build_voc2RepresentativeWord(config)
    # step4-1 构建网络
    # step4-1 构建子簇
    if 4 in steps:
        build_net(config)

    # step5 后处理获取所需文件
    if 5 in steps:
        post_out.exec_all(config)

    print("结束")

if __name__ == '__main__':
    init_dir()
    # main()
