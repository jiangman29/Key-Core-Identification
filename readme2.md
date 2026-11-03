# 关键字段
摘要spo_clean

# 产出的重要文件、定义说明
Step2 构建spo
    含有spo的文件：input文件夹：indata-spo.xlsx

Step3 构建词表及词向量，合并同义词
    将提取的s,o构建词表：output-sim文件夹：voc.txt
    构建词表bert向量表示：output-sim文件夹：voc_bert_vector.npy
    使用Kmeans聚类对词向量进行聚类，每个聚类的标签：output-sim文件夹：voc2RepresentativeWord.json
                                代表词汇的标签：output-sim文件夹：voc_raw2clean.json

Step4 构建网络、构建子簇
    Step4-1 构建网络
    voc2id：词汇到ID的映射  （从voc_raw2clean.json文件转换为Python字典）
    voc2RepresentativeWord：从词汇ID到其代表词汇ID的映射  （从voc2RepresentativeWord.json文件转换）
    spoid2word：s,o的ID对与spo词汇(此时已经转化为代表性词汇了)：graph文件夹：spoid2word.json

    representativeWord2spo：代表词汇ID到spo关系的映射，即每个代表词汇ID最相关的spo关系 ：graph文件夹：representativeWord2spo.json

    degreesOfNodes:每个节点的度 ：graph文件夹：degreesOfNodes.json
    
    Step4-2 构建子簇
    partition2nodes：每个子簇与节点ID的映射
    rtokenIDs: 词汇到代表词汇ID的映射
    ncol_list：rtokenIDs中每个代表性词汇ID到对应的簇ID的映射
    专利-所属的簇：output文件夹：专利-spo-子图.csv
 
    partition2patent：从簇ID到专利ID列表的映射

    簇-包含的专利-属性：output文件夹：子图.csv 
    属性信息包含：簇ID、簇密度、簇大小（簇的节点数量）、簇节点（簇的节点ID）、代表节点（前五个节点ID）、代表三元组id（前五个spoID）、代表三元组（前五个spo）、三元组
   说明：簇节点为代表词汇
    
