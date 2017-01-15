#!flask/bin/python
from flask import Flask, jsonify, request, current_app

import json

from config_tf import initTF
from config_tf import runTF
from gen_features import init_API, get_features, get_id

app = Flask(__name__, static_url_path='')

sess, prob, x, standardize = initTF()
riotAPI = init_API()

@app.route('/forecast', methods=['POST'])
def forecast():

  summs = json.loads(request.form['summs'])
  features = get_features(summs, riotAPI)

  ret = runTF(sess, prob, x, features, standardize)
  print(ret)
  return jsonify({"blue_victory": str(ret)})

@app.route('/test', methods=['GET'])
def test():

  # summs = ['31858318', '42270213', '56396690', '45290268', '53012710', '31877470', '19931164', '30857494', '24752272', '62835377'] # tmp
  summs = ['31858318', '31858318', '56396690', '45290268', '53012710', '31877470', '19931164', '30857494', '24752272', '62835377'] # tmp

  features = get_features(summs, riotAPI)

  ret = runTF(sess, prob, x, features, standardize)
  print(ret)
  return jsonify({"blue_victory": str(ret)})

@app.route('/name', methods=['GET'])
def name():
  name = request.args['name'].lower()
  return get_id(name, riotAPI)

@app.route('/')
def index():
  return current_app.send_static_file('index.html')


if __name__ == '__main__':
  # app.run(host='0.0.0.0', port=5000)
  app.run(debug=True)
