#!/usr/tce/bin/python3
'''
Get the runtime of the DAT for each node.
'''

import time
import pandas as pd
import sys
import os

def main():
    start = time.time()

    r = runtime(app=sys.argv[1], setID=int(sys.argv[2]), pcap=int(sys.argv[3]), runID=int(sys.argv[4]) )
    r.getRuntime()

    duration = time.time() - start
    print('finished in %d seconds.' % round(duration) )

class runtime:
    def __init__(self, app, setID, pcap, runID):
        self.app = app
        self.setID = setID
        self.pcap = pcap
        self.runID = runID

    def getfolders(self, extendpath):
        return [x[0] for x in os.walk(extendpath)][1:]

    def getRuntime(self):
        fi = '/p/lscratchf/marathe1/quartz_dat/%s/set_%d/pcap_%d/run_%d/cores_36' % (self.app, self.setID, self.pcap, self.runID)
        #fi = '/p/lscratchh/marathe1/traces/dat3.1/%s/set_%d/pcap_%d/run_%d/cores_36' % (self.app, self.setID, self.pcap, self.runID)
        folders = self.getfolders(fi)
        df = pd.DataFrame(columns=['node','runtime'])
        print('start fetching...')
        for f in folders:
            node = int(f.split('/')[-1][6:])
            fname = f+'/rank_0'
            if os.path.isfile(fname):
                if os.stat(fname).st_size != 0:
                    oneNode = pd.read_csv(fname, sep='\t')
                    begin = oneNode.at[0, 'Timestamp.g']
                    end = oneNode.at[len(oneNode)-1, 'Timestamp.g']
                    df.loc[len(df)] = [node, end-begin]
                else:
                    print('corrupt file: %s' % fname)
        fo = 'runtime_%s_set%d_pcap%d_run%d' % (self.app, self.setID, self.pcap, self.runID)
        df.to_csv('data/quartz/%s.csv' % fo, index=False)
        print(fo)


if __name__ == '__main__':
    main()
