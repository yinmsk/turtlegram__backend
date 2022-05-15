from flask import Flask, jsonify
from requests import request


app = Flask(__name__)


@app.route("/")
def hello_world():
    return jsonify({'message': 'success'})


@app.route("/signup", methods=["POST"])
def sign_up():
    print(request)
    print(request.form)

    return jsonify({'message': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
