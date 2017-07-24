#!/Users/zhang51/anaconda/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess

def main():
    p = {0:'Node ID', 1:'Temperature (degree Celcius)', 2:'Instruction per Cycle', 3:'Instruction per Cycle per Watt', 4:'Processor Power (W)', 5:'Frequency (GHz)', 6:'UNC_M_CAS_COUNT.WR', 7:'UNC_M_CAS_COUNT.RD', 8:'BR_INST_RETIRED.ALL_BRANCHES', 9:'runtime', 10:'Power-Cap (W)', 11:'Energy (kJ)', 12:'EnergyTime (J*seconds)'}
    for i in [1,4,9,11]:
        compare(figFolder='quartzFig', mode='box', app='lulesh', compare=p[10], x=p[10], y=p[i])#, runtime=t)
    #for app in ['mg.C', 'prime95','lulesh']:
    #    compare(figFolder='poster', mode='box', app=app, compare=p[10], x=p[10], y=p[3])#, runtime=t)
    #    compare(figFolder='quartzFig', mode='scatter', app=app, compare=p[10], x=p[4], y=p[11])#, runtime=t)
    #compare(figFolder='quartzFig', mode='reg', app=None, compare='timeTemp')#, runtime=t)

    #coreData(mode='scatter', figFolder='quartzFig', allTime=False, x=p[0], y=p[9])

    #ipmi(figFolder='cabFig')
    #correlation()

    #t = timeseries()
    #import os.path
    #for n in [294,329]:
    #    fname = 'rawdata/pr_s1_p50_r3/cores_36/quartz%d/rank_0' % n
    #    if os.path.isfile(fname):
    #        t.getData(fname, core=0)
    #        for metric in ['frequency']:#['frequency', 'IPC', 'PKG_POWER.0', 'Temp.00']:
    #            pic = t.draw(metric, 'quartz_pr_s1_p50_r3_node%d_core00' % n)

class timeseries():
    def __init__(self):
        pass

    def getfolders(self, path):
        from os import walk
        self.folders = [x[0] for x in walk(path)][1:]

    def getData(self, fname, core=1):
        df = pd.read_csv(fname, sep='\t')
        self.data = df[['Timestamp.g','Node','PKG_POWER.0','Temp.%02d'%core]].copy()
        self.data['IPC'] = (df['INST_RETIRED.ANY.%02d'%core].shift(-1) - df['INST_RETIRED.ANY.%02d'%core]) / (df['TSC.%02d'%core].shift(-1) - df['TSC.%02d'%core])
        self.data['frequency'] = 2.1 * (df['APERF.%02d'%core].shift(-1) - df['APERF.%02d'%core]) / (df['MPERF.%02d'%core].shift(-1) - df['MPERF.%02d'%core])

    def draw(self, metric, title):
        sns.set(font_scale=2)
        sns.set_style('white')
        fig, ax = plt.subplots(figsize=(10,5))
        sns.tsplot(self.data[metric])
        plt.title(title)
        #ax.set_xlim(0,600)
        ax.set_ylim(0,0.9)
        ax.set(xlabel='Time', ylabel=metric)
        pic = 'timeseries/%s_%s.png' % (metric, title)
        plt.savefig(pic)
        plt.close()
        print(title)
        subprocess.call('open %s' % pic, shell=True)
        return pic
        
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

def compare(figFolder, mode, app, compare, x='PKG_POWER', y='IPCpW', runtime=-1):
    if compare == 'Power-Cap (W)':
        data,time,oneTime,dataset = {},{},[],{}
        #if mode == 'scatter':
        #    dataset['prime95'] = [(1,120,3),(4,90,3),(5,70,2),(6,50,3)]
        #    dataset['mg.C'] = [(1,120,3),(4,90,3),(5,70,3),(6,50,2)]
        #    dataset['lulesh'] = [(1,120,3),(4,90,3),(5,70,3),(6,50,3)]
        #    dataset['firestarter'] = [(1,120,3),(2,110,3),(3,100,3)]
        dataset['prime95'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,2),(6,50,3)]
        dataset['mg.C'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,3),(6,50,2)]
        dataset['lulesh'] = [(1,120,3),(2,110,2),(3,100,3),(4,90,2),(5,70,3),(6,50,3)]
        dataset['firestarter'] = [(1,120,3),(2,110,3),(3,100,3)]
        for idx,pcap,run in dataset[app]:
            data[idx] = pd.read_csv('data/quartz/pavg10_processor_set1_%s_pcap%d_run%d.csv' % (app, pcap, run) )
            data[idx]['Power-Cap (W)'] = [pcap] * len(data[idx])
            if 'runtime' in y or 'Energy' in y:
                runtimeDF = pd.read_csv('data/quartz/runtime_%s_set1_pcap%d_run%d.csv' % (app, pcap, run) )
                data[idx] = pd.merge(data[idx], runtimeDF, on='node')
                data[idx]['Energy (kJ)'] = data[idx]['runtime'] * data[idx]['PKG_POWER'] / 1000
            time[idx] = sorted(set(data[idx]['time']), reverse=False)[runtime]
            oneTime.append( data[idx][data[idx]['time']==time[idx]] )
        merged = pd.concat(oneTime, ignore_index=True)
        merged = merged[ merged['PKG_POWER']>0 ]
        if runtime == -1:
            if mode == 'multiline':
                newtitle = 'comppcap_%s' % (app)
            else:
                newtitle = 'comppcap_%s_%s%s' % (app, x.split(' ')[0], y.split(' ')[0])
        else:
            newtitle = 'comppcap_%s_%s%s_time%d' % (app, x.split(' ')[0], y.split(' ')[0], 10*runtime)
        pic = drawing(merged, mode, figFolder, newtitle, x, y, compare if x != compare else 'no')

    elif compare == 'runtime':
        runtimeDF,dataset = {},{}
        dataset['app'] = [(1,'lulesh',50,3),(2,'mg.C',50,2)]
        for idx,app,pcap,run in dataset['app']:
            runtimeDF[idx] = pd.read_csv('data/quartz/runtime_%s_set1_pcap%d_run%d.csv' % (app, pcap, run) )
            runtimeDF[idx].rename(columns={'runtime':'runtime%d'%idx}, inplace=True)
        merged = pd.merge(runtimeDF[1], runtimeDF[2], on='node')
        newtitle = 'comp_%s' % (compare)
        pic = drawing(merged, mode, figFolder, newtitle, 'runtime1', 'runtime2', 'no')

    elif compare == 'timeTemp':
        df,dataset = {},{}
        df[1] = pd.read_csv('data/quartz/pavg10_processor_set1_%s_pcap%d_run%d.csv' % ('mg.C', 120, 3) )
        time = sorted(set(df[1]['time']), reverse=False)[-1]
        df[1] = df[1][ df[1]['time'] == time ]
        df[2] = pd.read_csv('data/quartz/runtime_%s_set1_pcap%d_run%d.csv' % ('mg.C', 50, 2) )
        merged = pd.merge(df[1], df[2], on='node')
        newtitle = 'comp_%s' % (compare)
        pic = drawing(merged, mode, figFolder, newtitle, 'Temperature (degree Celcius)', 'runtime', 'processor')

    elif compare == 'label':
        data,time,oneTime = {},{},[]
        dataset = [('air_mg_115',1,14,'mg.C',115,3),('air_mg_51',1,14,'mg.C',51,3),('air_pri_115',1,14,'prime95',115,3),('air_pri_51',1,14,'prime95',51,3), ('liq_mg_115',2,25,'mg.C',115,3),('liq_mg_51',2,25,'mg.C',51,3),('liq_pri_115',2,25,'prime95',115,3)]
        for idx,phase,setID,app,pcap,runID in dataset:
            data[idx] = pd.read_csv('data/cab/pavg10_processor_phase%d_set%d_%s_pcap%d_run%d.csv' % (phase, setID, app, pcap, runID) )
            data[idx]['label'] = [idx] * len(data[idx])
            time[idx] = sorted(set(data[idx]['time']), reverse=False)[runtime]
            oneTime.append( data[idx][ (data[idx]['time']==time[idx])] )
        merged = pd.concat(oneTime, ignore_index=True)
        merged = merged[ merged['PKG_POWER']>0 ]
        if runtime == -1:
            newtitle = 'comp%s_%s%s' % (compare, x, y)
        else:
            newtitle = 'comp%s_%s%s_time%d' % (compare, x, y, 10*runtime)
    elif compare == 'qlabel':
        data,time,oneTime = {},{},[]
        dataset = [('mg.C',50,2),('mg.C',70,3),('mg.C',90,3),('mg.C',100,3),('mg.C',110,3),('mg.C',120,3),
                    ('prime95',50,3),('prime95',70,2),('prime95',90,3),('prime95',100,3),('prime95',110,3),('prime95',120,3),
                    ('lulesh',90,3),('lulesh',100,3),('lulesh',110,3),('lulesh',120,3),
                    ('firestarter',100,3),('firestarter',110,3),('firestarter',120,3)]
        for app,pcap,runID in dataset:
            idx = '%s_%d' % (app, pcap)
            data[idx] = pd.read_csv('data/quartz/pavg10_processor_set1_%s_pcap%d_run%d.csv' % (app, pcap, runID) )
            data[idx]['qlabel'] = [idx] * len(data[idx])
            data[idx]['PowerCap'] = [pcap] * len(data[idx])
            data[idx]['app'] = [app] * len(data[idx])
            time[idx] = sorted(set(data[idx]['time']), reverse=False)[runtime]
            oneTime.append( data[idx][ (data[idx]['time']==time[idx])] )
        merged = pd.concat(oneTime, ignore_index=True)
        merged = merged[ merged['PKG_POWER']>0 ]
        if runtime == -1:
            newtitle = 'comp%s_%s%s' % (compare, x, y)
        else:
            newtitle = 'comp%s_%s%s_time%d' % (compare, x, y, 10*runtime)
        pic = drawing(merged, 'pointplot', figFolder, newtitle, x, y, 'app')

    elif compare == 'phase':
        pair = 'mg_51'
        data,time,oneTime,dataset,system = {},{},[],{},{1:'air-cooling',2:'liquid-cooling'}
        dataset['mg_115'] = [('air_mg_115',1,14,'mg.C',115,3),('liq_mg_115',2,25,'mg.C',115,3)]
        dataset['mg_51'] = [('air_mg_51',1,14,'mg.C',51,3),('liq_mg_51',2,25,'mg.C',51,3)]
        dataset['pri_115'] = [('air_pri_115',1,14,'prime95',115,3),('liq_pri_115',2,25,'prime95',115,3)]
        for idx,phase,setID,app,pcap,runID in dataset[pair]:
            data[idx] = pd.read_csv('data/cab/pavg10_processor_phase%d_set%d_%s_pcap%d_run%d.csv' % (phase, setID, app, pcap, runID) )
            data[idx]['System'] = [system[phase]] * len(data[idx])
            time[idx] = sorted(set(data[idx]['time']), reverse=False)[runtime]
            oneTime.append( data[idx][ (data[idx]['time']==time[idx])] )
        merged = pd.concat(oneTime, ignore_index=True)
        merged = merged[ merged['PKG_POWER']>0 ]
        if runtime == -1:
            newtitle = 'comp%s_%s' % (compare, pair)
        else:
            newtitle = 'comp%s_%s%s_%s_time%d' % (compare, x, y, pair, 10*runtime)
        pic = drawing(merged, 'scatter', figFolder, newtitle, x, y, 'System')

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
    files = getfiles('data/quartz/')
    for f in files:
        if f.split('/')[-1].startswith('pavg10_'):
            fnamesplit = f.split('/')[-1].split('_')
            setID = int(fnamesplit[2][3])
            app = fnamesplit[3]
            pcap = int(fnamesplit[4][4:])
            runID = int(fnamesplit[5][3])
            title = f.split('/')[-1].split('.csv')[0]

            if setID == 1 and pcap == 50 and runID == 2:
                df = pd.read_csv(f)
                if 'runtime' in x or 'runtime' in y:
                    runtimeDF = pd.read_csv('data/quartz/runtime_%s_set1_pcap%d_run%d.csv' % (app, pcap, runID) )
                    df = pd.merge(df, runtimeDF, on='node')
                    df['Energy (kJ)'] = df['runtime'] * df['PKG_POWER'] / 1000
                #metrics = set(df.columns) - set(['time','exactTime','node','processor'])
                times = sorted(list(set(df['time'])))
                if mode == 'scatter':
                    if allTime:
                        period = 0
                        for time in times:
                            newtitle = title + '_%s%s_time%d' % (x.split(' ')[0], y.split(' ')[0], 10*period)
                            drawing(df[ (df['time']==time) ].copy(), 'scatter', figFolder, newtitle, x, y, 'processor')
                            #for processor in [1,2]:
                                #newtitle = title + '_proc%d_period%d' % (processor, period)
                                #drawing(df[ (df['time']==time) & (df['processor']==processor) ], newtitle)
                            period += 1
                    else:
                        time = times[-1]
                        oneTime = df[ (df['time']==time) ].copy()
                        #merged = addLayout(oneTime)
                        newtitle = title + '_%s%s' % (x.split(' ')[0], y.split(' ')[0])
                        pic = drawing(oneTime, 'scatter', figFolder, newtitle, x, y, 'processor')
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
    #from colormap import rgb2hex
    q = {0:'Node ID', 1:'Temperature (degree Celcius)', 2:'Instruction per Cycle', 3:'Instruction per Cycle per Watt', 4:'Processor Power (W)', 5:'Frequency (GHz)', 6:'UNC_M_CAS_COUNT.WR', 7:'UNC_M_CAS_COUNT.RD', 8:'BR_INST_RETIRED.ALL_BRANCHES', 9:'Runtime (seconds)', 10:'Power-Cap (W)', 11:'Energy (kJ)', 12:'EnergyTime (J*seconds)'}
    print(folder + '/' + title)
    if 'runtime' in df.columns:
        df.rename(columns={'PKG_POWER':'Processor Power (W)', 'runtime':'Runtime (seconds)', 'node':'Node ID', 'frequency':'Frequency (GHz)', 'Temp':'Temperature (degree Celcius)', 'IPC':'Instruction per Cycle', 'IPCpW':'Instruction per Cycle per Watt'}, inplace=True)
    else:
        df.rename(columns={'PKG_POWER':'Processor Power (W)', 'node':'Node ID', 'frequency':'Frequency (GHz)', 'Temp':'Temperature (degree Celcius)', 'IPC':'Instruction per Cycle', 'IPCpW':'Instruction per Cycle per Watt'}, inplace=True)
    y = 'Runtime (seconds)' if y == 'runtime' else y
    if mode == 'scatter':
        sns.set(font_scale=5)
        sns.set_style('whitegrid')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
        g = sns.pairplot(df, kind='scatter', size=20, aspect=1.2, x_vars=[x], y_vars=[y], 
                        #vars=[q[i] for i in [0,1,2,9,11]], 
                        hue=hue if hue!='no' else None,
                        #palette=sns.color_palette('cubehelix', 19) )
                        palette=sns.color_palette('Set2') )
                        #palette=sns.color_palette('Blues') )
                        #palette=sns.cubehelix_palette(start=0.5, rot=-0.75) )
                        #palette=[rgb2hex(50,50,255),rgb2hex(70,70,255),rgb2hex(90,90,255),rgb2hex(100,100,255),rgb2hex(110,110,255),rgb2hex(120,120,255)] )
        #g.fig.legend(handles=g._legend_data.values(), labels=g._legend_data.keys(), loc='upper right')
        #g.axes[0,0].set_xlim(1.5,2.7)
        #g.axes[0,0].set_ylim(128,155)
        #g.axes[0,0].set_ylim(0.008,0.0105)# mg_115
        #g.axes[0,0].set_xlim(35,100)# mg_115
        #g.axes[0,0].set_ylim(0.0144,0.0156)# mg_51
        #g.axes[0,0].set_xlim(25,65)# mg_51 
        #g.axes[0,0].set_ylim(0.018,0.02)# pri_115
        #g.axes[0,0].set_xlim(40,110)# pri_115
        if x == 'Node ID':
            g.axes[0,0].set_xlim(0,3300)
        #plt.title(title)
        name = '%s/%s.png' % (folder, title)
        g.savefig(name)
    elif mode == 'multiline':
        g = sns.PairGrid(df, x_vars=x, y_vars=y, size=8, aspect=3)
        g.map(sns.violinplot)
        #g.axes[1,0].set_ylim(0,2.6)
        #g.axes[2,0].set_ylim(0,0.7)
        #g.axes[3,0].set_ylim(0,0.011)
        #g.axes[4,0].set_ylim(0,180)
        #g.axes[5,0].set_ylim(0,14000)
        name = '%s/%s.png' % (folder, title)
        g.savefig(name)
    elif mode == 'pointplot':
        fig, ax = plt.subplots(figsize=(10,10))
        g = sns.pointplot(data=df, x=x, y=y, 
                            hue=hue if hue!='no' else None,
                            palette=sns.color_palette('Set2',10) )
        name = '%s/%s.png' % (folder, title)
        plt.savefig(name)
    elif mode == 'reg':
        sns.set(font_scale=5)
        sns.set_style('whitegrid')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
        g = sns.jointplot(data=df, kind='reg', x=x, y=y, size=20)
        name = '%s/%s.png' % (folder, title)
        g.savefig(name)
    elif mode == 'traj':
        g = sns.tsplot(df, time=x, value=y)
    #for position in list(range(70, 631, 70)) + [650,670,690,760,830,900,970,974,1044,1114,1184,1254]:
    #    plt.axvline(x=position, color='b')
    #if x == 'node':
    #    g.axes[0,0].set_xlim(0,1550)
    #    alpha = 0.15
    #    for position in list(range(0, 631, 140)) + [690,830,1044,1184,1296]:
    #        g.axes[0,0].add_patch(patches.Rectangle((position, -100),70,250,alpha=alpha))
    #    for position in [650]:
    #        g.axes[0,0].add_patch(patches.Rectangle((position, -100),20,250,alpha=alpha))
    #    for position in [970]:
    #        g.axes[0,0].add_patch(patches.Rectangle((position, -100),4,250,alpha=alpha))
    elif mode == 'box':
        sns.set(font_scale=3.5)
        sns.set_style('whitegrid')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
        fig, ax = plt.subplots(figsize=(20,8))
        g = sns.boxplot(x=y, y=x, data=df, hue=hue if hue != 'no' else None, whis=1000, orient='h',
                            palette=sns.color_palette('Set3') )
        plt.tight_layout()
        #plt.title(title)
        name = '%s/%s.png' % (folder, title)
        plt.savefig(name)
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
