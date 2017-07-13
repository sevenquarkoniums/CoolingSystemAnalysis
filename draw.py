#!/Users/zhang51/anaconda/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess

def main():
    p = ['node', 'Temp', 'IPC', 'IPCpW', 'PKG_POWER', 'frequency']
    #coreData(mode='scatter', figFolder='cabFig', allTime=False, x=p[1], y=p[3])
    compare(figFolder='cabFig', x=p[4], y=p[2])
    #ipmi(figFolder='cabFig')
    #correlation()

    #t = timeseries()
    #t.getData('rawdata/quartzPrime95/cores_36/quartz1000/rank_0')
    #core = 0
    #t.getData('rawdata/mg_s1_p90_r2/cores_36/quartz1000/rank_0', core)
    #for metric in ['frequency']:#['frequency', 'IPC', 'PKG_POWER.0', 'Temp.00']:
    #    t.draw(metric, 'quartz_mg.C_core%02d'%core)

class timeseries():
    def __init__(self):
        pass

    def getfolders(self, path):
        from os import walk
        self.folders = [x[0] for x in walk(path)][1:]

    def getData(self, fname, core=0):
        df = pd.read_csv(fname, sep='\t')
        self.data = df[['Timestamp.g','Node','PKG_POWER.0','Temp.%02d'%core]].copy()
        self.data['IPC'] = (df['INST_RETIRED.ANY.%02d'%core].shift(-1) - df['INST_RETIRED.ANY.%02d'%core]) / (df['TSC.%02d'%core].shift(-1) - df['TSC.%02d'%core])
        self.data['frequency'] = 2.1 * (df['APERF.%02d'%core].shift(-1) - df['APERF.%02d'%core]) / (df['MPERF.%02d'%core].shift(-1) - df['MPERF.%02d'%core])

    def draw(self, metric, title):
        sns.set(font_scale=4)
        sns.set_style('white')
        fig, ax = plt.subplots(figsize=(20,10))
        sns.tsplot(self.data[metric])
        plt.title(title)
        #g.axes[0,0].set_xlim(1,1400)
        ax.set_xlim(0,600)
        ax.set_ylim(2.2,2.4)
        ax.set(xlabel='Time', ylabel=metric)
        plt.savefig('timeseries/%s_%s.png' % (metric, title) )
        plt.close()
        print(title)
        
def ipmi(figFolder):
    phase = 2
    setID = 1
    app = 'prime95'
    getTime = pd.read_csv('data/cab/processor_phase%d_set%d_%s_pcap115_run1.csv' % (phase, setID, app) )
    end = getTime['time'].max()
    if phase == 1:
        df = pd.read_csv('data/cabipmi/set_%d/ipmi.dat'%setID, sep=' ')
    elif phase == 2:
        df = pd.read_csv('data/cabipmi/ipmi_phase2.dat', sep=' ')
    oneTime = df[df['epoch']==end].copy()
    oneTime['DIMM_Thrm_Mrgn_avg'] = (oneTime['DIMM_Thrm_Mrgn_1'] + oneTime['DIMM_Thrm_Mrgn_2'] + oneTime['DIMM_Thrm_Mrgn_3'] + oneTime['DIMM_Thrm_Mrgn_4']) / 4
    title = 'ipmi_phase%d_set%d_%s_run1_DIMM_Thrm_Mrgn_avg' % (phase, setID, app)
    drawing(oneTime, figFolder, title, 'node', 'DIMM_Thrm_Mrgn_avg')
    #for metric in ['BB_Inlet_Temp','SSB_Temp','BB_BMC_Temp','P1_VR_Temp','IB_Temp','LAN_NIC_Temp','P1_Therm_Margin','P2_Therm_Margin','DIMM_Thrm_Mrgn_1','DIMM_Thrm_Mrgn_2','DIMM_Thrm_Mrgn_3','DIMM_Thrm_Mrgn_4']:
    #for metric in ['BB_Inlet_Temp','SSB_Temp','BB_BMC_Temp','P1_VR_Temp','IB_Temp','LAN_NIC_Temp','P1_Therm_Margin','P2_Therm_Margin','DIMM_Thrm_Mrgn_1','DIMM_Thrm_Mrgn_2','DIMM_Thrm_Mrgn_3','DIMM_Thrm_Mrgn_4','BB_P12V','BB_P3_3V','BB_P5V_STBY','BB_P1_Vcc','BB_P2_Vcc','BB_+1.5_P1DDR_AB','BB_+1.5_P1DDR_CD','BB_+1.5_P2DDR_AB','BB_+1.5_P2DDR_CD','BB_P1_8V_AUX','BB_+1.1V_SB','BB_P3_3V_STBY','BB_1_1V_PCH']:
    #    title = 'ipmi_phase1_set1_prime95_run1_%s' % metric
    #    drawing(oneTime, figFolder, title, 'node', metric)

def compare(figFolder, x='PKG_POWER', y='IPCpW'):
    compare = 'phase'
    if compare == 'PowerCap':
        app = 'mg.C'
        data1 = pd.read_csv('data/cab/avg10_processor_phase1_set1_%s_pcap115_run1.csv' % app)
        data2 = pd.read_csv('data/cab/avg10_processor_phase1_set14_%s_pcap51_run1.csv' % app)
        data1['PowerCap'] = [115] * len(data1)
        data2['PowerCap'] = [51] * len(data2)
    elif compare == 'phase':
        app = 'mg.C'
        data1 = pd.read_csv('data/cab/avg10_processor_phase1_set14_%s_pcap115_run1.csv' % app)
        data2 = pd.read_csv('data/cab/avg10_processor_phase2_set25_%s_pcap115_run1.csv' % app)
        data1['phase'] = [1] * len(data1)
        data2['phase'] = [2] * len(data2)
    time1 = data1['time'].max()
    time2 = data2['time'].max()
    merged = pd.concat([ data1[data1['time']==time1], data2[data2['time']==time2] ], ignore_index=True)
    newtitle = 'comp%s_%s%s_set1_%s_run1' % (compare, x, y, app)
    pic = drawing(merged, 'scatter', figFolder, newtitle, x, y, compare)
    subprocess.call('open %s' % pic, shell=True)
    #merged = addLayout(merged)
    #compRack(merged, figFolder, newtitle, metric='PKG_POWER')

def correlation():
    phase = 2
    df1 = pd.read_csv('data/cab/processor_phase%d_set1_prime95_pcap115_run1.csv' % phase)
    end = df1['time'].max()
    proc1 = df1[ (df1['time']==end) & (df1['processor']==1) ][['node','Temp']].copy()
    proc1.rename(columns={'Temp':'Temp_processor1'}, inplace=True)

    if phase == 1:
        df2 = pd.read_csv('data/cabipmi/set_1/ipmi.dat', sep=' ')
    elif phase == 2:
        df2 = pd.read_csv('data/cabipmi/ipmi_phase2.dat', sep=' ')
    df2end = df2[ df2['epoch']==end ][['node', 'BB_Inlet_Temp']]
    merged = pd.merge(proc1, df2end, on='node')
    newtitle = 'inletTemp_phase%d_set1_prime95_run1' % phase
    drawing(merged, 'reg', 'cabFig', newtitle, 'Temp_processor1', 'BB_Inlet_Temp')

def coreData(mode, figFolder, allTime, x, y):
    #metrics = ['Temp','IPC','IPCpW','PKG_POWER','DRAM_POWER']
    files = getfiles('data/cab/')
    for f in files:
        #level = f.split('/')[-1].split('_')[0]
        #app = f.split('/')[-1].split('_')[2]
        #phase = int(f.split('/')[-1].split('_')[1][5])
        #if level == 'processor' and app == 'mg.C':
        if f.split('/')[-1] == 'avg10_processor_phase2_set25_mg.C_pcap115_run1.csv':
        #if f.split('/')[-1].startswith('avg10'):
            title = f.split('/')[-1].split('.csv')[0]
            df = pd.read_csv(f)
            #metrics = set(df.columns) - set(['time','exactTime','node','processor'])
            times = sorted(list(set(df['time'])))
            if mode == 'scatter':
                if allTime:
                    period = 0
                    for time in times:
                        newtitle = title + '_%s%s_time%d' % (x, y, 10*period)
                        drawing(df[ (df['time']==time) ], 'scatter', figFolder, newtitle, x, y, 'processor')
                        #for processor in [1,2]:
                            #newtitle = title + '_proc%d_period%d' % (processor, period)
                            #drawing(df[ (df['time']==time) & (df['processor']==processor) ], newtitle)
                        period += 1
                else:
                    time = times[-1]
                    oneTime = df[ (df['time']==time) ].copy()
                    merged = addLayout(oneTime)
                    newtitle = title# + '_%s%s' % (x, y)
                    pic = drawing(merged, 'scatter', figFolder, newtitle, x, y, 'processor')
                    subprocess.call('open %s' % pic, shell=True)
                    #for rack in range(1, 24):
                    #    newtitle = title + '_TempIPCpW_rack%d' % rack
                    #    oneRack = merged[merged['Rack']==rack]
                    #    if len(oneRack) != 0:
                    #        drawing(oneRack, figFolder, newtitle)
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

def drawing(df, mode, folder, title, x, y, hue='no'):
    import matplotlib.patches as patches
    print(folder + '/' + title)
    sns.set(font_scale=4)
    sns.set_style('white')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
    if mode == 'scatter':
        g = sns.pairplot(df, kind='scatter', size=20, x_vars=[x], y_vars=[y], 
                        #vars=['node', 'Temp', 'PKG_POWER', 'IPC', 'IPCpW'], 
                        hue=hue if hue!='no' else None,
                        palette=sns.color_palette('Set2',10) )
    elif mode == 'reg':
        g = sns.jointplot(data=df, kind='reg', x=x, y=y, size=20)
    plt.title(title)
    #g.axes[0,0].set_xlim(35,95)
    #g.axes[0,0].set_ylim(0.008,0.011)
    #if 'mg.C' in title:
    #    g.axes[0,0].set_xlim(0.7,1.3)
    #    g.axes[0,0].set_ylim(90,115)
    #elif 'prime95' in title:
    #    g.axes[0,0].set_xlim(2,2.25)
    #    g.axes[0,0].set_ylim(105,115)
    #for position in list(range(70, 631, 70)) + [650,670,690,760,830,900,970,974,1044,1114,1184,1254]:
    #    plt.axvline(x=position, color='b')
    if x == 'node':
        g.axes[0,0].set_xlim(0,1550)
        alpha = 0.15
        for position in list(range(0, 631, 140)) + [690,830,1044,1184,1296]:
            g.axes[0,0].add_patch(patches.Rectangle((position, -100),70,250,alpha=alpha))
        for position in [650]:
            g.axes[0,0].add_patch(patches.Rectangle((position, -100),20,250,alpha=alpha))
        for position in [970]:
            g.axes[0,0].add_patch(patches.Rectangle((position, -100),4,250,alpha=alpha))
    name = '%s/%s.png' % (folder, title)
    g.savefig(name)
    plt.close()
    return name

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
