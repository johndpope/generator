from .MongoDriver import DBConnection
from helper.load import load_all_data_from_amazon


def drop_and_create_new(mongo):
    conn = DBConnection(mongo)
    all_data = load_all_data_from_amazon(conn.amazon)
    testamazon = conn.testamazon
    testamazon.insert_many(all_data)

