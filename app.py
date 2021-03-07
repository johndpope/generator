import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from flask_sitemap import Sitemap

from controller import MongoDriver
from helper.clean_url import clean_url

app = Flask(__name__)
ext = Sitemap(app=app)

load_dotenv('.env')
app.config["MONGO_URI"] = os.environ.get('PROD_DATABASE', "mongodb://127.0.0.1:27017/gen")

mongo = PyMongo(app)
ebay = mongo.db.ebay

driver = MongoDriver.DBConnection(mongo)


all_groups = []
sitemap = []
other_subpages = []


@app.before_first_request
def run_first():
    global all_groups
    all_groups = driver.get_all_groups(request.host_url)

    global sitemap, other_subpages
    (sitemap, other_subpages) = driver.generate_sitemap(all_groups)


@app.route("/")
def template_index():
    return render_template('index_template.html',
                           clean_url=clean_url,
                           groups=all_groups)


@ext.register_generator
def template_index():
    yield 'template_index', {}


@app.route("/<category>/")
def template_category(category):
    category = driver.get_category_by_url(category)
    if not category:
        return redirect(url_for('template_index'))

    subs = []
    for group in all_groups:
        if group.get("_id") == category:
            subs = group['subcategories']

    data = []
    for xx in subs:
        sub_data = ebay.aggregate([
            {"$match": {'main_subcategory': xx}},
            {'$group': {'_id': '$main_subcategory',
                        'keywords': {'$addToSet': '$keyword'},
                        'images': {'$addToSet': '$image'}
                        }},
            {'$limit': 1}
        ])
        data.append(list(sub_data)[0])

    return render_template('category_template.html',
                           clean_url=clean_url,
                           category=category,
                           group=group,
                           data=data
                           )


@app.route("/<category>/<subcategory>/")
def template_sub(category, subcategory):
    group = driver.get_group_by_category(all_groups, category)
    subcategory = driver.get_subcategory_by_url(subcategory)

    if not subcategory:
        return redirect(url_for('template_index'))

    category = driver.get_category_by_url(category)
    sub_data = ebay.aggregate([
            {"$match": {'main_subcategory': subcategory}},
            {'$group': {'_id': '$main_subcategory',
                        'keywords': {'$addToSet': '$keyword'},
                        'images': {'$addToSet': '$image'}
                        }},
            {'$limit': 1}
        ])

    data = list(sub_data)[0]
    return render_template(
        'subcategory_template.html',
        category=category,
        subcategory=subcategory,
        data=data,
        clean_url=clean_url,
        group=group
    )


@app.route("/<category>/<subcategory>/<keyword>/")
def template_page(category, subcategory, keyword):
    subcategory = driver.get_subcategory_by_url(subcategory)
    category = driver.get_category_by_url(category)
    keyword = driver.get_keyword_by_url(keyword)

    if not keyword:
        return redirect(url_for('template_index'))

    products = driver.get_all_data_that_contains(keyword)
    other_categories = []
    for group in all_groups:
        if group.get("_id") == category:
            other_categories = [x for x in group['subcategories'][:10] if x != subcategory]

    subpages = {}

    for subpage in other_subpages:
        if subpage.get('keyword') == keyword:
            subpages = subpage

    valid_subpages = [x for x in subpages['suggestions'] if clean_url(category) not in x]

    return render_template(
        'page_template.html',
        category=category,
        subcategory=subcategory,
        other_categories=other_categories,
        keyword=keyword,
        products=list(products),
        other_subpages=valid_subpages[:10],
        clean_url=clean_url,
        eval=eval
    )


@ext.register_generator
def template_sitemap():
    for url in sitemap:
        yield 'template_category', {'category': url}


@app.route("/datenschutz")
def template_datenschutz():
    return render_template(
        'datenschutz.html',
        domain=request.host
    )


@ext.register_generator
def template_datenschutz():
    yield 'template_datenschutz', {}


@app.route("/impressum")
def template_impressum():
    return render_template(
        'impressum.html',
        domain=request.host
    )


@ext.register_generator
def template_impressum():
    yield 'template_impressum', {}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
