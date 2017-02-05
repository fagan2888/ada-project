import tensorflow as tf
import pickle
import numpy as np



def initTF():
  "load the saved model"
  model_path = "../Model/finalmodel"

  f = open('../Model/mean.pckl', 'rb')
  meanX = pickle.load(f)
  f.close()
  f = open('../Model/std.pckl', 'rb')
  stdX = pickle.load(f)
  f.close()

  def standardize(X):
    return (X - meanX) / stdX


  sess = tf.Session()

  new_saver = tf.train.import_meta_graph(model_path + "/model.ckpt.meta")
  new_saver.restore(sess, model_path + '/model.ckpt')

  return sess, standardize

def runTF(sess, features, standardize):
  "run the forecasting using the the loaded model"
  print(features)
  print(standardize(features))

  # with sess.as_default():
  #     prob_value = prob.eval(feed_dict={x: standardize(features)})
  prob_value = sess.run("prob:0", feed_dict={'xa:0': standardize(features), 'dropout_prob:0': 1})

  print(prob_value)

  return prob_value[0][0]
