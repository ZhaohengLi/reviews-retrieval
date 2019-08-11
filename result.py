import numpy as np
from tools import *


class Result:
    def __init__(self, _review_text, _keyword_list):
        self.review_text = _review_text  # 评论原文
        self.review_length = len(self.review_text)  # 评论原文长度
        self.review_length_average = 0.0  # 评论原文平均长度

        self.keyword_list = _keyword_list  # 关键词列表
        self.keywords_count = []  # 每个关键词出现出现次数
        self.keywords_average = []  # 每个关键词在所有Result中平均出现次数
        self.keywords_location = []  # 每个关键词出现的位置
        self.keywords_distance = []  # 相邻关键词最短距离
        self.keywords_interval = []  # 最短相邻关键词距离起始终止区间(可为空)

        self.reference_interval = []  # 与关键词最相关摘录语句区间(可为空)
        self.reference_text = ''  # 与关键词最相关摘录语句

        self.sentiment = 0.0  # 摘录语句情感得分
        self.sentiment_average = 0.0  # 摘录语句平均情感得分
        self.topic = ''  # 评论原文主题提取

        self.count_score = 0.0  # 关键词出现次数得分 (-1.0,1.0)
        self.distance_score = 0.0  # 关键词最短距离得分 [0.0, 1.0]
        self.length_score = 0.0  # 评论原文长度得分 (0.0, 1.0)

        self.score = 0.0  # 总评分数

    def set_score(self):
        """
        计算的总得分
        :return:
        """
        keywords_count = np.array(self.keywords_count)
        keywords_average = np.array(self.keywords_average)
        self.count_score = float(np.mean(sigmoid(np.true_divide(keywords_count-keywords_average, keywords_average))))

        for i in self.keywords_distance:
            self.distance_score += (1-(i/self.review_length)) / len(self.keywords_distance)

        self.length_score = float(sigmoid(self.review_length/self.review_length_average))

        # 总分计算
        self.score = 0.5*self.count_score + 0.4*self.distance_score + 0.1*self.length_score
        return self.score

    def set_reference(self):
        """
        根据最短相邻关键词距离起始终止区间生成与关键词最相关摘录语句
        :return:
        """
        break_symbol = [' ', ',', '，', '.', '。', '!', '！', '?', '？', '#']

        # 摘录语句区间选取过程-1: 根据keywords_interval进行初步确定
        if self.keywords_interval:
            # 如果有相邻的关键词
            self.reference_interval = self.keywords_interval[:]

            # 如果间隔过长需要提前处理
            if self.reference_interval[1]-self.reference_interval[0] > 30:
                self.reference_interval[1] = self.reference_interval[0]+30
        else:
            # 没有相邻关键词 则挑选第一个出现的关键词
            for i in range(len(self.keywords_count)):
                if self.keywords_count[i] != 0:
                    self.keywords_interval.append(self.keywords_location[i][0])
                    self.keywords_interval.append(self.keywords_location[i][0]+len(self.keyword_list[i]))
                    self.reference_interval = self.keywords_interval[:]
                    break

        # 摘录语句区间选取过程-2: 根据review_text进行最终确定
        for i in range(self.reference_interval[0], -1, -1):
            if self.review_text[i] not in break_symbol:
                self.reference_interval[0] = i
            else:
                break
        for i in range(self.reference_interval[1], self.review_length):
            if self.review_text[i] not in break_symbol:
                self.reference_interval[1] = i + 1
            else:
                break

        # 摘录语句生成
        self.reference_text = self.review_text[self.reference_interval[0]:self.reference_interval[1]]
        return self.reference_text

    def expand_reference(self):
        break_symbol = [' ', ',', '，', '.', '。', '!', '！', '?', '？', '#']

        # 在原来的reference_interval的基础上，再扩大范围（一个标点）
        if self.reference_interval[0]-2 >= 0:
            self.reference_interval[0] = self.reference_interval[0]-2
        else:
            self.reference_interval[0] = 0

        if self.reference_interval[1]+1 <= self.review_length:
            self.reference_interval[1] = self.reference_interval[1]+1

        for i in range(self.reference_interval[0], -1, -1):
            if self.review_text[i] not in break_symbol:
                self.reference_interval[0] = i
            else:
                break
        for i in range(self.reference_interval[1], self.review_length):
            if self.review_text[i] not in break_symbol:
                self.reference_interval[1] = i + 1
            else:
                break

        # 摘录语句更新
        self.reference_text = self.review_text[self.reference_interval[0]:self.reference_interval[1]]
        return self.reference_text

    def get_review_info(self):
        """
        获取原评论信息
        :return:
        """
        return self.review_text, self.review_length
