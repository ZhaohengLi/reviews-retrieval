from reviews import *
import re
import os
from operator import attrgetter
from result import *
from sentence_distance import *
from snownlp import SnowNLP
from tools import *
import collections


def search_for_keywords(item_id, category, keyword_list):
    """
    首先获得含有关键词的评论 返回Result的列表
    :param shop_id: (int) This's also the table's name.
    :param keyword_list: (list) A list of keywords.
    :return: (list) A list of 'Result'(Class)s.
    """
    review_list = get_review(item_id, category)  # 从数据库中获取评论文本
    result_list = []
    review_text_linked_together = ''
    for review in review_list:
        for i in keyword_list:
            if i in review[1]:
                result_list.append(Result(review[1], keyword_list, review[0], review[2]))
                review_text_linked_together += review[1]
                break
    return result_list, review_text_linked_together


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
    # todo
    # similarity = sentences_similarity(model, reference_list)
    similarity = 0.5
    if similarity >= 0.65:
        write_info("Reference expand.\n", file_path+'/extra.txt')
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


def topic_process(result_list):
    assert result_list
    for result in result_list:
        s = SnowNLP(result.review_text)
        result.topic = s.keywords()
    return result_list


def word_counts_process(text):
    text = clean_text(text)
    word_list = remove_stopwords(text)
    word_counts = collections.Counter(word_list)
    word_counts_top10 = word_counts.most_common(10)
    write_info(str(word_counts_top10), file_path+'/word_counts.txt')


def search_keywords(results, keywords):
    temp = []
    for result in results:
        for keyword in keywords:
            if keyword in result.review_text:
                temp.append(Result(result.review_text, keywords, result.star, result.category))
                break
    return temp


def generate(current_item, category, keywords, results=[]):
    if len(results) == 0:
        results, review_text_linked_together = search_for_keywords(current_item, category, keywords)
        if not results:
            write_info("No related results!", file_path + '/EmptyResult.txt')
            print("无搜索结果")
            return []
        word_counts_process(review_text_linked_together)

    results = search_keywords(results, keywords)
    if not results:
        write_info("No related results!", file_path + '/EmptyResult.txt')
        print("无搜索结果")
        return []

    write_info('Size of results: '+str(len(results)), file_path + '/Find' + str(len(results)) + 'Results.txt')
    print("找到"+str(len(results))+"条搜索结果")
    results = keywords_process(results)
    results = length_process(results)
    results = score_process(results)
    results = reference_process(vector_model, results)
    results = topic_process(results)
    results, pos_results, neg_results = sentiment_process(results)

    normal_results = sorted(results, key=attrgetter('score', 'count_score', 'distance_score'), reverse=True)[:12]
    neg_results = sorted(neg_results, key=attrgetter('star'), reverse=False)

    write_results(normal_results, file_path+'/normal.txt')
    write_results(neg_results, file_path+'/negative.txt')
    write_results(results, file_path+'/all.txt')
    return results


if __name__ == '__main__':
    print("程序正在载入 请稍后")
    # vector_model = prep_vector()  # For sentence distance.
    vector_model = ''
    print("已载入程序")

    while True:
        file_name = input("是否开始全新的搜索 文件名/no\n")
        if file_name == 'no':
            break
        else:
            last_results = []
            item = ''
            category = ''
            keywords = []
            with open('./input/'+file_name, 'r') as file:
                item = str(file.readline().strip())
                category = str(file.readline().strip())
                keywords = file.readline().split()

            file_path = os.path.abspath('./output')
            file_path = os.path.join(file_path, item)
            if not os.path.exists(file_path):
                os.mkdir(file_path)

            if category == '':
                file_path = os.path.join(file_path, str(keywords))
                if not os.path.exists(file_path):
                    os.mkdir(file_path)
            else:
                file_path = os.path.join(file_path, str(category) + "-" + str(keywords))
                if not os.path.exists(file_path):
                    os.mkdir(file_path)

            print('Now processing: ' + item + ' with category: ' + category + ' with keywords: ' + str(keywords))
            last_results = generate(item, category, keywords)
            while True:
                ans = input("是否进一步搜索 keywords/no\n")
                if ans == 'no':
                    break
                keywords = ans.split()
                file_path = os.path.join(file_path, str(keywords))
                if not os.path.exists(file_path):
                    os.mkdir(file_path)
                last_results = generate(item, category, keywords, last_results)

    print("程序正在退出")
