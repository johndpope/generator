import datetime
from typing import List

from controller import MongoDriver
from helper.clean_url import clean_url

conn = MongoDriver.DBConnection()


def generate_sitemap(domain, data: List):

    # Get Today's Date to add as Lastmod
    lastmod_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")+"+00:00"

    # Fill the Sitemap Template and Write File
    i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0', 'loc': domain}
    each_map = [i]
    for each in data:  # For each URL in the list of URLs ...
        i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
        link = f"{domain}/{clean_url(each['category'])}"
        i['loc'] = link
        each_map.append(i)
        # print(i['loc'])

        for lnk in each['subcategory']:
            i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
            sub_link = f'{link}/{clean_url(lnk)}'
            i['loc'] = sub_link
            each_map.append(i)
            # print(i['loc'])

            kw_data = conn.get_all_kw_of_subcategory(lnk)
            for kw in kw_data['keywords']:
                i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
                kw_lnk = f'{sub_link}/{clean_url(kw)}'
                i['loc'] = kw_lnk
                each_map.append(i)
                # print(i['loc'])

    return each_map



