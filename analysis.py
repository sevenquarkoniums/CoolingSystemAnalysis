#!/usr/tce/bin/python3
'''
by Yijia Zhang at June 19, 2017

Data preprocessing.
Input the raw metric data.

'''
import time
import pandas as pd
import sys
import os

def main():
    start = time.time()


    # use this line to run it using the current node.
    #m = merge(cluster='catalyst', phase=2, setID=3, app='cg.C', pcap=50, runID=1, level='processor', sock='dual')

    # use this line for submitting it to batch job.
    m = merge(cluster=sys.argv[1], phase=int(sys.argv[2]), setID=int(sys.argv[3]), app=sys.argv[4], pcap=int(sys.argv[5]), runID=int(sys.argv[6]), level='processor', sock=sys.argv[7])


    m.fetchData(mode='entire')

    duration = time.time() - start
    print('finished in %d seconds.' % round(duration) )

class merge:
    '''
    This class is for merging the relevant data distributed in different files into a single file.
    '''
    def __init__(self, cluster, phase, setID, app, pcap, runID, level, sock):
        self.cluster = cluster
        self.phase = phase
        self.setID = setID
        self.app = app
        self.pcap = pcap
        self.runID = runID
        self.level = level
        self.sock = sock

        # locating the raw data path here.
        if cluster == 'cab':
            self.coresPerProc = 8
            self.baseFreq = 2.4
            path = '/p/lscratchd/marathe1/'
            if phase == 1:
                phasedir = 'cabtraces4'
            elif phase == 2:
                phasedir = 'dat2.1'
            extend = path + '%s/set_%d/%s/pcap_%d/run_%d/' % (phasedir, setID, app, pcap, runID)
        elif cluster == 'catalyst':
            self.coresPerProc = 12
            self.baseFreq = 2.4
            path = '/g/g92/marathe1/lscratchd/catalyst_dat/combined/'
            extend = path + '%s/run_%d_%d/' % (app, runID, pcap)
        elif cluster == 'quartz':
            self.coresPerProc = 18
            self.baseFreq = 2.1
            #path = '/p/lscratchf/marathe1/quartz_dat/'# on catalyst
            #path = '/p/lscratchh/marathe1/traces/dat3.1/'# on quartz.
            #extend = path + '%s/set_%d/pcap_%d/run_%d/cores_36/' % (app, setID, pcap, runID)

            path = '/p/lscratchh/nirmalk/quartz10/set_3/'
            extend = path + '%s_%s/run_%d_%d/' % (app, sock, runID, pcap)
        self.folders = self.getfolders(extend)

        print('Processing initiated.')
        print(extend)

    def getfolders(self, extendpath):
        '''
        return a list of folders inside the given path.
        '''
        return [x[0] for x in os.walk(extendpath)][1:]

    def getfiles(self, path):
        '''
        return a list of files inside the given path.
        '''
        f = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            f.extend(filenames)
            break
        return f

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
        Obsolete function.
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

    def fetchData(self, mode):
        '''
        Fetch the data from all the nodes (at a specific time / in a time interval / during entire run) and store them in a .csv file.
        '''
        perProcMetrics = self.getPerProcMetrics()
        if self.level == 'processor':# average values on each processor.
            # metric columns
            allMetrics = ['time', 'exactTime' if mode == 'interval' else 'runtime', 'node', 'processor']
            allMetrics.extend([x for x in perProcMetrics if x != 'Temp'])# be careful that .extend() itself doesn't return a value.
            allMetrics.extend(['Temp'])
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

        if self.sock in ['both','dual']:
            procs = [1,2]
        elif self.sock == 'sock1':
            procs = [1]
        elif self.sock == 'sock2':
            procs = [2]

        count = -1
        for path in self.folders:
            count += 1
            if count % 100 == 0:
                print(count)
            if self.cluster == 'cab':
                node = int(path.split('/')[-1][3:])# count from 1.
            elif self.cluster == 'quartz':
                node = int(path.split('/')[-1][6:])# count from 1.
            elif self.cluster == 'catalyst':
                node = int(path.split('/')[-1][8:])# count from 1.
            allfiles = self.getfiles(path)
            logfiles = [x for x in allfiles if x.startswith('out.log')]
            rankfiles = [x for x in allfiles if x.startswith('rank_')]
            ranknumbers = [int(x[5:]) for x in rankfiles]
            ranknumbers.sort()
            if self.sock == 'dual':
                runtime = {0:0,1:0}
                for ilog,logf in enumerate(logfiles):
                    f = open('%s/%s' % (path, logf), 'r')
                    for line in f:
                        if line.endswith('core 0 \n'):
                            package = int(line.split()[-3])# 0 or 1.
                    f.seek(0)
                    for line in f:
                        if self.app in ['cg.C','ep.D','ft.C','mg.D']:
                            if line.startswith(' Time in seconds'):
                                runtime[package] = float(line.split()[-1])
                        elif self.app == 'dgemm':
                            if line.startswith('Multiply time:'):
                                runtime[package] = float(line.split()[-2])
                    f.close()
                for proc in [1,2]:
                    fname = path + '/rank_%d' % ranknumbers[proc-1]
                    if not os.path.isfile(fname):
                        print('not exist: %s' % fname)
                    else:
                        if os.stat(fname).st_size == 0:
                            print('empty file: %s' % fname)
                        else:
                            oneNode = pd.read_csv(fname, sep='\t')
                            oneTime = oneNode.iloc[[0]]# get the first timestep row after the start.
                            starttime = oneTime['Timestamp.g'].values[0]
                            if runtime[proc-1] != 0:
                                stoptime = starttime + runtime[proc-1]
                                nextTime = oneNode[oneNode['Timestamp.g']>=stoptime].iloc[[0]]
                                interval = oneNode[oneNode['Timestamp.g']<stoptime]
                            else:# for apps whose running time are not provided in the log files.
                                nextTime  = oneNode.iloc[[len(oneNode)-1]]
                                runtime[proc-1] = nextTime['Timestamp.g'].values[0] - starttime
                                interval = oneNode
                            if self.level == 'processor':
                                values = []
                                for metric in [x for x in perProcMetrics if x != 'Temp']:# the other metrics are differential.
                                    cores = ['%s.%02d' % ( metric, (x) ) for x in range(self.coresPerProc)]# count from 0.
                                    values.append( (nextTime[cores].mean(axis=1).values[0] - oneTime[cores].mean(axis=1).values[0]) )# not averaged over time.
                                allValues = [starttime, runtime[proc-1], node, proc]
                                allValues.extend(values)
                                allValues.extend( [nextTime[['Temp.%02d' % (x) for x in range(self.coresPerProc)]].mean(axis=1).values[0]] )# get the finish time temperature.

                                if self.phase == 1:# the power and ipc are averaged from start to stop (not end).
                                    allValues.extend([ interval[interval['PKG_POWER.%d' % (proc-1)]>0]['PKG_POWER.%d' % (proc-1)].mean() ])
                                elif self.phase == 2:
                                    allValues.extend([ interval[interval['PKG_POWER.%d' % (proc-1)]>0]['PKG_POWER.%d' % (proc-1)].mean(), interval[interval['DRAM_POWER.%d' % (proc-1)]>0]['DRAM_POWER.%d' % (proc-1)].mean() ])

                                ipc = ( 
                                        ( nextTime[ ['INST_RETIRED.ANY.%02d' % (x) for x in range(self.coresPerProc)] ].mean(axis=1).values[0]
                                        - oneTime[ ['INST_RETIRED.ANY.%02d' % (x) for x in range(self.coresPerProc)] ].mean(axis=1).values[0] )
                                        /
                                        ( nextTime['TSC.00'].values[0] - oneTime['TSC.00'].values[0] )
                                      )
                                ipcw = ipc / interval[interval['PKG_POWER.%d' % (proc-1)]>0]['PKG_POWER.%d' % (proc-1)].mean()# divided by processor power, excluding DRAM.
                                freqs = []
                                for core in range(0, self.coresPerProc):
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
            else:
                fname = path + '/rank_0'
                if os.path.isfile(fname):
                    if os.stat(fname).st_size != 0:
                        oneNode = pd.read_csv(fname, sep='\t')
                        if mode == 'entire':
                            oneTime = oneNode.iloc[[0]]# get the first timestep row after the start.
                            nextTime = oneNode.iloc[[len(oneNode)-1]]# the last row.
                            time = oneTime['Timestamp.g'].values[0]
                            runtime = nextTime['Timestamp.g'].values[0] - time
                            if self.level == 'processor':
                                for proc in procs:
                                    values = []
                                    for metric in [x for x in perProcMetrics if x != 'Temp']:# the other metrics are differential.
                                        cores = ['%s.%02d' % ( metric, (self.coresPerProc*(proc-1)+x) ) for x in range(self.coresPerProc)]# count from 0.
                                        values.append( (nextTime[cores].mean(axis=1).values[0] - oneTime[cores].mean(axis=1).values[0]) )# not averaged over time.
                                    allValues = [time, runtime, node, proc]
                                    allValues.extend(values)
                                    allValues.extend( [nextTime[['Temp.%02d' % (self.coresPerProc*(proc-1)+x) for x in range(self.coresPerProc)]].mean(axis=1).values[0]] )# get the finish time temperature.

                                    if self.phase == 1:
                                        allValues.extend([ oneNode[oneNode['PKG_POWER.%d' % (proc-1)]>0]['PKG_POWER.%d' % (proc-1)].mean() ])
                                    elif self.phase == 2:
                                        allValues.extend([ oneNode[oneNode['PKG_POWER.%d' % (proc-1)]>0]['PKG_POWER.%d' % (proc-1)].mean(), oneNode[oneNode['DRAM_POWER.%d' % (proc-1)]>0]['DRAM_POWER.%d' % (proc-1)].mean() ])

                                    ipc = ( 
                                            ( nextTime[ ['INST_RETIRED.ANY.%02d' % (self.coresPerProc*(proc-1)+x) for x in range(self.coresPerProc)] ].mean(axis=1).values[0]
                                            - oneTime[ ['INST_RETIRED.ANY.%02d' % (self.coresPerProc*(proc-1)+x) for x in range(self.coresPerProc)] ].mean(axis=1).values[0] )
                                            /
                                            ( nextTime['TSC.00' if proc==1 else ('TSC.%02d'% self.coresPerProc)].values[0] - oneTime['TSC.00' if proc==1 else ('TSC.%02d'% self.coresPerProc)].values[0] )
                                          )
                                    ipcw = ipc / oneNode[oneNode['PKG_POWER.%d' % (proc-1)]>0]['PKG_POWER.%d' % (proc-1)].mean()# divided by processor power, excluding DRAM.
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
                        elif mode == 'interval':
                            for time in range( int(self.startMax+1), int(self.endMin-11), 10):
                                oneTime = oneNode[oneNode['Timestamp.g']>=time].iloc[[0]]# get the first timestep row after the input time.
                                nextTime = oneNode[oneNode['Timestamp.g']>=time+10].iloc[[0]]# to calculate IPC etc.
                                interval = oneNode[ (oneNode['Timestamp.g']>=time) & (oneNode['Timestamp.g']<time+10) ]
                                #nextTime = oneNode[oneNode['Timestamp.g']>=time].iloc[[1]]# to calculate IPC etc.
                                exactTime = oneTime['Timestamp.g'].values[0]
                                if self.level == 'processor':
                                    for proc in procs:

                                        values = []
                                        for metric in [x for x in perProcMetrics if x != 'Temp']:
                                            cores = ['%s.%02d' % ( metric, (self.coresPerProc*(proc-1)+x) ) for x in range(self.coresPerProc)]# count from 0.
                                            values.append( (nextTime[cores].mean(axis=1).values[0] - oneTime[cores].mean(axis=1).values[0]) / (nextTime['Timestamp.g'].values[0] - oneTime['Timestamp.g'].values[0]) )
                                        allValues = [time, exactTime, node, proc]
                                        allValues.extend(values)
                                        allValues.extend( [oneTime[['Temp.%02d' % (self.coresPerProc*(proc-1)+x) for x in range(self.coresPerProc)]].mean(axis=1).values[0]] )
                                        #allValues.extend( [interval[['Temp.%02d' % (self.coresPerProc*(proc-1)+x) for x in range(self.coresPerProc)]].mean(axis=1).mean(axis=0)] )

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

        # output the preprocessed data to a certain location.
        if self.cluster == 'cab':
            df.to_csv('data/%s/%s_%s_phase%d_set%d_%s_pcap%d_run%d.csv' % (self.cluster, 'pavg10' if mode == 'interval' else 'pavgall', self.level, self.phase, self.setID, self.app, self.pcap, self.runID), index=False)
        elif self.cluster == 'quartz':
            df.to_csv('data/%s7/%s_%s_set%d_%s_%s_pcap%d_run%d.csv' % (self.cluster, 'pavg10' if mode == 'interval' else 'pavgall', self.level, self.setID, self.sock, self.app, self.pcap, self.runID), index=False)
        elif self.cluster == 'catalyst':
            df.to_csv('data/%s/%s_%s_set%d_%s_%s_pcap%d_run%d.csv' % (self.cluster, 'pavg10' if mode == 'interval' else 'pavgall', self.level, self.setID, self.sock, self.app, self.pcap, self.runID), index=False)
        self.data = df

    def getPerProcMetrics(self):
        '''
        Get the list of metrics.
        '''
        perProcMetrics = []
        allfiles = self.getfiles(self.folders[0])
        rankfiles = [x for x in allfiles if x.startswith('rank_')]
        dfGetMetrics = pd.read_csv(self.folders[0] + '/' + rankfiles[0], sep='\t')
        for col in dfGetMetrics.columns:
            if col.endswith('.00'):
                perProcMetrics.append( col.split('.00')[0] )
        return perProcMetrics

if __name__ == '__main__':
    main()
