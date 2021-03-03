import random
import time
from typing import List

from helper.clean_url import clean_url


class DBConnection:

    def __init__(self, mongo):
        """
        Sets up a connection to the MongoDB instance.
        Credentials are set up in config.py
        """
        self.mongo = mongo
        self.ebay = self.mongo.db.ebay

    def get_all_groups(self):
        """
        Groups the entire data in the database and returns a
        list of all the data grouped into categories
        eg: [
            {   '_id': 'Sport',
                'subcategories': ['Druckluftkompressoren', ...]
                'images': [   'https://i.ebayimg.com/images/g/JekAAOSwE3RftrU8/s-l300.jpg',...]
            ...
        ]
        :type ebay: object
        :return: List of 10 randomly selected categories
        """

        # start timer
        start_timer = time.perf_counter()
        grouped_data = self.ebay.aggregate([{'$group': {'_id': "$category",
                                                        'subcategories': {'$addToSet': '$main_subcategory'},
                                                        'images': {'$addToSet': '$image'}
                                                        }}
                                            ])

        # timestamp1
        timestamp1 = time.perf_counter()

        filtered_list = list(
            filter(lambda x: (len(x['subcategories']) > 5 and '' not in x['subcategories']), grouped_data))

        new_list = []
        for each in filtered_list:
            each['subcategories'] = each['subcategories'][:10]
            each['images'] = each['images'][:10]
            new_list.append(each)

        randomized = random.sample(new_list, 10)

        # timestamp2
        timestamp2 = time.perf_counter()

        print(timestamp1 - start_timer)
        print(timestamp2 - timestamp1)
        return randomized

    @classmethod
    def get_group_by_category(cls, groups, category):
        """
        Gets a single group by 'category'
        :return:
        """
        for group in groups:
            if group.get("_id") == category:
                return group if group else None

    def get_all_data_that_contains(self, keyword):
        """
        Gets all the data in the database that contains that keyword
        :param ebay:
        :param keyword:
        :return: [List]
        """
        data = self.ebay.find({'keyword': keyword})
        return data

    def get_category_by_url(self, url_category):
        result = self.ebay.find_one({'url_category': url_category})
        return result['category'] if result else None

    def get_subcategory_by_url(self, url_subcategory):
        result = self.ebay.find_one({'url_mainsubcategory': url_subcategory})
        return result['main_subcategory'] if result else None

    def get_keyword_by_url(self, url_keyword):
        result = self.ebay.find_one({'url_keyword': url_keyword})
        return result['keyword'] if result else None

    def generate_sitemap(self, data: List):
        domain = '{}'
        all_kws = []
        subpage_links = []

        each_map = [domain]
        for each in data:  # For each URL in the list of URLs ...
            link = f"{domain}{clean_url(each['_id'])}"
            each_map.append(link)

            each_map.extend([f"{domain}{clean_url(each['_id'])}/{clean_url(sub)}" for sub in each['subcategories']])

            for sub in each['subcategories']:
                data = list(self.ebay.aggregate([
                    {"$match": {'main_subcategory': sub}},
                    {'$group': {'_id': '$main_subcategory',
                                'keywords': {'$addToSet': '$keyword'},
                                'images': {'$addToSet': '$image'}
                                }},
                    {'$limit': 1}
                ]))[0]

                all_kws.extend([i for i in data['keywords'][:10]])
                subpage_links.extend([f"{domain}{clean_url(each['_id'])}/{clean_url(sub)}/{clean_url(i)}"
                                      for i in data['keywords'][:10]])
                each_map.extend(subpage_links)

        # Add the following
        y = f'{domain}/datenschutz'
        each_map.append(y)

        z = f'{domain}/impressum'
        each_map.append(z)

        other_subpages = []
        for q in all_kws:
            k = {'keyword': q, 'suggestions': random.sample(subpage_links, 10)}
            other_subpages.append(k)

        return each_map, other_subpages
