import csv
import random


def load_all_groups():
    all = []
    with open('./database/data.csv') as file:
        reader = csv.DictReader(file)
        for line in reader:
            data = {}

            item = line['keyword']
            image = line['image']

            category = line['category'].split('|')
            categ = category[0]
            if categ not in [each['category'] for each in all if all]:
                data['category'] = categ
                data['subcategory'] = []
                data['items'] = []
                data['image'] = []

                all.append(data)

            # Update the list of dictionaries while still in motion using generators
            # Return dict that has key == current iteration category value
            allcat = next(item for item in all if item['category'] == categ)

            # Update when we get a match
            if allcat and item not in allcat['items']:  # only add that keyword once
                if (category[-2] not in allcat['subcategory']) and (category[-2] != categ):
                     allcat['subcategory'].append(category[-2])
                allcat['image'].append(image)

                allcat['items'].append(item)

    # return all
    return random.sample(list(filter(lambda x: len(x['subcategory']) > 4, all)), 10)


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
            if subcategory in line['category'].split('|')[-2]:
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
