from sensor import sensor

class mettower:
    """ This is the main met tower class we will initialize the data and the sensors
        from this class and would be used in later stages of the data analysis
        this is intended to keep the code more readable.
        data structures
        sensorlist = [0-sensorid, 1-sensorname, 2-sensor height, 3-sensor type, 4-sensor make , 5-variable measured]
        """

    def __init__(self,dataassetid, name, sensorlist, columnlist):
        self.dataassetid = dataassetid
        self.name = name
        self.sensorlist = sensorlist
        self.columnlist = columnlist
        self.slist = []
        for idx, i in enumerate(sensorlist):
            s = sensor(idx,self.columnlist,self.sensorlist, *list(i) )
            self.slist.append(s)

        primaryanemoindex = self.getprimaryanemo(sensorlist, self.slist)
        self.primaryanemo = self.slist[primaryanemoindex]



    def getprimaryanemo(self, sensorlist, slist):
        p = []
        for i, sen in enumerate(sensorlist):
            p.append([i, sen[2], sen[3], sen[4]])
        anemo = [sen for sen in p if sen[2]==u'Anemometer']
        index = sorted(anemo, key = lambda x: x[1], reverse = True)[0][0]
        return index
