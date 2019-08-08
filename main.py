from reviews import *
import re
import numpy as np
from operator import attrgetter
from result import *
from sentence_distance import *
from snownlp import SnowNLP


def search_for_keywords(shop_id, keyword_list):
    """
    首先获得含有关键词的评论 返回Result的列表
    :param shop_id: (int) This's also the table's name.
    :param keyword_list: (list) A list of keywords.
    :return: (list) A list of 'Result'(Class)s.
    """
    review_list = get_review_text(shop_id)  # 从数据库中获取评论文本
    result_list = []
    for review in review_list:
        for i in keyword_list:
            if i in review:
                result_list.append(Result(review, keyword_list))
                break
    assert result_list
    return result_list


def length_process(result_list):
    """
    写入评论平均长度
    :param result_list:
    :return:
    """
    assert result_list
    sum_length = 0
    for result in result_list:
        sum_length += result.review_length
    average_length = sum_length/len(result_list)

    for result in result_list:
        result.review_length_average = average_length  # 对列表中的Result的唯一写入操作
    return result_list


def keywords_process(result_list):
    assert result_list
    keyword_list = result_list[0].keyword_list
    keywords_sum = np.zeros([len(keyword_list)])  # 生成初始sum数组

    for result in result_list:
        for keyword in keyword_list:
            count = 0
            location = []
            for match in re.finditer(keyword, result.review_text):
                location.append(match.start())
                count += 1
            result.keywords_count.append(count)
            result.keywords_location.append(location)

        keywords_sum += np.array(result.keywords_count)

        # 寻找相邻关键词最短距离并标记起始终止区间
        minimum_distance = result.review_length
        for i in range(len(result.keywords_location) - 1):
            if result.keywords_location[i] and result.keywords_location[i + 1]:
                distance = result.review_length
                for location_i in result.keywords_location[i]:
                    for location_j in result.keywords_location[i + 1]:
                        new_distance = location_j - location_i - len(result.keyword_list[i])
                        if 0 < new_distance < distance:
                            distance = new_distance
                        if 0 < new_distance < minimum_distance:
                            minimum_distance = new_distance
                            result.keywords_interval = [location_i, location_j + len(result.keyword_list[i + 1])]
                result.keywords_distance.append(distance)
            else:
                result.keywords_distance.append(result.review_length)

    for result in result_list:
        result.keywords_average = list(keywords_sum/len(result_list))

    return result_list


def reference_process(model, result_list):
    """
    为每一条Result设定摘录语句,如果语义相关度极高，将进一步拓展摘录语句
    :param result_list:
    :return:
    """
    assert result_list
    reference_list = []
    for result in result_list:
        reference_list.append(result.set_reference())
    similarity = sentences_similarity(model, reference_list)
    print("Similarity is " + str(similarity))
    if similarity >= 0.2:
        print("Reference expand.")
        for result in result_list:
            result.expand_reference()
    return result_list


def score_process(result_list):
    """
    给列表中每一条Result进行最终得分计算
    :param result_list:
    :return:
    """
    assert result_list
    for result in result_list:
        result.set_score()
    return result_list


def write_results(result_list):
    """
    将最终结果写到文件中
    :param result_list:
    :return:
    """
    assert result_list
    keyword_list = result_list[0].keyword_list
    with open('./data/log.txt', 'w') as file:
        file.write('Keywords: ')
        for keyword in keyword_list:
            file.write(keyword + ' ')
        file.write('\nTop ten results are:\n\n')
        for i in result_list:
            # file.write('Total_score: ' + str(i.score) +
            #            '\nCount_score: ' + str(i.count_score) +
            #            '\nDistance_score: ' + str(i.distance_score) +
            #            '\nLength_score: ' + str(i.length_score) + '\n')
            file.write('Sentiment: ' + i.sentiment + '\n')
            file.write('Full: ' + i.review_text + '\n')
            file.write('Cut: ' + i.reference_text + '\n\n')


def sentiment_process(result_list):
    assert result_list
    for result in result_list:
        s = SnowNLP(result.reference_text)
        result.sentiment = s.sentiments
    return result_list


if __name__ == '__main__':

    model = prep_vector()  # For sentence distance.

    shop_list = ['4665606', '66641167', '2743444']
    current_shop = 'QUILT'
    keywords = ['质量']

    results = search_for_keywords(current_shop, keywords)
    results = keywords_process(results)
    results = length_process(results)
    results = score_process(results)
    results = reference_process(model, results)
    results = sentiment_process(results)
    show_list = sorted(results, key=attrgetter('score', 'count_score', 'distance_score'), reverse=True)[:10]
    write_results(results)
