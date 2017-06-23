#!/Users/zhang51/anaconda/bin/python
'''
by Yijia Zhang at June 19, 2017

Data analysis.

'''
import time
import pandas as pd

def main():
    start = time.time()

    m = merge(path='/p/lscratchd/marathe1/', phase=1, setID=2, app='mg.C', pcap=115, runID=1, level='processor')
    #check = m.checkStartEnd()
    #check.to_csv('StartEnd.csv', index=False)
    #df = m.merging(outfile='temp_proc_air_set1_prime95_pcap115_run1.csv')
    #m.fetchData(time=1484382570)
    #m.fetchData(time=int(m.endMin)-5)
    m.data = pd.read_csv('data/%s_ending_phase%d_set%d_%s_pcap%d_run%d.csv' % (m.level, m.phase, m.setID, m.app, m.pcap, m.runID))
    m.cluster(algorithm='dbscan')

    duration = time.time() - start
    print('finished in %d seconds.' % round(duration) )

class merge:
    '''
    This class is for merging the relevant data distributed in different files into a single file.
    '''
    def __init__(self, path, phase, setID, app, pcap, runID, level):
        self.phase = phase
        self.setID = setID
        self.app = app
        self.pcap = pcap
        self.runID = runID
        self.level = level

        if phase == 1:
            phasedir = 'cabtraces4'
        elif phase == 2:
            phasedir = 'dat2.1'
        extend = path + '%s/set_%d/%s/pcap_%d/run_%d/' % (phasedir, setID, app, pcap, runID)
        self.folders = self.getfolders(extend)

        print('Processing initiated.')

    def getfolders(self, extendpath):
        from os import walk
        return [x[0] for x in walk(extendpath)][1:]

    def checkStartEnd(self):
        '''
        Check the start time and end time of different nodes.
        Find the overlapping durations for analysis.
        '''
        check = pd.DataFrame(columns=['node', 'length', 'start', 'end'])
        for path in self.folders:
            oneNode = pd.read_csv(path + '/rank_0', sep='\t')
            node = int(path.split('/')[-1][3:])# count from 1.
            check.loc[len(check)] = [ node, len(oneNode), oneNode.iloc[0,:]['Timestamp.g'], oneNode.iloc[-1,:]['Timestamp.g'] ]
        print('length.min = %d' % check['length'].min())
        print('length.max = %d' % check['length'].max())
        print('start.min = %f at node %d' % (check['start'].min(), check['start'].idxmin()) )
        print('start.max = %f at node %d' % (check['start'].max(), check['start'].idxmax()) )
        print('end.min = %f' % check['end'].min())
        print('end.max = %f' % check['end'].max())
        self.startMax = check['start'].max()
        self.endMin = check['end'].min()
        return check

    def merging(self, outfile):
        '''
        not finished.
        Only merge the overlapping duration.
        '''
        df = pd.DataFrame()
        for path in self.folders:
            oneNode = pd.read_csv(path + '/rank_0', sep='\t')
            if len(df) == 0:# only do it once.
                len0 = len(oneNode)
                df['time'] = oneNode['Timestamp.g']
                start0 = df.iloc[0]['time']
                print(start0)
            else:
                print(oneNode.iloc[0]['Timestamp.g'])
                if len(oneNode) != len0:
                    print('Time doesn\'t match.')
            node = int(path.split('/')[-1][3:])# count from 1.
            for proc in [1, 2]:
                cores = ['Temp.%02d' % (8*(proc-1)+x) for x in range(8)]# count from 0.
                metric = 'node%d_proc%d' % (node, proc)
                df[metric] = oneNode[cores].mean(axis=1)
        print(df)
        return df

    def fetchData(self, time):
        '''
        Fetch the data from all the nodes at a specific time and store them in a .csv file.
        '''
        perProcMetrics = self.getPerProcMetrics()
        if self.level == 'processor':
            # metric columns
            allMetrics = ['time', 'exactTime', 'node', 'processor']
            allMetrics.extend(perProcMetrics)# be careful that .extend() itself doesn't return a value.
            if self.phase == 1:# phase 1 didn't have DRAM_POWER.
                allMetrics.extend(['PKG_POWER'])
            elif self.phase == 2:
                allMetrics.extend(['PKG_POWER', 'DRAM_POWER'])
            allMetrics.extend(['IPC', 'IPCpW', 'frequency'])
            df = pd.DataFrame( columns=allMetrics )
        elif self.level == 'core':
            df = pd.DataFrame( columns=['time', 'exactTime', 'node', 'core', 'Temp'] )
        elif self.level == 'node':
            df = pd.DataFrame( columns=['time', 'exactTime', 'node', 'Temp'] )
        count = 0
        for path in self.folders:
            count += 1
            if count % 100 == 0:
                print(count)
            node = int(path.split('/')[-1][3:])# count from 1.
            oneNode = pd.read_csv(path + '/rank_0', sep='\t')
            oneTime = oneNode[oneNode['Timestamp.g']>=time].iloc[[0]]# get the first timestep row after the input time.
            nextTime = oneNode[oneNode['Timestamp.g']>=time].iloc[[1]]# to calculate IPC etc.
            exactTime = oneTime['Timestamp.g'].values[0]
            if self.level == 'processor':
                for proc in [1, 2]:

                    values = []
                    for metric in perProcMetrics:
                        cores = ['%s.%02d' % ( metric, (8*(proc-1)+x) ) for x in range(8)]# count from 0.
                        values.append( oneTime[cores].mean(axis=1).values[0] )
                    allValues = [time, exactTime, node, proc]
                    allValues.extend(values)

                    if self.phase == 1:
                        allValues.extend([ oneTime['PKG_POWER.%d' % (proc-1)].values[0] ])
                    elif self.phase == 2:
                        allValues.extend([ oneTime['PKG_POWER.%d' % (proc-1)].values[0], oneTime['DRAM_POWER.%d' % (proc-1)].values[0] ])

                    ipc = ( 
                            ( nextTime[ ['INST_RETIRED.ANY.%02d' % (8*(proc-1)+x) for x in range(8)] ].mean(axis=1).values[0]
                            - oneTime[ ['INST_RETIRED.ANY.%02d' % (8*(proc-1)+x) for x in range(8)] ].mean(axis=1).values[0] )
                            /
                            ( nextTime['TSC.00'].values[0] - oneTime['TSC.00'].values[0] )
                          )
                    ipcw = ipc / oneTime['PKG_POWER.%d' % (proc-1)].values[0]# divided by processor power, excluding DRAM.
                    freqs = []
                    for core in range(8*(proc-1), 8*proc):
                        freqs.append(
                                        ( 
                                            2.4 * (nextTime['APERF.%02d' % core].values[0] - oneTime['APERF.%02d' % core].values[0]) 
                                            / 
                                            (nextTime['MPERF.%02d' % core].values[0] - oneTime['MPERF.%02d' % core].values[0])
                                        )
                                    )
                    freq = sum(freqs)/len(freqs)
                    allValues.extend([ipc, ipcw, freq])

                    df.loc[len(df)] = allValues
            elif self.level == 'core':
                for core in range(16):
                    temp = oneTime['Temp.%02d' % core].values[0]
                    df.loc[len(df)] = [time, exactTime, node, core, temp]
            elif self.level == 'node':
                cores = ['%s.%02d' % ( 'Temp', x ) for x in range(16)]# count from 0.
                temp = oneTime[cores].mean(axis=1).values[0]
                df.loc[len(df)] = [time, exactTime, node, temp]
        df.to_csv('data/%s_ending_phase%d_set%d_%s_pcap%d_run%d.csv' % (self.level, self.phase, self.setID, self.app, self.pcap, self.runID), index=False)
        self.data = df

    def getPerProcMetrics(self):
        perProcMetrics = []
        dfGetMetrics = pd.read_csv(self.folders[0] + '/rank_0', sep='\t')
        for col in dfGetMetrics.columns:
            if col.endswith('.00'):
                perProcMetrics.append( col.split('.00')[0] )
        return perProcMetrics

    def cluster(self, algorithm):
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import StandardScaler
        train = StandardScaler().fit_transform(self.data[['Temp', 'PKG_POWER', 'IPC']])
        if algorithm == 'dbscan':
            db = DBSCAN().fit(train)
            n_clusters_ = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
        print(n_clusters_)

if __name__ == '__main__':
    main()
