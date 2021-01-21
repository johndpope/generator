import pprint

from flask import Flask, render_template, make_response, request, redirect, url_for, current_app
from flask_pymongo import PyMongo

from controller import MongoDriver
from controller.config import *
from helper.clean_url import clean_url

app = Flask(__name__)
app.config["MONGO_URI"] = f'mongodb+srv://{mongo_user}:{mongo_pw}@cluster0.en1dj.mongodb.net/gen?retryWrites=true&w=majority'
# app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/gen"
mongo = PyMongo(app)
ebay = mongo.db.ebay

driver = MongoDriver.DBConnection()
all_groups = driver.get_all_groups(ebay)

(sitemap, other_subpages) = driver.generate_sitemap(ebay, all_groups)

pp = pprint.PrettyPrinter(indent=4)


@app.route("/")
def template_index():
    # pp.pprint(all_groups)
    return render_template('index_template.html',
                           clean_url=clean_url,
                           groups=all_groups)


@app.route("/<category>")
def template_category(category):
    category = driver.get_category_by_url(ebay, category)
    if not category:
        return redirect(url_for('template_index'))

    subs = []
    for group in all_groups:
        if group.get("_id") == category:
            subs = group['subcategories'][:10]

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


@app.route("/<category>/<subcategory>")
def template_sub(category, subcategory):
    group = driver.get_group_by_category(all_groups, category)
    subcategory = driver.get_subcategory_by_url(ebay, subcategory)

    if not subcategory:
        return redirect(url_for('template_index'))

    category = driver.get_category_by_url(ebay, category)
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


@app.route("/<category>/<subcategory>/<keyword>")
def template_page(category, subcategory, keyword):
    subcategory = driver.get_subcategory_by_url(ebay, subcategory)
    category = driver.get_category_by_url(ebay, category)
    keyword = driver.get_keyword_by_url(ebay, keyword)

    if not keyword:
        return redirect(url_for('template_index'))

    products = driver.get_all_data_that_contains(ebay, keyword)

    other_categories = []
    for group in all_groups:
        if group.get("_id") == category:
            other_categories = group['subcategories'][:10]

    subpages = {}
    for subpage in other_subpages:
        if subpage.get('keyword') == keyword:
            subpages = subpage

    return render_template(
        'page_template.html',
        category=category,
        subcategory=subcategory,
        other_categories=other_categories,
        keyword=keyword,
        products=list(products),
        other_subpages=subpages['suggestions'],
        clean_url=clean_url,
        eval=eval
    )


@app.route("/<category>/<subcategory>/<keyword>/")
def template_page_redirect(category, subcategory, keyword):
    keyword = keyword.replace('/', '')
    return redirect(url_for('template_page', category=category, subcategory=subcategory, keyword=keyword))


@app.route("/sitemap.xml")
def template_sitemap():
    template = render_template(
        'sitemap.xml',
        all_urls=sitemap
    )
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route("/datenschutz")
def template_datenschutz():
    return render_template(
        'datenschutz.html',
        domain=request.host
    )


@app.route("/impressum")
def template_impressum():
    return render_template(
        'impressum.html',
        domain=request.host
    )


@app.route("/generic")
def template_generic():
    return render_template('generic.html', my_string="Wheeeee!", my_list=[0, 1, 2, 3, 4, 5])


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
