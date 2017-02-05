#!flask/bin/python
from flask import Flask, jsonify, request, current_app

import json

from config_tf import initTF
from config_tf import runTF
from gen_features import init_API, get_features, get_id

app = Flask(__name__, static_url_path='')

sess, standardize = initTF()
riotAPI = init_API()

@app.route('/forecast', methods=['POST'])
def forecast():
  """Takes the ordered summoner ids of the participants, gives them to the NN prediction function
  and returns the predicted win chance
  """

  summs = json.loads(request.form['summs'])
  features = get_features(summs, riotAPI)

  ret = runTF(sess, features, standardize)
  print(ret)
  return jsonify({"blue_victory": str(ret)})

@app.route('/test', methods=['GET'])
def test():
  summs = ['20391818', '51399696', '44405988', '50740446', '21344514', '51878309', '22192141',
    '28239076', '34358720', '35527349']

  features = get_features(summs, riotAPI)

  ret = runTF(sess, features, standardize)
  print(ret)
  return jsonify({"blue_victory": str(ret)})

@app.route('/name', methods=['GET'])
def name():
  "Returns the summoner id for a given summoner name or an empty value if not found"

  name = request.args['name'].lower()
  return get_id(name, riotAPI)

@app.route('/features', methods=['GET'])
def features():
  "Returns the generated features for the given summoner id"
  id = request.args['id'].lower()
  return jsonify(get_features([id], riotAPI))

@app.route('/')
def index():
  return current_app.send_static_file('index.html')


if __name__ == '__main__':
  # app.run(host='0.0.0.0', port=5000)
  app.run(debug=True)
