import pprint

from flask import Flask, render_template, make_response, request

from controller import MongoDriver
from helper.clean_url import clean_url

app = Flask(__name__)
driver = MongoDriver.DBConnection()

all_groups = driver.get_all_groups()

pp = pprint.PrettyPrinter(indent=4)


@app.route("/")
def template_test():
    return render_template('index_template.html',
                           clean_url=clean_url,
                           groups=all_groups)


@app.route("/<category>")
def template_category(category):
    category = driver.get_category_by_url(all_groups, category)
    # pp.pprint(category)
    group = driver.get_group_by_category(all_groups, category)
    return render_template('category_template.html',
                           clean_url=clean_url,
                           category=category,
                           group=group,
                           get_all_kw_of=driver.get_all_kw_of_subcategory
                           )


@app.route("/<category>/<subcategory>")
def template_sub(category, subcategory):
    group = driver.get_group_by_category(all_groups, category)
    (category, subcategory) = driver.get_subcategory_by_url(all_groups, category, subcategory)
    sub_kw_data = driver.get_all_kw_of_subcategory(subcategory)

    # pp.pprint(sub_kw_data)
    return render_template(
        'subcategory_template.html',
        category=category,
        subcategory=subcategory,
        sub_kw_data=sub_kw_data,
        length=len(sub_kw_data['keyword']),
        clean_url=clean_url,
        group=group
    )


@app.route("/<category>/<subcategory>/<keyword>/")
def template_page(category, subcategory, keyword):
    (category, subcategory) = driver.get_subcategory_by_url(all_groups, category, subcategory)
    keyword = driver.get_keyword_by_url(driver.get_all_data(), keyword)
    products = driver.get_all_data_that_contains(keyword)
    sub_kw_data = driver.get_all_kw_of_subcategory(subcategory)
    # pp.pprint(products)
    return render_template(
        'page_template.html',
        category=category,
        subcategory=subcategory,
        keyword=keyword,
        products=products,
        sub_kw_data=sub_kw_data,
        clean_url=clean_url
    )


@app.route("/sitemap.xml")
def template_sitemap():
    # pp.pprint(generate_urls())
    template = render_template(
        'sitemap.xml',
        all_urls=driver.generate_sitemap(request.url_root[:-1], all_groups)
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
