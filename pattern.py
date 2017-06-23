#!/Users/zhang51/anaconda/bin/python
'''
by Yijia Zhang at June 22, 2017

Machine learning analysis of the data.
'''
import time
import pandas as pd

def main():
    start = time.time()

    a = analysis(phase=1, setID=2, app='mg.C', pcap=115, runID=1, level='processor')
    a.data = pd.read_csv('data/%s_ending_phase%d_set%d_%s_pcap%d_run%d.csv' % (a.level, a.phase, a.setID, a.app, a.pcap, a.runID))
    a.cluster(algorithm='dbscan')

    duration = time.time() - start
    print('finished in %d seconds.' % round(duration) )

class analysis:
    '''
    This class is for merging the relevant data distributed in different files into a single file.
    '''
    def __init__(self, phase, setID, app, pcap, runID, level):
        self.phase = phase
        self.setID = setID
        self.app = app
        self.pcap = pcap
        self.runID = runID
        self.level = level

        print('Processing initiated.')
        print('phase=%d' % phase)
        print('setID=%d' % setID)
        print('app=%s' % app)
        print('runID=%d' % runID)

    def getfolders(self, extendpath):
        from os import walk
        return [x[0] for x in walk(extendpath)][1:]

    def cluster(self, algorithm):
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import StandardScaler
        train = StandardScaler().fit_transform(self.data[['Temp', 'PKG_POWER', 'IPC']])
        if algorithm == 'dbscan':
            db = DBSCAN().fit(train)
            n_clusters_ = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
        print('number of clusters: %d' % n_clusters_)

if __name__ == '__main__':
    main()
