#!/Users/zhang51/anaconda/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    #coreData(mode='violin', figFolder='cabNodeMetric')
    compPhase(figFolder='cabFig')
    #ipmi()
    #t = timeseries()
    #t.getData('rawdata/mg_s1_p90_r2/cores_36/quartz1000/rank_0')
    #for metric in ['frequency', 'IPC', 'PKG_POWER.0', 'Temp.00']:
    #    t.draw(metric, 'quartz_mg.C')

class timeseries():
    def __init__(self):
        pass

    def getfolders(self, path):
        from os import walk
        self.folders = [x[0] for x in walk(path)][1:]

    def getData(self, fname):
        df = pd.read_csv(fname, sep='\t')
        self.data = df[['Timestamp.g','Node','PKG_POWER.0','Temp.00']].copy()
        self.data['IPC'] = (df['INST_RETIRED.ANY.00'].shift(-1) - df['INST_RETIRED.ANY.00']) / (df['TSC.00'].shift(-1) - df['TSC.00'])
        self.data['frequency'] = 2.4 * (df['APERF.00'].shift(-1) - df['APERF.00']) / (df['MPERF.00'].shift(-1) - df['MPERF.00'])

    def draw(self, metric, title):
        sns.set(font_scale=4)
        sns.set_style('white')
        fig, ax = plt.subplots(figsize=(20,10))
        sns.tsplot(self.data[metric])
        plt.title(title)
        #g.axes[0,0].set_xlim(1,1400)
        #ax.set_ylim(89.5,89.7)
        ax.set(xlabel='Time', ylabel=metric)
        plt.savefig('timeseries/%s_%s.png' % (metric, title) )
        plt.close()
        
def ipmi():
    df = pd.read_csv('ipmi.dat',sep=' ')
    #node = df[df['node']==2]
    #node.to_csv('ipmi_node2.csv', index=False)
    oneTime = df[df['epoch']==1465584164]
    for metric in ['BB_Inlet_Temp','SSB_Temp','BB_BMC_Temp','P1_VR_Temp','IB_Temp','LAN_NIC_Temp','P1_Therm_Margin','P2_Therm_Margin','DIMM_Thrm_Mrgn_1','DIMM_Thrm_Mrgn_2','DIMM_Thrm_Mrgn_3','DIMM_Thrm_Mrgn_4','BB_P12V','BB_P3_3V','BB_P5V_STBY','BB_P1_Vcc','BB_P2_Vcc','BB_+1.5_P1DDR_AB','BB_+1.5_P1DDR_CD','BB_+1.5_P2DDR_AB','BB_+1.5_P2DDR_CD','BB_P1_8V_AUX','BB_+1.1V_SB','BB_P3_3V_STBY','BB_1_1V_PCH']:
        title = 'ipmi_phase1_set2_prime95_run1_end_%s' % metric
        drawing(oneTime, metric, title)

def compPhase(figFolder):
    phase1 = pd.read_csv('data/cab/processor_phase1_set1_prime95_pcap115_run1.csv')
    phase2 = pd.read_csv('data/cab/processor_phase2_set1_prime95_pcap115_run1.csv')
    phase1['phase'] = [1] * len(phase1)
    phase2['phase'] = [2] * len(phase2)
    time1 = phase1['time'].max()
    time2 = phase2['time'].max()
    merged = pd.concat([ phase1[phase1['time']==time1], phase2[phase2['time']==time2] ], ignore_index=True)
    newtitle = 'compPhase_nodePower_set1_prime95_pcap115_run1'
    #drawing(merged, figFolder, newtitle)
    merged = addLayout(merged)

    compRack(merged, figFolder, newtitle, metric='PKG_POWER')

def coreData(mode, figFolder):
    #metrics = ['Temp','IPC','IPCpW','PKG_POWER','DRAM_POWER']
    files = getfiles('data/cab/')
    for f in files:
        level = f.split('/')[-1].split('_')[0]
        app = f.split('/')[-1].split('_')[2]
        #phase = int(f.split('/')[-1].split('_')[1][5])
        #if level == 'processor' and app == 'mg.C':
        if f.split('/')[-1] == 'processor_phase2_set1_prime95_pcap115_run1.csv':
            title = f.split('/')[-1].split('.csv')[0]
            df = pd.read_csv(f)
            #metrics = set(df.columns) - set(['time','exactTime','node','processor'])
            times = sorted(list(set(df['time'])))
            if mode == 'scatter':
                period = 0
                for time in times:
                    newtitle = title + '_Temp_period%d' % (period)
                    drawing(df[ (df['time']==time) ], figFolder, newtitle)
                    #for processor in [1,2]:
                        #newtitle = title + '_proc%d_period%d' % (processor, period)
                        #drawing(df[ (df['time']==time) & (df['processor']==processor) ], newtitle)
                    period += 1
            elif mode == 'violin':
                time = times[-1]
                oneTime = df[ (df['time']==time) ].copy()
                merged = addLayout(oneTime)

                newtitle = title + '_Temp_compRack'
                compRack(merged, figFolder, newtitle, 'Temp')

                #for rack in range(1,24):
                #    newtitle = title + '_rack%d' % (rack)
                #    oneRack = merged[merged['Rack']==rack]
                #    if len(oneRack) != 0:
                #        compRack(oneRack, figFolder, newtitle)
    print('I created some figures!')

def addLayout(df):
    layout = pd.read_csv('cab_layout.csv')
    layout.rename(columns={'Node':'node'}, inplace=True)
    return pd.merge(df, layout, on='node')

def compRack(df, folder, title, metric='Temp'):
    print(title)
    sns.set(font_scale=4)
    sns.set_style('white')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
    fig, ax = plt.subplots(figsize=(20,20))
    sns.violinplot(data=df, x='Rack', y=metric,
                    hue='phase', #hue_order=[0, 7], 
                    inner='box', 
                    palette=sns.color_palette('Set2',10) )
    plt.title(title)
    #g.axes[0,0].set_xlim(0,1450)
    #g.axes[0,0].set_ylim(50,90)
    plt.savefig('%s/%s.png' % (folder, title) )
    plt.close()

def drawing(df, folder, title, metric='Temp'):
    print(title)
    sns.set(font_scale=4)
    sns.set_style('white')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
    g = sns.pairplot(df, kind='scatter', x_vars=['Temp'], y_vars=['IPCpW'], 
                    #vars=['node', 'Temp', 'PKG_POWER', 'IPC', 'frequency'], 
                    hue='phase', #hue_order=[0, 7], 
                    size=20, palette=sns.color_palette('Set2',10) )
    plt.title(title)
    #g.axes[0,0].set_xlim(0,1450)
    g.axes[0,0].set_ylim(0.017,0.021)
    #if 'mg.C' in title:
    #    g.axes[0,0].set_xlim(0.7,1.3)
    #    g.axes[0,0].set_ylim(90,115)
    #elif 'prime95' in title:
    #    g.axes[0,0].set_xlim(2,2.25)
    #    g.axes[0,0].set_ylim(105,115)
    #for position in list(range(70, 631, 70)) + [650,670,690,760,830,900,970,974,1044,1114,1184,1254,1296]:
    #    plt.axvline(x=position, color='r')
    #plt.legend(bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.1)
    g.savefig('%s/%s.png' % (folder, title) )
    plt.close()

def getfiles(path):
    from os import listdir
    from os.path import isfile, join
    files = []
    for f in listdir(path):
        F = join(path, f)
        if isfile(F):
            files.append(F)
    print('File list with %d items created.' % len(files) )
    return files

if __name__ == '__main__':
    main()
