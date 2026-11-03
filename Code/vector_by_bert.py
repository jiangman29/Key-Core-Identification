# 使用bert模型将文本转换为向量
# step3-2 构建bert向量，中英文有区别

import os


import sys
import numpy as np
from tqdm import tqdm

from transformers import BertTokenizer, BertModel
import torch

# 检查是否有可用的GPU
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

model = None
tokenizer = None

# 加载相应的BERT模型和分词器
def load_model(config): 
    global model,tokenizer
    if config.LANG=="en":
        checkpoint_path = config.EN_checkpoint_path
    else:
        checkpoint_path = config.ZH_checkpoint_path
    print(config.LANG, checkpoint_path)
        

    # 加载预训练的BERT模型和分词器
    tokenizer = BertTokenizer.from_pretrained(checkpoint_path)
    model = BertModel.from_pretrained(checkpoint_path)
    model.to(device)

def exit_model():
    global model,tokenizer
    model = None
    tokenizer = None

# 输入文本
text1 = "I love machine learning"
text2 = "Machine learning is great"

# 定义文本嵌入函数
# embed函数接收文本列表，使用分词器处理文本，然后通过BERT模型获取每个文本的嵌入向量（特别是CLS标记的向量），最后返回这些向量的numpy数组
def embed(texts):

    # 输入文本
    # texts = ["I love machine learning", "Machine learning is great", "BERT is awesome"]

    # 分词和编码文本，并将它们移到GPU上
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(device)
    # 获取BERT模型的输出
    outputs = model(**inputs)

    # 提取句子的表示向量（CLS标记的向量）
    embeddings = outputs.last_hidden_state[:, 0, :]
    vectors = embeddings.detach().cpu().numpy()
    return vectors


    # 计算余弦相似度
    # similarity = 1 - cosine(embeddings1.detach().numpy(), embeddings2.detach().numpy())

    # print(f"相似度：{similarity}")

# 批处理生成器 (batch_generator)
def batch_generator(data, batch_size):
    total_batches = len(data) // batch_size
    if len(data) > total_batches * batch_size:
        total_batches += 1
    for batch_idx in tqdm(range(total_batches)):
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(data))
        yield data[start_idx:end_idx]

# 构建词表向量：voc_emb_bert函数读取词表文件，将词表分批转换为向量表示，并将结果保存为numpy数组
def voc_emb_bert(inf,out_file ):
    """
        inf:词汇表txt，每个单词一行
        outf: numpy矩阵
    """
    # 设置批处理大小
    batch_size = 30
    # 使用生成器来迭代数据
    vectors = np.empty((0, 768), dtype=float) # 
    with open(inf, encoding="utf8") as fr:
        data_txt = [l.strip() for l in fr]
        for batch in batch_generator(data_txt, batch_size):
            # 提取向量
            if not batch:continue
            batch_vector = embed(batch)
            # print(vectors.shape)
            # print(batch_vector.shape)
            vectors = np.concatenate([vectors, batch_vector])
    # 使用numpy.save保存矩阵到文件中
    np.save(out_file, vectors)

# 主函数
def generate_bert_vector(config):
    """ 对输入词表构建bert向量表示 """
    # inf = "/home/wjz/projects/others/jiangman/data/chinese_data_1112/output/sim/voc.txt"
    # out_file = "/home/wjz/projects/others/jiangman/data/chinese_data_1112/output/sim/voc_bert_vector.npy"
    if not model:
        load_model(config)
    inf = f"{config.sub_project_dir}/output/sim/voc.txt"
    out_file = f"{config.sub_project_dir}/output/sim/voc_bert_vector.npy"
    voc_emb_bert(inf, out_file)
    exit_model()

def test():
    # 输入文本
    text1 = "这家拍卖行和"
    text2 = "国家"
    embed(texts=[text1,text2])
    exit_model()
if __name__ == '__main__':
    # embed(["I love machine learning", "Machine learning is great", "BERT is awesome"])
    test()
    sys.exit()

