import csv

from helper.clean_url import clean_url


def load_all_data_from_csv():
    """
    Loads every single entry from csv and adds sanitized urls
    :return: List
    [
        {'keyword',
        'name',
        'category',
        'subcategory',
        'sanitized_keyword',
        'sanitized_name',¸
        'sanitized_category',
        'sanitized_subcategory',
        'image',
        'price',
        'item_no',
        'location',
        'description',
        'description_link',
        'url'


    ]
    """
    all_data = []
    with open('./database/data.csv') as file:
        reader = csv.DictReader(file)
        for line in reader:
            data = {
                "keyword": line['keyword'],
                "name": line['name'],
                "category": line['category'],
                "subcategories": line['subcategory'].split('|'),
                "image": line['image'], "price": line['price'],
                "item_no": line['item_no'],
                "location": line.get('location'),
                "description": line['description'],
                "description_link": line['description_link'],
                "url": line['url'],
                "main_subcategory": ""
            }

            if data['category'] in data['subcategories']:
                data['subcategories'].remove(data['category'])

            if 'Sonstige' in data['subcategories']:
                data['subcategories'].remove('Sonstige')

            if len(data['subcategories']):
                data["main_subcategory"] = data['subcategories'][-2] \
                    if len(data['subcategories']) > 1 else data['subcategories'][0]

            data["url_keyword"] = clean_url(data["keyword"])
            data["url_category"] = clean_url(data["category"])
            data["url_mainsubcategory"] = clean_url(data["main_subcategory"])

            all_data.append(data)

    return all_data
