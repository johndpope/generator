from controller import MongoDriver
from temp.sitemap import generate_urls


conn = MongoDriver.DBConnection()
# print(conn.get_all_groups())
# cat = conn.get_category_by_url('reisen')
# print(cat)
# print(conn.get_group_by_category(cat))


print(generate_urls(conn.get_all_data()))