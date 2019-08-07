import gensim
import jieba
import numpy as np
from scipy.linalg import norm


def prep_vector():
    """
    极度耗时，注意一开始准备好。
    :return:
    """
    model_file = './data/news_12g_baidubaike_20g_novel_90g_embedding_64.bin'
    model = gensim.models.KeyedVectors.load_word2vec_format(model_file, binary=True)
    return model


def vector_similarity(model, s1, s2):
    def sentence_vector(s):
        words = jieba.lcut(s)
        v = np.zeros(64)
        for word in words:
            v += model[word]
        v /= len(words)
        return v

    v1, v2 = sentence_vector(s1), sentence_vector(s2)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))

