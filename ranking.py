#!/Users/zhang51/anaconda/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess

def main():
    #generateRanking('IPCpW')
    #correlation('IPC')
    rank(cluster='quartz')

def rank(cluster):
    numPick = 50

    if cluster == 'cab':
        data = pd.read_csv('data/cab/pavgall_processor_phase1_set14_%s_pcap%d_run%d.csv' % ('mg.C', 51, 3) )
        data = data[['node','IPC']].groupby('node', as_index=False).mean().sort_values('IPC', ascending=False)
        data.to_csv('data/cab/rank_mg.C_IPC.csv', index=False)
        goodNodes = set(data.head(numPick*2)['node'])
        badNodes = set(data.tail(numPick*2)['node'])

        data = pd.read_csv('data/cab/pavgall_processor_phase1_set14_%s_pcap%d_run%d.csv' % ('prime95', 51, 3) )
        data = data[['node','IPC']].groupby('node', as_index=False).mean().sort_values('IPC', ascending=False)
        data.to_csv('data/cab/rank_prime95_IPC.csv', index=False)
        goodNodes = goodNodes & set(data.head(numPick*2)['node'])
        badNodes = badNodes & set(data.tail(numPick*2)['node'])

        data = pd.read_csv('data/cab/pavgall_processor_phase1_set14_%s_pcap%d_run%d.csv' % ('mg.C', 115, 3) )
        data = data[['node','PKG_POWER']].groupby('node', as_index=False).mean().sort_values('PKG_POWER', ascending=True)
        data.to_csv('data/cab/rank_mg.C_power.csv', index=False)
        goodNodes = goodNodes & set(data.head(numPick*2)['node'])
        badNodes = badNodes & set(data.tail(numPick*2)['node'])

        data = pd.read_csv('data/cab/pavgall_processor_phase1_set14_%s_pcap%d_run%d.csv' % ('prime95', 115, 3) )
        data = data[['node','PKG_POWER']].groupby('node', as_index=False).mean().sort_values('PKG_POWER', ascending=True)
        data.to_csv('data/cab/rank_prime95_power.csv', index=False)
        goodNodes = goodNodes & set(data.head(numPick*2)['node'])
        badNodes = badNodes & set(data.tail(numPick*2)['node'])

    elif cluster == 'quartz':
        data = pd.read_csv('data/quartz/pavgall_processor_set1_%s_pcap%d_run%d.csv' % ('mg.C', 50, 2) )
        node = data[['node','IPC']].groupby('node', as_index=False).mean().sort_values('IPC', ascending=False)
        proc1 = data[data['processor']==1][['node','IPC']].copy()
        proc1.rename(columns={'IPC':'IPC_proc1'}, inplace=True)
        fo = pd.merge(node, proc1, on='node')
        proc2 = data[data['processor']==2][['node','IPC']].copy()
        proc2.rename(columns={'IPC':'IPC_proc2'}, inplace=True)
        fo = pd.merge(fo, proc2, on='node')
        fo.to_csv('data/quartz/rank_mg.C_IPC.csv', index=False)

        #data = pd.read_csv('data/quartz/pavgall_processor_set1_%s_pcap%d_run%d.csv' % ('mg.C', 50, 2) )
        #data = data[['node','runtime']].drop_duplicates().sort_values('runtime', ascending=True)
        #data.to_csv('data/quartz/rank_mg.C_runtime.csv', index=False)
        #goodNodes = set(data.head(numPick)['node'])
        #badNodes = set(data.tail(numPick)['node'])

        #data = pd.read_csv('data/quartz/pavgall_processor_set1_%s_pcap%d_run%d.csv' % ('mg.C', 120, 3) )
        #data = data[['node','IPCpW']].groupby('node', as_index=False).mean().sort_values('IPCpW', ascending=False)
        #data.to_csv('data/quartz/rank_mg.C_IPCpW.csv', index=False)
        ##goodNodes = goodNodes & set(data.head(numPick*2)['node'])
        ##badNodes = badNodes & set(data.tail(numPick*2)['node'])

        #data = pd.read_csv('data/quartz/pavgall_processor_set1_%s_pcap%d_run%d.csv' % ('mg.C', 120, 3) )
        #data = data[['node','IPC']].groupby('node', as_index=False).mean().sort_values('IPC', ascending=False)
        #data.to_csv('data/quartz/rank_mg.C_IPC.csv', index=False)
        ##goodNodes = goodNodes & set(data.head(numPick*2)['node'])
        ##badNodes = badNodes & set(data.tail(numPick*2)['node'])

        #data = pd.read_csv('data/quartz/pavgall_processor_set1_%s_pcap%d_run%d.csv' % ('mg.C', 120, 3) )
        #data = data[['node','PKG_POWER']].groupby('node', as_index=False).mean().sort_values('PKG_POWER', ascending=True)
        #data.to_csv('data/quartz/rank_mg.C_power.csv', index=False)
        #goodNodes = goodNodes & set(data.head(numPick*2)['node'])
        #badNodes = badNodes & set(data.tail(numPick*2)['node'])

def generateRank(rank):
    data = {}
    for app,pcap,run in [('mg.C',50,2),('lulesh',50,3),('mg.C',120,3),('lulesh',120,3)]:
        data[(app, pcap, run)] = pd.read_csv('data/quartz/pavgall_processor_set1_%s_pcap%d_run%d.csv' % (app, pcap, run) )
    if rank == 'runtime':
        colname = 'avgReRuntime'
        merged = pd.merge(data[('mg.C',50,2)][['node','runtime']].drop_duplicates(), data[('lulesh',50,3)][['node','runtime']].drop_duplicates(), on='node')
        numPick = 50
    elif rank == 'PKG_POWER':
        colname = 'avgRePower'
        merged = pd.merge(data[('mg.C',120,3)][ data[('mg.C',120,3)]['PKG_POWER']>0 ][['node','processor','PKG_POWER']], data[('lulesh',120,3)][ data[('lulesh',120,3)]['PKG_POWER']>0 ][['node','processor','PKG_POWER']], on=['node','processor'])
        numPick = 100
    elif rank == 'IPCpW':
        colname = 'avgReIPCpW'
        print(len(data[('mg.C',120,3)][ data[('mg.C',120,3)]['PKG_POWER']<0 ]))
        merged = pd.merge(data[('mg.C',120,3)][ data[('mg.C',120,3)]['PKG_POWER']>0 ][['node','processor','IPCpW']], data[('lulesh',120,3)][ data[('lulesh',120,3)]['PKG_POWER']>0 ][['node','processor','IPCpW']], on=['node','processor'])
        numPick = 100
    medx = merged['%s_x' % rank].median()
    medy = merged['%s_y' % rank].median()
    merged[colname] = (merged['%s_x' % rank] / medx + merged['%s_y' % rank] / medy) / 2
    merged.sort_values(colname, ascending=False if rank == 'IPCpW' else True, inplace=True)
    merged.to_csv('data/quartz/rank_%s.csv' % rank, index=False)

    merged['color'] = [1] * len(merged)
    merged.iloc[:numPick]['color'] = [2] * numPick 
    merged.iloc[-numPick:]['color'] = [3] * numPick 
    sns.set(font_scale=5)
    sns.set_style('whitegrid')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
    g = sns.pairplot(merged, kind='scatter', size=20, aspect=1.2, x_vars=['node'], y_vars=[colname], 
                    hue='color', 
                    palette=sns.color_palette('Set2') )
    g.axes[0,0].set_xlim(0,3300)
    name = '%s/%s.png' % ('quartzFig', 'rank_%s' % rank)
    g.savefig(name)
    subprocess.call('open %s' % name, shell=True)

def correlation(metric):
    df1 = pd.read_csv('data/quartz/rank_mg.C_runtime.csv')
    df2 = pd.read_csv('data/quartz/rank_mg.C_%s.csv' % metric)
    merged = pd.merge(df1, df2, on='node')
    sns.set(font_scale=5)
    sns.set_style('whitegrid')#, {'grid.color':'.15', 'axes.edgecolor':'.15'})
    g = sns.pairplot(merged, kind='scatter', size=20, aspect=1.2, x_vars=['runtime'], y_vars=['IPC'], 
                    hue=None, 
                    palette=sns.color_palette('Set2') )
    name = '%s/%s.png' % ('quartzFig', 'corr')
    g.savefig(name)
    subprocess.call('open %s' % name, shell=True)

if __name__ == '__main__':
    main()
