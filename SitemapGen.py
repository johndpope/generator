import MongoDriver

connection = MongoDriver.DBConnection()

domain = "testurl"


def generate_urls():
    all_data = connection.get_all_data()

    urls = {domain: True}

    for item in all_data:
        slug_keyword = item["sanitized_keyword"]
        slug_category = item["sanitized_category"]
        slug_mainsubcategory = item["sanitized_mainsubcategory"]

        url_cat = domain + "/" + slug_category + "/"
        url_subcat = url_cat + slug_mainsubcategory + "/"
        url_keyword = url_subcat + slug_keyword + "/"

        urls[url_cat] = True
        urls[url_subcat] = True
        urls[url_keyword] = True

    return list(urls.keys())


generate_urls()
