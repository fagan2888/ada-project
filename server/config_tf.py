import tensorflow as tf
import pickle
import numpy as np



def initTF():
  model_path = "../Model/tmp"

  seed = 42

  feature_count = 170

  n_nodes_hl1 = 150
  n_nodes_hl2 = 150
  n_nodes_hl3 = 150

  n_classes = 2

  x = tf.placeholder('float', [None, feature_count])

  f = open('../Model/mean.pckl', 'rb')
  meanX = pickle.load(f)
  f.close()
  f = open('../Model/std.pckl', 'rb')
  stdX = pickle.load(f)
  f.close()

  def standardize(X):
    return (X - meanX) / stdX


  def neural_network_model(data):

      hidden_1_layer = {
          'weights': tf.Variable(tf.truncated_normal([feature_count, n_nodes_hl1], stddev=0.1, seed=seed)),
          'biases': tf.Variable(tf.constant(1.0, shape=[n_nodes_hl1]))
      }

      hidden_2_layer = {
          'weights': tf.Variable(tf.truncated_normal([n_nodes_hl1, n_nodes_hl2], stddev=0.1, seed=seed)),
          'biases': tf.Variable(tf.constant(1.0, shape=[n_nodes_hl2]))
      }

      hidden_3_layer = {
          'weights': tf.Variable(tf.truncated_normal([n_nodes_hl2, n_nodes_hl3], stddev=0.1, seed=seed)),
          'biases': tf.Variable(tf.constant(1.0, shape=[n_nodes_hl3]))
      }

      output_layer = {
          'weights': tf.Variable(tf.truncated_normal([n_nodes_hl3, n_classes], stddev=0.1, seed=seed)),
          'biases': tf.Variable(tf.constant(1.0, shape=[n_classes]))
      }

      l1 = tf.add(tf.matmul(data, hidden_1_layer['weights']), hidden_1_layer['biases'])
      l1 = tf.nn.relu(l1)

      l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']), hidden_2_layer['biases'])
      l2 = tf.nn.relu(l2)

      l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']), hidden_3_layer['biases'])
      l3 = tf.nn.sigmoid(l3)

      output = tf.matmul(l3, output_layer['weights']) +  output_layer['biases']

      regularizers = (tf.nn.l2_loss(hidden_1_layer['weights']) + tf.nn.l2_loss(hidden_1_layer['biases']) +
                          tf.nn.l2_loss(hidden_2_layer['weights']) + tf.nn.l2_loss(hidden_2_layer['biases']) +
                              tf.nn.l2_loss(hidden_3_layer['weights']) + tf.nn.l2_loss(hidden_3_layer['biases']) +
                                  tf.nn.l2_loss(output_layer['weights']) + tf.nn.l2_loss(output_layer['biases']))

      return output, regularizers


  prediction, regularizers = neural_network_model(x)
  #Eval this to get probability of [winning,losing]
  prob = tf.nn.softmax(prediction)


  sess = tf.Session()
  sess.run(tf.global_variables_initializer())

  new_saver = tf.train.import_meta_graph(model_path + "/model.ckpt.meta")
  new_saver.restore(sess, tf.train.latest_checkpoint(model_path))

  return sess, prob, x, standardize

def runTF(sess, prob, x, features, standardize):

  print(features)
  print(standardize(features))

  with sess.as_default():
      prob_value = prob.eval(feed_dict={x: standardize(features)})

  return prob_value[0][0]
