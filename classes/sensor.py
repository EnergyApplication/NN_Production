
class sensor:
    """" this is a sensor class
        we intend to use it to initialize a sensor and get the data from it
        we would initialize this from a met tower class
        and set data from the met tower import data file.

        """

    def __init__(self,i,columnlist, sensorlist, sensorid, name, height, sensortype, make, tag):
        # essentially assigning the values which we get from the database into a class

        self.i = i
        self.sensorlist = sensorlist
        self.sensorid = sensorid
        self.name = name
        self.height = height
        self.sensortype = sensortype
        self.make = make
        self.tag = tag
        # creating the name of the sensor based on the database standard
        self.Avg = name+'_Avg'
        self.SD = name+'_SD'
        self.Max = name+'_Max'
        self.Min = name+'_Min'
        self.Flag = name+'_Flag'
        #getting the column values from the database and assigning them to the instance
        self.Avgid = columnlist.index(self.Avg)-1
        self.SDid = columnlist.index(self.SD)-1
        self.Maxid = columnlist.index(self.Max)-1
        self.Minid = columnlist.index(self.Min)-1
        self.Flagid = columnlist.index(self.Flag)-1
        #getting the index value of the temparature , colocated , barometer, vane sensors
        #this index is the index with in sensor table as it is imported
        self.coloc_idx = self.colocatedsen(i,sensorlist, height, sensortype)
        self.tempsen_idx = self.tempsen(i,sensorlist, height, sensortype)
        self.barsen_idx  = self.barsen(i,sensorlist, height, sensortype)
        self.vanesen_idx = self.vanesen(i,sensorlist, height, sensortype)


    def colocatedsen(self,i, sensorlist, height, sensortype):
        senheight_diff = [abs(sen[2]- sensorlist[i][2]) for sen in sensorlist]
        sen_itr = zip(range(len(senheight_diff)), senheight_diff, [ sen[3] for sen in sensorlist])
        for idx, sen in enumerate(sen_itr):
            if (idx != i) and (sen[2]== sensortype) and (sen[1]<2):
                return (idx)


    def tempsen(self,i, sensorlist, height, sensortype):
        senheight_diff = [abs(sen[2]- sensorlist[i][2]) for sen in sensorlist]
        sen_ = zip(range(len(senheight_diff)), senheight_diff, [ sen[3] for sen in sensorlist])
        sen_itr = sorted(sen_, key = lambda sen: sen[1])
        #return sen_itr
        for sen in sen_itr:
            if (sen[0]!= i) and (sen[2]== 'Temperature'):
                return (sen[0])

    def barsen(self,i, sensorlist, height, sensortype):
        senheight_diff = [abs(sen[2]- sensorlist[i][2]) for sen in sensorlist]
        sen_ = zip(range(len(senheight_diff)), senheight_diff, [ sen[3] for sen in sensorlist])
        sen_itr = sorted(sen_, key = lambda sen: sen[1])
        #return sen_itr
        for sen in sen_itr:
            if (sen[0] != i) and (sen[2]== 'Barometer'):
                return (sen[0])

    def vanesen(self,i, sensorlist, height, sensortype):
        senheight_diff = [abs(sen[2]- sensorlist[i][2]) for sen in sensorlist]
        sen_ = zip(range(len(senheight_diff)), senheight_diff, [ sen[3] for sen in sensorlist])
        sen_itr = sorted(sen_, key = lambda sen: sen[1])
        #return sen_itr
        for sen in sen_itr:
            if (sen[0] != i) and (sen[2]== 'Wind Vane'):
                return (sen[0])
