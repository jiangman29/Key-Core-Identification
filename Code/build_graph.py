# step4 构建网络、构建子簇
# 包含信息：专利-簇关系，簇属性（密度、大小、代表节点、代表性SPO关系），节点和spo关系，簇分析

import json
import pandas as pd
import numpy as np
import networkx as nx
import community
from tqdm import tqdm  # 引入进度条库，用于在长任务执行时显示进度
from collections import Counter  # 引入计数器，用于统计元素出现的频率

# 引入自定义的辅助函数，用于文件操作和数据去重
from .utils.fopener import json_open_write
from .utils import deduplicate

import matplotlib.pyplot as plt
from scipy.sparse import coo_array
# plt.figure(figsize=(10,8))
# nx.draw_networkx(G,node_size=100, width=3)
# plt.show()
# plt.savefig('../data/example_plot.png')


# step4-1 构建网络

def build_net(config):
    sub_project_dir = config.sub_project_dir

    # 加载词表：从词汇到ID的映射(voc2id)
    with open(f"{sub_project_dir}/output/sim/voc_raw2clean.json") as fr:  # 打开词汇到ID映射的JSON文件
        voc2id = json.loads(fr.read())   # 将JSON字符串转换为Python字典，存储每个词汇到其唯一ID的映射

    # 加载词语映射：从词汇到其代表词汇的映射(voc2RepresentativeWord)
    with open(f"{sub_project_dir}/output/sim/voc2RepresentativeWord.json","r",) as fr:
        voc2RepresentativeWord = json.loads(fr.read())

    
    # 处理摘要数据
    data_patent_xlsx = pd.read_excel(config.xlsx_spo_path)
    ab_spos = data_patent_xlsx["摘要spo_clean"]
    ab_spos = [json.loads(l) for l in ab_spos]   # 将摘要数据从JSON字符串转换为Python列表
    ab_spos_c = sum(ab_spos,[])   # 将所有摘要的SPO列表合并成一个大的列表

    # 构建边
    representativeWord2spo = {}  # 初始化一个字典，用于存储每个代表性词汇到其对应的SPO关系的映射
    spoid2word = {}   # 初始化一个字典，用于存储每对主语和宾语的ID到原始SPO文本的映射
    edges = []   # 初始化一个列表，用于存储图中的所有边
    
    # 计算节点的度（连接的边数）
    degreesOfNodes = {}  # 初始化一个字典，用于存储图中每个节点的度（即连接到该节点的边的数量）
    for s,p,o in tqdm(ab_spos_c):
        spoword = "||".join([s,p,o]) # s p o的分割方式
        s = voc2id[s]  # 将主语和宾语的文本转换为它们对应的ID，voc2id字典存储了词汇到ID的映射
        o = voc2id[o]
        s = voc2RepresentativeWord[s]  # 将主语和宾语的ID进一步映射到它们的代表性词汇的ID
        o = voc2RepresentativeWord[o]

        spoid2word[(s,o)] = spoword    # 将每对主语和宾语的ID映射到它们原始的SPO文本

        if s!=o:   # 检查主语和宾语是否不同，避免自环
            if type(s)!=int or type(o)!=int:    # 检查主语和宾语ID是否为整数类型，确保它们是有效的ID
                print(type(s),type(o))
                continue
            edges.append((s,o))   # 将主语和宾语的ID作为一条边添加到edges列表中
            degreesOfNodes[s] = degreesOfNodes.get(s,0) + 1  # 更新主语和宾语节点的度，即每遇到一条边，就将相应节点的度加一
            degreesOfNodes[o] = degreesOfNodes.get(o,0) + 1

            # edges.append((p,o))
            # 更新代表性词汇到SPO关系的映射，对于每个代表性词汇，记录它作为主语或宾语出现在哪些SPO关系中
            representativeWord2spo[s] = representativeWord2spo.get(s, [])+ [(s,o)] 
            representativeWord2spo[o] = representativeWord2spo.get(o, [])+ [(s,o)]



    # 存储中间结果
    # 记得打开！！！
    json_open_write(f"{sub_project_dir}/output/graph/degreesOfNodes.json",  degreesOfNodes) # 中间结果


    for k in representativeWord2spo:
        v = representativeWord2spo[k]   # 获取当前代表性词汇IDk对应的所有SPO关系列表
        # 使用Counter统计每个元素（SPO关系）的出现次数
        count = Counter(v)

        # 找出出现最频繁的一项
        most_common_item = count.most_common(1)  # most_common(1)返回一个列表，其中包含了一个元组，元组的第一个元素是出现次数最多的SPO关系，第二个元素是该SPO关系的出现次数。

        # 输出结果
        # 将出现次数最多的SPO关系更新到representativeWord2spo字典中，作为代表性词汇k的最相关SPO关系。
        representativeWord2spo[k] = most_common_item[0][0]  
        if representativeWord2spo[k] not in spoid2word:
            print("spowrong", representativeWord2spo[k])

    spoid2word ={str(k):v for k,v in spoid2word.items()}  # 将spoid2word字典的键（主语和宾语的ID对）转换为字符串格式
    json_open_write(f"{sub_project_dir}/output/graph/representativeWord2spo.json",  representativeWord2spo) # 中间结果
    json_open_write(f"{sub_project_dir}/output/graph/spoid2word.json",  spoid2word) # 中间结果

    edges = Counter([(so[0],so[1]) for so in edges])
    edges = [(k[0], k[1], {'weight': v}) for k,v in edges.items() ]

    # 创建一个有向图对象
    G = nx.DiGraph()
    G.add_edges_from(edges)

    print("图构建完毕")


    # 计算节点度
    in_degrees = dict(G.in_degree())  # 计算每个节点的入度 
    out_degrees = dict(G.out_degree())  # 计算每个节点的出度
    print("出度:", out_degrees)

    # 总度
    degrees = dict(G.degree())

    # 度排名
    in_degrees_sorted = sorted(in_degrees.items(), key=lambda x:x[1], reverse=True)
    out_degrees_sorted = sorted(out_degrees.items(), key=lambda x:x[1], reverse=True)
    sum_degrees = sorted(degrees.items(), key=lambda x:x[1], reverse=True)

    # sys.exit()


    # step4-2 构建子簇
    #first compute the best partition

    G = G.to_undirected()  # 将之前创建的有向图G转换为无向图。社区发现算法通常在无向图上运行
    # 使用community库的best_partition方法找到图G的最佳划分，即将图分割成若干社区（子图）的方式
    partition = community.best_partition(G, resolution=0.1, random_state=1)  

    # 构建子图
    partition_ids = sorted(set(partition.values())) # 提取partition字典中的子图ID，并对它们进行排序。

    # sys.exit()

    partition2nodes = {}  # 初始化partition2nodes字典，目的是将每个社区ID映射到属于该社区的所有节点ID列表
    for value, key in partition.items():
        if key in partition2nodes:
            partition2nodes[key].append(value)
        else:
            partition2nodes[key] = [value] 

    # sys.exit()

    subgraphs = [G.subgraph(partition2nodes[pid]) for pid in partition_ids] # 错的

    # 输出每个子图的密度、边总强度、边数量
    subgraph_edgetotalweights = [0]*len(subgraphs)
    subgraph_edgenums = [0]*len(subgraphs)
    density_record = {}
    subgraph_degrees = {}
    for idx, subgraph in enumerate(subgraphs):
        subgraph_edgetotalweights[idx] = sum(d['weight'] for u, v, d in subgraph.edges(data=True))
        subgraph_edgenums[idx] = len(subgraph.edges(data=True))
        density = nx.density(subgraph)
        density_record[idx] = density
        subgraph_degrees[idx] = dict(subgraph.degree(weight='weight'))
    json_open_write(f"{sub_project_dir}/output/graph/subgraph_degrees.json",  subgraph_degrees) # 中间结果
    


    # 新表1  专利 - 实体 - 代表词 - 簇
    ncol_list = []
    for pid, row in data_patent_xlsx.iterrows():
        # 实体词的代表性词汇（图节点）
        ab_spos = json.loads(row["摘要spo_clean"])
        # ab_spos_c = sum(ab_spos,[])

        # 构建边
        rtokenIDs = []  # 用于存储当前专利中所有实体词的代表性词汇ID
        for s,p,o in ab_spos:
            s = voc2id[s]
            o = voc2id[o]
            s = voc2RepresentativeWord[s]
            o = voc2RepresentativeWord[o]

            rtokenIDs.append(s)
            rtokenIDs.append(o)

        # rtokenIDs = json.loads(row["摘要代表词汇"])

        # 代表词 -》簇
        # 根据之前计算的社区划分，为专利中的每个代表词汇找到对应的簇ID。这里过滤掉了不在partition映射中的ID。
        sub_parts = [partition[id] for id in rtokenIDs if id in partition] 
        sub_parts = ";".join(deduplicate.deduplicate_list([str(id) for id in sub_parts]))  # 去重，把分隔符改成了;避免Excel将这些ID识别为一个长数字
        if not sub_parts: sub_parts = "-1"  # 如果sub_parts为空，则将其设置为"-1"，表示没有找到对应的簇。

        ncol_list.append(sub_parts)

    data_patent_xlsx["子图"] = ncol_list
    # data_patent_xlsx.to_excel(f"{sub_project_dir}/output/专利-spo-子图.xlsx", index=False) # 用户需要
    data_patent_xlsx.to_csv(f"{sub_project_dir}/output/专利-spo-子图.csv", index=False) # 将更新后的DataFrame导出为CSV

    # 构建映射： 簇 -》专利
    partition2patent = {}
    for pid, row in data_patent_xlsx.iterrows(): # pid表示专利ID
        # 实体词的代表性词汇（图节点）
        cuids = [int(i) for i in row["子图"].replace(";", ",").split(",")]  # 整数列表cuids，包含了当前专利所属的簇ID
        for id in cuids:
            if id in partition2patent:
                if pid not in partition2patent[id]: #检查当前的专利ID是否还没有被加入到该簇ID对应的专利ID列表中，这样做是为了确保每个簇ID对应的专利ID列表中不包含重复的专利ID
                    partition2patent[id].append(pid) 
            else:
                partition2patent[id] = [pid] 

    # 新表2 簇 - 专利 - 节点 - 代表节点 - 簇属性
    partition_ids = sorted(set(partition.values()))[:]   # 簇ID 排序
    partition_patents = [partition2patent.get(id, []) for id in partition_ids] #簇的专利列表
    partition_nodes = [partition2nodes.get(id, []) for id in partition_ids]  # 簇的节点列表
    partition_nodes_num = [len(id) for id in partition_nodes]  #簇的节点数量
    
 
    partition_symb_nodes = []
    partition_symb_spo = []
    partition_symb_spo_word = []
    partition_all_nodes = []
    partition_all_spo = []
    partition_all_spo_word = []
    for id in partition_ids:
        nids = partition2nodes.get(id, []) # 获取当前簇的所有节点ID
        # 如果当前簇有节点，则计算这些节点在图中的度，并对节点按度进行降序排序
        nids_record = subgraph_degrees[id]
        nids_record_sort = sorted(nids_record.items(), key=lambda x:x[1], reverse=True)

        # 选出前五个节点ID作为簇的代表节点，获取代表节点和所有节点的spo信息
        symb_nodes = [l[0] for l in nids_record_sort[:5]] # 前五个节点id
        symb_spo =  [representativeWord2spo[id] for id in symb_nodes] # 节点id - spo,id，这里用的代表词汇ID最相关的spo关系，来表示词汇和SPO的映射
        symb_spo = [x for i, x in enumerate(symb_spo) if x not in symb_spo[:i]]
        symb_spo_word = [spoid2word[str((spo[0], spo[1]))] for spo in symb_spo] # spoid-word
        partition_symb_nodes.append(symb_nodes) # 代表节点
        partition_symb_spo.append(symb_spo)
        partition_symb_spo_word.append("; ".join(symb_spo_word))
        # 全部节点
        all_spo =  [representativeWord2spo[id] for id in nids] # 节点id - spo,id
        all_spo_word = [spoid2word[str((spo[0], spo[1]))] for spo in all_spo] # spoid-word
        partition_all_nodes.append(nids)
        partition_all_spo.append(all_spo)
        partition_all_spo_word.append("; ".join(deduplicate.deduplicate_list(all_spo_word)))

    partition_density = [density_record[id] for id in partition_ids]  # 为每个簇计算密度

    
    # 数据整理和导出
    def dump(data):
        rls = []
        for l in data:
            l = json.dumps(l, ensure_ascii=False)
            rls.append(l)
        return rls


    print("子网:", len(partition_ids))
    print("单节点子网:", len([1 for l in partition_patents if len(l)<2]))

    print("子网最大节点数:", max(partition_nodes_num))


    # sys.exit()
    # 列
    partition_ids = partition_ids # 簇
    partition_density = partition_density # 簇密度
    partition_nodes_num = partition_nodes_num # 簇大小
    partition_patents = dump(partition_patents) # 专利
    partition_nodes = dump(partition_nodes) # 簇节点
    partition_symb_nodes = dump(partition_symb_nodes) # 代表节点
    partition_symb_spo = dump(partition_symb_spo) # 代表三元组id
    partition_symb_spo_word = partition_symb_spo_word # 代表三元组
    partition_all_spo_word = partition_all_spo_word # 三元组


    subnet_data = {"簇":partition_ids,
                "簇密度":partition_density,
                "簇总链接强度":subgraph_edgetotalweights,
                "簇边数": subgraph_edgenums, # 平均链接强度时可能用到
                "簇大小":partition_nodes_num,
                "专利":partition_patents,
                "簇节点":partition_nodes,
                "代表节点":partition_symb_nodes,
                "代表三元组id":partition_symb_spo,
                "代表三元组":partition_symb_spo_word,
                "三元组":partition_all_spo_word
                }
    subnet_xlsx = pd.DataFrame(subnet_data)
    # subnet_xlsx.to_excel(f"{sub_project_dir}/output/子图.xlsx", index=False)
    subnet_xlsx.to_csv(f"{sub_project_dir}/output/子图.csv", index=False)
