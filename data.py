# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 16:46:26 2017

@author: nikhil.kondabala
"""

xxd = "python master_prod_1.py / python init_and_train.py"

import os
import sys

root          = os.path.dirname(os.path.realpath(__file__))
classes       = os.path.join(root, 'classes')

sys.path.append(os.path.join(root,classes))

from multiprocessing import Process,Pipe
from mettower import mettower
import importmetdata as imp
import numpy as np
import pyodbc

cnxn = pyodbc.connect(driver='{SQL Server}', server='APEX-GIS\WINDRESOURCE', database='WTDMS',
               trusted_connection='yes')
cursor = cnxn.cursor()


def get_predictedflagvalues(datatoworkon):
    return datatoworkon

def put_flagvaluestodb(flagvalues):
    return 'successfully sent the flag data to the database'

# gets sensor data and flag status for each sensor for each tower-->output table
def singletowerMCP(towername):
    imp.intialize(towername)
    tower      = mettower(imp.DataAssetid,towername,imp.Sensor,imp.column)
    sensors    = tower.slist
    anemos     = [sen for sen in sensors if sen.sensortype == u'Anemometer']
    sen_data   = imp.sensordata_array
    timestamps = imp.datatime_array
    data       = []

    for anemo in anemos:
        sensor_dict = {}

        tower_id  = tower.dataassetid
        sensor_id = anemo.sensorid

        # dataset features
        anemo_coloc          = sensors[anemo.coloc_idx] # colocatd sensor
        anemo_data_avg       = sen_data[:,anemo.Avgid] # anemometer average wind speed data
        anemo_data_sd        = sen_data[:,anemo.SDid] # sd data
        anemo_coloc_data_avg = sen_data[:,anemo_coloc.Avgid] # colocated anemometer data
        temp                 = sensors[anemo.tempsen_idx] # temparature sensor
        anemo_temp_data      = sen_data[:,temp.Avgid] # temparature data
        anemo_flag           = sen_data[:,anemo.Flagid]

        sensor_dict      = {}
        anemodata        = np.column_stack((anemo_data_avg, anemo_data_sd, anemo_data_avg - anemo_coloc_data_avg, anemo_temp_data))
        f                = np.all(np.isfinite(np.column_stack((anemodata, anemo_flag))),axis = 1)
        anemo_flag_check = anemo_flag[f]

        anemo_flag_check[anemo_flag_check < 0] = 1
        anemo_flag_check[anemo_flag_check > 0] = 0

        flags       = list(anemo_flag_check)
        tower_id    = tower.dataassetid
        sensor_id   = anemo.sensorid

        sensor_dict['DataAsset_id'] = tower_id
        sensor_dict['sensor_id']    = sensor_id
        sensor_dict['data']         = np.nan_to_num(anemodata)
        sensor_dict['flags']        = flags

        data.append(sensor_dict)

    return data,timestamps,str(tower_id)



def send_data(child_conn):
    # returns names of all towers
    q      = "SELECT Name FROM [AssetDB].[dbo].[SortRef]"
    towers = [x[0] for x in cursor.execute(q).fetchall()]

    number_of_towers = len(towers)
    
    #communicates through pipe with predict.py, where number_of_towers is received
    child_conn.send(number_of_towers)

    for t in towers:
        try:
        	tower_data = singletowerMCP(t)
        	child_conn.send((tower_data,0))    #sends the tower ID itself through pipe to predict.py?
        except:
            bad_data_tower = (t,1)
            child_conn.send(bad_data_tower)
