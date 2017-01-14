#!flask/bin/python
from flask import Flask, jsonify

from config_tf import initTF
from config_tf import runTF
from gen_features import get_features


app = Flask(__name__)

sess, prob, x = initTF()

@app.route('/forecast', methods=['GET'])
def forecast():
  features = get_features()

  ret = runTF(sess, prob, x, features)
  print(ret)
  return jsonify({"blue_victory": str(ret)})


@app.route('/')
def index():
  return "Hello, World!"

if __name__ == '__main__':
  app.run(debug=True)
