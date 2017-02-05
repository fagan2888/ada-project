# This code uses the player generated features to train a neural network to make predictions on match outcome
 
 Here is a brief summary of some key points:
 
 * The neural net is coded using TensorFlow in the Neural_Network.ipynb file
 * The input to the model is the features of each player in the match
 * Each player feature for each role in each team is always in the same place in the input layer 
 * The model is saved in the finalmodel folder
 * The Neural Net has 1 hidden layer of 110 neurons
 * We use L2 regularization and dropout rate of 0.5 when training
