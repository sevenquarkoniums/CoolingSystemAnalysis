#!/usr/tce/bin/python3
def main():
    import time
    start = time.time()

    dp = dataProcess('/usr/workspace/wsb/variorum/cab/rrd/', '/p/lscratchf/zhang51/analysis/cab/xml/', '/usr/workspace/wsb/variorum/cab/csv/')
    dp.getfiles()
    dp.transformData()
    dp.draw()

    duration = time.time() - start
    print('finished in %d seconds.' % round(duration) )

class dataProcess:
    def __init__(self, rrdDir, xmlDir, csvDir):
        import subprocess
        self.rrdDir = rrdDir
        self.xmlDir = xmlDir
        self.csvDir = csvDir
        subprocess.call('mkdir -p %s' % self.xmlDir, shell=True)# the subprocess.call will wait for the execution to finish.
        subprocess.call('mkdir -p %s' % self.csvDir, shell=True)
        self.files = {'cab':[]}
        self.dfs = {'cab':[]}
        print('Processing initiated.')

    def getfiles(self):
        from os import listdir
        from os.path import isfile, join
        for f in listdir(self.rrdDir):
            F = join(self.rrdDir, f)
            if isfile(F):
                if F.split('.')[-1] == 'rrd' and f.split('.')[0].isdigit():
                    self.files['cab'].append(F)
                else:
                    print('Jumping file %s.' % f)
        print('File list with %d items created.' % len(self.files['cab']) )

    def dump(self, fname):
        import subprocess
        fNum = int( fname.split('/')[-1].split('.')[0] )
        callReturn = subprocess.call('rrdtool dump %s %s%d.xml' % (fname, self.xmlDir, fNum), shell=True)
        return '%s%d.xml' % (self.xmlDir, fNum)

    def metricName(self, metrics):
        with open('metrics_cab.txt', 'r') as f:
            metricsNamed = []
            for metric in metrics:
                for line in f:
                    if '|' in line:
                        linesplit = line.split('|')
                        if linesplit[1] != ' var ':
                            if metric == int(linesplit[1].split()[0]):
                                metricsNamed.append(linesplit[2].strip())
                                break
        return metricsNamed

    def xml2df(self, xml):
        '''
        Only the 5 min granularity rra is stored.
        '''
        import pandas as pd
        import numpy as np
        import xml.etree.ElementTree as et
        tree = et.parse(xml)
        root = tree.getroot()
        metrics = [int(root[x][0].text) for x in range(3, len(root)-2) ]# stored as int.
        metricsNamed = self.metricName(metrics)
        df = pd.DataFrame(columns=metricsNamed)
        data = root[-2][4]
        for row in data:
            values = []
            for value in row:
                if value.text == 'NaN':
                    values.append(np.nan)
                else:
                    values.append(float(value.text))
            df.loc[len(df)] = values
        with open(xml, 'r') as txt:
            unixTs = []
            years = []
            months = []
            days = []
            hours = []
            minutes = []
            seconds = []
            for line in txt:
                if line.startswith('\t\t\t<!--'):
                    time = line.split('--')[1].split()
                    unixTime = int(time[4])
                    unixTs.append(unixTime)

                    date = time[0].split('-')
                    year = int(date[0])
                    month = int(date[1])
                    day = int(date[2])
                    clock = time[1].split(':')
                    hour = int(clock[0])
                    minute = int(clock[1])
                    second = int(clock[2])

                    years.append(year)
                    months.append(month)
                    days.append(day)
                    hours.append(hour)
                    minutes.append(minute)
                    seconds.append(second)
        lendf = len(df)
        df['unixTime'] = unixTs[:lendf]
        df['year'] = years[:lendf]
        df['month'] = months[:lendf]
        df['day'] = days[:lendf]
        df['hour'] = hours[:lendf]
        df['minute'] = minutes[:lendf]
        df['second'] = seconds[:lendf]
        return df

    def transformData(self):
        import pandas as pd
        for fname in self.files['cab']:
            fNum = int( fname.split('/')[-1].split('.')[0] )
            if fNum > 4000:
                print('parsing %d.rrd' % fNum)
                xmlName = self.dump(fname)
                df = self.xml2df(xmlName)
                dfName = '%s%d.csv' % (self.csvDir, fNum)
                df.to_csv(dfName, index=False)
                #self.dfs['cab'].append(df)
        print('rrd files are transformed.')

    def draw(self):
        pass

if __name__ == '__main__':
    main()
