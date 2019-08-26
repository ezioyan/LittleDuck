import json
import logging
import copy
from math import radians, cos, sin, asin, sqrt

# 邻接矩阵示例
adjacency = [[5.5] * 40] * 40

# 所有x为longitude y为latitude
# from app.models import AttractionImage



class Recommend:
    dimensions = [
        'drive', 'walking', 'nature', 'human', "hot_on_net",
        'cold_on_net', 'historic', 'modern', 'price', "entertainment",
    ]

    attractions = []

    def __init__(self, user_id):
        self.user_id = user_id

        self.scores = {}
        for i in self.dimensions:
            self.scores[i] = 50.0

    def like(self, attraction):
        for key in self.dimensions:
            after = float(self.scores[key] + (attraction[key] - 50) / 10)
            if 0 <= after <= 100:
                self.scores[key] = after

    def dislike(self, attraction):
        for key in self.dimensions:
            after = float(self.scores[key] - (attraction[key] - 50) / 10)
            if 0 <= after <= 100:
                self.scores[key] = after

    def recommend(self, day, start_x=0.0, start_y=0.0):
        rec_list = self._recommend(day, start_x, start_y)[0]
        logging.info("Recommend Score: {}".format(self.scores))
        ll = self.divide(rec_list, day)
        return ll

    def _recommend(self, day, start_x, start_y):
        score_dic = self.scores
        rec_attr_list = []
        dis_dic = {}

        for attr in self.attractions:
            distance = 0
            for i in score_dic:
                distance += pow(score_dic[i] - attr[i], 2)
            dis_dic[attr] = int(distance)

        dis_list = sorted(dis_dic.items(), key=lambda item: item[1])
        for dis in dis_list:
            rec_attr_list.append(dis[0])
        choose_list = [Recommend.choose(rec_attr_list, day * 100)]
        adjust_list = Recommend.adjust(choose_list, day * 100, start_x, start_y)
        # print(adjust_list)
        route_list = Recommend.routes(adjust_list, start_x, start_y)
        # print(route_list)
        return route_list

    def first_recommend(self, day, start_x=0, start_y=0):
        score_dic = self.scores
        rec_attr_list = []
        dis_dic = {}

        for attr in self.attractions:
            distance = 0
            for i in score_dic:
                distance += pow(score_dic[i] - attr[i], 2)
            dis_dic[attr] = int(distance)

        dis_list = sorted(dis_dic.items(), key=lambda item: item[1])
        for dis in dis_list:
            rec_attr_list.append(dis[0])
        choose_list = [Recommend.choose(rec_attr_list, day * 100)]
        # print(choose_list)
        return choose_list

    @staticmethod
    def split(choose_list, start_x=0, start_y=0):
        route_list = Recommend.routes(choose_list, start_x, start_y)
        ll = Recommend.divide(route_list[0])
        return ll

    @staticmethod
    def choose(lst, target):
        value = []

        for l in lst:
            value.append(len(lst) - lst.index(l))
        ll = Recommend.knapsack(value, lst, target)
        return ll

    @staticmethod
    def knapsack(weight, lst, v):
        n = len(weight)
        value = []
        lists = []

        for i in weight:
            value.append(i * lst[weight.index(i)].day)
        arr = [[0] * (v + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, v + 1):
                if lst[i - 1].day <= j:
                    arr[i][j] = max(arr[i - 1][j], value[i - 1] + arr[i - 1][j - lst[i - 1].day])
                else:
                    arr[i][j] = arr[i - 1][j]
        # print(arr)
        remain = v
        for i in range(n, 0, -1):
            if arr[i][remain] > arr[i - 1][remain]:
                lists.append(lst[i - 1])
                remain -= lst[i - 1].day
        return lists

    @staticmethod
    def route(lst, start_x, start_y):
        used = lst
        new_list = []
        temp_x = start_x
        temp_y = start_y

        while len(lst) != 0:
            dis_dic = {}
            for i in used:
                dis = pow((i.x - temp_x), 2) + pow((i.y - temp_y), 2)
                dis_dic[i.name] = dis
            chosen = sorted(dis_dic.items(), key=lambda item: item[1])[0][0]
            for i in used:
                if i.name == chosen:
                    temp_x = i.x
                    temp_y = i.y
                    new_list.append(i)
                    used.remove(i)
        return new_list

    @staticmethod
    def routes(lst, start_x, start_y):
        ll = []
        for l in lst:
            ll.append(Recommend.route(l, start_x, start_y))
        return ll

    @staticmethod
    def adjust(lst, target, start_x, start_y):
        final_ll = []

        for i in range(len(lst[0])):
            temp_ll = lst[0][:(i+1)]
            # print(temp_ll)
            temp_time = Recommend.time_cal(final_ll, start_x, start_y)
            # print(temp_time)
            if temp_time <= target+10:
                final_ll = temp_ll
            else:
                break
        return [final_ll]

    @staticmethod
    def time_cal(lst, start_x, start_y):
        used = copy.copy(lst)
        temp_x = start_x
        temp_y = start_y
        last_id = 0
        sum_time = 0

        while used:
            dis_dic = {}
            for i in used:
                dis = pow((i.x - temp_x), 2) + pow((i.y - temp_y), 2)
                dis_dic[i.name] = dis
            chosen = sorted(dis_dic.items(), key=lambda item: item[1])[0][0]
            for i in used:
                if i.name == chosen:
                    sum_time = sum_time + adjacency[last_id][i.id] + i.day
                    temp_x = i.x
                    temp_y = i.y
                    last_id = i.id
                    used.remove(i)
        return sum_time

    @staticmethod
    def divide(lst, day):
        divided = []

        for i in range(day):
            if i != day-1:
                this_day = []
                last_id = 0
                sum_time = 0

                while len(lst) and sum_time + lst[0].day + adjacency[last_id][lst[0].id] <= 120:
                    this_day.append(lst[0])
                    sum_time = sum_time + lst[0].day + adjacency[last_id][lst[0].id]
                    # print(sum_time)
                    last_id = lst[0].id
                    lst.pop(0)
                divided.append(this_day)
            else:
                divided.append(lst)
        return divided


class _Attr:
    def __init__(self, _dict):
        self._dict = _dict

    def __getitem__(self, item):
        return self._dict[item]

    def __getattr__(self, item):
        return self._dict[item]

    def __repr__(self):
        return "{}:{}".format(self.id, self.name)


def start_to_each(user, start_x, start_y):
    for attr in user.attractions:
        lng1, lat1, lng2, lat2 = map(radians, [float(start_x), float(start_y), float(attr.x), float(attr.y)])
        delta_lng = lng2 - lng1
        delta_lat = lat2 - lat1
        a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lng / 2) ** 2
        distance = 2 * asin(sqrt(a)) * 6371 * 1000
        distance = round(distance / 1000, 3)
        adjacency[0][attr.id] = adjacency[attr.id][0] = round(distance / 50 * 10, 2)


def init_from_local():
    with open("attrs.json", "rb") as file:
        data = file.read().decode()
        data = json.loads(data)
        Recommend.attractions = [_Attr(_dict) for _dict in data]


init_from_local()

"""
在这里写你的测试
"""

a = Recommend("123")

a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.dislike(a.attractions[15])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[5])
a.like(a.attractions[4])
a.like(a.attractions[4])
a.like(a.attractions[4])
a.like(a.attractions[4])
a.like(a.attractions[4])
a.like(a.attractions[4])
a.like(a.attractions[4])
a.like(a.attractions[4])
a.like(a.attractions[25])
a.like(a.attractions[25])
a.like(a.attractions[25])
a.like(a.attractions[25])
a.like(a.attractions[25])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])
a.like(a.attractions[20])

# update adjacency matrix
print(a.attractions)
start_to_each(a, 108.964174, 34.218263)
# recommend
print(a.recommend(5, 108.964174, 34.218263))
# print adjacency matrix
# print("adjacency: ")
# for attr in a.attractions:
#     print("start to attr", attr.id, ": ", adjacency[0][attr.id])


