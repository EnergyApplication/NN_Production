import numpy as np
import pandas
import pyodbc
import os
import csv
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from multiprocessing import Process,Queue,Pipe
from keras.utils import np_utils
from keras.models import load_model
from data import send_data
from sklearn import preprocessing


def update_sql_flags(output, sensor_id, tower_id, network_id):
      
    #write results vs actual results for each sensor on each tower
    for o in output:
        prediction = str(o[0])
        timestamp  = str(o[1])
        actual     = str(o[2])
        sensor_id  = str(d['sensor_id'])
        tower_id   = str(tower_id)
        network_id = str(network_id)
        sql        = "INSERT INTO [AssetDB].[dbo].[NN_V1] (prediction, actual, ts, sensor_id, tower_id, network_id) VALUES (" + prediction + "," + actual + "," + "'" + timestamp + "'" + "," + sensor_id + "," + tower_id + "," + network_id + ")"
        cursor.execute(sql)


cnxn          = pyodbc.connect(driver='{SQL Server}', server='APEX-GIS\WINDRESOURCE', database='WTDMS',
               trusted_connection='yes')

root          = os.path.dirname(os.path.realpath(__file__))
csv_path      = os.path.join(root, 'accuracy')
csv_file      = os.path.basename(root) + '_results.csv'
model_path    = os.path.join(root, "model")
model_name    = os.path.basename(root) + "_model.h5"

 
#load the NN model trained by "network.py"-->predict flag-->output and write "accuracy" to csv  
if __name__ == '__main__':
    #jtl:added following line due to spyder issue using python 3.6+...will get error & early termination if don't include
    __spec__ = None
    
    simple_model           = load_model(os.path.join(model_path,model_name))
    
    #Pipe is a method of different multiprocesses/functions to share data (queue is another method of sharing data between functions via a shared memory) 
    parent_conn,child_conn = Pipe()
    
    #multiprocess the send_data funciton with this module's main code.  Multiprocessing allows computer to surpass memory management safeguard (global interpreter lock (GIL), only allows for ~16% of CPU to be used by Python)
    # args is passing the child_conn back to the function send_data (if only 1 argument, need to follow by a comma)
    p                      = Process(target=send_data, args=(child_conn,))
    # starts the multiprocess.  since no p.join() in script, the processes are run irrespective of eachother
    p.start()
    
    # .recv() is allowing for transfer (receiving) of the connection object sent (using ".send") from data.py's "send_data"  
    number_of_towers       = parent_conn.recv()

    csv_list = []

    # predict flag for every observation and build output table of results
    for _ in range(number_of_towers):
        tower = parent_conn.recv()
        if tower[1] == 0:
            p = tower[0]
            data,timestamps,tower_id = p[0],p[1],p[2]
            csv_data = {}
            accuracy = []

            for d in data:
                cursor       = cnxn.cursor()
                X            = d['data']
                #aren't next two steps already accomplished in function "clean_and_scale"?
                X            = np.nan_to_num(X)
                X            = preprocessing.scale(X)
                
                flags        = d['flags']
                predictions  = simple_model.predict(X)
                rounded      = [round(x[0]) for x in predictions]
                output       = list(zip(rounded, timestamps, flags))
                output       = [o for o in output if o[0] != o[2]]
                compare      = list(zip(rounded,flags))
                sensor_id    = d['sensor_id']

                #write updated flags to sql db
                update_sql_flags(output, sensor_id, tower_id, 1)
                cursor.commit()
                cursor.close()

                i = 0
                for row in compare:
                    if row[0] == row[1]:
                        i = i + 1
                #accuracy=matches/total flags
                accuracy.append(i/len(compare))

            csv_data['id'] = tower_id
            csv_data['accuracy'] = accuracy
            csv_list.append(csv_data)

        else:
            print("Bad Data: " + tower[0])

    #try:
    keys_ = csv_list[0].keys()
    
    # outputs the trained neural network's accuracy test results per sensor per tower OR sensor (i think) to a csv
    with open(os.path.join(csv_path, csv_file), 'w') as f:
        w = csv.DictWriter(f, keys_)
        w.writeheader()
        w.writerows(csv_list)
    #except:
        #pass

    print("FINISHED")
