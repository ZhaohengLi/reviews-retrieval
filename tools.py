import numpy as np
import jieba
import re

def sigmoid(x):
    s = 1 / (1 + np.exp(-x))
    return s


def nan():
    for i in range(5, -4, -1):
        print(i)


def write_results(result_list, file_name):
    """
    将最终结果写到文件中
    :param result_list:
    :return:
    """
    with open(file_name, 'w') as file:
        file.write('Top '+str(len(result_list))+' results are:\n')
        if not result_list:
            return
        for i in result_list:
            # file.write('Total_score: ' + str(i.score) +
            #            '\nCount_score: ' + str(i.count_score) +
            #            '\nDistance_score: ' + str(i.distance_score) +
            #            '\nLength_score: ' + str(i.length_score) + '\n')
            file.write('节选:\n' + i.reference_text + '\n')
            file.write('全部评论:\n' + i.review_text + '\n')
            file.write('星级: ' + str(i.star) + '\n')
            # file.write('Topic: ' + str(i.topic) + '\n')
            file.write('分类: ' + str(i.category) + '\n')
            file.write('Sentiment:' + str(i.sentiment) + '\n\n\n')


def write_info(info, file_name):
    with open(file_name, 'w') as file:
        file.write(str(info)+'\n')


def clean_text(text):
    """
    Replace all non-chinese characters with ','.
    :param text: (str) A text to be processed.
    :return: (str) A processed text.
    """
    text = re.sub('[^\u4e00-\u9fa5]', ',', str(text))
    return text


def remove_stopwords(text):
    """
    Cut a chinese text into a word list and remove all stopwords.
    :param text: (str) A text to be processed.
    :return: (list) A list of words like "['Google','Microsoft','Apple']".
    """
    with open('others/stopwords_only_chinese.txt', 'r') as file:
        stopwords_list = file.read().splitlines()
        file.close()
    words_list = jieba.lcut(text)
    words_list = [i for i in words_list if not i in stopwords_list]
    return words_list


if __name__ == '__main__':
    nan()
