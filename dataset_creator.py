# -*- coding: utf-8 -*-
"""
Created on Wed Aug 01 15:29:47 2018
@author: nikhil.kondabala & john lyons


Generate dataset for training auto-flagger machine learning algorithm-->save as .csv file that's used by network.py

"""

#%%
from class_mettower_v2_python3 import mettower
import pandas as pd
import numpy as np
import pyodbc
from matplotlib.pyplot import (figure,plot, subplot, title, imshow, xticks, yticks, 
                               show, cm,close,legend,scatter,xlabel,ylabel,hist,boxplot,
                               xlim,ylim,contour,pie,axis)
import sqlalchemy
from sqlalchemy import create_engine
import time

cnxn = pyodbc.connect(driver='{SQL Server}', server='APEX-GIS\WINDRESOURCE', database='WTDMS',
               trusted_connection='yes')
cursor = cnxn.cursor()

'''
NK: 200years of data?
workbench option ideas:
    import specified percentage of all given mettowers (2% or X amount of observations per anemo)
    import specified number of towers
    time and space distribution:
        space will be handled by 
        randomly choose start date for each tower?
        assure that across all mettowers, there is ~equal distribution across months & days for data
 
'''

#%% get list of tower IDs and names

conn= pyodbc.connect(r'DRIVER={SQL Server Native Client 11.0};SERVER=apex-gis\windresource;DATABASE=AssetDB;Trusted_Connection=yes')       
cursor = conn.cursor()
#datasql = "select id, name, elevation, lat, long from DataAsset"

datasql = "select id, name from DataAsset"
cursor.execute(datasql)
data = cursor.fetchall()
column = [column[0] for column in cursor.description]
columnlist = column
everything_else = [x for x in data]
data_sensor_array2 = np.array(everything_else)#,dtype = np.float64)        

df=pd.DataFrame(data_sensor_array2,columns=columnlist)

number_of_towers = len(df)

#%% time scales

#how much total data to build
target_yr=200

r=target_yr*365*24*60

#number of 10min observations per tower to extract for dataset to meet target_yr
obs=int(np.round(r/number_of_towers))


#%%

#initialize
ex_time=[]
error_towers=[]

data_anemos1=[]
fill=[]


for i,x in enumerate(np.asarray(df.id)):
    start_time = time.time()
    print('------------execution is %.2f %% done------------'%(i/number_of_towers*100))
    
    try:
        tower = mettower(int(x)) # met tower intialization
    #tower.sensorlist # list of sensors 
    #tower.slist # list of sensor objects    
        data = tower.data_sensor_array # data of all the sensors 
        #cleaning data by removing nans from troublesome columns based on tower 1058 analysis
#        data=data[~np.isnan(data[:,np.r_[0:31,34:36]]).any(axis=1)]
        
        timestamp = tower.data_time_array # data of all the timestamps
        anemos = []
        for s in tower.slist: # list of all the anemos of the tower
            if s.sensortype == 'Anemometer':
                anemos.append(s)
            
        # random starting element number of tower's time series.  Subtracting obs ensures that will not sample beyond amount of elements 
        start=np.random.randint(len(data)-obs)  
    
    except:
        print('unknown error on %i'%(int(x)))
        error_towers.append(int(x))
    else:                   
        for a in anemos:
            
            ws=data[start:(start+obs),a.Avgid]
            ws_sd=data[start:(start+obs),a.SDid]
            
            temp_id = tower.slist[a.tempsen_idx]
            temp = data[start:(start+obs),temp_id.Avgid]
            
            vane_id = tower.slist[a.vanesenn_idx]
            vane_sd = data[start:(start+obs),vane_id.SDid]
            
            data_tower_flag = tower.flagdata
            
            # following line is possible source of runtime errors...i think for flagged events, only including start/end time instead of every timestep
            flags = np.asarray(a.get_flagcolumn_bytype(timestamp,data_tower_flag)).ravel() # this is a df
            flags=flags[start:(start+obs)]
            
            data_anemo=np.concatenate([[flags,ws,ws_sd,temp,vane_sd]],axis=1).T
            
            data_anemos1.append(data_anemo)
                    
        #turn list into matrix
        data_anemos2=np.array(data_anemos1)    
        
        #concatenate along 3rd dimension
        data_anemos=np.vstack(data_anemos2)
        
        #fill=flag datafill logging array for towers
        f = data_anemos[:,0]!=1
        fill.append(float(f.sum())/float(len(f))*100)
        #print('%.2f%% of data had flags' %(float(f.sum())/float(len(f))*100))
        
        # timing : execution end
        ex_time.append((time.time() - start_time)/60)
        print("--- tower took %s minutes ---" % ex_time)

np.savetxt("NN_Vxxxx_training_data.csv", data_anemos, delimiter=",",)


#%% write training dataset to sql
    
#Techdashengine = create_engine('mssql+pyodbc://Techdash') # Connecting to the database with the computer DSN 
#Techdashengine.connect() #connecting to the database 
#
## limit based on sp_prepexec parameter count
#tsql_chunksize = 2097 // len(df2.columns)
## cap at 1000 (limit for number of rows inserted by table-value constructor)
#tsql_chunksize = 1000 if tsql_chunksize > 1000 else tsql_chunksize
#
#
#data_anemo.to_sql( con= Techdashengine, name = 'JTL_flagtraining', if_exists='replace',index=False, chunksize=tsql_chunksize)

