import pprint

from flask import Flask, render_template, send_from_directory, make_response, request

from controller import MongoDriver
from helper.clean_url import clean_url
from sitemap import generate_sitemap

app = Flask(__name__)
driver = MongoDriver.DBConnection()

all_groups = driver.get_all_groups()

pp = pprint.PrettyPrinter(indent=4)


@app.route("/")
def template_test():
    return render_template('index_template.html',
                           my_string="Wheeeee!",
                           clean_url=clean_url,
                           groups=all_groups)


@app.route("/<category>")
def template_category(category):
    category = driver.get_category_by_url(category)
    group = driver.get_group_by_category(all_groups, category)
    return render_template('category_template.html',
                           clean_url=clean_url,
                           category=category,
                           group=group,
                           get_all_kw_of=driver.get_all_kw_of_subcategory
                           )


@app.route("/<category>/<subcategory>/<keyword>/")
def template_page(category, subcategory, keyword):
    subcategory = driver.get_subcategory_by_url(subcategory)
    keyword = driver.get_keyword_by_url(keyword)
    products = driver.get_all_data_that_contains(keyword)
    # pp.pprint(products)
    return render_template(
        'page_template.html',
        category=category,
        subcategory=subcategory,
        keyword=keyword,
        products=products
    )


@app.route("/sitemap.xml")
def template_sitemap():
    # pp.pprint(generate_urls())
    template = render_template(
        'sitemap.xml',
        all_urls=generate_sitemap(request.host_url, all_groups)
    )
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route("/generic")
def template_generic():
    return render_template('generic.html', my_string="Wheeeee!", my_list=[0, 1, 2, 3, 4, 5])


@app.route('/assets/<path:path>')
def static_files(path):
    return send_from_directory('templates/assets', path)


@app.route('/images/<path:path>')
def static_files_img(path):
    return send_from_directory('templates/images', path)


if __name__ == '__main__':
    app.run(debug=True)
