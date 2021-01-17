import pprint
import time

from flask import Flask, render_template, make_response, request
from flask_pymongo import PyMongo
from controller.config import *

from controller import MongoDriver
from helper.clean_url import clean_url

app = Flask(__name__)
app.config["MONGO_URI"] = f'mongodb+srv://{mongo_user}:{mongo_pw}@cluster0.en1dj.mongodb.net/gen?retryWrites=true&w=majority'
# app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/gen"
mongo = PyMongo(app)
ebay = mongo.db.ebay

driver = MongoDriver.DBConnection()
all_groups = driver.get_all_groups(ebay)

pp = pprint.PrettyPrinter(indent=4)



@app.route("/")
def template_test():
    # pp.pprint(all_groups)
    return render_template('index_template.html',
                           clean_url=clean_url,
                           groups=all_groups)


@app.route("/<category>")
def template_category(category):
    category = driver.get_category_by_url(ebay, category)
    group = driver.get_group_by_category(all_groups, category)
    subs = group['subcategories'][:10]

    data = []
    for xx in subs:
        start = time.perf_counter()
        sub_data = ebay.aggregate([
            {"$match": {'main_subcategory': xx}},
            {'$group': {'_id': '$main_subcategory',
                        'keywords': {'$addToSet': '$keyword'},
                        'images': {'$addToSet': '$image'}
                        }},
            {'$limit': 1}
        ])
        data.append(list(sub_data)[0])
        end = time.perf_counter()
        # print(f'took {end - start} secs')

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
    products = driver.get_all_data_that_contains(ebay, keyword)

    sub_data = ebay.aggregate([
        {"$match": {'main_subcategory': subcategory}},
        {'$group': {'_id': '$main_subcategory',
                    'keywords': {'$addToSet': '$keyword'},
                    'images': {'$addToSet': '$image'}
                    }},
        {'$limit': 1}
    ])

    data_of_sub = list(sub_data)[0]
    return render_template(
        'page_template.html',
        category=category,
        subcategory=subcategory,
        keyword=keyword,
        data_of_sub=data_of_sub,
        products=list(products),
        clean_url=clean_url
    )


@app.route("/sitemap.xml")
def template_sitemap():
    template = render_template(
        'sitemap.xml',
        all_urls=driver.generate_sitemap(request.url_root[:-1], ebay, all_groups)
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
