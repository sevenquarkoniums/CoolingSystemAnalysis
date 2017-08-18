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
                    '#SBATCH -t 0:01:0\n'
                    '#SBATCH -p pbatch\n'
                    #'#SBATCH -A intelpwr\n'
                    #'#SBATCH -o outfile/submit%d.out\n'
                    './analysis.py %s %d %d %s %d %d %s\n'
                    #'./runtime.py %s %d %d %d\n'
                    #) % (self.app, self.setID, self.pcap, self.runID)
                    ) % (self.cluster, self.phase, self.setID, self.app, self.pcap, self.runID, self.sock)
            f.write(words)

    def run(self):
        import subprocess
        self.cluster = 'quartz'
        for self.phase in [2]:
            for self.setID in [3]:
                for self.sock in ['sock2']:#, 'sock1','sock2']:
                    for self.app in ['cg.C','dgemm','ep.D','firestarter','ft.C','mg.D','prime95','stream']:
                        for self.pcap in [0,50,70,120]:
                            for self.runID in range(1,4):
                                self.shfile = 'shfile/ph%ds%d%sp%dr%d%s.sh' % (self.phase, self.setID, self.app, self.pcap, self.runID, self.sock) 
                                #self.shfile = 'shfile/Rs%d%sp%dr%d.sh' % (self.setID, self.app, self.pcap, self.runID) 
                                self.create()
                                subprocess.call('sbatch %s' % self.shfile, shell=True)

if __name__ == '__main__':
    main()
