#!/Users/zhang51/anaconda/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    coreData()
    #ipmi()

def ipmi():
    df = pd.read_csv('ipmi.dat',sep=' ')
    #node = df[df['node']==2]
    #node.to_csv('ipmi_node2.csv', index=False)
    oneTime = df[df['epoch']==1465584164]
    for metric in ['BB_Inlet_Temp','SSB_Temp','BB_BMC_Temp','P1_VR_Temp','IB_Temp','LAN_NIC_Temp','P1_Therm_Margin','P2_Therm_Margin','DIMM_Thrm_Mrgn_1','DIMM_Thrm_Mrgn_2','DIMM_Thrm_Mrgn_3','DIMM_Thrm_Mrgn_4','BB_P12V','BB_P3_3V','BB_P5V_STBY','BB_P1_Vcc','BB_P2_Vcc','BB_+1.5_P1DDR_AB','BB_+1.5_P1DDR_CD','BB_+1.5_P2DDR_AB','BB_+1.5_P2DDR_CD','BB_P1_8V_AUX','BB_+1.1V_SB','BB_P3_3V_STBY','BB_1_1V_PCH']:
        title = 'ipmi_phase1_set2_prime95_run1_end_%s' % metric
        drawing(oneTime, metric, title)

def coreData():
    metrics = ['Temp']
    #metrics = ['INST_RETIRED.ANY','CPU_CLK_UNHALTED.THREAD','CPU_CLK_UNHALTED.REF_TSC','IA32_PERF_STATUS','ARITH.FPU_DIV','BR_INST_RETIRED.ALL_BRANCHES','UNC_M_CAS_COUNT.WR','UNC_M_CAS_COUNT.RD','APERF','MPERF','TSC','Temp','OPENMP.INST','OPENMP.ID']
    files = getfiles('data/')
    for f in files:
        level = f.split('/')[-1].split('_')[0]
        #phase = int(f.split('/')[-1].split('_')[1][5])
        if level == 'processor':# and phase == 1:
            for metric in metrics:
                title = f.split('/')[-1].split('.csv')[0]
                df = pd.read_csv(f)
                times = sorted(list(set(df['time'])))
                period = 0
                for time in times:
                    for processor in [1,2]:
                        newtitle = title + '_proc%d_period%d' % (processor, period)
                        drawing(df[ (df['time']==time) & (df['processor']==processor) ], metric, newtitle)
                    period += 1
    print('I created some figures!')

def drawing(df, metric, title):
    print(title)
    sns.set(font_scale=4)
    sns.set_style('whitegrid', {'grid.color':'.15', 'axes.edgecolor':'.15'})
    g = sns.pairplot(df, kind='scatter', x_vars=['IPC'], y_vars=['PKG_POWER'], 
                    #vars=['node', 'Temp', 'PKG_POWER', 'IPC', 'frequency'], 
                    hue='processor', #hue_order=[0, 7], 
                    palette=sns.color_palette('Set2',10), size=20)
    plt.title(title)
    #g.axes[0,0].set_xlim(90,115)
    #g.axes[0,0].set_ylim(45,90)
    if 'mg.C' in title:
        g.axes[0,0].set_xlim(0.7,1.3)
        g.axes[0,0].set_ylim(90,115)
    elif 'prime95' in title:
        g.axes[0,0].set_xlim(2,2.25)
        g.axes[0,0].set_ylim(105,115)
    #for position in range(70, 1296, 70):
    #    plt.axvline(x=position, color='r')
    #plt.legend(bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.1)
    g.savefig('oneProcIPCPower/%s.png' % (title) )
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
