from pymongo import MongoClient
from helper.load import load_all_data_from_csv
import config
import pprint

# setup
client = MongoClient(
    "mongodb+srv://" + config.mongo_user + ":" + config.mongo_pw + "@cluster0.en1dj.mongodb.net/gen?retryWrites=true&w=majority")
db = client['gen']

ebay = db.ebay
ebay.drop()

all_data = load_all_data_from_csv()

pprint.pprint(all_data[0])

result = ebay.insert_many(all_data)

# print(result.inserted_ids)
