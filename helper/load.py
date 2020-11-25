import csv
import random


def load_all_groups():
    """
    Groups the entire ebay csv file in the /database folder and returns a
    list of all the original data grouped into categories
    :return: List
    eg: [
        {'category': 'Büro & Schreibwaren',
        'subcategory': ['Möbel', 'Koffer, Taschen & Accessoires', ...],
        'image': ['https://i.ebayimg.com/images/g/8HsAAOSwmQxfgGeV/s-l300.jpg']
        },
        ...
    ]
    """
    grouped_data = []
    with open('./database/data.csv') as file:
        reader = csv.DictReader(file)
        for line in reader:
            data = {}
            image = line['image']

            subcategory = line['subcategory'].split('|')
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
                subcat = subcategory[-2] if len(subcategory) > 1 else subcategory[0]

                # Check if subcategory not in list already and if it does not have same
                # name as the 'category'
                if (subcat not in allcat['subcategory']) and (subcat != category) and (subcat != 'Sonstige'):
                    allcat['subcategory'].append(subcat)
                allcat['image'].append(image)

            if len(allcat['subcategory']) > 10:
                allcat['subcategory'] = random.sample(allcat['subcategory'], 10)
            # allcat['image'] = [random.choice(allcat['image'])]

    # return all
    return random.sample(list(filter(lambda x: len(x['subcategory']) > 4, grouped_data)), 10)


def get_all_sub_kw(subcategory):
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

    with open('./database/data.csv') as file:
        reader = csv.DictReader(file)

        for line in reader:
            subcategory_ = line['subcategory'].split('|')
            subcat = subcategory_[-2] if len(subcategory_) > 1 else subcategory_[0]
            if subcategory in subcat:
                keyword = line['keyword']
                image = line['image']

                if keyword not in data['keywords']:
                    data['keywords'].append(keyword)
                    data['images'].append(image)

    return data if data['keywords'] else None


def get_kw_data(kw):
    """
    Gets all the data in the scraped CSV file that contains that keyword
    :param kw:
    :return:
    """
    with open('./database/data.csv') as file:
        reader = csv.DictReader(file)
        data = [line for line in reader if kw == line['keyword']]
        return data
