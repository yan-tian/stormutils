#!/usr/bin/env python
'''
Submit multi-thread upload/download jobs in client
'''

import threading
import time,os

def addFile(m):
    timeStart = time.time()
    n = m + 0 
    #print 'Adding file100m-%04d' %n
    cmd = 'dirac-dms-add-file /cepc/stormtest/100M-files-10/file100m-%04d random100M IHEP-STORM' %n
    os.system(cmd)
    timeEnd = time.time()
    print 'Finished add file100m-%04d with Speed %.3f M/s' %(n, 100/(timeEnd-timeStart))

def getFile(m):
    timeStart = time.time()
    n = m + 0 
    print 'Downloading file100m-%04d' %n
    cmd = "lcg-cp -b -D srmv2 --connect-timeout 3600 --sendreceive-timeout 3600 -n 4\
        srm://storm.ihep.ac.cn:8444/srm/managerv2?SFN=/cepc/stormtest/100M-files-10/file100m-%04d file:///dev/null" %n
    os.system(cmd)
    timeEnd = time.time()
    print 'Finished download file100m-%04d with Speed %.3f M/s' %(n, 100/(timeEnd-timeStart))

class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = 0
    def run(self):
        self.result = apply(self.func, self.args)
    def getResult(self):
        return self.result

def main():
    worker = sys.argv[1] + 'File'  # addFile or getFile
    n = sys.argv[2]  # number of workers
    threads = []
    for i in range(n):
        t = MyThread(worker, (i,))
        t.setDaemon(True)
        threads.append(t)
    timeS = time.time()
    for i in range(n):
        threads[i].start()
    for i in range(n):
        threads[i].join()
    timeE = time.time()
    print 'Total time %.2f, average Speed: %.3f M/s' %(timeE-timeS, n*100/(timeE-timeS))

if __name__ == '__main__':
    main()
