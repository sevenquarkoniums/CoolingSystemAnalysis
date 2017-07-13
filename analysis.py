#!/usr/tce/bin/python3
'''
by Yijia Zhang at June 19, 2017

Data analysis.

'''
import time
import pandas as pd
import sys
import os

def main():
    start = time.time()

    #m = merge(cluster='cab', phase=1, setID=14, app='prime95', pcap=51, runID=1, level='processor')
    m = merge(cluster='cab', phase=int(sys.argv[1]), setID=int(sys.argv[2]), app=sys.argv[3], pcap=int(sys.argv[4]), runID=int(sys.argv[5]), level='processor')
    check = m.checkStartEnd()
    #df = m.merging(outfile='temp_proc_air_set1_prime95_pcap115_run1.csv')
    #m.fetchData(time=1484382570)
    #period = 0
    #for moment in range( int(m.startMax), int(m.endMin), 10 ):
    #    m.fetchData(time=moment, period=period)
    #    period += 1
    m.fetchData()#time=int(m.endMin)-5)

    duration = time.time() - start
    print('finished in %d seconds.' % round(duration) )

class merge:
    '''
    This class is for merging the relevant data distributed in different files into a single file.
    '''
    def __init__(self, cluster, phase, setID, app, pcap, runID, level):
        self.cluster = cluster
        self.phase = phase
        self.setID = setID
        self.app = app
        self.pcap = pcap
        self.runID = runID
        self.level = level

        if cluster == 'cab':
            self.coresPerProc = 8
            self.baseFreq = 2.4
            path = '/p/lscratchd/marathe1/'
            if phase == 1:
                phasedir = 'cabtraces4'
            elif phase == 2:
                phasedir = 'dat2.1'
            extend = path + '%s/set_%d/%s/pcap_%d/run_%d/' % (phasedir, setID, app, pcap, runID)
        elif cluster == 'quartz':
            self.coresPerProc = 18
            self.baseFreq = 2.1
            path = '/p/lscratchh/marathe1/traces/dat3.1/'
            extend = path + '%s/set_%d/pcap_%d/run_%d/cores_36/' % (app, setID, pcap, runID)
        self.folders = self.getfolders(extend)

        print('Processing initiated.')
        print(extend)

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
            fname = path + '/rank_0'
            if os.path.isfile(fname):
                if os.stat(fname).st_size != 0:
                    oneNode = pd.read_csv(path + '/rank_0', sep='\t')
                    if self.cluster == 'cab':
                        node = int(path.split('/')[-1][3:])# count from 1.
                    elif self.cluster == 'quartz':
                        node = int(path.split('/')[-1][6:])# count from 1.
                    check.loc[len(check)] = [ node, len(oneNode), oneNode.iloc[0,:]['Timestamp.g'], oneNode.iloc[-1,:]['Timestamp.g'] ]
                else:
                    print('empty file: %s' % fname)
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

    def fetchData(self):#, time):
        '''
        Fetch the data from all the nodes at a specific time and store them in a .csv file.
        '''
        perProcMetrics = self.getPerProcMetrics()
        if self.level == 'processor':# average values on each processor.
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
            df = pd.DataFrame( columns=['time', 'exactTime', 'node', 'core', 'Temp', 'deltaTSC'] )
        elif self.level == 'node':
            df = pd.DataFrame( columns=['time', 'exactTime', 'node', 'Temp'] )
        count = -1
        for path in self.folders:
            count += 1
            if count % 100 == 0:
                print(count)
            if self.cluster == 'cab':
                node = int(path.split('/')[-1][3:])# count from 1.
            elif self.cluster == 'quartz':
                node = int(path.split('/')[-1][6:])# count from 1.
            fname = path + '/rank_0'
            if os.path.isfile(fname):
                if os.stat(fname).st_size != 0:
                    oneNode = pd.read_csv(path + '/rank_0', sep='\t')
                    for time in range( int(self.startMax+1), int(self.endMin-11), 10):
                        oneTime = oneNode[oneNode['Timestamp.g']>=time].iloc[[0]]# get the first timestep row after the input time.
                        nextTime = oneNode[oneNode['Timestamp.g']>=time+10].iloc[[0]]# to calculate IPC etc.
                        interval = oneNode[ (oneNode['Timestamp.g']>=time) & (oneNode['Timestamp.g']<time+10) ]
                        #nextTime = oneNode[oneNode['Timestamp.g']>=time].iloc[[1]]# to calculate IPC etc.
                        exactTime = oneTime['Timestamp.g'].values[0]
                        if self.level == 'processor':
                            for proc in [1, 2]:

                                values = []
                                for metric in perProcMetrics:
                                    cores = ['%s.%02d' % ( metric, (self.coresPerProc*(proc-1)+x) ) for x in range(self.coresPerProc)]# count from 0.
                                    values.append( oneTime[cores].mean(axis=1).values[0] )
                                allValues = [time, exactTime, node, proc]
                                allValues.extend(values)

                                if self.phase == 1:
                                    #allValues.extend([ max(oneTime['PKG_POWER.%d' % (proc-1)].values[0], -1) ])# max() is used to replace problematic point.
                                    allValues.extend([ max(interval['PKG_POWER.%d' % (proc-1)].mean(), -1) ])# max() is used to replace problematic point.
                                elif self.phase == 2:
                                    #allValues.extend([ max(oneTime['PKG_POWER.%d' % (proc-1)].values[0], -1), max(oneTime['DRAM_POWER.%d' % (proc-1)].values[0], -1) ])
                                    allValues.extend([ max(interval['PKG_POWER.%d' % (proc-1)].mean(), -1), max(interval['DRAM_POWER.%d' % (proc-1)].mean(), -1) ])

                                ipc = ( 
                                        ( nextTime[ ['INST_RETIRED.ANY.%02d' % (self.coresPerProc*(proc-1)+x) for x in range(self.coresPerProc)] ].mean(axis=1).values[0]
                                        - oneTime[ ['INST_RETIRED.ANY.%02d' % (self.coresPerProc*(proc-1)+x) for x in range(self.coresPerProc)] ].mean(axis=1).values[0] )
                                        /
                                        ( nextTime['TSC.00'].values[0] - oneTime['TSC.00'].values[0] )
                                      )
                                ipcw = ipc / interval['PKG_POWER.%d' % (proc-1)].mean()# divided by processor power, excluding DRAM.
                                freqs = []
                                for core in range(self.coresPerProc*(proc-1), self.coresPerProc*proc):
                                    freqs.append(
                                                    ( 
                                                        self.baseFreq * (nextTime['APERF.%02d' % core].values[0] - oneTime['APERF.%02d' % core].values[0]) 
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
                                deltaTSC = nextTime['TSC.%02d' % core].values[0] - oneTime['TSC.%02d' % core].values[0]
                                df.loc[len(df)] = [time, exactTime, node, core, temp, deltaTSC]
                        elif self.level == 'node':
                            cores = ['%s.%02d' % ( 'Temp', x ) for x in range(16)]# count from 0.
                            temp = oneTime[cores].mean(axis=1).values[0]
                            df.loc[len(df)] = [time, exactTime, node, temp]
        if self.cluster == 'cab':
            df.to_csv('data/%s/pavg10_%s_phase%d_set%d_%s_pcap%d_run%d.csv' % (self.cluster, self.level, self.phase, self.setID, self.app, self.pcap, self.runID), index=False)
        elif self.cluster == 'quartz':
            df.to_csv('data/%s/pavg10_%s_set%d_%s_pcap%d_run%d.csv' % (self.cluster, self.level, self.setID, self.app, self.pcap, self.runID), index=False)
        self.data = df

    def getPerProcMetrics(self):
        perProcMetrics = []
        dfGetMetrics = pd.read_csv(self.folders[0] + '/rank_0', sep='\t')
        for col in dfGetMetrics.columns:
            if col.endswith('.00'):
                perProcMetrics.append( col.split('.00')[0] )
        return perProcMetrics

if __name__ == '__main__':
    main()
