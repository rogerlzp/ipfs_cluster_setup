import yaml


class IPFSConfig(object):
    def __init__(self, yamlFile):
        self.IPFS_BIN = None  # ipfs binary
        self.IPFS_CLUSTER_SERVICE_BIN = None  # ipfs service bin
        self.IPFS_CLUSTER_CTL_BIN = None  # ipfs ctl bin
        self.ROOT_PATH = None # root Path
        self.TMP_PATH = None  # root Path
        self.BIN_PATH = None  # root Path
        self.NODE_NUM = None # node num

        self.IPFS_FILE_URL = None #ipfs download url
        self.IPFS_CLUSTER_SERVICE_FILE_URL = None #
        self.IPFS_CLUSTER_CTL_FILE_URL = None #

        self.IPFS_FOLDER = None # ipfs folder
        self.IPFS_BIN_NAME = None #ipfs bin name
        self.IPFS_CLUSTER_SERVICE_FOLDER = None # ipfs cluster service foler
        self.IPFS_CLUSTER_SERVICE_BIN_NAME = None # ipfs cluster service name
        self.IPFS_CLUSTER_CTL_FOLDER = None  # ipfs cluster ctl foler
        self.IPFS_CLUSTER_CTL_BIN_NAME = None  # ipfs cluster ctl name


        self.parse(yamlFile)

    def parse(self, yamlFile):
        """
        parse yaml file, and get all the properties
        :param yamlFile:
        :return:
        """
        file = open(yamlFile, 'r', encoding='utf-8')
        yamlCfg = file.read()
        yamlCfgD = yaml.load(yamlCfg)  #
        file.close()
        self.ROOT_PATH = yamlCfgD.get("ipfs").get("root_path")
        self.TMP_PATH = yamlCfgD.get("ipfs").get("tmp_path")
        self.BIN_PATH = yamlCfgD.get("ipfs").get("bin_path")
        self.NODE_NUM = yamlCfgD.get("ipfs").get("node_num")
        self.IPFS_BIN = yamlCfgD.get("ipfs").get("ipfs_bin")
        self.IPFS_CLUSTER_SERVICE_BIN = yamlCfgD.get("ipfs").get("ipfs_cluster_service_bin")
        self.IPFS_CLUSTER_CTL_BIN = yamlCfgD.get("ipfs").get("ipfs_cluster_ctl_bin")
        self.IPFS_FILE_URL = yamlCfgD.get("ipfs").get("ipfs_url")
        self.IPFS_CLUSTER_SERVICE_FILE_URL = yamlCfgD.get("ipfs").get("ipfs_cluster_service_url")
        self.IPFS_CLUSTER_CTL_FILE_URL =  yamlCfgD.get("ipfs").get("ipfs_cluster_ctl_url")
        self.IPFS_FOLDER =  yamlCfgD.get("ipfs").get("ipfs_folder")
        self.IPFS_BIN_NAME=  yamlCfgD.get("ipfs").get("ipfs_bin_name")
        self.IPFS_CLUSTER_SERVICE_FOLDER =yamlCfgD.get("ipfs").get("ipfs_cluster_service_folder")
        self.IPFS_CLUSTER_SERVICE_BIN_NAME =yamlCfgD.get("ipfs").get("ipfs_cluster_service_bin_name")
        self.IPFS_CLUSTER_CTL_FOLDER =yamlCfgD.get("ipfs").get("ipfs_cluster_ctl_folder")
        self.IPFS_CLUSTER_CTL_BIN_NAME =yamlCfgD.get("ipfs").get("ipfs_cluster_ctl_bin_name")

