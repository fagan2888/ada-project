import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
import os
import matplotlib.pyplot as plt

print(tf.__version__)

df = pd.read_csv("../features/features_global.csv", sep=',', header=None, low_memory=False, na_values=['null'])

df = df.dropna()


#Global constants
seed = 7875
validation_size = 750
feature_count = df.shape[1] - 2

#feed forward neural net
n_nodes_hl1 = 10
n_nodes_hl2 = 0
n_nodes_hl3 = 0

#cycles of feed forward + backprop on all K-folded samples
hm_epochs = 100

n_classes = 2

model_path = "./tmp2/model.ckpt"
save_dir = './tmp2/'


import pickle

X = np.asarray(df.ix[:,2:feature_count+2])
#standardize X
meanX = np.mean(X, axis = 0)
stdX = np.std(X, axis = 0)

f = open('mean.pckl', 'wb')
pickle.dump(meanX, f)
f.close()

f = open('std.pckl', 'wb')
pickle.dump(stdX, f)
f.close()

X = (X - meanX) / stdX

Y_1 = np.asarray(df.ix[:,0])
Y_1 = [int(y == "purple") for y in Y_1]
#one hot Y
Y = np.zeros(shape=(len(Y_1), n_classes))
Y[np.arange(len(Y_1)), Y_1] = 1

validation_features = X[:validation_size]
validation_labels = Y[:validation_size]

train_features = X[validation_size:]
train_labels = Y[validation_size:]

num_examples = train_features.shape[0]



a = [[1.6804181,0.49852886,4.68621827,4.68621826,4.50822828,0.03580143,-0.10327194,1.11961983,1.16662829,-2.59213006,-2.15577311,-0.32022004,0.87494358,-0.3034381,0.44390429,-0.9642744,1.7493962,1.67095743,0.69076133,4.4399695,4.44861103,4.26084272,0.03987201,-0.14456116,0.90806216,0.81786188,-2.50698302,-2.00234836,-0.22628798,0.6579448,-0.17845283,0.47368511,-0.80479309,1.408297,1.64860553,0.70200482,4.72736236,4.72736237,4.44769614,0.03626145,0.04033567,0.33755175,0.75715305,-2.45430391,-2.00318108,-0.22711913,0.56923335,-0.09720827,0.45787225,-0.78624504,1.29222884,1.67716915,0.87944803,4.48648949,4.48648951,4.36315752,0.03896885,0.33587276,0.20004711,0.95438807,-1.26753452,-1.01436325,-0.18031334,0.8690158,-0.19019017,0.6512756,-0.7698582,1.43403969,1.67769236,1.6202947,5.31265535,5.31580678,4.57505363,0.09417575,0.82132863,1.06235223,1.47566381,-0.98403807,-0.55367055,-0.06619805,1.05889562,0.94749619,1.4462239,-0.82575137,1.81650112,1.69393505,-0.50636279,-0.38058631,-0.38115383,-0.28339066,0.02493915,-0.08373125,1.38452495,-0.01616468,0.5839239,1.3074927,-0.12853191,1.95446989,-0.51831303,0.56786057,0.78366344,2.28102814,1.70327953,-0.34011586,-0.38891879,-0.38891879,-0.31460238,0.69192088,-0.14674832,1.21164145,-0.16154233,0.74865022,1.49296323,-0.08883207,1.4747889,-0.41843723,0.58222621,0.56613175,1.87400862,1.67513806,-0.27380067,-0.21605136,-0.21685638,-0.12251433,0.0310034,0.04648352,0.60668838,-0.19738641,0.80700148,1.28186932,-0.10891574,1.3434002,-0.32644551,0.57091916,0.51084989,1.75807871,1.66664503,-0.15264277,-0.2966544,-0.29665439,-0.18298142,0.02726963,0.33640392,0.46980638,-0.33200365,1.71883422,2.34222495,-0.00543134,1.85421563,-0.40626715,0.76359548,0.60093312,1.86782826,1.6850769,0.75551959,0.61185085,0.61281902,0.77107876,0.05504225,0.83392616,1.30531808,0.11927163,1.80383548,2.35012493,0.11102919,2.12662138,0.76019262,1.52140581,0.87453483,2.35768973]]

new_saver = tf.train.import_meta_graph(model_path + ".meta")

with tf.Session() as sess:
    # Initialize variables
    # sess.run(tf.initialize_all_variables())

#     saver.restore(sess, model_path)
    new_saver.restore(sess, './tmp2/model.ckpt')

#     #test random sample from validation test
    # prob_test = X[20].reshape((1,validation_features[0].shape[0]))
    prob_test = a
#     prob_value = prob.eval(feed_dict={ x:prob_test})
    prob_value = sess.run("prob:0", feed_dict={'xa:0':prob_test})
    print('probability test', prob_value)

    prob_value = sess.run("prob:0", feed_dict={'xa:0':prob_test})
    print('probability test', prob_value)

    prob_value = sess.run("prob:0", feed_dict={'xa:0':prob_test})
    print('probability test', prob_value)

    prob_value = sess.run("prob:0", feed_dict={'xa:0':prob_test})
    print('probability test', prob_value)

    prob_value = sess.run("prob:0", feed_dict={'xa:0':prob_test})
    print('probability test', prob_value)

    prob_value = sess.run("prob:0", feed_dict={'xa:0':prob_test})
    print('probability test', prob_value)

    prob_value = sess.run("prob:0", feed_dict={'xa:0':prob_test})
    print('probability test', prob_value)

