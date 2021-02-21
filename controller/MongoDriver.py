import random
from datetime import datetime
from typing import List

from pymongo import MongoClient

from helper.clean_url import clean_url
from .config import *


class DBConnection:

    def __init__(self):
        """
        Sets up a connection to the MongoDB instance.
        Credentials are set up in config.py
        """
        self.client = MongoClient(
            # f'mongodb+srv://{mongo_user}:{mongo_pw}@cluster0.en1dj.mongodb.net/gen?retryWrites=true&w=majority'
            # "mongodb://127.0.0.1:27017"
	    f'mongodb://{mongo_user}:{mongo_pw}@202.61.242.18'
        )
        self.db = self.client['crawler']
        self.ebay = self.db.ebay

    def test(self):
        """
           Tests the connection and returns + prints single item
           :return: Dict[]
        """
        item = self.ebay.find_one()
        # pprint.pprint(item)
        return item

    @classmethod
    def get_all_groups(cls, ebay):
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
        grouped_data = ebay.aggregate([{'$group': {'_id': "$category",
                                                   'subcategories': {'$addToSet': '$main_subcategory'},
                                                   'images': {'$addToSet': '$image'}
                                                   }}
                                       ])
        grouped_data.close()
        return random.sample(list(filter(lambda x: (len(x['subcategories']) > 5 and '' not in x['subcategories'])
                                         , grouped_data)), 10)

    @classmethod
    def get_group_by_category(cls, groups, category):
        """
        Gets a single group by 'category'
        :return:
        """
        for group in groups:
            if group.get("_id") == category:
                return group if group else None

    @classmethod
    def get_all_kw_of_subcategory(cls, ebay, subcategory):
        """
        Scans through the scraped CSV file and returns a Dict
        in the form
        eg. {
            '_id': 'Grills',
            'keywords': ['kombigrill', 'kingstone grillwagen black angus'],
            'images': ['https://i.ebayimg.com/images/g/x0EAAOSw0VteZPJ0/s-l300.jpg', 'https://i.ebayimg.com/images/g/woQAAOSw-2letTfS/s-l300.jpg'
            }
        :param ebay:
        :param subcategory:
        :return:
        """
        data = ebay.aggregate([
            {"$match": {'main_subcategory': subcategory}},
            {'$group': {'_id': '$main_subcategory',
                        'keywords': {'$addToSet': '$keyword'},
                        'images': {'$addToSet': '$image'}
                        }},
            {'$limit': 1}
        ])

        return list(data)[0] if list(data) else None

    @classmethod
    def get_all_data_that_contains(cls, ebay, keyword):
        """
        Gets all the data in the database that contains that keyword
        :param ebay:
        :param keyword:
        :return: [List]
        """
        data = ebay.find({'keyword': keyword})
        return data

    @classmethod
    def get_category_by_url(cls, ebay, url_category):
        result = ebay.find_one({'url_category': url_category})
        return result['category'] if result else None

    @classmethod
    def get_subcategory_by_url(cls, ebay, url_subcategory):
        result = ebay.find_one({'url_mainsubcategory': url_subcategory})
        return result['main_subcategory'] if result else None

    @classmethod
    def get_keyword_by_url(cls, ebay, url_keyword):
        result = ebay.find_one({'url_keyword': url_keyword})
        return result['keyword'] if result else None

    @classmethod
    def generate_sitemap(cls, ebay, data: List):
        empty = '{}'

        all_kws = []
        subpages = []

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
                    ebay.aggregate([
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

                    all_kws.append(kw)
                    subpages.append(kw_lnk)
                    each_map.append(i)
                    # print(i['loc'])

        # Add the following
        y = i.copy()
        y['loc'] = f'{empty}/datenschutz'
        each_map.append(y)

        z = i.copy()
        z['loc'] = f'{empty}/impressum'
        each_map.append(z)

        other_subpages = []
        for q in all_kws:
            k = {'keyword': q, 'suggestions': random.sample(subpages, 15)}
            other_subpages.append(k)

        return each_map, other_subpages
