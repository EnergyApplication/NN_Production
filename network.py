'''
started by the honorable Marko K.

continued by john L. on 8/1/18
'''

import numpy as np
import pandas
import os
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn import preprocessing


def clean_and_scale(dataset_):
    # define X (feature dataset) 
    x_values = dataset_[:,0:4].astype(float)
        
    #standardize features 
    x_scaled = preprocessing.scale(x_values)
    #handles nan, +inf, and -inf values
    X_       = np.nan_to_num(x_scaled)
    
    # define Y (response variable)
    y_values = dataset_[:,4]
    Y_       = np.nan_to_num(y_values)
    return X_,Y_

# define NN model parameters-->train model-->save model in "model_path"
def baseline_model(X_,Y_):
    model = Sequential()
    model.add(Dense(8, input_dim = 4 , activation = 'relu'))
    model.add(Dense(6, activation='relu'))
    model.add(Dense(1, activation='sigmoid')) # Needs to be 2 for softmax, any other classifier uses 1 node
    model.compile(loss = 'binary_crossentropy', optimizer = 'adam', metrics = ['accuracy'])
    model.fit(X_,Y_,epochs = 5, batch_size = 10)
    model.save(os.path.join(model_path,model_name))
    return model


# the following line is special python command --> if this module is run, then _name_ is set to _main_...if _name_ being imported from another module, _name will be set to that module's name (not "_main_")
if __name__ == '__main__':
    # use seed to generate pseudo-random number (internal initialization of random number gen) (why?)
    seed      = 7
    np.random.seed(seed)
    
    #write 
    #"os" package provides way of using operating system dependent functionality
    root          = os.path.dirname(os.path.realpath(__file__))
    
    #upload .csv training data as dataframe to be used in baseline_model
    training      = os.path.join(root, "training")
    data_file_    = os.path.join(training,'NN_V1_training_data.csv')
    
    #path and filename for model trained in baseline_model
    model_path    = os.path.join(root, "model")
    model_name    = os.path.basename(root) + "_model.h5"

    dataframe_    = pandas.read_csv(data_file_, header=None)
    dataset_      = dataframe_.values

    X_, Y_       = clean_and_scale(dataset_)
    simple_model = baseline_model(X_,Y_)

    print("Training Finished")
