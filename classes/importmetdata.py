import pyodbc
import numpy as np

##
# CONNECT TO THE ASSETDB DATABASE
conn = pyodbc.connect(r'DRIVER={SQL Server Native Client 11.0};SERVER=apex-gis\windresource;DATABASE=AssetDB;Trusted_Connection=yes')

# SET A TOWER NAME YOU WANT TO GET THE DATA FROM
##print 'Please input the tower name you want to import the data from'
##dataassetname = input()

def intialize(dataassetname):
    cursor = conn.cursor()
    cursor.execute("select id, name from DataAsset where name = ?",dataassetname)

    # GET THE ID FOR THE TOWER
    global DataAsset
    DataAsset = cursor.fetchall()
    global DataAssetid
    DataAssetid = DataAsset[0][0]
    #print DataAssetid

    # GET THE SENSOR INFROMATION FOR THE TOWER
    cursor.execute(""" select S.id, s.name, s.height, ST.SensorType,SM.Name, ST.Tag from
    sensor S join SensorMake SM on S.MakeID = SM.ID
    join SensorType ST on ST.ID = SM.SensorType
    where s.DataAssetID = ? """,DataAssetid)
    global Sensor
    Sensor = [list(x) for x in cursor.fetchall()]

    print ("Calling the database, AssetDB for the data from the tower")
    # GET DATA FROM THE TOWER
    datasql = "select * from tower.Flag_"+str(DataAssetid)+" order by Timestamp asc"
    cursor.execute(datasql)
    data = cursor.fetchall()
    global datatime_array
    datetime = [x[0] for x in data]
    datatime_array = np.array(datetime)
    global sensordata_array
    everything_else = [x[1:] for x in data]
    sensordata_array = np.array(everything_else,dtype = np.float64)


    #data = np.array(data)
    print ("got the data for the tower")
    global column
    column = [column[0] for column in cursor.description]

    # GET FLAG-DATA FROM THE TOWER
    print ("Calling the database, AssetDB for the flag data from the tower")
    cursor.execute("select * from windogflags where DataAsset_ID = ?",DataAssetid)
    global flagdata
    flagdata = cursor.fetchall()
    print ("got the flag data for the tower")
