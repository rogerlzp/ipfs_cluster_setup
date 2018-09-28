import socket
import os
from log.log import LOG, logger

def isInuse(ipList, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    flag=True
    for ip in ipList:
        try:
            s.connect((ip, int(port)))
            s.shutdown(2)
            LOG.info('%d is inuse' % port)
            flag=True
            break
        except:
            LOG.info('%d is free' % port)
            flag=False
    return flag


def getLocalIp():
    localIP = socket.gethostbyname(socket.gethostname())
    return localIP

def checkTwoPort(startPort):
    flag = True
    ipList = ("127.0.0.1","0.0.0.0",getLocalIp())
    for i in range(1, 3):
        if (isInuse(ipList, startPort)):
            flag = False
            break
        else:
            startPort = startPort + 1
    return flag, startPort


def findPort(startPort):
    startPort += 3
    while True:
        flag, endPort = checkTwoPort(startPort)
        if (flag == True):  #ninePort is ok
            break
        else:
            startPort = endPort + 1
    return startPort

