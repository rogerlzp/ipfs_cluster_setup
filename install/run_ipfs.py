# -*- coding: utf-8 -*-
#
# 1. set IPFS_PATH, and start the daemon
#
#
import subprocess
import os
from log.log import LOG, logger
from config import ipfs_config
from util.ip_check import checkTwoPort, findPort
from subprocess import Popen, DEVNULL, STDOUT
import json
import sys
import signal
import yaml
import time



def startIPFSDaemon(ipfsBin, ipfsPath ):
    os.putenv("IPFS_PATH", ipfsPath)

    cmd = "nohup %s daemon" % ipfsBin
    LOG.info("command: %s " % cmd )

    child = subprocess.Popen(cmd,stdout=open(os.path.join(ipfsPath, "ipfs.log"), 'w'),
                 stderr=open(os.path.join(ipfsPath, "error.log"), 'a'), shell=True) #preexec_fn=os.setpgrp

    pid = child.pid
    pgid = os.getpgid(pid)
    # os.waitpid(pid, 0)
    # out, err = child.communicate()
    # LOG.info(out)
    # child.wait()
    LOG.info("child pid: %d, parent pid: %d" % (child.pid, pgid))
    time.sleep(15)



def initIPFS(ipfsBin, ipfsPath):
    """
    init ipfs given ipfsPath
    :param ipfsBin:
    :param ipfsPath:
    :return:
    """
    os.putenv("IPFS_PATH", ipfsPath)
    retcode = subprocess.call([ipfsBin,"init" ])
    LOG.info(retcode)




dic = {}

def update_json_txt(dic_json, key_name, key_value):
    if isinstance(dic_json,dict): #判断是否是字典类型isinstance 返回True false
        for key in dic_json:
            if isinstance(dic_json[key],dict):#如果dic_json[key]依旧是字典类型
               # print("****key--：%s value--: %s"%(key,dic_json[key]))
                update_json_txt(dic_json[key],key_name, key_value)
                dic[key] = dic_json[key]
            else:
                if(key==key_name):
                    print("****key--：%s value--: %s" % (key, dic_json[key]))
                    strList = dic_json[key].strip().split("/")
                    strList[-1]=str(key_value)
                    dic_json[key]= "/".join(strList)
                dic[key] = dic_json[key]

def get_key_from_json(dic_json, dict1_name, key_name):
    target_dic = {}
    if isinstance(dic_json,dict): #判断是否是字典类型isinstance 返回True false
        for key in dic_json:
            if ((key == dict1_name) and (isinstance(dic_json[key],dict))): # get the first dict with name dict1_name
                for key2 in dic_json[key]:
                    if ((key2 == key_name) and not (isinstance(dic_json[key][key2], dict))):
                        return dic_json[key][key2]


def updateIPFSConfig(nodeNum, ipfsNodeConfig, startPort):
    apiPort = findPort(startPort)
    with open(ipfsNodeConfig,'r') as load_f:
        load_dict = json.load(load_f)
    update_json_txt(load_dict, "API", apiPort)
    gatewayPort = findPort(apiPort)
    update_json_txt(load_dict, "Gateway", gatewayPort)
    with open(ipfsNodeConfig,'w') as load_f:
        json.dump(load_dict, load_f)

    updateConfig(nodeNum, apiPort, gatewayPort)
    return gatewayPort

def updateConfig(nodeNum, apiPort, gatewayPort):
    # update config file
    yamlPath = os.path.join(CURRENT_PATH, "../config/config.yaml")
    with open(yamlPath, 'r') as f:
        cfg = f.read()
    d = yaml.load(cfg)  # 用load方法转字典
    d["ipfs"].setdefault("node"+str(nodeNum), {})
    d["ipfs"]["node" + str(nodeNum)].setdefault("api_port",None)
    d["ipfs"]["node" + str(nodeNum)].setdefault("gateway_port",None)

    d["ipfs"]["node"+str(nodeNum)]["api_port"] = apiPort
    d["ipfs"]["node" + str(nodeNum)]["gateway_port"] = gatewayPort

    with open(yamlPath, 'w') as f:
        yaml.dump(d, f)


def prepareIPFSNode(startPort):
    global CURRENT_PATH
    curPath = os.path.dirname(os.path.realpath(__file__))
    CURRENT_PATH = curPath
    ipfsConfig = ipfs_config.IPFSConfig(os.path.join(curPath, "../config/config.yaml"))
    for i in range(ipfsConfig.NODE_NUM):
        ipfsPath = os.path.join(ipfsConfig.ROOT_PATH, "node" + str(i), "ipfs")
        initIPFS(ipfsConfig.IPFS_BIN, ipfsPath)
        ipfsNodeConfigFile = os.path.join(ipfsPath, "config")
        startPort = updateIPFSConfig(i,ipfsNodeConfigFile, startPort)
        startIPFSDaemon(ipfsConfig.IPFS_BIN, ipfsPath)




def prepareIPFSClusterNode(startPort):

    ipfsConfig = ipfs_config.IPFSConfig(os.path.join(CURRENT_PATH, "../config/config.yaml"))
    for i in range(ipfsConfig.NODE_NUM):
        ipfsServicePath = os.path.join(ipfsConfig.ROOT_PATH, "node" + str(i), "config")
        initIPFSService(ipfsConfig.IPFS_CLUSTER_SERVICE_BIN, ipfsServicePath)
        ipfsServiceNodeConfigFile = os.path.join(ipfsServicePath, "service.json")
        startPort = updateIPFSServiceConfig(i,ipfsServiceNodeConfigFile, startPort )
        startIPFSServiceDaemon(i, ipfsConfig.IPFS_CLUSTER_SERVICE_BIN, ipfsServicePath)

def initIPFSService(ipfsServiceBin, ipfsServicePath):
    """
    init ipfs given ipfsPath
    :param ipfsBin:
    :param ipfsPath:
    :return:
    """
    os.putenv("CLUSTER_SECRET", "8512641fc38bd61cd784b09def7c72075c4ad4995d1f8d91db2bef4433fdb2d5")
    os.putenv("IPFS_CLUSTER_PATH", ipfsServicePath)
    LOG.info("ipfs-cluster-service init cmd: %s init, with IPFS_CLUSTER_PATH: %s " % (ipfsServiceBin, ipfsServicePath ))
    retcode = subprocess.call([ipfsServiceBin,"init" ])
    LOG.info(retcode)

def updateIPFSServiceConfig(nodeNum, ipfsServiceNodeConfig, startPort):
    listen_multiaddress_port = findPort(startPort)
    with open(ipfsServiceNodeConfig,'r') as load_f:
        load_dict = json.load(load_f)
    update_json_txt(load_dict, "listen_multiaddress", listen_multiaddress_port)
    http_listen_multiaddress_port = findPort(listen_multiaddress_port)
    update_json_txt(load_dict, "http_listen_multiaddress", http_listen_multiaddress_port)
    proxy_listen_multiaddress_port = findPort(http_listen_multiaddress_port)
    update_json_txt(load_dict, "proxy_listen_multiaddress", proxy_listen_multiaddress_port)


    yamlPath = os.path.join(CURRENT_PATH, "../config/config.yaml")
    with open(yamlPath, 'r') as f:
        cfg = f.read()
    d = yaml.load(cfg)  # 用load方法转字典
    apiPort = d["ipfs"]["node"+str(nodeNum)]["api_port"]
    update_json_txt(load_dict, "node_multiaddress", apiPort)


    with open(ipfsServiceNodeConfig,'w') as load_f:
        json.dump(load_dict, load_f)

    updateServiceNodeConfig(nodeNum, listen_multiaddress_port, http_listen_multiaddress_port,proxy_listen_multiaddress_port)
    return proxy_listen_multiaddress_port

def updateServiceNodeConfig(nodeNum, listen_multiaddress_port, http_listen_multiaddress_port,proxy_listen_multiaddress_port):
    # update config file
    yamlPath = os.path.join(CURRENT_PATH, "../config/config.yaml")
    with open(yamlPath, 'r') as f:
        cfg = f.read()
    d = yaml.load(cfg)  # 用load方法转字典
    d["ipfs"]["node"+str(nodeNum)]["listen_multiaddress_port"] = listen_multiaddress_port
    d["ipfs"]["node" + str(nodeNum)]["http_listen_multiaddress_port"] = http_listen_multiaddress_port
    d["ipfs"]["node" + str(nodeNum)]["proxy_listen_multiaddress_port"] = proxy_listen_multiaddress_port

    with open(yamlPath, 'w') as f:
        yaml.dump(d, f)


def startIPFSServiceDaemon(nodeNum,ipfsServiceBin, ipfsServicePath ):
    os.putenv("IPFS_CLUSTER_PATH", ipfsServicePath)
    os.putenv("CLUSTER_SECRET", "8512641fc38bd61cd784b09def7c72075c4ad4995d1f8d91db2bef4433fdb2d5")

    if nodeNum == 0:
        cmd = "nohup %s daemon" % ipfsServiceBin
        LOG.info("command: %s " % cmd )

        child = subprocess.Popen(cmd,stdout=open(os.path.join(ipfsServicePath, "ipfs_service.log"), 'w'),
                 stderr=open(os.path.join(ipfsServicePath, "error.log"), 'a'), shell=True)

        pid = child.pid
        pgid = os.getpgid(pid)
        LOG.info("child pid: %d, parent pid: %d" % (child.pid, pgid))
    else:
       # node:/ip4/127.0.0.1/tcp/9096/ipfs/QmStfZRBxoNFb8KnKVzxumA1CzEHgMVU84cXRtT9KjpUCA
       # get cluster id from service.json: cluster:id
       # get port from service.json:cluster: listen_multiaddress
       #
       ipfsConfig = ipfs_config.IPFSConfig(os.path.join(CURRENT_PATH, "../config/config.yaml"))
       ipfsServiceNodeConfigFile = os.path.join(ipfsConfig.ROOT_PATH, "node" + str(0), "config", "service.json")
       with open(ipfsServiceNodeConfigFile, 'r') as load_f:
           load_dict = json.load(load_f)
       id =load_dict["cluster"]["id"]

       listen_multiaddress = load_dict["cluster"]["listen_multiaddress"].split("/")[-1]
       bootStrapNode = "/ip4/127.0.0.1/tcp/%s/ipfs/%s" % (listen_multiaddress, id)
       cmd = "nohup %s daemon --bootstrap %s" % (ipfsServiceBin, bootStrapNode)
       LOG.info("command: %s " % cmd)

       child = subprocess.Popen(cmd, stdout=open(os.path.join(ipfsServicePath, "ipfs_service.log"), 'w'),
                                stderr=open(os.path.join(ipfsServicePath, "error.log"), 'a'), shell=True)

       pid = child.pid
       pgid = os.getpgid(pid)
       LOG.info("child pid: %d, parent pid: %d" % (child.pid, pgid))

    time.sleep(15)


if __name__=="__main__":
    secret="8512641fc38bd61cd784b09def7c72075c4ad4995d1f8d91db2bef4433fdb2d5"
    prepareIPFSNode(5001)
    prepareIPFSClusterNode(6001)
 #   startIPFSDaemon()
   # port = findPort(5001)

