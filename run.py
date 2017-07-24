#!/usr/tce/bin/python3
def main():
    s = submit()
    s.run()

class submit():
    def __init__(self):
        pass

    def create(self):
        with open(self.shfile, 'w') as f:
            words = (
                    '#!/bin/bash\n'
                    '#SBATCH -N 1\n'
                    #'#SBATCH -J asdf\n'
                    '#SBATCH -t 0:58:0\n'
                    '#SBATCH -p pbatch\n'
                    #'#SBATCH -A intelpwr\n'
                    #'#SBATCH -o outfile/submit%d.out\n'
                    './analysis.py %s %d %d %s %d %d\n'
                    #'./runtime.py %s %d %d %d\n'
                    #) % (self.app, self.setID, self.pcap, self.runID)
                    ) % (self.cluster, self.phase, self.setID, self.app, self.pcap, self.runID)
            f.write(words)

    def run(self):
        import subprocess
        self.cluster = 'quartz'
        for self.phase in [2]:
            for self.setID in [1]:
                for self.app in ['mg.C','firestarter','prime95','lulesh']:
                    for self.pcap in [50,70,90,100,110,120]:
                        for self.runID in [1,2,3]:
                            self.shfile = 'shfile/ph%ds%d%sp%dr%d.sh' % (self.phase, self.setID, self.app, self.pcap, self.runID) 
                            #self.shfile = 'shfile/Rs%d%sp%dr%d.sh' % (self.setID, self.app, self.pcap, self.runID) 
                            self.create()
                            subprocess.call('sbatch %s' % self.shfile, shell=True)

if __name__ == '__main__':
    main()
