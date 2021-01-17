import time

from flask import Flask, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/gen"
mongo = PyMongo(app)


@app.route('/test')
def index():
    data = mongo.db.ebay.aggregate([
        {"$match": {'main_subcategory': 'Pflege'}},
        {'$group': {'_id': '$main_subcategory',
                    'keywords': {'$addToSet': '$keyword'},
                    'images': {'$addToSet': '$image'}
                    }},
        {'$limit': 1}
    ])

    for i in data:
        print(i)
    return 'how far'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


from controller import MongoDriver

# conn = MongoDriver.DBConnection()
#
#
# for i in dd:
#     start = time.perf_counter()
#     cato = conn.ebay.aggregate([
#         {"$match": {'main_subcategory': i}},
#         {'$group': {'_id': '$main_subcategory',
#                     'keywords': {'$addToSet': '$keyword'},
#                     'images': {'$addToSet': '$image'}
#                     }},
#         {'$limit': 1}
#     ])
#     end = time.perf_counter()
#     print(f'took {end - start} secs')
#
#     cato.close()
#     print(list(cato))

