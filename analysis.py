#!/usr/tce/bin/python3
'''
by Yijia Zhang at June 19, 2017

Data analysis.

start.max = 1465584064.3972
end.min = 1465584164.6577
'''

def main():
    import time
    start = time.time()

    m = merge(path='/p/lscratchd/marathe1/', phase=1, setID=2, app='prime95', pcap=115, runID=1, level='processor')
    check = m.checkStartEnd()
    #check.to_csv('StartEnd.csv', index=False)
    #df = m.merging(outfile='temp_proc_air_set1_prime95_pcap115_run1.csv')
    m.fetchData(time=int(m.endMin))

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
        import pandas as pd
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
        import pandas as pd
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
        import pandas as pd
        df = pd.DataFrame(columns=['time', 'exactTime', 'node', 'processor', 'temp'])
        for path in self.folders:
            node = int(path.split('/')[-1][3:])# count from 1.
            oneNode = pd.read_csv(path + '/rank_0', sep='\t')
            oneTime = oneNode[oneNode['Timestamp.g']>=time].iloc[[0]]# get the first timestep after the input time.
            exactTime = oneTime['Timestamp.g'].values[0]
            for proc in [1, 2]:
                cores = ['Temp.%02d' % (8*(proc-1)+x) for x in range(8)]# count from 0.
                temp = oneTime[cores].mean(axis=1).values[0]
                df.loc[len(df)] = [time, exactTime, node, proc, temp]
        self.temp = df
        df.to_csv('data/temp_%s_ending_phase%d_set%d_%s_pcap%d_run%d.csv' % (level, phase, setID, app, pcap, runID), index=False)

class analysis:
    def __init__(self):
        pass

    def draw(self):
        pass

if __name__ == '__main__':
    main()
