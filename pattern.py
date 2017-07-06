#!/Users/zhang51/anaconda/bin/python
'''
by Yijia Zhang at June 22, 2017

Machine learning analysis of the data.
'''
import time
import pandas as pd

def main():
    start = time.time()

    for phase in [1]:
        for setID in range(1, 2):
            for app in ['prime95']:
                for pcap in [115]:
                    for runID in [1]:

                        a = analysis(phase, setID, app, pcap, runID, level='processor')
                        a.readData()

                        #for (eps, min_samples) in [(0.3,20),(0.4,30),(0.5,60),(0.6,100),(0.7,160),(0.8,240)]:
                        if a.exist:
                            a.times = sorted(list(set(a.data['time'])))
                            period = 0
                            for epoch in a.times:
                                for processor in [1]:

                                    #for eps in [x/10 for x in range(1, 10)]:
                                        #for min_samples in range(10, 101, 10):
                                    #a.cluster(algorithm='dbscan', metrics=['Temp','PKG_POWER','IPC','IPCpW','frequency','IA32_PERF_STATUS','BR_INST_RETIRED.ALL_BRANCHES','UNC_M_CAS_COUNT.WR','UNC_M_CAS_COUNT.RD'], eps=eps, min_samples=min_samples)
                                    #a.cluster(algorithm='dbscan', metrics=['Temp','PKG_POWER','IPC','IPCpW','frequency','INST_RETIRED.ANY','CPU_CLK_UNHALTED.THREAD','CPU_CLK_UNHALTED.REF_TSC','IA32_PERF_STATUS','ARITH.FPU_DIV','BR_INST_RETIRED.ALL_BRANCHES','UNC_M_CAS_COUNT.WR','UNC_M_CAS_COUNT.RD','APERF','MPERF','TSC','Temp','OPENMP.INST','OPENMP.ID'], eps=eps, min_samples=min_samples)
                                    #a.data.to_csv('clusters_phase1_set2_prime95_run1.csv', index=False)
                                    (eps, min_samples) = (0.6, 60) if processor == 1 else (0.5, 20)
                                    a.cluster(epoch, processor, algorithm='dbscan', metrics=['Temp', 'PKG_POWER', 'IPC'], eps=eps, min_samples=min_samples)
                                    #if a.clusters >= 2 and a.normalRatio > 0.6:
                                    print('time=%d, proc=%d, eps=%.2f, min_samples=%d' % (epoch, processor, eps, min_samples) )
                                    print('number of clusters: %d' % a.clusters)
                                    print('ratio of non-noise: %.2f' % a.normalRatio )
                                    print()
                                    a.draw(epoch, processor, eps, min_samples)
                                period += 1

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

    def readData(self):
        import os.path
        self.name = '%s_phase%d_set%d_%s_pcap%d_run%d' % (self.level, self.phase, self.setID, self.app, self.pcap, self.runID)
        if os.path.isfile('data/%s.csv' % self.name):
            self.data = pd.read_csv('data/%s.csv' % self.name)
            self.exist = True
        else:
            print('file not exist.')
            self.exist = False

    def getfolders(self, extendpath):
        from os import walk
        return [x[0] for x in walk(extendpath)][1:]

    def cluster(self, epoch, processor, algorithm, metrics, eps, min_samples):
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import StandardScaler
        self.selecData = self.data[ (self.data['time']==epoch) & (self.data['processor']==processor) ].copy()
        train = StandardScaler().fit_transform(self.selecData[metrics])
        if algorithm == 'dbscan':
            db = DBSCAN(eps=eps, min_samples=min_samples).fit(train)
            n_clusters_ = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
            self.selecData['cluster'] = db.labels_
            self.clusters = n_clusters_
            self.normalRatio = 1 - self.selecData['cluster'].value_counts()[-1] / self.selecData['cluster'].count()

    def draw(self, epoch, processor, eps, min_samples):
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set(font_scale=4)
        sns.set_style('whitegrid', {'grid.color':'.15', 'axes.edgecolor':'.15'})
        g = sns.pairplot(self.selecData, kind='scatter', x_vars=['Temp'], y_vars=['IPC'], 
                        #vars=['node', 'processor', 'cluster'], 
                        #vars=['node','Temp','IPC','PKG_POWER'],
                        hue='cluster', #hue_order=[0, 7], 
                        palette=sns.color_palette('Set2',10), size=20)
        plt.title('%s_proc%d_period%d_eps%.2f_samples%d' % (self.name, processor, epoch, eps, min_samples) )
        g.axes[0,0].set_xlim(50,85)
        g.axes[0,0].set_ylim(2,2.25)
        g.savefig('oneProcCluster/%s_proc%d_period%d_eps%.2f_samples%d.png' % (self.name, processor, epoch, eps, min_samples) )
        plt.close()

if __name__ == '__main__':
    main()
