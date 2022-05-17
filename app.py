import json
import hashlib
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.dbturtle


app = Flask(__name__)
# 같은 호스트 이름이 아니더라도 정상적으로 호출 가능하도록 cors를 사용하고 *을 사용해 모든곳에서이 호출을 허용한다
cors = CORS(app, resources={r"*": {"origins": "*"}})


@ app.route("/")
def hello_world():
    # 어디에 나오는걸까?
    return jsonify({'message': 'success'})


@ app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data)

    # 코드 형식?
    email = data["email"]
    password = data["password"]
    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        'email': email,
        'password': pw_hash,
    }
    db.users.insert_one(doc)
    return jsonify({'message': 'success'})


# 다른데서 부르면 실행하지 말라는 뜻이다
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

    # print(request)
    # print(request.form.get('id'))
    # print(data.get('email'))
    # print(data.get["password"])

# email_receive = request.form['email_give']


# 질문
# request.form의 의미 form 데이터를 주고 받을때 사용

# request 프론트엔드에서 데이터를 가져온다

# print(request.form)은 get 사용 가능

# print(request.data)은 get 사용 불가
# data = json.loads(request.data)
# print(data) 라고 사용해야한다
# print(data["password"])

# return jsonify({'message': 'success'})
