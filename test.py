from controller import MongoDriver


conn = MongoDriver.DBConnection()
# all_g = conn.get_all_groups()
# cat = conn.get_category_by_url(all_g, 'reisen')
# # print(cat)
# (x, y) = conn.get_subcategory_by_url(all_g, 'reisen', 'reiseaccessoires')
# print(f'{x}, {y}')
print(conn.get_keyword_by_url(list(conn.get_all_data()), 'batterie-12v-a23'))

