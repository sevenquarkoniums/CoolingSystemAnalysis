#!/Users/zhang51/anaconda/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    metrics = ['Temp']
    #metrics = ['INST_RETIRED.ANY','CPU_CLK_UNHALTED.THREAD','CPU_CLK_UNHALTED.REF_TSC','IA32_PERF_STATUS','ARITH.FPU_DIV','BR_INST_RETIRED.ALL_BRANCHES','UNC_M_CAS_COUNT.WR','UNC_M_CAS_COUNT.RD','APERF','MPERF','TSC','Temp','OPENMP.INST','OPENMP.ID']
    files = getfiles('data/')
    for f in files:
        level = f.split('/')[-1].split('_')[0]
        if level == 'processor':
            for metric in metrics:
                title = f.split('/')[-1].split('.csv')[0]
                df = pd.read_csv(f)
                #df = df[df['node']<=120]
                sns.set(font_scale=4)
                sns.set_style('whitegrid', {'grid.color':'.15', 'axes.edgecolor':'.15'})
                g = sns.pairplot(df, kind='scatter', x_vars=['node'], y_vars=[metric], #vars=['node', 'temp'], 
                                hue='processor', #hue_order=[0, 7], 
                                palette=sns.color_palette('Set2',10), size=20)
                plt.title(title)
                for position in range(70, 1296, 70):
                    plt.axvline(x=position, color='r')
                #plt.legend(bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.1)
                g.savefig('fig/hist_%s_%s.png' % (metric, title) )
                print('I created a figure!')

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
