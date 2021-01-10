from .MongoDriver import DBConnection
from helper.load import load_all_data_from_csv


def drop_and_create_new():
    conn = DBConnection()
    all_data = load_all_data_from_csv()
    conn.ebay.drop()

    ebay = conn.ebay
    ebay.insert_many(all_data)
    # print(result.inserted_ids)

