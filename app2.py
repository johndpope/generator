from helper.load import load_all_groups, get_all_sub_kw, get_kw_data, get_group_by_category
from flask import Flask, render_template, request, send_from_directory
import pprint
from datetime import datetime
from helper.to_dict import to_dict
from SitemapGen import generate_urls


app = Flask(__name__)

products = get_kw_data("napapijri rainforest winter herren")
all_groups = load_all_groups()[:10]


pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(all_categories)


@app.route("/products/<category>/<subcategory>/<keyword>/")
def template_page(category, subcategory, keyword):
    return render_template('page_template.html',
                           category=category,
                           subcategory=subcategory,
                           keyword=keyword,
                           products=products
                           )


@app.route("/sitemap.xml")
def template_sitemap():
    now = datetime.now()
    return render_template('sitemap.html',
                           urls=generate_urls(),
                           datetime=now.strftime("%Y-%m-%dT%H:%M:%S")+"+00:00"
                           )


@app.route("/<category>")
def template_cateogry(category):
    group = get_group_by_category(all_groups, category)
    pp.pprint(group)
    return render_template('category_template.html', my_string="Wheeeee!",
                           ownurl="http://localhost:5000",
                           group=group)


@ app.route("/")
def template_test():
    return render_template('index_template.html', my_string="Wheeeee!",
                           ownurl="http://localhost:5000",
                           groups=all_groups)


@ app.route("/generic")
def template_generic():
    return render_template('generic.html', my_string="Wheeeee!", my_list=[0, 1, 2, 3, 4, 5])


@ app.route('/assets/<path:path>')
def static_files(path):
    return send_from_directory('templates/assets', path)


@ app.route('/images/<path:path>')
def static_files_img(path):
    return send_from_directory('templates/images', path)


if __name__ == '__main__':
    app.run(debug=True)
