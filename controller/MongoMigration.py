from .MongoDriver import DBConnection
from helper.load import load_all_data_from_amazon


def drop_and_create_new(mongo):
    conn = DBConnection(mongo)
    all_data = load_all_data_from_amazon(conn.amazon)
    print(all_data)
    # conn.ebay.drop()

    # ebay = conn.ebay
    # ebay.insert_many(all_data)
    # print(result.inserted_ids)

