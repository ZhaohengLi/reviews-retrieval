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
    :param model:
    :param result_list:
    :return:
    """
    assert result_list
    reference_list = []
    for result in result_list:
        reference_list.append(result.set_reference())
    similarity = sentences_similarity(model, reference_list)
    write_info("Similarity is " + str(similarity)+'\n', log_file_name)
    if similarity >= 0.65:
        write_info("Reference expand.\n", log_file_name)
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


def write_results(result_list, filename='log', mode='w'):
    """
    将最终结果写到文件中
    :param result_list:
    :param filename:
    :param mode:
    :return:
    """
    assert result_list
    with open('./data/'+filename+'.txt', mode) as file:
        file.write('\nTop '+str(len(result_list))+' results are:\n\n')
        for i in result_list:
            # file.write('Total_score: ' + str(i.score) +
            #            '\nCount_score: ' + str(i.count_score) +
            #            '\nDistance_score: ' + str(i.distance_score) +
            #            '\nLength_score: ' + str(i.length_score) + '\n')
            file.write('Sentiment: ' + str(i.sentiment) + '\n')
            file.write('Full: ' + i.review_text + '\n')
            file.write('Cut: ' + i.reference_text + '\n\n')


def write_info(info='\n', filename='log', mode='a'):
    with open('./data/'+filename+'.txt', mode) as file:
        file.write(info)


def sentiment_process(result_list):
    assert result_list
    sentiment_all = 0.0
    for result in result_list:
        s = SnowNLP(result.reference_text)
        result.sentiment = s.sentiments
        sentiment_all += s.sentiments
    sentiment_all /= len(result_list)
    neg_result_list = []
    pos_result_list = []
    for result in result_list:
        result.sentiment_average = sentiment_all
        if result.sentiment < 0.4:
            neg_result_list.append(result)
        else:
            pos_result_list.append(result)
    return result_list, pos_result_list, neg_result_list


def generate(current_item, keywords):
    results = search_for_keywords(current_item, keywords)
    if not results:
        write_info("No related results!", log_file_name)
        return
    results = keywords_process(results)
    results = length_process(results)
    results = score_process(results)
    results = reference_process(vector_model, results)
    results, pos_results, neg_results = sentiment_process(results)
    show_list = sorted(results, key=attrgetter('score', 'count_score', 'distance_score'), reverse=True)[:12]
    # neg_results = sorted(neg_results, key=attrgetter('sentiment'), reverse=False)
    write_results(show_list, log_file_name, 'a')
    # write_results(neg_results, 'neg_list_' + current_item + 'keywords: ' + str(keywords))


if __name__ == '__main__':

    vector_model = prep_vector()  # For sentence distance.

    # # item_list = ['1694588451', '1214322183']
    # item_list = ['44794700281', '44982816890', '45050097562']  # 三款裙子
    # final_test_list = []
    #
    # keywords_list = [['颜色'], ['质量'], ['款式'], ['长短'], ['腰线'], ['合身'], ['款式', '长短'], ['合身', '款式'], ['腰线', '合身']]
    # for item in item_list:
    #     for keywords in keywords_list:
    #         log_file_name = 'show_list_' + item + '_keywords_' + str(keywords)
    #         print(log_file_name)
    #         write_info('Keywords: ' + str(keywords), log_file_name, 'w')
    #         generate(item, keywords)

    while(True):
        file_name = input("请输入解析文件名：")
        if file_name == 'end':
            break;
        else:
            with open('./input/'+file_name, 'r') as file:
                item = str(file.readline())
                keywords = file.readline().split()
                log_file_name = 'show_list_' + item + '_keywords_' + str(keywords)
                print(log_file_name)
                write_info('Keywords: ' + str(keywords), log_file_name, 'w')
                generate(item, keywords)
