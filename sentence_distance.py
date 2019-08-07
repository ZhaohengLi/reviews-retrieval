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


def sentence_vector(model, s):
    words = jieba.lcut(s)
    v = np.zeros(64)
    for word in words:
        v += model[word]
    v /= len(words)
    return v


def sentences_similarity(model, sentence_list):
    similarity = 0.0
    vector_list = []

    for sentence in sentence_list:
        vector_list.append(sentence_vector(model, sentence))

    for i in range(len(vector_list)):
        for j in range(i+1, len(vector_list)):
            similarity += np.dot(vector_list[i], vector_list[j]) / (norm(vector_list[i]) * norm(vector_list[j]))

    similarity /= len(vector_list)*(len(vector_list)-1)/2
    return similarity
