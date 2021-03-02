import random
import time
from datetime import datetime
from typing import List

from pymongo import MongoClient

from helper.clean_url import clean_url
from .config import *


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
        randomized = random.sample(filtered_list, 10)

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

    def get_all_kw_of_subcategory(self, subcategory):
        """
        Scans through the scraped CSV file and returns a Dict
        in the form
        eg. {
            '_id': 'Grills',
            'keywords': ['kombigrill', 'kingstone grillwagen black angus'],
            'images': ['https://i.ebayimg.com/images/g/x0EAAOSw0VteZPJ0/s-l300.jpg',...]
            }
        :param ebay:
        :param subcategory:
        :return:
        """
        data = self.ebay.aggregate([
            {"$match": {'main_subcategory': subcategory}},
            {'$group': {'_id': '$main_subcategory',
                        'keywords': {'$addToSet': '$keyword'},
                        'images': {'$addToSet': '$image'}
                        }},
            {'$limit': 1}
        ])

        return list(data)[0] if list(data) else None

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
        empty = '{}'
        # Get Today's Date to add as Lastmod
        lastmod_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "+00:00"

        # Fill the Sitemap Template and Write File
        i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0', 'loc': empty}
        each_map = [i]
        for each in data:  # For each URL in the list of URLs ...
            i = i.copy()
            link = f"{empty}{clean_url(each['_id'])}"
            i['loc'] = link
            each_map.append(i)
            # print(i['loc'])

            for lnk in each['subcategories']:
                i = i.copy()
                sub_link = f'{link}/{clean_url(lnk)}'
                i['loc'] = sub_link
                each_map.append(i)
                # print(i['loc'])

                kw_data = list(
                    self.ebay.aggregate([
                        {"$match": {'main_subcategory': lnk}},
                        {'$group': {'_id': '$main_subcategory',
                                    'keywords': {'$addToSet': '$keyword'},
                                    'images': {'$addToSet': '$image'}
                                    }},
                        {'$limit': 1}
                    ])
                )[0]
                for kw in kw_data['keywords'][:10]:
                    i = i.copy()
                    kw_lnk = f'{sub_link}/{clean_url(kw)}'
                    i['loc'] = kw_lnk
                    each_map.append(i)

        # Add the following
        y = i.copy()
        y['loc'] = f'{empty}/datenschutz'
        each_map.append(y)

        z = i.copy()
        z['loc'] = f'{empty}/impressum'
        each_map.append(z)

        return each_map
