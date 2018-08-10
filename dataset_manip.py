# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 18:02:09 2018

@author: john.lyons


Manipulate dataset from dataset_creator to adjust flagtype distribution, etc


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
from class_mettower_v2_python3 import mettower
from network_v1 import *

from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score

from matplotlib.pyplot import (figure,plot, subplot, title, imshow, xticks, yticks, 
                               show, cm,close,legend,scatter,xlabel,ylabel,hist,boxplot,
                               xlim,ylim,contour,pie,axis,matshow,subplots)




#%%

ddd=pd.read_csv(r'C:\Users\john.lyons\Documents\GitHub\NN_Production\training\NN_V2_training_data.csv')

#%%  adjust dataset distribution so that have less counts of flagtype=1 ("unflagged")-->greatly save on training time to facilitate NN model versioning

flag_counts=[]
flag_types=np.unique(ddd.iloc[:,0])
for i,x in enumerate(flag_types):
    flag_counts.append(ddd.iloc[:,0].value_counts()[x])

# mean of flag counts across all types excluding unflagged type (since it has outlyingly high counts within dataset)
avg_amt=int(np.mean(flag_counts[1:]))

# ensure that flagtype=1 is first in list so that only remove rows of its type in later line
ddd1=ddd.sort_values(by=ddd.columns[0])

# reduce dataset size by reducing flagtype=1 to only include the average amount of flag counts across all types
ddd3=ddd1.iloc[(flag_counts[0]-int(avg_amt)):,:]

# save to numpy matrix to allow for more efficient saving
ddd4=np.asarray(ddd3)

np.savetxt("NN_Vxxxx_training_data.csv", ddd4, delimiter=",",)

#%%

df=pd.DataFrame({'flag_type':flag_types,'flag_counts':flag_counts})

flag_counts2=flag_counts
flag_counts2[0]=avg_amt

df2=pd.DataFrame({'flag_type':flag_types,'flag_counts':flag_counts2})


close('all')
figure()
hist(ddd.iloc[:,0])
title('200yr random dataset across all towers: unmanipulated flag type distribution')
xlabel('flag type'),ylabel('counts')

figure()
hist(ddd3.iloc[:,0])
title('200yr random dataset across all towers: unflagged counts reduced to avg')
xlabel('flag type'),ylabel('counts')

