#!/usr/bin/env python
# testing load in StoRM server
# need root to run
import commands, sys, time, os
import psutil


def getGridftpCnx():
    cmd = "netstat -ntup | grep 33.149 | grep globus | grep -v 148:2811 | wc -l"
    cnx = commands.getoutput(cmd)
    return int(cnx)
    
def getFrontendCnx():
    cmd = "netstat -ntup | grep front | grep 33.149 | wc -l"
    cnx = commands.getoutput(cmd)
    return int(cnx)

class Queue(object):
    def __init__(self, size):
        self.data = []
        self.size = size
    def length(self):
        return len(self.data)
    def isFull(self):
        if len(self.data) == self.size :
            return True
        else:
            return False
    def delete(self):
        del self.data[0]
    def add(self, newElement):
        if self.isFull():
            self.delete()
            self.data.append(newElement)
        else:
            self.data.append(newElement)
    def show(self):
        print self.data
    def pop(self):
        head = self.data[0]
        del self.data[0]
        return head

class CPUTimes(Queue):
    def usedPercent(self):
        if self.isFull():
            total = sum(self.data[-1]) - sum(self.data[0])
            idle = self.data[-1].idle - self.data[0].idle
            return 100 * (total - idle) / total
        else:
            return -1
    def sysPercent(self):
        if self.isFull():
            total = sum(self.data[-1]) - sum(self.data[0])
            system = self.data[-1].system - self.data[0].system
            return 100 * system / total
        else:
            return -1
    def iowaitPercent(self):
        if self.isFull():
            total = sum(self.data[-1]) - sum(self.data[0])
            iowait = self.data[-1].iowait - self.data[0].iowait
            return 100 * iowait / total
        else:
            return -1

class NetIO(Queue):
    '''[(sent, recv, time), (sent, recv, time)]'''
    def outSpeed(self):
        if self.isFull():
            speed = (self.data[-1][0] - self.data[0][0]) / (self.data[-1][2] - self.data[0][2])
            return speed/(1024*1024)
        else:
            return -1
    def inSpeed(self):
        if self.isFull():
            speed = (self.data[-1][1] - self.data[0][1]) / (self.data[-1][2] - self.data[0][2])
            return speed/(1024*1024)
        else:
            return -1

def main():
    if len(sys.argv) != 2:
        n = 30
    else:
        n = int(sys.argv[1])
    inteval = 0.5
    maxLoad = 0
    maxFtpCnx = 0
    maxFrontCnx = 0
    maxusCPU = 0
    maxsysCPU = 0
    maxwaCPU = 0
    maxnetI = 0
    maxnetO = 0
    cputimes = CPUTimes(20)
    netioq = NetIO(20)
    for i in range(n):
        load = os.getloadavg()[0]
        ftpCnx = getGridftpCnx()
        frontCnx = getFrontendCnx()

        cputimes.add(psutil.cpu_times())
        usCPU = cputimes.usedPercent()
        sysCPU = cputimes.sysPercent()
        waCPU = cputimes.iowaitPercent()

        netio = list(psutil.net_io_counters(pernic=True)['em1'][:2])
        netio.append(time.time())
        netioq.add(netio)
        oSpeed = netioq.outSpeed()
        iSpeed = netioq.inSpeed()

        print '%4d  Load: %6.2f  FTP: %4d  FEX: %4d  CPU: %5.2f%%  sys: %5.2f%%  wa: %5.2f%%  net_I: %5.1f M/s  net_O: %5.1f M/s'\
            %(i, load, ftpCnx, frontCnx, usCPU, sysCPU, waCPU, iSpeed, oSpeed)
        if load > maxLoad :
            maxLoad = load
        if ftpCnx > maxFtpCnx :
            maxFtpCnx = ftpCnx
        if frontCnx > maxFrontCnx :
            maxFrontCnx = frontCnx
        if usCPU > maxusCPU:
            maxusCPU = usCPU
        if sysCPU > maxsysCPU:
            maxsysCPU = sysCPU
        if waCPU > maxwaCPU:
            maxwaCPU = waCPU
        if iSpeed > maxnetI:
            maxnetI = iSpeed
        if oSpeed > maxnetO:
            maxnetO = oSpeed
        if ((i > 100) and (ftpCnx < 5)) and (usCPU <10):
            break
        time.sleep(inteval)
    print '\nMax:'
    print 'Load: %.2f  GridFTP: %d  FE: %d  CPU used: %.2f%%   sys: %.2f%%   iowait: %.2f%%  net_I: %5.1f M/s  net_O: %5.1f M/s'\
        %(maxLoad, maxFtpCnx, maxFrontCnx, maxusCPU, maxsysCPU, maxwaCPU, maxnetI, maxnetO)

if __name__ == '__main__':
    main()
