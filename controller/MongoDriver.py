import random

from pymongo import MongoClient
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
        data = {'subcategory': subcategory, 'keywords': [], 'images': []}

        all_data = self.get_all_data()

        for line in all_data:
            subcat = line['main_subcategory']
            if subcategory in subcat:
                keyword = line['keyword']
                image = line['image']

                if keyword not in data['keywords']:
                    data['keywords'].append(keyword)
                    data['images'].append(image)

        return data if data['keywords'] else None

    def get_all_data_that_contains(self, keyword):
        """
        Gets all the data in the database that contains that keyword
        :param keyword:
        :return: [List]
        """
        data = self.ebay.find({'keyword': keyword})
        return data

    def get_category_by_url(self, url_category):
        result = self.ebay.find_one({'url_category': url_category})
        category = result['category'] if result else None
        return category

    def get_subcategory_by_url(self, url_subcategory):
        result = self.ebay.find_one({'url_mainsubcategory': url_subcategory})
        sub = result['main_subcategory'] if result else None
        return sub

    def get_keyword_by_url(self, url_keyword):
        result = self.ebay.find_one({'url_keyword': url_keyword})
        keyword = result['keyword'] if result else None
        return keyword

    # FELIX EXTRA CODE DOWN HERE 👇🏼👇🏼👇🏼👇🏼👇🏼👇🏼👇🏼
    """
    Update cateogry tree
    """

    def update_all_categories(self):
        tree = self.get_all_categories()
        tree_collection = self.db["tree"]

        myquery = {"id": "main_tree"}
        newvalues = {"$set": {"tree": tree}}
        tree_collection.delete_one(myquery)
        result = tree_collection.update_one(myquery, newvalues, True)
        print(result)

    """
    returns complete tree for sitemap 
    """

    def get_tree(self):
        tree_collection = self.db["tree"]
        tree = tree_collection.find_one({"id": "main_tree"})
        return tree
