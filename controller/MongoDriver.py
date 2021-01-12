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
            f'mongodb+srv://{mongo_user}:{mongo_pw}@cluster0.en1dj.mongodb.net/gen?retryWrites=true&w=majority'
            # "mongodb://127.0.0.1:27017"
            )
        self.db = self.client['gen']
        self.ebay = self.db.ebay

    def test(self):
        """
           Tests the connection and returns + prints single item
           :return: Dict[]
        """
        item = self.ebay.find_one()
        # pprint.pprint(item)
        return item

    def get_all_data(self):
        """
        returns all scraped data 'ebay' from the database
        :return: [List]
        """
        return self.ebay.find()

    def get_all_groups(self):
        """
        Groups the entire data in the database and returns a
        list of all the data grouped into categories
        eg: [
            {'category': 'Büro & Schreibwaren',
            'subcategory': ['Möbel', 'Koffer, Taschen & Accessoires', ...],
            'image': ['https://i.ebayimg.com/images/g/8HsAAOSwmQxfgGeV/s-l300.jpg']
            },
            ...
        ]
        :return: List of 10 randomly selected categories
        """
        grouped_data = []
        all_data = self.get_all_data()
        for line in all_data:
            data = {}
            image = line['image']

            subcategories = line['subcategories']
            category = line['category']
            if category not in [each['category'] for each in grouped_data if grouped_data]:
                data['category'] = category
                data['subcategory'] = []
                data['image'] = []

                grouped_data.append(data)

            # Update the list of dictionaries while still in motion using generators
            # Return dict that has key == current iteration category value
            allcat = next(item for item in grouped_data if item['category'] == category)

            # Update when we get a match
            if allcat:
                # Use value at 2nd to the last if list elements are more than 1 otherwise 1st
                subcategory = line['main_subcategory']

                # Check if subcategory not in list already and if it does not have same
                # name as the 'category'
                if (subcategory not in allcat['subcategory']) and (subcategory != category) and (subcategory != 'Sonstige'):
                    allcat['subcategory'].append(subcategory)
                allcat['image'].append(image)

            if len(allcat['subcategory']) > 10:
                allcat['subcategory'] = random.sample(
                    allcat['subcategory'], 10)
            allcat['image'] = [random.choice(allcat['image'])]

        return random.sample(list(
            filter(lambda x: len(x['subcategory']) > 4, grouped_data)
        ), 10)

    @classmethod
    def get_group_by_category(cls, all_groups, category):
        """
        Gets a single group by 'category'
        :return:
        """
        # for group in self.get_all_groups():
        #     if group.get("category") == category:
        #         return group
        group = [group for group in all_groups if category == group['category']]
        return group[0] if group else None

    def get_all_kw_of_subcategory(self, subcategory):
        """
        Scans through the scraped CSV file and returns a Dict
        in the form
        eg. {'subcategory': 'Grills',
            'keywords': ['kombigrill', 'kingstone grillwagen black angus'],
            'images': ['https://i.ebayimg.com/images/g/x0EAAOSw0VteZPJ0/s-l300.jpg', 'https://i.ebayimg.com/images/g/woQAAOSw-2letTfS/s-l300.jpg'
            }
        :param subcategory:
        :return:
        """
        data = {'subcategory': subcategory, 'keyword': [], 'images': []}

        all_data = self.get_all_data()

        for line in all_data:
            subcat = line['main_subcategory']
            if subcategory == subcat:
                keyword = line['keyword']
                image = line['image']

                if keyword not in data['keyword']:
                    data['keyword'].append(keyword)
                    data['images'].append(image)

        return data if data['keyword'] else None

    def get_all_data_that_contains(self, keyword):
        """
        Gets all the data in the database that contains that keyword
        :param keyword:
        :return: [List]
        """
        data = self.ebay.find({'keyword': keyword})
        return data

    @classmethod
    def get_category_by_url(cls, all_groups, url_category):
        filtered = next(filter(lambda x: clean_url(x['category']) == url_category, all_groups), None)
        return filtered['category'] if filtered else None

    @classmethod
    def get_subcategory_by_url(cls, all_groups, url_category, url_subcategory):
        result = [x['subcategory'] for x in all_groups if clean_url(x['category']) == url_category]
        if not result:
            return None
        subcategory = next(filter(lambda x: clean_url(x) == url_subcategory, result[0]), None)
        category = cls.get_category_by_url(all_groups, url_category)
        return category, subcategory if subcategory else None

    @classmethod
    def get_keyword_by_url(cls, all_data, url_keyword):
        keyword = next(filter(lambda x: clean_url(x['keyword']) == url_keyword, all_data), None)
        return keyword['keyword'] if keyword else None

    def generate_sitemap(self, domain, data: List):

        # Get Today's Date to add as Lastmod
        lastmod_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "+00:00"

        # Fill the Sitemap Template and Write File
        i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0', 'loc': domain}
        each_map = [i]
        for each in data:  # For each URL in the list of URLs ...
            i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
            link = f"{domain}/{clean_url(each['category'])}"
            i['loc'] = link
            each_map.append(i)
            # print(i['loc'])

            for lnk in each['subcategory']:
                i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
                sub_link = f'{link}/{clean_url(lnk)}'
                i['loc'] = sub_link
                each_map.append(i)
                # print(i['loc'])

                kw_data = self.get_all_kw_of_subcategory(lnk)
                for kw in kw_data['keyword']:
                    i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
                    kw_lnk = f'{sub_link}/{clean_url(kw)}'
                    i['loc'] = kw_lnk
                    each_map.append(i)
                    # print(i['loc'])

        return each_map
