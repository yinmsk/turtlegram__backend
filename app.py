from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
from bson import ObjectId
from flask import Flask, abort, jsonify, request, Response
from flask_cors import CORS
import jwt
from pymongo import MongoClient
# from bson.json_util import loads, dumps
SECRET_KEY = 'turtle'


app = Flask(__name__)
# 같은 호스트 이름이 아니더라도 정상적으로 호출 가능하도록 cors를 사용하고 *을 사용해 모든곳에서이 호출을 허용한다
cors = CORS(app, resources={r"*": {"origins": "*"}})
client = MongoClient('localhost', 27017)
db = client.dbturtle


def authorize(f):
    @wraps(f)
    def decorated_function():
        if not 'Authorization' in request.headers:
            abort(401)
        token = request.headers['Authorization']

        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            abort(401)
        return f(user)

    return decorated_function


@ app.route("/")
@authorize
def hello_world(user):
    print(user)
    return jsonify({'message': 'success'})


@ app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data)
    print(data)

    # 코드 형식?
    email = data["email"]
    password = data["password"]
    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        # 'email': email,
        'email': data.get('email'),
        'password': pw_hash
    }
    db.users.insert_one(doc)
    return jsonify({'message': 'success'})


@app.route('/login', methods=['POST'])
def login():
    print(request)
    data = json.loads(request.data)
    print(data)

    email = data.get("email")
    password = data.get("password")
    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(pw_hash)

    result = db.users.find_one({
        'email': email,
        # password: password
        'password': pw_hash
    })
    print(result)

    if result is None:
        return jsonify({"message": "아이디나 비밀번호가 옳지 않습니다"}), 401

    payload = {
        # "_id"는 몽고디비에서 만들어준 프라이머리키(이게 뭘까요?)
        # 꼭 str화해서 저장해주어야 한다
        'id': str(result["_id"]),
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(token)

    return jsonify({"message": "success", "token": token})


@app.route("/getuserinfo", methods={"GET"})
@authorize
def get_user_info(user):
    # @authorize를 사용해 def get_user_info에 user을 사용해준것 만으로도 코드 실행 가능
    # token = request.headers.get("Autforization")

    # if not token:
    #     return jsonify({"message": "no token"})
    # print(token)

    # user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    return jsonify({"message": "success", "email": result["email"]})


@app.route("/article", methods={"POST"})
@authorize
def post_article(user):
    data = json.loads(request.data)
    print(data)

    db_user = db.users.find_one({'_id': ObjectId(user.get('id'))})

    now = datetime.now().strftime("%H:%M:%S")
    doc = {
        'title': data.get('title', None),
        'content': data.get('content', None),
        'user': user['id'],
        'user_email': db_user['email'],
        'time': now,
    }
    print(doc)

    db.article.insert_one(doc)

    return jsonify({"message": "success"})


@app.route("/article", methods={"GET"})
def get_article():
    articles = list(db.article.find())
    for article in articles:
        article["_id"] = str(article["_id"])

    return jsonify({"message": "success", "article": article})


# 다른데서 부르면 실행하지 말라는 뜻이다
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
