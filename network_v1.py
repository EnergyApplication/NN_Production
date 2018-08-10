'''
started by the honorable Marko K.

continued by john L. on 8/1/18
'''

import numpy as np
import pandas as pd
import os
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn import preprocessing
from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder
#import pyodbc
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)

def clean_and_scale(dataset_):
    # define X (feature dataset) 
    x_values = dataset_[:,1:].astype(float)    
    
    #handles nan, +inf, and -inf values
    x_values=np.nan_to_num(x_values)
    
    #standardize features 
    X_ = preprocessing.scale(x_values)    
        
    # define Y (response variable)
    y_values = dataset_[:,0]
    Y_= np.nan_to_num(y_values)
    Y_types=np.unique(Y_)
    return X_,Y_,Y_types

# define NN model parameters-->train model-->save model in "model_path"
def baseline_model(X_,Y_,Y_types):
    
    #encode class values as integers
    encoder = LabelEncoder()
    encoder.fit(Y_)
    encoded_Y = encoder.transform(Y_)

    # convert integers to dummy variables (i.e. one hot encoded)
    dummy_y = np_utils.to_categorical(encoded_Y)

    model = Sequential()
    #defining number of nodes in 1st hidden layer (using "rectifier" activation function) and shape of input feature matrix.  NOTE: 10units is arbitrary & non optimal-->should run CV loop to determine best
    model.add(Dense(100, input_dim = 4 , activation = 'relu'))
    
#    defining 2nd hidden layer.  Use "rectifier" activation function.  NOTE: 10units is arbitrary & non optimal-->should run CV loop to determine best
    model.add(Dense(100, activation='relu'))
#    model.add(Dense(1, activation='sigmoid')) # Needs to be 2 for softmax, any other classifier uses 1 node
    
    #output layer.  Use 'softmax' for multi-class (eg beyond binary) categorical classifcation 
    #14 categories (13 flag types + "1" for unflagged)
    #model needs to have one-hot-encoded array of class types (dummy_y)
    model.add(Dense(len(Y_types), activation='softmax')) # Needs to be 2 for softmax, any other classifier uses 1 node

    model.compile(loss = 'categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

#    Epochs (nb_epoch) is the number of times that the model is exposed to the training dataset.
#    Batch Size (batch_size) is the number of training instances shown to the model before a weight update is performed.

    #One epoch involves exposing each pattern in the training dataset to the model.
    #One epoch is comprised of one or more batches.
    #One batch involves showing a subset of the patterns in the training data to the model and updating weights.
    #The number of patterns in the dataset for one epoch must be a factor of the batch size (e.g. divide evenly).

    model.fit(X_,dummy_y,epochs = 5, batch_size = 100)
    model.save(os.path.join(model_path,model_name))
    
    # "KerasClassifier" is model suggested by Keras literature for multi-class classification...
    #...however due to bug, it's not easy to save trained model...thus just using the above "model.fit(X,Y)" for now in order to save
#    classifier = KerasClassifier(build_fn=model, epochs=1, batch_size=5)    
    
    return model


# the following line is special python command --> if this module is run, then _name_ is set to _main_...if _name_ being imported from another module, _name will be set to that module's name (not "_main_")
if __name__ == '__main__':
    #"os" package provides way of using operating system dependent functionality
    root          = os.path.dirname(os.path.realpath(__file__))
    #%% if uploading training from csv    
    
    #upload .csv training data as dataframe to be used in baseline_model
    training      = os.path.join(root, "training")
    data_file_    = os.path.join(training,'NN_V3_training_data.csv')
    
    #%% if uploading training from SQL
#    conn2= pyodbc.connect(r'DRIVER={SQL Server Native Client 11.0};SERVER=ace-ra-sql1;DATABASE=GIS_TechDash;Trusted_Connection=yes')       
#    cursor2 = conn2.cursor()
#    cursor2.execute("select * from JTL_flag_trainingv1")
#    data2 = cursor2.fetchall()
#    column2 = [column[0] for column in cursor2.description]
#    columnlist2 = column2
#    everything_else2 = [x for x in data2]
#    data_sensor_array2 = np.array(everything_else2)#,dtype = np.float64)        
#    data_file_=pd.DataFrame(data_sensor_array2,columns=columnlist2)
    #%%
    
    #path and filename for model trained in baseline_model
    model_path    = os.path.join(root, "model")
    model_name    = os.path.basename(root) + "Vxxxx_model.h5"

    dataframe_    = pd.read_csv(data_file_, header=None)
#    dataframe_    = dataframe_[0:10000,:]
    dataset_      = dataframe_.values

    X_, Y_,Y_types       = clean_and_scale(dataset_)
    simple_model = baseline_model(X_,Y_,Y_types)
    
#    print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))    
    print("Training Finished")
