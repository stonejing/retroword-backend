from flask import Flask, redirect, request, url_for, g, Blueprint, render_template, abort, jsonify
from jinja2 import TemplateNotFound
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from errors import unauthorized, forbidden
import pymongo

app = Flask(__name__)
auth = HTTPBasicAuth()
# CORS(app, resources={r"/*": {"Access-Control-Allow-Origin": "*"}})
CORS(app)

users = {"john": generate_password_hash("hello"),
         "susan": generate_password_hash("bye"),
         "stonejing": generate_password_hash("stonejing"),
         "admin": generate_password_hash("admin"),
         }

api = Blueprint('api', __name__, url_prefix='/api')

# 连接 mongodb
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# 获取数据库
mydb = myclient["stonejing"]
# 获取集合
mycol = mydb["vocabulary"]


@auth.verify_password
def verify_password(username, password):
    if username in users:
        g.current_user = username
        return check_password_hash(users.get(username), password)
    else:
        return False


@api.route('/add_vocabulary', methods=["POST"])
def add_vocabulary():
    if request.method == "POST":
        word = request.form["vocabulary"]
        tag = request.form["tag"]
        mycol.insert_one({"username": auth.username(), "word": word, "tag": tag})
        return jsonify({"message": True})


@api.route('/')
def index():
    return "Hello, %s!" % auth.username()


@api.before_request
@auth.login_required
def before_request():
    # if g.current_user not in users:
    #     return forbidden('Unconfirmed account')
    return None


@api.route('/all_vocabulary', methods=['GET'])
def all_vocabulary():
    result = []
    if request.method == "GET":
        for x in mycol.find({}, {"_id": 0}):
            result.append(x)
        return jsonify({"data": result})


@api.route('/add_user', methods=["POST"])
def add_user():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if auth.current_user() == "admin" and username is not None and password is not None:
            users[username] = generate_password_hash(password)
            return "<h1> ADD USER </h1>"
        return f"POST DATA {auth.username()}"


if __name__ == '__main__':
    # blueprint should be registered after the route definition
    app.register_blueprint(api, url_prefix='/api')
    app.run(debug=True)
