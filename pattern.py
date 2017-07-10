#!/Users/zhang51/anaconda/bin/python
'''
by Yijia Zhang at June 22, 2017

Machine learning analysis of the data.
Using DBSCAN clustering algorithm to cluster the 3-d data (Temp, Power, IPC).
'''
import time
import pandas as pd

def main():
    start = time.time()

    #findPara()
    compareCluster(compare='epoch')

    duration = time.time() - start
    print('finished in %d seconds.' % round(duration) )

def findPara():
    for phase in [1]:
        for setID in range(1, 2):
            for app in ['prime95']:
                for pcap in [90]:
                    for runID in [1]:
                        machine = 'quartz'
                        a = analysis(machine, phase, setID, app, pcap, runID, level='processor')
                        a.readData()

                        #for (eps, min_samples) in [(0.3,20),(0.4,30),(0.5,60),(0.6,100),(0.7,160),(0.8,240)]:
                        if a.exist:
                            a.times = sorted(list(set(a.data['time'])), reverse=True)
                            period = 0
                            epoch = a.times[0]
                            #for epoch in a.times:
                            for processor in [1]:
                                #(eps, min_samples) = (0.6, 60) if processor == 1 else (0.5, 20)
                                for eps in [x/10 for x in range(1, 10)]:
                                    for min_samples in range(10, 101, 10):
                                        a.cluster(epoch, processor, algorithm='dbscan', metrics=['Temp', 'PKG_POWER', 'IPC'], eps=eps, min_samples=min_samples)
                                        #if period == 9:
                                        #    a.selecData.to_csv('prime95_proc1_clusters.csv',index=False)
                                        if a.clusters >= 2 and a.normalRatio > 0.85:
                                            print('time=%d, proc=%d, eps=%.2f, min_samples=%d' % (epoch, processor, eps, min_samples) )
                                            print('number of clusters: %d' % a.clusters)
                                            print('ratio of non-noise: %.2f' % a.normalRatio )
                                            print()
                                            a.draw(99, processor, eps, min_samples)
                            period += 1

def compareCluster(compare):
    data1 = analysis(machine='quartz', phase=1, setID=1, app='prime95', pcap=90, runID=1, level='processor')
    data1.readData()
    data1.epoch = sorted(list(set(data1.data['time'])), reverse=True)[0]
    data1.cluster(data1.epoch, processor=1, algorithm='dbscan', metrics=['Temp', 'PKG_POWER', 'IPC'], eps=0.4, min_samples=10)

    if compare == 'app':
        mg = analysis(phase=1, setID=1, app='mg.C', pcap=115, runID=1, level='processor')
        mg.readData()
        mg.epoch = sorted(list(set(mg.data['time'])), reverse=True)[0]
        mg.cluster(mg.epoch, processor=1, algorithm='dbscan', metrics=['Temp', 'PKG_POWER', 'IPC'], eps=0.6, min_samples=60)

        mg.selecData.drop(['cluster'], axis=1, inplace=True)
        mg.selecData = pd.merge(mg.selecData, data1.selecData[['node','cluster']], on='node')
        mg.draw(99, 1, 0.6, 60)# draw using the cluster from prime95.
    elif compare == 'set':
        data2 = analysis(phase=1, setID=2, app='prime95', pcap=115, runID=1, level='processor')
        data2.readData()
        if len(set(data2.data['time'])) == 0:
            return 1
        data2.epoch = sorted(list(set(data2.data['time'])), reverse=True)[0]
        data2.cluster(data2.epoch, processor=1, algorithm='dbscan', metrics=['Temp', 'PKG_POWER', 'IPC'], eps=0.6, min_samples=60)

        data2.selecData.drop(['cluster'], axis=1, inplace=True)
        data2.selecData = pd.merge(data2.selecData, data1.selecData[['node','cluster']], on='node')
        data2.draw(99, 1, 0.6, 60, compSet)# draw using the cluster from prime95.
    elif compare == 'epoch':
        data2 = analysis(machine='quartz', phase=1, setID=1, app='prime95', pcap=90, runID=1, level='processor')
        data2.readData()
        epochs = sorted(list(set(data2.data['time'])))
        for data2.epoch in epochs:
            data2.cluster(data2.epoch, processor=1, algorithm='dbscan', metrics=['Temp', 'PKG_POWER', 'IPC'], eps=0.4, min_samples=10)
            data2.selecData.drop(['cluster'], axis=1, inplace=True)
            data2.selecData = pd.merge(data2.selecData, data1.selecData[['node','cluster']], on='node')
            data2.draw(period=data2.epoch, processor=1, eps=0.4, min_samples=10)# draw using the cluster from prime95.

class analysis:
    '''
    Pattern recognitino.
    '''
    def __init__(self, machine, phase, setID, app, pcap, runID, level):
        self.machine = machine
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
        '''
        Check file existence and read.
        '''
        import os.path
        if self.machine == 'cab':
            self.name = '%s_phase%d_set%d_%s_pcap%d_run%d' % (self.level, self.phase, self.setID, self.app, self.pcap, self.runID)
        elif self.machine == 'quartz':
            self.name = '%s_set%d_%s_pcap%d_run%d' % (self.level, self.setID, self.app, self.pcap, self.runID)

        if os.path.isfile('data/%s/%s.csv' % (self.machine, self.name) ):
            self.data = pd.read_csv('data/%s/%s.csv' % (self.machine, self.name) )
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

    def draw(self, period, processor, eps, min_samples):
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set(font_scale=4)
        sns.set_style('whitegrid', {'grid.color':'.15', 'axes.edgecolor':'.15'})
        g = sns.pairplot(self.selecData, kind='scatter', x_vars=['IPC'], y_vars=['PKG_POWER'], 
                        #vars=['node', 'processor', 'cluster'], 
                        #vars=['node','Temp','IPC','PKG_POWER'],
                        hue='cluster', #hue_order=[0, 7], 
                        palette=sns.color_palette('Set2',10), size=20)
        plt.title('%s_proc%d_period%d_eps%.2f_samples%d' % (self.name, processor, period, eps, min_samples) )
        #g.axes[0,0].set_xlim(105,115)
        #g.axes[0,0].set_ylim(2,2.25)
        g.savefig('quartzCluster/%s_proc%d_period%d_eps%.2f_samples%d_clusterFromEnd.png' % (self.name, processor, period, eps, min_samples) )
        plt.close()

if __name__ == '__main__':
    main()
