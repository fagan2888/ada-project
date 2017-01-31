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
seed = 42
validation_size = 750
feature_count = df.shape[1] - 2

#feed forward neural net
n_nodes_hl1 = 10
n_nodes_hl2 = 0
n_nodes_hl3 = 0

#cycles of feed forward + backprop on all K-folded samples
hm_epochs = 500

n_classes = 2

model_path = "./tmp2/model.ckpt"
save_dir = './tmp2/'

x = tf.placeholder('float', [None, feature_count], name = 'xa')
y = tf.placeholder('float', [None, n_classes], name='ya')
dropout_prob = tf.placeholder('float', (), name = 'dropout_prob')



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

# def neural_network_model(data):



    # return output, regularizers, ret

def display_stat(x_range, trains, tests, vals, acc_0s, acc_1s):

    #plt.plot(x_range, trains,'-b', label='Training acc')
    #plt.plot(x_rang±ange, tests,'-y', label='Test acc')
    plt.plot(x_range, acc_0s,'-r', label='Acc Class 0')
    plt.plot(x_range, acc_1s,'-k', label='Acc Class 1')

    plt.legend(loc='lower right', frameon=False)
    plt.ylim(ymax = 1.1, ymin = 0.0)

    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.show()


def train_neural_network_CV(x, lambda_):

    data = x

    # dropout_prob = 0.5

    hidden_1_layer = {
        'weights': tf.Variable(tf.truncated_normal([feature_count, n_nodes_hl1], stddev=0.1, seed=seed), name="h1_weights"),
        # 'weights': tf.Variable(tf.zeros([feature_count, n_nodes_hl1]), name="h1_weights"),
        'biases': tf.Variable(tf.constant(1.0, shape=[n_nodes_hl1]), name="h1_biases")
    }
    hidden_2_layer = {
        'weights': tf.Variable(tf.truncated_normal([n_nodes_hl1, n_nodes_hl2], stddev=0.1, seed=seed), name="h2_weights"),
        'biases': tf.Variable(tf.constant(1.0, shape=[n_nodes_hl2]), name="h2_biases")
    }

    hidden_3_layer = {
        'weights': tf.Variable(tf.truncated_normal([n_nodes_hl2, n_nodes_hl3], stddev=0.1, seed=seed), name="h3_weights"),
        'biases': tf.Variable(tf.constant(1.0, shape=[n_nodes_hl3]), name="h3_biases")
    }
    output_layer = {
        'weights': tf.Variable(tf.truncated_normal([n_nodes_hl1, n_classes], stddev=0.1, seed=seed), name="o_weights"),
        # 'weights': tf.Variable(tf.zeros([n_nodes_hl1, n_classes]), name="o_weights"),
        'biases': tf.Variable(tf.constant(1.0, shape=[n_classes]), name="o_biases")
    }

    l1 = tf.add(tf.matmul(data, hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu6(l1)

    l1_drop = tf.nn.dropout(l1, dropout_prob, seed=seed)


    l2 = tf.add(tf.matmul(l1_drop, hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu6(l2)

    l2_drop = tf.nn.dropout(l2, dropout_prob, seed=seed)

    l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.sigmoid(l3)

    l3_drop = tf.nn.dropout(l3, dropout_prob, seed=seed)


    ret = [hidden_1_layer['weights'], hidden_1_layer['biases'], output_layer['weights'], output_layer['biases']]

    output = tf.matmul(l1_drop, output_layer['weights']) +  output_layer['biases']

    regularizers = (tf.nn.l2_loss(hidden_1_layer['weights']) + tf.nn.l2_loss(hidden_1_layer['biases']) +
                                tf.nn.l2_loss(output_layer['weights']) + tf.nn.l2_loss(output_layer['biases']))

    vals = []
    trains = []
    tests = []
    x_range = []

    f1_vals = []

    acc_1s = []
    acc_0s = []

    # prediction, regularizers, to_save = neural_network_model(x)
    prediction, regularizers, to_save =  output, regularizers, ret

    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(prediction, y))
    #log_loss = tf.contrib.losses.log_loss(predictions=prediction, labels=y)

    #Eval this to get probability of [winning,losing]
    prob = tf.nn.softmax(prediction, name="prob")

    #learning rate can be passed
    optimizer = tf.train.AdamOptimizer(1e-4).minimize(cost + lambda_ * regularizers)

    #metrics
    correct_prediction = tf.equal(tf.argmax(prediction,1), tf.argmax(y,1))
    false_prediction = tf.logical_not(correct_prediction)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))

    #use for f1 score if needed
    true_positives = tf.reduce_sum(tf.to_int32(tf.logical_and(correct_prediction, tf.equal(tf.argmax(tf.nn.softmax(y),1), True) )))
    false_positives = tf.reduce_sum(tf.to_int32(tf.logical_and(false_prediction, tf.equal(tf.argmax(tf.nn.softmax(y),1), True) )))
    true_negatives = tf.reduce_sum(tf.to_int32(tf.logical_and(correct_prediction, tf.equal(tf.argmax(tf.nn.softmax(y),1), False) )))
    false_negatives = tf.reduce_sum(tf.to_int32(tf.logical_and(false_prediction, tf.equal(tf.argmax(tf.nn.softmax(y),1), False) )))

    #acc for each class
    class_0 = tf.where(tf.equal(tf.argmax(y, 1), 0))
    class_0 = tf.reshape(class_0, [tf.shape(class_0)[0]])
    pred_0 = tf.gather(prediction, class_0)
    y_0 = tf.gather(y, class_0)
    class_0_correct = tf.equal(tf.argmax(pred_0,1), tf.argmax(y_0,1))
    acc_0 = tf.reduce_mean(tf.cast(class_0_correct, 'float'))

    class_1 = tf.where(tf.equal(tf.argmax(y, 1), 1))
    class_1 = tf.reshape(class_1, [tf.shape(class_1)[0]])
    pred_1 = tf.gather(prediction, class_1)
    y_1 = tf.gather(y, class_1)
    class_1_correct = tf.equal(tf.argmax(pred_1,1), tf.argmax(y_1,1))
    acc_1 = tf.reduce_mean(tf.cast(class_1_correct, 'float'))

    display_step = 1

    saver = tf.train.Saver(to_save)

    with tf.Session() as sess:
        sess.run(tf.initialize_all_variables())

        for epoch in range(hm_epochs):
            #epoch_loss = 0
            fold_index = 0

            kf = KFold(n_splits=5, random_state=seed, shuffle=True)
            for train_index, test_index in kf.split(train_features, train_labels):
                fold_index += 1
                X_train, X_test = train_features[train_index], train_features[test_index]
                y_train, y_test = train_labels[train_index], train_labels[test_index]

                _, c = sess.run([optimizer, cost], feed_dict = {x: X_train, y: y_train, dropout_prob: 0.5})

                # a = [[1.6804181,0.49852886,4.68621827,4.68621826,4.50822828,0.03580143,-0.10327194,1.11961983,1.16662829,-2.59213006,-2.15577311,-0.32022004,0.87494358,-0.3034381,0.44390429,-0.9642744,1.7493962,1.67095743,0.69076133,4.4399695,4.44861103,4.26084272,0.03987201,-0.14456116,0.90806216,0.81786188,-2.50698302,-2.00234836,-0.22628798,0.6579448,-0.17845283,0.47368511,-0.80479309,1.408297,1.64860553,0.70200482,4.72736236,4.72736237,4.44769614,0.03626145,0.04033567,0.33755175,0.75715305,-2.45430391,-2.00318108,-0.22711913,0.56923335,-0.09720827,0.45787225,-0.78624504,1.29222884,1.67716915,0.87944803,4.48648949,4.48648951,4.36315752,0.03896885,0.33587276,0.20004711,0.95438807,-1.26753452,-1.01436325,-0.18031334,0.8690158,-0.19019017,0.6512756,-0.7698582,1.43403969,1.67769236,1.6202947,5.31265535,5.31580678,4.57505363,0.09417575,0.82132863,1.06235223,1.47566381,-0.98403807,-0.55367055,-0.06619805,1.05889562,0.94749619,1.4462239,-0.82575137,1.81650112,1.69393505,-0.50636279,-0.38058631,-0.38115383,-0.28339066,0.02493915,-0.08373125,1.38452495,-0.01616468,0.5839239,1.3074927,-0.12853191,1.95446989,-0.51831303,0.56786057,0.78366344,2.28102814,1.70327953,-0.34011586,-0.38891879,-0.38891879,-0.31460238,0.69192088,-0.14674832,1.21164145,-0.16154233,0.74865022,1.49296323,-0.08883207,1.4747889,-0.41843723,0.58222621,0.56613175,1.87400862,1.67513806,-0.27380067,-0.21605136,-0.21685638,-0.12251433,0.0310034,0.04648352,0.60668838,-0.19738641,0.80700148,1.28186932,-0.10891574,1.3434002,-0.32644551,0.57091916,0.51084989,1.75807871,1.66664503,-0.15264277,-0.2966544,-0.29665439,-0.18298142,0.02726963,0.33640392,0.46980638,-0.33200365,1.71883422,2.34222495,-0.00543134,1.85421563,-0.40626715,0.76359548,0.60093312,1.86782826,1.6850769,0.75551959,0.61185085,0.61281902,0.77107876,0.05504225,0.83392616,1.30531808,0.11927163,1.80383548,2.35012493,0.11102919,2.12662138,0.76019262,1.52140581,0.87453483,2.35768973]]

                # prob_test = a
                # prob_value = sess.run(prob, feed_dict={x:prob_test, dropout_prob: 1})
                # print('probability test', prob_value)


                # prob_value = sess.run(prob, feed_dict={x:prob_test, dropout_prob: 1})
                # print('probability test', prob_value)
                #epoch_loss += c

                train_accuracy = accuracy.eval(feed_dict={ x: X_train, y: y_train, dropout_prob: 1})
                test_accuracy = accuracy.eval(feed_dict={ x: X_test, y: y_test, dropout_prob: 1})

                # increase display_step after 10 iteration of same decimal
                if epoch%(display_step*10) == 0 and epoch:
                       display_step *= 10

                if (epoch%display_step == 0 or (epoch+1) == hm_epochs) and fold_index == 5:
                    print('train:%.4f, test:%.4f,  epoch %d, fold %d' % (train_accuracy, test_accuracy, epoch, fold_index))

                    #if (fold_index == kf.n_splits):
                    validation_accuracy = accuracy.eval(feed_dict={ x: validation_features, y: validation_labels, dropout_prob: 1})
                    print ('val:%.2f' % (validation_accuracy))

                    tp = true_positives.eval(feed_dict={ x: validation_features, y: validation_labels, dropout_prob: 1})
                    fp = false_positives.eval(feed_dict={ x: validation_features, y: validation_labels, dropout_prob: 1})
                    fn = false_negatives.eval(feed_dict={ x: validation_features, y: validation_labels, dropout_prob: 1})

                    precision = float(tp) / float(tp+fn + 0.0000000000001)
                    recall = float(tp) / float(tp + fn + 0.0000000000001)
                    F1_val = 2 * ( precision * recall ) / ( precision + recall + 0.0000000000001 )

                    x_range.append(epoch)
                    vals.append(validation_accuracy)
                    trains.append(train_accuracy)
                    tests.append(test_accuracy)
                    f1_vals.append(F1_val)

                    #print(validation_labels)
                    #print(class_1.eval(feed_dict={ x: validation_features, y: validation_labels})  )

                    acc_1s.append(acc_1.eval(feed_dict={ x: validation_features, y: validation_labels, dropout_prob: 1}))
                    acc_0s.append(acc_0.eval(feed_dict={ x: validation_features, y: validation_labels, dropout_prob: 1}))

        a = [[1.6804181,0.49852886,4.68621827,4.68621826,4.50822828,0.03580143,-0.10327194,1.11961983,1.16662829,-2.59213006,-2.15577311,-0.32022004,0.87494358,-0.3034381,0.44390429,-0.9642744,1.7493962,1.67095743,0.69076133,4.4399695,4.44861103,4.26084272,0.03987201,-0.14456116,0.90806216,0.81786188,-2.50698302,-2.00234836,-0.22628798,0.6579448,-0.17845283,0.47368511,-0.80479309,1.408297,1.64860553,0.70200482,4.72736236,4.72736237,4.44769614,0.03626145,0.04033567,0.33755175,0.75715305,-2.45430391,-2.00318108,-0.22711913,0.56923335,-0.09720827,0.45787225,-0.78624504,1.29222884,1.67716915,0.87944803,4.48648949,4.48648951,4.36315752,0.03896885,0.33587276,0.20004711,0.95438807,-1.26753452,-1.01436325,-0.18031334,0.8690158,-0.19019017,0.6512756,-0.7698582,1.43403969,1.67769236,1.6202947,5.31265535,5.31580678,4.57505363,0.09417575,0.82132863,1.06235223,1.47566381,-0.98403807,-0.55367055,-0.06619805,1.05889562,0.94749619,1.4462239,-0.82575137,1.81650112,1.69393505,-0.50636279,-0.38058631,-0.38115383,-0.28339066,0.02493915,-0.08373125,1.38452495,-0.01616468,0.5839239,1.3074927,-0.12853191,1.95446989,-0.51831303,0.56786057,0.78366344,2.28102814,1.70327953,-0.34011586,-0.38891879,-0.38891879,-0.31460238,0.69192088,-0.14674832,1.21164145,-0.16154233,0.74865022,1.49296323,-0.08883207,1.4747889,-0.41843723,0.58222621,0.56613175,1.87400862,1.67513806,-0.27380067,-0.21605136,-0.21685638,-0.12251433,0.0310034,0.04648352,0.60668838,-0.19738641,0.80700148,1.28186932,-0.10891574,1.3434002,-0.32644551,0.57091916,0.51084989,1.75807871,1.66664503,-0.15264277,-0.2966544,-0.29665439,-0.18298142,0.02726963,0.33640392,0.46980638,-0.33200365,1.71883422,2.34222495,-0.00543134,1.85421563,-0.40626715,0.76359548,0.60093312,1.86782826,1.6850769,0.75551959,0.61185085,0.61281902,0.77107876,0.05504225,0.83392616,1.30531808,0.11927163,1.80383548,2.35012493,0.11102919,2.12662138,0.76019262,1.52140581,0.87453483,2.35768973]]

        prob_test = a
        prob_value = prob.eval(feed_dict={'xa:0':prob_test, dropout_prob: 1})
        print('probability test', prob_value)

        prob_value = prob.eval(feed_dict={'xa:0':prob_test, dropout_prob: 1})
        print('probability test', prob_value)


        save_path = saver.save(sess, model_path)

        display_stat(x_range, trains, tests, vals, acc_0s, acc_1s)

model_path = "./tmp2/model.ckpt"
save_dir = './tmp2/'
if not os.path.isdir(save_dir):
    os.mkdir(save_dir)


L2_lambda_ = 1.5e-3
train_neural_network_CV(x, L2_lambda_)
