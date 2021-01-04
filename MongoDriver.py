from pymongo import MongoClient
from helper.load import load_all_data_from_csv
from helper.sanitize_url import clean_url
import config
import pprint


class DBConnection:
    """
    Sets up a connection to the MongoDB instance.
    Credentials are set up in config.py
    """

    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://" + config.mongo_user + ":" + config.mongo_pw + "@cluster0.en1dj.mongodb.net/gen?retryWrites=true&w=majority")
        self.db = self.client['gen']
        self.ebay = self.db.ebay

    """
    Tests the connection and returns + prints single item
    :return: Dict[]
    """

    def test(self):
        item = self.ebay.find_one()
        pprint.pprint(item)
        return item

    """
    Returns all items with specific keyword
    """

    def find_item_by_keyword(self, keyword):
        return self.ebay.find({"keyword": keyword})

    """
    Builds a tree and returns all
    """

    def get_all_data(self):
        return self.ebay.find(
            {})

    """
    Get specific subcategory
    """

    """
    Get specific category
    """

    """
    Get specific 
    """

    """
    Get all categories and subcategories 
    """
    def get_categories_and_subcategories(self):
        all_categories = self.get_all_data()
        tree = {}
        for item in all_categories:
            # print(item.get("category"))
            category = item["category"]
            subcategory = item["mainsubcategory"]
            keyword = item["keyword"]
            item = item["name"]

            clean_category = item["sanitized_category"]
            clean_subcategory = item["sanitized_mainsubcategory"]

            if tree.get(clean_category) == None:
                tree[clean_category] = {
                    "subcategories": {},
                    "name": category,
                }
            if tree.get(clean_category).get("subcategories").get(clean_subcategory) == None:
                tree[clean_category]["subcategories"][clean_subcategory] = {
                    "name": subcategory
                }

    """
    Creates a tree for the sitemap
    """

    def get_all_categories(self):

        all_categories = self.get_all_data()
        tree = {}
        for item in all_categories:
            # print(item.get("category"))
            category = item["category"]
            subcategories = item["mainsubcategory"]
            keyword = item["keyword"]
            item = item["name"]

            for subcategory in subcategories:
                # We take the slug as keys
                clean_category = clean_url(category)
                clean_subcategory = clean_url(subcategory)
                clean_keyword = clean_url(keyword)

                if tree.get(clean_category) == None:
                    tree[clean_category] = {
                        "subcategories": {},
                        "name": category,
                    }
                if tree.get(clean_category).get("subcategories").get(clean_subcategory) == None:
                    tree[clean_category]["subcategories"][clean_subcategory] = {
                        "keywords": {},
                        "name": subcategory
                    }
                if tree.get(clean_category).get("subcategories").get(clean_subcategory).get("keywords").get(clean_keyword) == None:
                    tree[clean_category]["subcategories"][clean_subcategory]["keywords"][clean_keyword] = {
                        "items": [],
                        "name": keyword
                    }
                tree[clean_category]["subcategories"][clean_subcategory]["keywords"][clean_keyword]["items"].append({
                    "name": item,
                    "slug": clean_url(item)})
        print(tree)
        return tree

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


connection = DBConnection()

# item_by_id = connection.find_item_by_keyword("elektro kabinenroller")
# for item in item_by_id:
#     pprint.pprint(item)

# connection.get_categories_and_subcategories()
