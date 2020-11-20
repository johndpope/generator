import datetime
from typing import List

from jinja2 import Environment, FileSystemLoader

from helper.load import load_all_groups, get_all_sub_kw
from helper.sanitize_url import sanitize_url


def generate_sitemap(domain: str, data: List):
    template_env = Environment(loader=FileSystemLoader(searchpath='./templates'))
    template = template_env.get_template('sitemap.xml')

    # Get Today's Date to add as Lastmod
    lastmod_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # Fill the Sitemap Template and Write File
    each_map = []
    for each in data:  # For each URL in the list of URLs ...
        i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
        link = f"{domain}/{sanitize_url(each['category'])}"
        i['loc'] = link
        each_map.append(i)

        for lnk in each['subcategory'][0:10]:
            i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
            sub_link = f'{link}/{sanitize_url(lnk)}'
            i['loc'] = sub_link
            each_map.append(i)

            kw_data = get_all_sub_kw(lnk)
            for kw in kw_data['keywords']:
                i = {'lastmod': lastmod_date, 'changefreq': 'daily', 'priority': '1.0'}
                kw_lnk = f'{sub_link}/{sanitize_url(kw)}'
                i['loc'] = kw_lnk
                each_map.append(i)

    with open(f'layout/{domain[6:]}/sitemap.xml', 'w') as sm:
        sm.write(template.render(
            each_map=each_map
        ))
