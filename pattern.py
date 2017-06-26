#!/Users/zhang51/anaconda/bin/python
'''
by Yijia Zhang at June 22, 2017

Machine learning analysis of the data.
'''
import time
import pandas as pd

def main():
    start = time.time()

    a = analysis(phase=1, setID=2, app='prime95', pcap=115, runID=1, level='processor')
    a.data = pd.read_csv('data/%s_phase%d_set%d_%s_pcap%d_run%d_period5.csv' % (a.level, a.phase, a.setID, a.app, a.pcap, a.runID))
    #for (eps, min_samples) in [(0.3,20),(0.4,30),(0.5,60),(0.6,100),(0.7,160),(0.8,240)]:
    for eps in [x/10 for x in range(20, 31, 1)]:
        for min_samples in range(300, 600, 10):
            print('eps=%.2f, min_samples=%d' % (eps, min_samples) )
            a.cluster(algorithm='dbscan', metrics=['Temp', 'PKG_POWER', 'IPC'], eps=eps, min_samples=min_samples)
            #a.cluster(algorithm='dbscan', metrics=['Temp','PKG_POWER','IPC','IPCpW','frequency','INST_RETIRED.ANY','CPU_CLK_UNHALTED.THREAD','CPU_CLK_UNHALTED.REF_TSC','IA32_PERF_STATUS','ARITH.FPU_DIV','BR_INST_RETIRED.ALL_BRANCHES','UNC_M_CAS_COUNT.WR','UNC_M_CAS_COUNT.RD','APERF','MPERF','TSC','Temp','OPENMP.INST','OPENMP.ID'])
            if a.clusters in [3, 6]:
                print('good one')
                a.draw(eps, min_samples)

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

    def cluster(self, algorithm, metrics, eps, min_samples):
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import StandardScaler
        train = StandardScaler().fit_transform(self.data[metrics])
        if algorithm == 'dbscan':
            db = DBSCAN(eps=eps, min_samples=min_samples).fit(train)
            n_clusters_ = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
            print('number of clusters: %d' % n_clusters_)
            self.data['cluster'] = db.labels_
            self.clusters = n_clusters_

    def draw(self, eps, min_samples):
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set(font_scale=4)
        sns.set_style('whitegrid', {'grid.color':'.15', 'axes.edgecolor':'.15'})
        g = sns.pairplot(self.data, kind='scatter', #x_vars=['Temp'], y_vars=['IPC'], 
                        #vars=['node', 'processor', 'cluster'], 
                        vars=['node','Temp','IPC','PKG_POWER'],
                        hue='cluster', #hue_order=[0, 7], 
                        palette=sns.color_palette('Set2',10), size=20)
        plt.title('clusterAll_eps%.2f_samples%d' % (eps, min_samples) )
        g.savefig('clusterAll_eps%.2f_samples%d.png' % (eps, min_samples) )
        plt.close()

if __name__ == '__main__':
    main()
