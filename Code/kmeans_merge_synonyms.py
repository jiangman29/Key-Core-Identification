# 使用Kmeans聚类方法对词向量进行聚类，并根据相似度进行同义合并
# step3-3 构建同义词

# 导入所需的库
from sklearn.cluster import KMeans
import numpy as np
from scipy.spatial.distance import cdist
from scipy.spatial.distance import cosine
import json

# os.environ["OMP_NUM_THREADS"] = '2'
# os.environ['OPENBLAS_NUM_THREADS'] = '1'

from .utils.fopener import json_open
import time


# step1函数：该函数实现了K均值聚类的第一步，即使用K均值算法将词向量进行聚类，并找到每个簇的最近单词。主要步骤包括：
# 加载词向量数据并准备数据。
# 创建K均值聚类模型，并指定簇数K。
# 拟合模型到数据并获取每个样本所属的簇标签。
# 获取簇的中心点。
# 计算每个单词到所有簇中心的距离，并找到每个簇的最近单词。
# 将原始簇标签转换为单词标签并存储。

def step1(config):
    vector_file = f"{config.sub_project_dir}/output/sim/voc_bert_vector.npy"
    initial_voc2RepresentativeWord_file = f"{config.sub_project_dir}/output/sim/voc2RepresentativeWord_initial.json" # 中间文件

    # 准备数据，假设X是您的数据集，每行代表一个样本，每列代表一个特征
    # X = np.array([[x1, y1], [x2, y2], ...])
    # 创建K均值聚类模型，指定要分成的簇数K
    X = np.load(vector_file)[:]
    print("词表数:",len(X))

    k= min(10000,int(len(X)/10))  #指定K的数量，这里是词表数/10
    print("聚类k:",k)
    kmeans = KMeans(n_clusters=k)

    # 拟合模型到数据
    kmeans.fit(X,)

    # 获取每个样本所属的簇标签
    labels = kmeans.labels_

    # 获取簇的中心点
    cluster_centers = kmeans.cluster_centers_

    # 初始化一个字典，用于存储每个簇的最近单词
    nearest_words = {}

    # 计算每个单词到所有簇中心的距离
    distances = cdist(X, cluster_centers, 'euclidean')

    # 找到每个簇的最近单词
    for cluster_id in range(k):
        cluster_indices = np.where(labels == cluster_id)[0]
        nearest_word_index = cluster_indices[np.argmin(distances[cluster_indices, cluster_id])]
        nearest_words[cluster_id] = nearest_word_index

    # 将label标签换为word标签
    raw_labels = [int(nearest_words[l]) for l in labels]

    # 存储labels
    with open(initial_voc2RepresentativeWord_file,"w",encoding="utf8") as fw:
        fw.write(json.dumps(raw_labels, ensure_ascii=False))

# step2函数：该函数实现了K均值聚类的第二步，即根据设定的相似度阈值对聚类结果进行筛选的功能。主要步骤包括：
# 加载词向量数据和初始聚类结果。
# 计算每个样本与其所属簇的词向量之间的余弦相似度。
# 根据设定的相似度阈值筛选出满足条件的聚类结果，并重新标记。
# 存储经过筛选后的聚类结果。

def step2(config):

    vector_file = f"{config.sub_project_dir}/output/sim/voc_bert_vector.npy"
    initial_voc2RepresentativeWord_file = f"{config.sub_project_dir}/output/sim/voc2RepresentativeWord_initial.json" # 中间文件
    voc2RepresentativeWord_file = f"{config.sub_project_dir}/output/sim/voc2RepresentativeWord.json"
    cosine_similarity_thresh=config.synonyms_thresh

    X = np.load(vector_file)[:]
    raw_labels = json_open(initial_voc2RepresentativeWord_file)
    Y = X[raw_labels]

    n_labels = raw_labels[:]
    similarities=[]
    for id, vector1_vector2 in enumerate( zip(X, Y)):
        vector1, vector2 = vector1_vector2
        cosine_similarity = 1 - cosine(vector1, vector2)
        similarities.append(cosine_similarity)
        if cosine_similarity < cosine_similarity_thresh:
            n_labels[id] = id

    print("相似度阈值:", cosine_similarity_thresh)
    print("聚类情况：","词表数",len(X), ";满足阈值的聚类结果数量",len([i for i in similarities if i>=cosine_similarity_thresh]))
    

    outf = voc2RepresentativeWord_file
    with open(outf,"w",encoding="utf8") as fw:
        fw.write(json.dumps(n_labels, ensure_ascii=False))


    # # 输出每个簇的最近单词
    # for cluster_id, word_index in nearest_words.items():
    #     nearest_word = your_word_list[word_index]  # 替换your_word_list为您的单词列表
    #     print(f"Cluster {cluster_id}: Nearest Word - {nearest_word}")


# build_voc2RepresentativeWord函数：该函数是对step1和step2的封装，用于构建最终的词汇到代表性单词的映射。
def build_voc2RepresentativeWord(config):
    print(time.asctime())
    start = time.time()
    # 先聚类
    step1(config)
    # 再筛选
    step2(config)
    print(time.time() - start)
    print(time.asctime())



if __name__ == '__main__':

    build_voc2RepresentativeWord(config)