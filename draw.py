#!/Users/zhang51/anaconda/bin/python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import random
import os
from scipy import optimize as opt

def main():
    p = {0:'Node ID', 1:'Temperature (degree Celcius)', 2:'Instructions per Cycle', 3:'Instruction per Cycle per Watt', 4:'Processor Power (W)', 5:'Frequency (GHz)', 6:'UNC_M_CAS_COUNT.WR', 7:'UNC_M_CAS_COUNT.RD', 8:'BR_INST_RETIRED.ALL_BRANCHES', 9:'runtime', 10:'Power-Cap (W)', 11:'Energy (kJ)', 12:'Dram Power (W)', 13:'EnergyTime (J*seconds)', 14:'nan', 15:'Cycle per Instruction', 16:'TSC', 17:'Total Power (W)', 18:'Total Energy (kJ)', 19:'IPS', 20:'LLC_REF', 21:'LLC_MISS', 22:'Runtime (seconds)', 23:'IPCfit', 24:'IPCpWfit', 25:'INST_RETIRED.ANY'}
    #for i in [2,9]:
    #    compare(figFolder='quartzFig', cluster='quartz', mode='box', app='lulesh', compare=p[10], x=p[10], y=p[i])

    paramultiline('app', p, [25,1,2,5,8,12,16,20,21], DAT=False, sock='both')
    #parascatter(p, cluster='quartz', x=p[22], xcap='low', y=[p[i] for i in [2,5,25,8]], ycap='low')
    #ranked('runtime', powercap=50, cluster='quartz', sortapp='ep.D')

    #for i in [2,3,5,9]:
    #    for app in ['cg.C','dgemm','ep.D','firestarter','ft.C','mg.D','prime95','stream']:#['mg.C', 'prime95', 'lulesh', 'firestarter']: 
        #    compare(figFolder='quartzFig', cluster='quartz', mode='scatter', app=app, compare=p[10], x=p[2], y=p[19])
    #linkedline(mode='single', figFolder='quartz2', cluster='quartz', app='dgemm', x=p[4], y='IPCfit')

    #for pcap in [50,90,100,120]:
    #    drawCorr(figFolder='quartzFig', cluster='quartz', mode='reg', ax1=(1,'lulesh',pcap,2,'runtime'), ax2=(1,'lulesh',pcap,3,'runtime') )
    #drawCorr(figFolder='cabFig', cluster='cab', mode='scatter', ax1=(14,'mg.C',115,3,'PKG_POWER'), ax2=(14,'prime95',115,3,'PKG_POWER') )

    #for col,app in enumerate(['cg.C','stream','dgemm','ep.D','firestarter','prime95','ft.C','mg.D']):
    #    drawCorr(figFolder='quartz2', cluster='quartz', mode='reg', ax1=(3,app,50,1,'IPC'), ax2=(3,app,50,2,'IPC') )
    #drawCorr(figFolder='quartz2', cluster='quartz', mode='scatter', ax1=(3,'cg.C',50,2,'IPC'), ax2=(3,'cg.C',50,1,'IPC') )

    #coreData(mode='scatter', cluster='quartz', figFolder='quartzFig', allTime=False, x=p[14], y=p[14])

    #ipmi(figFolder='cabFig')
    #correlation()

    #t = timeseries()
    #import os.path
    #for n in [294,329]:
    #    fname = 'rawdata/pr_s1_p50_r3/cores_36/quartz%d/rank_0' % n
    #    if os.path.isfile(fname):
    #        for core in [0,1,18,19]:
    #            t.getData(fname, core=core)
    #            for metric in ['frequency']:#['frequency', 'IPC', 'PKG_POWER.0', 'Temp.00']:
    #                pic = t.draw(metric, 'quartz_pr_s1_p50_r3_node%d_core%02d' % (n, core) )

def paramultiline(mode, p, metrics, DAT, sock):
    #apps = ['mg.C', 'prime95']
    if DAT:
        apps = ['mg.C','prime95']
    else:
        apps = ['cg.C','stream','dgemm']
        #apps = ['prime95','dgemm','ep.D','firestarter','ft.C','mg.D','stream','cg.C']
    fs = 18
    plt.rc('xtick', labelsize=fs)
    plt.rc('ytick', labelsize=fs)
    fig, ax = plt.subplots(len(metrics), len(apps), figsize=(27,48))
    nodec = {}# record the color for each processor.
    nodecoef = {}# record the alpha coef for each processor.
    v = {}
    fitError = {}# record the fitting error of each app.
    for app in apps:
        fitError[app] = []
    for row,i in enumerate(metrics):
        print(p[i])
        if mode == 'app':
            for col,app in enumerate(apps):
                linkedline(mode='subplots', figFolder='quartz2', cluster='quartz', app=app, run=1, x=p[4], y=p[i], sel=100 if DAT else None, ax=ax, row=row, col=col, fs=fs, rowN=len(metrics), nodec=nodec, nodecoef=nodecoef, v=v, fitError=fitError, DAT=DAT, sock=sock)
        elif mode == 'run2run':
            for col,run in enumerate(range(1,11)):
                linkedline(mode='subplots', figFolder='quartz2', cluster='quartz', app='cg.C', run=run, x=p[4], y=p[i], sel=None, ax=ax, row=row, col=col, fs=fs, rowN=len(metrics), nodec=nodec, nodecoef=nodecoef, v=v, fitError=fitError, DAT=DAT, sock=sock)
    fig.tight_layout()
    if 23 in metrics:
        name = '%s/%s_%s.png' % ('quartz7', 'IPCfit2' if DAT else 'IPCfit', sock)
    else:
        name = '%s/%s_%s_instr.png' % ('quartz7', 'quartz7', sock)
    fig.savefig(name)
    plt.close()
    subprocess.call('open %s' % name, shell=True)

    if 23 in metrics:
        fig2, ax2 = plt.subplots(1, len(apps), figsize=(16,9))
        for col,app in enumerate(apps):
            if len(fitError[app]) > 0:
                ax2[col].boxplot([x for x in fitError[app] if x != 'nan'])
                ax2[col].set_xlabel('Application')
                if col == 0:
                    ax2[0].set_ylabel('Relative Fitting Error')
                ax2[col].text(1,-0.3,app)
                ax2[col].set_ylim(-0.3,0.3)
        fig2.tight_layout()
        name2 = 'quartz7/%s_%s.png' % ('fitError2' if DAT else 'fitError', sock)
        fig2.savefig(name2)
        plt.close()
        subprocess.call('open %s' % name2, shell=True)

def ranked(metric, powercap, cluster, sortapp):
    data,dataset = {},{}
    if cluster == 'quartz':
        #dataset['prime95'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,2),(6,50,3)]
        #dataset['mg.C'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,3),(6,50,2)]
        #dataset['lulesh'] = [(1,120,3),(2,110,2),(3,100,3),(4,90,2),(5,70,3),(6,50,3)]
        #dataset['firestarter'] = [(1,120,3),(2,110,3),(3,100,3)]
        dataset = dict.fromkeys(['cg.C','dgemm','ep.D','firestarter','prime95','stream'], [(1,0,2),(2,120,2),(3,70,2),(4,50,2)])
        dataset['ft.C'] = [(1,0,1),(2,70,2),(3,50,2)]
        dataset['mg.D'] = [(1,0,2),(2,120,2),(3,70,1),(4,50,2)]
        setID = 3
    for app in ['dgemm','cg.C','ep.D','firestarter','ft.C','mg.D','prime95','stream']:
        for idx,pcap,run in dataset[app]:
            fname = 'data/%s/pavgall_processor%s_set%d_%s_pcap%d_run%d.csv' % (cluster, '_phase1' if cluster=='cab' else '', setID, app, pcap, run)
            if os.path.isfile(fname):
                data[(app,pcap)] = pd.read_csv(fname)[['node','processor',metric]]
                data[(app,pcap)].rename(columns={metric:'%s_%s' % (metric, app)}, inplace=True)
            else:
                print('missing file: %s' % fname)
    merged = data[('dgemm',powercap)]
    for app in ['cg.C','ep.D','firestarter','ft.C','mg.D','prime95','stream']:
        merged = merged.merge(data[(app,powercap)], on=['node','processor'], how='inner')
    merged.sort_values('%s_%s' % (metric, sortapp),ascending=True, inplace=True)
    merged['Sorted Node'] = range(len(merged))

    fs = 20
    plt.rc('xtick', labelsize=fs)
    plt.rc('ytick', labelsize=fs)
    fig, ax = plt.subplots(figsize=(16,9))
    for app in ['dgemm','cg.C','ep.D','firestarter','ft.C','mg.D','prime95','stream']:
        ax.plot(merged['Sorted Node'], merged['%s_%s' % (metric, app)], '-')
        ax.text(0, merged['%s_%s' % (metric, app)].min(), app, fontsize=fs)
    ax.set_ylabel(metric, fontsize=fs)
    ax.set_xlabel('Sorted Node', fontsize=fs)
    fig.tight_layout()
    name = '%s/sorted_%s.png' % ('quartz2', metric)
    fig.savefig(name)
    plt.close()
    subprocess.call('open %s' % name, shell=True)

def parascatter(p, cluster, x, xcap, y, ycap):
    apps = ['dgemm','ep.D','firestarter','ft.C','mg.D','prime95','stream','cg.C']
    fs = 24
    plt.rc('xtick', labelsize=fs)
    plt.rc('ytick', labelsize=fs)
    fig, ax = plt.subplots(len(y), len(apps), figsize=(48,27))
    nodec = {}

    for row,metric in enumerate(y):
        print(metric)
        for col,app in enumerate(apps):
            data,dataset = {},{}
            if cluster == 'quartz':
                #dataset['prime95'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,2),(6,50,3)]
                #dataset['lulesh'] = [(1,120,3),(2,110,2),(3,100,3),(4,90,2),(5,70,3),(6,50,3)]
                #dataset['firestarter'] = [(1,120,3),(2,110,3),(3,100,3)]
                #dataset['mg.C'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,3),(6,50,2)]

                dataset = dict.fromkeys(apps, [(1,0,1),(2,120,1),(3,70,1),(4,50,1)])
                #dataset = dict.fromkeys(['cg.C','dgemm','ep.D','firestarter','prime95','stream'], [(1,0,2),(2,120,2),(3,70,2),(4,50,2)])
                #dataset['ft.C'] = [(1,0,1),(2,70,2),(3,50,2)]
                #dataset['mg.D'] = [(1,0,2),(2,120,2),(3,70,1),(4,50,2)]
                setID = 3
            elif cluster == 'cab':
                dataset['mg.C'] = [(1,115,3),(2,51,3)]
                dataset['prime95'] = [(1,115,3),(2,51,3)]
            for idx,pcap,run in dataset[app]:
                fname = 'data/%s7/pavgall_processor%s_set%d_both_%s_pcap%d_run%d.csv' % (cluster, '_phase1' if cluster=='cab' else '', setID, app, pcap, run)
                if os.path.isfile(fname):
                    data[idx] = pd.read_csv(fname)
                else:
                    print('missing file: %s' % fname)
                    return 0
                data[idx]['Power-Cap (W)'] = [pcap] * len(data[idx])
                data[idx].rename(columns={'DRAM_POWER':'Dram Power (W)', 'PKG_POWER':'Processor Power (W)', 'runtime':'Runtime (seconds)', 'node':'Node ID', 'frequency':'Frequency (GHz)', 
                                'Temp':'Temperature (degree Celcius)', 'IPC':'Instructions per Cycle', 'IPCpW':'Instruction per Cycle per Watt'}, inplace=True)
            nodeList = list( set.intersection( *[set(data[idx]['Node ID']) for idx in range(1,idx+1)] ) )
            values = [ data[1 if ycap=='high' else idx][ (data[1 if ycap=='high' else idx]['processor']==1) & (data[1 if ycap=='high' else idx]['Node ID']==node) ][metric].values[0] for node in nodeList ]
            allx = [ data[1 if xcap=='high' else idx][ (data[1 if xcap=='high' else idx]['processor']==1) & (data[1 if xcap=='high' else idx]['Node ID']==node) ][x].values[0] for node in nodeList ]
            nodeV = pd.DataFrame(columns=['node','value'])
            nodeV['node'] = nodeList
            nodeV['value'] = values
            nodeV['x'] = allx
            rb = plt.get_cmap('rainbow')
            vmax = nodeV['value'].max()
            vmin = nodeV['value'].min()
            #ax[col].set_xlim(39, 122)
            if col == 0:
                ax[row][col].set_ylabel(metric, fontsize=fs)
            if row == len(y) - 1:
                ax[row][col].set_xlabel(x, fontsize=fs)
            ax[row][col].text(nodeV['x'].min(), vmin, app, fontsize=fs)
            for node in nodeList:
                for proc in [1,2]:
                    xv = data[1 if xcap=='high' else idx][ (data[1 if xcap=='high' else idx]['processor']==proc) & (data[1 if xcap=='high' else idx]['Node ID']==node) ][x].values[0]
                    yv = data[1 if ycap=='high' else idx][ (data[1 if ycap=='high' else idx]['processor']==proc) & (data[1 if ycap=='high' else idx]['Node ID']==node) ][metric].values[0]
                    if row == 0 and col == 0:# assign color according to the first subplot.
                        nodec[(node,proc)] = rb( (yv - vmin)/(vmax-vmin) )
                    if (node,proc) in nodec:
                        ax[row][col].plot(xv, yv, 'o', color=nodec[(node,proc)])
    fig.tight_layout()
    name = '%s/%s_%s.png' % ('quartz7', x.split(' ')[0], 'metric')
    fig.savefig(name)
    plt.close()
    subprocess.call('open %s' % name, shell=True)

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

def drawCorr(figFolder, cluster, mode, ax1, ax2):
    data = {}
    newtitle = 'comp_%s-%d-%s_%s-%d-%s' % (ax1[1],ax1[2],ax1[4],ax2[1],ax2[2],ax2[4])
    data[1] = pd.read_csv('data/%s/pavgall_processor%s_set%s_%s_pcap%d_run%d.csv' % (cluster, '_phase1' if cluster=='cab' else '', ax1[0], ax1[1], ax1[2], ax1[3]) )
    data[1] = data[1][['node','processor',ax1[4]]]
    data[2] = pd.read_csv('data/%s/pavgall_processor%s_set%s_%s_pcap%d_run%d.csv' % (cluster, '_phase1' if cluster=='cab' else '', ax2[0], ax2[1], ax2[2], ax2[3]) )
    data[2] = data[2][['node','processor',ax2[4]]]
    merged = pd.merge(data[1], data[2], on=['node','processor'])
    pic = drawing(merged, mode, figFolder, newtitle, ('%s_x' % ax1[4]) if ax1[4]==ax2[4] else ax1[4], ('%s_y' % ax2[4]) if ax1[4]==ax2[4] else ax2[4], 'processor', changeAxis=False)
    #data[1] = data[1][['node',ax1[4]]].groupby('node', as_index=False).mean().sort_values(ax1[4], ascending=False)
    #data[2] = data[2][['node',ax1[4]]].groupby('node', as_index=False).mean().sort_values(ax1[4], ascending=False)
    #merged = pd.merge(data[1], data[2], on='node')
    #pic = drawing(merged, mode, figFolder, newtitle, ('%s_x' % ax1[4]) if ax1[4]==ax2[4] else ax1[4], ('%s_y' % ax2[4]) if ax1[4]==ax2[4] else ax2[4], 'no', changeAxis=False)
    subprocess.call('open %s' % pic, shell=True)

def linkedline(mode, figFolder, cluster, app, run, x, y, sel=100, ax=None, row=0, col=0, fs=25, rowN=4, nodec={}, nodecoef={}, v={}, fitError={}, DAT=False, sock='both'):
    data,oneTime,dataset = {},[],{}
    if cluster == 'quartz':
        if DAT:
            dataset['prime95'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,2),(6,50,3)]
            dataset['mg.C'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,3),(6,50,2)]
            dataset['lulesh'] = [(1,120,3),(2,110,2),(3,100,3),(4,90,2),(5,70,3),(6,50,3)]
            dataset['firestarter'] = [(1,120,3),(2,110,3),(3,100,3)]
            setID = 1
        else:
            if run == None:
                dataset = dict.fromkeys(['cg.C','dgemm','ep.D','firestarter','prime95'], [(1,0,2),(2,120,2),(3,70,2),(4,50,2)])
                dataset['stream'] = [(1,0,1),(2,120,1),(3,70,1),(4,50,1)]
                dataset['ft.C'] = [(1,0,1),(2,70,2),(3,50,2)]
                dataset['mg.D'] = [(1,0,2),(2,120,2),(3,70,1),(4,50,2)]
            else:
                dataset = dict.fromkeys(['dgemm','ep.D','firestarter','ft.C','mg.D','prime95','stream','cg.C'], [(1,0,run),(2,120,run),(3,70,run),(4,50,run)])
                #dataset = dict.fromkeys(['cg.C','stream'], [(1,0,run),(2,120,run),(3,70,run),(4,50,run)])
            setID = 3
    elif cluster == 'cab':
        dataset['mg.C'] = [(1,115,3),(2,51,3)]
        dataset['prime95'] = [(1,115,3),(2,51,3)]
        setID = 14

    #intersecNode = set(range(3000))
    #for iapp in ['prime95','mg.C','lulesh','firestarter'] if cluster=='quartz' else ['mg.C','prime95']:
    #    for idx,pcap,run in dataset[iapp]:
    #        data[idx] = pd.read_csv('data/%s/pavgall_processor%s_set%d_%s_pcap%d_run%d.csv' % (cluster, '_phase1' if cluster=='cab' else '', 1 if cluster=='quartz' else 14, iapp, pcap, run) )
    #        intersecNode = intersecNode & set(data[idx]['node'])
    #random.seed(1)
    #nodeList = random.sample(intersecNode, sel)

    for idx,pcap,run in dataset[app]:
        fname = 'data/%s7/pavgall_processor%s_set%d_%s_%s_pcap%d_run%d.csv' % (cluster, '_phase1' if cluster=='cab' else '', setID, sock, app, pcap, run)
        if os.path.isfile(fname):
            data[idx] = pd.read_csv(fname)
        else:
            print('missing file: %s' % fname)
            return 0
        data[idx]['Power-Cap (W)'] = [pcap if pcap!=0 else 130] * len(data[idx])
        if y == 'Total Power (W)':
            data[idx]['Total Power (W)'] = data[idx]['PKG_POWER'] + data[idx]['DRAM_POWER']
        elif y == 'IPS':
            data[idx]['IPS'] = data[idx]['INST_RETIRED.ANY'] / data[idx]['runtime']
        data[idx]['Energy (kJ)'] = data[idx]['runtime'] * data[idx]['PKG_POWER'] / 1000
        data[idx].rename(columns={'DRAM_POWER':'Dram Power (W)', 'PKG_POWER':'Processor Power (W)', 'runtime':'Runtime (seconds)', 'node':'Node ID', 'frequency':'Frequency (GHz)', 
                        'Temp':'Temperature (degree Celcius)', 'IPC':'Instructions per Cycle', 'IPCpW':'Instruction per Cycle per Watt'}, inplace=True)
        oneTime.append( data[idx] )

    if sock == 'both':
        procs = [1,2]
    else:
        procs = [1]
    x = 'Runtime (seconds)' if x == 'runtime' else x
    y = 'Runtime (seconds)' if y == 'runtime' else y
    if mode == 'single':
        plt.rc('xtick', labelsize=fs)
        plt.rc('ytick', labelsize=fs)
        fig, ax = plt.subplots(figsize=(15,15))
    nodeList = list( set.intersection( *[set(data[idx]['Node ID']) for idx in range(1,len(oneTime)+1)] ) )
    if row == 0:
        print('%s nodeList length: %d' % (app, len(nodeList)) )
    if sel != None:
        nodeList = nodeList[0:sel]
    nodeV = pd.DataFrame(columns=['node','processor','value'])
    for node in nodeList:
        for proc in procs:
            value = data[idx][ (data[idx]['processor']==proc) & (data[idx]['Node ID']==node) ][y if not y.endswith('fit') else 'Instructions per Cycle'].values[0]
            nodeV.loc[len(nodeV)] = [node, proc, value]
    imax = nodeV['value'].idxmax()
    #print(nodeV.loc[imax])
    imin = nodeV['value'].idxmin()
    vmax = nodeV.loc[imax].values[2]
    vmin = nodeV.loc[imin].values[2]
    if y == 'IPCfit' and col == 0:
        v['max'] = nodeV.loc[imax].values
        v['min'] = nodeV.loc[imin].values
    if y.endswith('fit'):
        # only fit curves for the best and worst processor identified in the 1st app.
        ipcs = [ data[idx][ (data[idx]['processor']==v['max'][1]) & (data[idx]['Node ID']==v['max'][0]) ]['Instructions per Cycle'].values[0] for idx in range(1, len(oneTime)+1) ]
        powers = [ data[idx][ (data[idx]['processor']==v['max'][1]) & (data[idx]['Node ID']==v['max'][0]) ]['Processor Power (W)'].values[0] for idx in range(1, len(oneTime)+1) ]
        popt, pcov = opt.curve_fit(f, ipcs, powers)
        Amax, Cmax = popt

        ipcs = [ data[idx][ (data[idx]['processor']==v['min'][1]) & (data[idx]['Node ID']==v['min'][0]) ]['Instructions per Cycle'].values[0] for idx in range(1, len(oneTime)+1) ]
        powers = [ data[idx][ (data[idx]['processor']==v['min'][1]) & (data[idx]['Node ID']==v['min'][0]) ]['Processor Power (W)'].values[0] for idx in range(1, len(oneTime)+1) ]
        popt, pcov = opt.curve_fit(f, ipcs, powers)
        Amin, Cmin = popt

    if mode == 'single':
        title = 'linked_%s_%s%s' % (app, x.split(' ')[0], y.split(' ')[0])
        plt.title(title, fontsize=fs)
        plt.xlabel(x, fontsize=fs)
        plt.ylabel(y, fontsize=fs)
        plt.text(70, vmin, app, fontsize=fs)
    else:
        ax[row][col].set_xlim(39, 122)
        if col == 0:
            ax[row][col].set_ylabel(y, fontsize=fs)
        if row == rowN - 1:
            ax[row][col].set_xlabel(x, fontsize=fs)
        ax[row][col].text(70, vmin, app, fontsize=fs)
        if row < 0:
            ax[row][col].set_ylim(0, 1.6)

    rb = plt.get_cmap('rainbow')
    for node in nodeV['node']:
        for proc in procs:
            if not y.endswith('fit'):
                xs = [ data[idx][ (data[idx]['processor']==proc) & (data[idx]['Node ID']==node) ][x].values[0] for idx in range(1,len(oneTime)+1) ]
                ys = [ data[idx][ (data[idx]['processor']==proc) & (data[idx]['Node ID']==node) ][y].values[0] for idx in range(1,len(oneTime)+1) ]
            elif y == 'IPCfit':
                if col == 0:
                    power, ipc = data[idx][ (data[idx]['processor']==proc) & (data[idx]['Node ID']==node) ][['Processor Power (W)', 'Instructions per Cycle']].values[0]# the power, ipc at 50W powercap.
                    nodecoef[(node, proc)] = (power - Amax * ipc**2 - Cmax) / ( (Amin - Amax) * ipc**2 + Cmin - Cmax )
                if (node, proc) in nodecoef:
                    A = nodecoef[(node, proc)] * Amin + (1 - nodecoef[(node, proc)]) * Amax
                    C = nodecoef[(node, proc)] * Cmin + (1 - nodecoef[(node, proc)]) * Cmax
                    xs = np.linspace(40, 120)
                    ys = np.sqrt( (xs - C)/A )

                    powers = [ data[idx][ (data[idx]['processor']==proc) & (data[idx]['Node ID']==node) ]['Processor Power (W)'].values[0] for idx in range(1,len(oneTime)+1) ]
                    ipcs = [ data[idx][ (data[idx]['processor']==proc) & (data[idx]['Node ID']==node) ]['Instructions per Cycle'].values[0] for idx in range(1,len(oneTime)+1) ]
                    for i, ipower in enumerate(powers):
                        fitError[app].append( np.sqrt( (ipower - C)/A ) / ipcs[i] - 1 )
                else:
                    continue
            elif y == 'IPCpWfit':
                if (node, proc) in nodecoef:
                    A = nodecoef[(node, proc)] * Amin + (1 - nodecoef[(node, proc)]) * Amax
                    C = nodecoef[(node, proc)] * Cmin + (1 - nodecoef[(node, proc)]) * Cmax
                    xs = np.linspace(40, 120)
                    ys = np.sqrt( (xs - C)/A ) / xs
                else:
                    continue
            if row == 0 and col == 0:# assign color according to the first subplot.
                if y!= 'IPCfit':
                    nodec[(node,proc)] = rb( (vmax - ys[len(oneTime)-1])/(vmax-vmin) )
                else:
                    nodec[(node,proc)] = rb( nodecoef[(node, proc)] ) 
            if (node,proc) in nodec:
                if mode == 'single':
                    plt.plot(xs, ys, '-' if y.endswith('fit') else '-o', color=nodec[(node,proc)])
                else:
                    ax[row][col].plot(xs, ys, '-' if y.endswith('fit') else '-o', color=nodec[(node,proc)])
            #ax[row][col].plot(xs, ys, '-o', color=rb( (ys[len(oneTime)-1] - vmin)/(vmax-vmin) ))
    if mode == 'single':
        name = '%s/%s.png' % (figFolder, title)
        plt.savefig(name)
        plt.close()
        subprocess.call('open %s' % name, shell=True)

def f(ipc, A, C):
    return A * ipc**2 + C

def compare(figFolder, cluster, mode, app, compare, x='PKG_POWER', y='IPCpW', runtime=-1):
    if compare == 'Power-Cap (W)':
        data,time,oneTime,dataset = {},{},[],{}
        #if mode == 'scatter':
        #    dataset['prime95'] = [(1,120,3),(4,90,3),(5,70,2),(6,50,3)]
        #    dataset['mg.C'] = [(1,120,3),(4,90,3),(5,70,3),(6,50,2)]
        #    dataset['lulesh'] = [(1,120,3),(4,90,3),(5,70,3),(6,50,3)]
        #    dataset['firestarter'] = [(1,120,3),(2,110,3),(3,100,3)]
        if cluster == 'quartz':
            dataset['prime95'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,2),(6,50,3)]
            dataset['mg.C'] = [(1,120,3),(2,110,3),(3,100,3),(4,90,3),(5,70,3),(6,50,2)]
            dataset['lulesh'] = [(1,120,3),(2,110,2),(3,100,3),(4,90,2),(5,70,3),(6,50,3)]
            dataset['firestarter'] = [(1,120,3),(2,110,3),(3,100,3)]
        elif cluster == 'cab':
            dataset['mg.C'] = [(1,115,3),(2,51,3)]
        for idx,pcap,run in dataset[app]:
            data[idx] = pd.read_csv('data/%s/pavgall_processor%s_set%d_%s_pcap%d_run%d.csv' % (cluster, '_phase1' if cluster=='cab' else '', 1 if cluster=='quartz' else 14, app, pcap, run) )
            data[idx]['Power-Cap (W)'] = [pcap] * len(data[idx])
            if y == 'Total Power (W)':
                data[idx]['Total Power (W)'] = data[idx]['PKG_POWER'] + data[idx]['DRAM_POWER']
            if y == 'IPS':
                data[idx]['IPS'] = data[idx]['INST_RETIRED.ANY'] / data[idx]['runtime']
            data[idx]['Energy (kJ)'] = data[idx]['runtime'] * data[idx]['PKG_POWER'] / 1000
            oneTime.append( data[idx] )
            #time[idx] = sorted(set(data[idx]['time']), reverse=False)[runtime]
            #oneTime.append( data[idx][data[idx]['time']==time[idx]] )
        merged = pd.concat(oneTime, ignore_index=True)
        #merged = merged[ merged['PKG_POWER']>0 ]
        if runtime == -1:
            if mode == 'multiline':
                newtitle = 'comppcap_%s' % (app)
            else:
                newtitle = 'comppcap_%s_%s%s' % (app, x.split(' ')[0], y.split(' ')[0])
        else:
            newtitle = 'comppcap_%s_%s%s_time%d' % (app, x.split(' ')[0], y.split(' ')[0], 10*runtime)
        pic = drawing(merged, mode, figFolder, newtitle, x, y, compare if x != compare else 'no')

    #elif compare == 'runtime':
    #    runtimeDF,dataset = {},{}
    #    dataset['app'] = [(1,'mg.C',50,3),(2,'mg.C',50,2)]
    #    for idx,app,pcap,run in dataset['app']:
    #        runtimeDF[idx] = pd.read_csv('data/quartz/runtime_%s_set1_pcap%d_run%d.csv' % (app, pcap, run) )
    #        runtimeDF[idx].rename(columns={'runtime':'runtime%d'%idx}, inplace=True)
    #    merged = pd.merge(runtimeDF[1], runtimeDF[2], on='node')
    #    newtitle = 'comp_%s' % (compare)
    #    pic = drawing(merged, mode, figFolder, newtitle, 'runtime1', 'runtime2', 'no')

    elif compare == 'power':
        runtimeDF,dataset = {},{}
        dataset['app'] = [(1,'mg.C',120,3),(2,'lulesh',120,3)]
        for idx,app,pcap,run in dataset['app']:
            runtimeDF[idx] = pd.read_csv('data/quartz/pavgall_processor_set1_%s_pcap%d_run%d.csv' % (app, pcap, run) )
        merged = pd.merge(runtimeDF[1], runtimeDF[2], on=['node','processor'])
        newtitle = 'comp_%s' % (compare)
        pic = drawing(merged, mode, figFolder, newtitle, 'PKG_POWER_x', 'PKG_POWER_y', 'no')

    elif compare in ['IPC', 'frequency', 'runtime']:
        runtimeDF,dataset = {},{}
        dataset['app'] = [(1,app[0],50,2),(2,app[1],50,2)]
        for idx,iapp,pcap,run in dataset['app']:
            runtimeDF[idx] = pd.read_csv('data/quartz/pavgall_processor_set1_%s_pcap%d_run%d.csv' % (iapp, pcap, run) )
            runtimeDF[idx] = runtimeDF[idx][['node','processor',compare]]
        merged = pd.merge(runtimeDF[1], runtimeDF[2], on=['node','processor'])
        newtitle = 'comp_%s_%s%s' % (compare, app[0], app[1])
        pic = drawing(merged, mode, figFolder, newtitle, '%s_x' % compare, '%s_y' % compare, 'no')

    elif compare == 'timeIPCpW':
        df,dataset = {},{}
        df[1] = pd.read_csv('data/quartz/pavg10_processor_set1_%s_pcap%d_run%d.csv' % (app, 120, 3) )
        time = sorted(set(df[1]['time']), reverse=False)[-1]
        df[1] = df[1][ df[1]['time'] == time ]
        df[2] = pd.read_csv('data/quartz/runtime_%s_set1_pcap%d_run%d.csv' % (app, 50, 2) )
        merged = pd.merge(df[1], df[2], on='node')
        merged = merged[ (merged['PKG_POWER']>0) & (merged['runtime']>0) ]
        newtitle = 'comp_%s_%s' % (compare, app)
        pic = drawing(merged, mode, figFolder, newtitle, 'Instruction per Cycle per Watt', 'Runtime (seconds)', 'processor')

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

def coreData(mode, cluster, figFolder, allTime, x, y):
    files = getfiles('data/%s/' % cluster)
    for f in files:
        if f.split('/')[-1].startswith('pavgall_'):
            fnamesplit = f.split('/')[-1].split('_')
            if cluster == 'cab':
                setID = int(fnamesplit[3][3:])
                app = fnamesplit[4]
                pcap = int(fnamesplit[5][4:])
                runID = int(fnamesplit[6][3])
            else:
                setID = int(fnamesplit[2][3:])
                app = fnamesplit[3]
                pcap = int(fnamesplit[4][4:])
                runID = int(fnamesplit[5][3])
            title = f.split('/')[-1].split('.csv')[0]

            if app == 'mg.C' and setID == 1 and pcap == 50 and runID == 2:
                df = pd.read_csv(f)
                df['Energy (kJ)'] = df['runtime'] * df['PKG_POWER'] / 1000
                df['IPS'] = df['INST_RETIRED.ANY'] / df['runtime']
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
                        #if cluster == 'cab':
                        #    time = times[-1]
                        #    df = df[ (df['time']==time) ]
                        newtitle = title + '_%s%s' % (x.split(' ')[0], y.split(' ')[0])
                        pic = drawing(df, 'scatter', figFolder, newtitle, x, y, 'processor')
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

def drawing(df, mode, folder, title, x, y, hue='no', changeAxis=True):
    #import matplotlib.patches as patches
    #from colormap import rgb2hex
    q = {0:'Node ID', 1:'Temperature (degree Celcius)', 2:'Instructions per Cycle', 3:'Instruction per Cycle per Watt', 4:'Processor Power (W)', 5:'Frequency (GHz)', 6:'UNC_M_CAS_COUNT.WR', 7:'UNC_M_CAS_COUNT.RD', 8:'BR_INST_RETIRED.ALL_BRANCHES', 9:'Runtime (seconds)', 10:'Power-Cap (W)', 11:'Energy (kJ)', 12:'EnergyTime (J*seconds)'}
    print(folder + '/' + title + '.png')
    if changeAxis:
        if 'runtime' in df.columns:
            df.rename(columns={'DRAM_POWER':'Dram Power (W)', 'PKG_POWER':'Processor Power (W)', 'runtime':'Runtime (seconds)', 'node':'Node ID', 'frequency':'Frequency (GHz)', 
                        'Temp':'Temperature (degree Celcius)', 'IPC':'Instructions per Cycle', 'IPCpW':'Instruction per Cycle per Watt'}, inplace=True)
        else:
            df.rename(columns={'DRAM_POWER':'Dram Power (W)', 'PKG_POWER':'Processor Power (W)', 'node':'Node ID', 'frequency':'Frequency (GHz)', 'Temp':'Temperature (degree Celcius)', 
                        'IPC':'Instructions per Cycle', 'IPCpW':'Instruction per Cycle per Watt'}, inplace=True)
        x = 'Runtime (seconds)' if x == 'runtime' else x
        y = 'Runtime (seconds)' if y == 'runtime' else y
    if mode == 'scatter':
        sns.set(font_scale=5)
        sns.set_style('whitegrid')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
        g = sns.pairplot(df, kind='scatter', size=20, aspect=1, x_vars=[x] if x!= 'nan' else None, y_vars=[y] if x!= 'nan' else None, 
                        vars=None if x!='nan' else [q[i] for i in [1,2,3,4,5,9]], 
                        hue=hue if hue!='no' else None,
                        #palette=sns.color_palette('cubehelix', 19) )
                        palette=sns.color_palette('Set2') )
                        #palette=sns.color_palette('Blues') )
                        #palette=sns.cubehelix_palette(start=0.5, rot=-0.75) )
                        #palette=[rgb2hex(50,50,255),rgb2hex(70,70,255),rgb2hex(90,90,255),rgb2hex(100,100,255),rgb2hex(110,110,255),rgb2hex(120,120,255)] )
        #g.fig.legend(handles=g._legend_data.values(), labels=g._legend_data.keys(), loc='upper right')
        #g.axes[0,0].set_ylim(0.008,0.0105)# mg_115
        #g.axes[0,0].set_xlim(35,100)# mg_115
        #g.axes[0,0].set_ylim(0.0144,0.0156)# mg_51
        #g.axes[0,0].set_xlim(25,65)# mg_51 
        #g.axes[0,0].set_ylim(0.018,0.02)# pri_115
        #g.axes[0,0].set_xlim(40,110)# pri_115
        if x == 'Node ID' and 'quartz' in folder:
            g.axes[0,0].set_xlim(0,3300)
        plt.title(title)
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
        sns.set(font_scale=2)
        sns.set_style('whitegrid')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
        g = sns.jointplot(data=df, kind='reg', x=x, y=y, size=10)
        name = '%s/%s.png' % (folder, title)
        plt.title(title, y=-0.15)
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
