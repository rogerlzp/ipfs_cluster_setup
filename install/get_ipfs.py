# -*- coding: utf-8 -*-
#
# get file from the link, and download it to currently folder
#
# First create the directory according to how many nodes are needed, default is two
#
#

import yaml
import os, shutil

from config import ipfs_config
from log.log import LOG, logger

global ROOT_PATH
global NODE_NUM
global IPFS
global IPFS_CLUSTER_SERVICE
global IPFS_CLUSTER_CTL
global CURRENT_PATH
global BIN_PATH


# global TMP_PATH


def prepareENV():
    """
    1. get the parameter
    """
    global CURRENT_PATH
    curPath = os.path.dirname(os.path.realpath(__file__))
    CURRENT_PATH = curPath
    ipfsConfig = ipfs_config.IPFSConfig(os.path.join(curPath, "../config/config.yaml"))

    if ipfsConfig.IPFS_BIN != None:
        LOG.info("ipfs bin already exists, no need to reinstall, check if you want to update it? ")
        return ipfsConfig

    createDirs(ipfsConfig)
    downloadFile(ipfsConfig, ipfsConfig.IPFS_FILE_URL)
    downloadFile(ipfsConfig,ipfsConfig.IPFS_CLUSTER_SERVICE_FILE_URL)
    downloadFile(ipfsConfig,ipfsConfig.IPFS_CLUSTER_CTL_FILE_URL)

    IPFS_BIN = os.path.join(ipfsConfig.BIN_PATH, ipfsConfig.IPFS_BIN_NAME)
    copyFileToBin(os.path.join(ipfsConfig.TMP_PATH, ipfsConfig.IPFS_FOLDER, ipfsConfig.IPFS_BIN_NAME), IPFS_BIN)

    IPFS_CLUSTER_SERVICE_BIN = os.path.join(ipfsConfig.BIN_PATH, ipfsConfig.IPFS_CLUSTER_SERVICE_BIN_NAME)
    copyFileToBin(
        os.path.join(ipfsConfig.TMP_PATH, ipfsConfig.IPFS_CLUSTER_SERVICE_FOLDER, ipfsConfig.IPFS_CLUSTER_SERVICE_BIN_NAME),
        IPFS_CLUSTER_SERVICE_BIN)

    IPFS_CLUSTER_CTL_BIN = os.path.join(ipfsConfig.BIN_PATH, ipfsConfig.IPFS_CLUSTER_CTL_BIN_NAME)
    copyFileToBin(
        os.path.join(ipfsConfig.TMP_PATH, ipfsConfig.IPFS_CLUSTER_CTL_FOLDER, ipfsConfig.IPFS_CLUSTER_CTL_BIN_NAME),
        IPFS_CLUSTER_CTL_BIN)

    # update config file
    yamlPath = os.path.join(curPath, "../config/config.yaml")
    f = open(yamlPath, 'r', encoding='utf-8')
    cfg = f.read()
    f.close()
    d = yaml.load(cfg)  # 用load方法转字典
    d["ipfs"]["ipfs_bin"] = IPFS_BIN
    d["ipfs"]["ipfs_cluster_service_bin"] = IPFS_CLUSTER_SERVICE_BIN
    d["ipfs"]["ipfs_cluster_ctl_bin"] = IPFS_CLUSTER_CTL_BIN
    d["ipfs"]["tmp_path"] = ipfsConfig.TMP_PATH
    d["ipfs"]["bin_path"]  = ipfsConfig.BIN_PATH


    f = open(yamlPath, 'w+', encoding='utf-8')
    yaml.dump(d, f)
    f.close()
    # reload ipfsconfig
    ipfsConfig = ipfs_config.IPFSConfig(os.path.join(curPath, "../config/config.yaml"))
    return ipfsConfig


def getVariable():
    pass

def createDirs(ipfsConfig):
    """
    1. create tmp dir to store the execute binaries from internet,
    2. create bin dir to put the execute binary
    3. create node1,
        1). create node1/ipfs as IPFS_PATH
        2). create node1/config
    """
    if ipfsConfig.TMP_PATH == None:
        ipfsConfig.TMP_PATH = os.path.join(ipfsConfig.ROOT_PATH, "tmp")
        mkdir(ipfsConfig.TMP_PATH)
    if ipfsConfig.BIN_PATH == None:
        ipfsConfig.BIN_PATH = os.path.join(ipfsConfig.ROOT_PATH, "bin")
        mkdir(ipfsConfig.BIN_PATH)
    for i in range(ipfsConfig.NODE_NUM):
        mkdir(os.path.join(ipfsConfig.ROOT_PATH, "node" + str(i)))
        mkdir(os.path.join(ipfsConfig.ROOT_PATH, "node" + str(i), "ipfs"))
        mkdir(os.path.join(ipfsConfig.ROOT_PATH, "node" + str(i), "config"))


def mkdir(path):
    # strip head
    path = path.strip()
    # strip end
    path = path.rstrip("\\")

    isExists = os.path.exists(path)

    if not isExists:
        os.makedirs(path)
        LOG.info('create path: %s succeed' % path)
        return True
    else:
        LOG.info('path: %s already exists' % path)
        return False


def downloadFile(ipfsConfig,fileUrl):
    import requests

    fileName = fileUrl.split("/")[-1]
    filePath = os.path.join(CURRENT_PATH, fileName)
    if os.path.exists(filePath):
        LOG.info('file: %s already downloaded' % filePath)
        extract(os.path.join(CURRENT_PATH, fileName), ipfsConfig.TMP_PATH)
        return
    LOG.info('file: %s download starting...' % fileUrl)
    res = requests.get(fileUrl, stream=True)
    res.raise_for_status()
    sourceFile = open(fileName, 'wb')
    for chunk in res.iter_content(chunk_size=512):
        if chunk:
            sourceFile.write(chunk)
    res.close()
    sourceFile.close()
    LOG.info('file: %s downloaded' % fileUrl)
    extract(os.path.join(CURRENT_PATH, fileName), ipfsConfig.TMP_PATH)


def copyFileToBin(srcPath, targetPath):
    if os.path.isfile(srcPath):
        LOG.info('copy file from srcPath: %s to targetPath:%s' % (srcPath, targetPath))
        shutil.move(srcPath, targetPath)


def extract(tar_path, target_path):
    import tarfile
    try:
        tar = tarfile.open(tar_path, "r:gz")
        tar.extractall(target_path)
        tar.close()
    except Exception:
        LOG.info("failed to extract file %s" % tar_path)


def initIPFS(nodePath):
    """
    1. ipfs init it
    2. modify the config file, just change the port
    3.
    :return:
    """


if __name__ == '__main__':
    prepareENV()
