# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 11:07:35 2018
@author: john.lyons


Predict for flagtypes for a single tower 

TODO:  one-hot-encode the input towers flag column so that on same scale as the classification model (which was trained on one-hot-encoded list of flag type classes (Keras multi-class model requirement))
        Then decode model's predictions for tower in order to view on scale of the actual numbers associated with the different flagtypes

"""

from data import singletowerMCP
import numpy as np
import pandas as pd
import pyodbc
import os
import csv
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from multiprocessing import Process,Queue,Pipe
from keras.utils import np_utils
from keras.models import load_model
#from data import send_data
from sklearn import preprocessing
from class_mettower_v2 import mettower
from network_v1 import *

from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score

from matplotlib.pyplot import (figure,plot, subplot, title, imshow, xticks, yticks, 
                               show, cm,close,legend,scatter,xlabel,ylabel,hist,boxplot,
                               xlim,ylim,contour,pie,axis,matshow,subplots)

#%%

#initialize
ex_time=[]
error_towers=[]

data_anemos1=[]
fill=[]

start=0
obs=-1

metID=1058

#%%

try:
    
    tower = mettower(metID) # met tower intialization
    #tower.sensorlist # list of sensors 
    #tower.slist # list of sensor objects    
    data = tower.data_sensor_array # data of all the sensors 
    
    timestamp = tower.data_time_array # data of all the timestamps
    anemos = []

    for s in tower.slist: # list of all the anemos of the tower
        if s.sensortype == 'Anemometer':
            anemos.append(s)
except:
    print('unknown error on %i'%(int(metID)))
else:
    for a in anemos:
    #    print(a)
        ws=data[start:(start+obs),a.Avgid]
        ws_sd=data[start:(start+obs),a.SDid]
        
        temp_id = tower.slist[a.tempsen_idx]
        temp = data[start:(start+obs),temp_id.Avgid]
        
        vane_id = tower.slist[a.vanesenn_idx]
        vane = data[start:(start+obs),vane_id.SDid]
        
        data_tower_flag = tower.flagdata
        flags = np.asarray(a.get_flagcolumn_bytype(timestamp,data_tower_flag)).ravel() # this is a df
        flags=flags[start:(start+obs)]
        
        data_anemo=np.concatenate([[flags,ws,ws_sd,temp,vane]],axis=1).T
        data_anemos1.append(data_anemo)    
        
    #turn list into matrix
    data_anemos2=np.array(data_anemos1)    
    
    #concatenate along 3rd dimension
    data_anemos=np.vstack(data_anemos2)
    
    #fill=flag datafill logging array for towers
    f = data_anemos[:,0]!=1
    
    # need to change in case of no flags (div by zero)
    fill.append(float(f.sum())/float(len(f))*100)

#%%

X,y,y_types=clean_and_scale(data_anemos)

#%%

simple_model           = load_model(r'C:\Users\john.lyons\Documents\GitHub\NN_Production\model\NN_ProductionVxxxx_model.h5')


#%%

## fix random seed for reproducibility
#seed = 7
#numpy.random.seed(seed)
#
#kfold = KFold(n_splits=10, shuffle=True, random_state=seed)
#
#results = cross_val_score(simple_model, X, y, cv=kfold)
#
#print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

#predictions  = simple_model.predict(X)
#       OR
predictions  = simple_model.predict_classes(X)

#%%

from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder


#encode class values as integers
encoder = LabelEncoder()
encoder.fit(y)
encoded_Y = encoder.transform(y)

# convert integers to dummy variables (i.e. one hot encoded)
dummy_y = np_utils.to_categorical(encoded_Y)

figure()
plot(predictions)
plot(encoded_Y)

tally=np.count_nonzero([encoded_Y==predictions])
