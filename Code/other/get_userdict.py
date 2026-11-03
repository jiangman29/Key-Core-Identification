import pandas as pd

def get_userdict(inf, outf):
    """获取用户词表"""
    # 读取xlsx文件
    df = pd.read_excel(inf, header=None, )

    # 去除每个单元格的空格，并将每行的单词按行存储到txt文件
    with open(outf, 'w', encoding='utf-8') as file:
        for index, row in df.iterrows():
            words = [word.strip() for word in row[0].split()]
            line = ' '.join(words)
            file.write(line + '\n')
