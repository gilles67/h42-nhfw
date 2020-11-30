from uuid import uuid4
import requests
import yaml
import platform
import os

CONFIG_FILE="/etc/nhfw/router.yml"

class RouterConfig:
    _config = []
    def __init__(self):
        self._parseConfig()
    
    def _parseConfig(self):
        if os.path.isfile(CONFIG_FILE):
            try:
                fd = open(CONFIG_FILE, 'r')
                self._config = yaml.load(fd, Loader=yaml.SafeLoader)
                fd.close()
            except:
                print("[Error] Parse configuration file : {}".format(CONFIG_FILE))
        else:
            self._genereateConfig()

    def _genereateConfig(self):
        config = {}
        config['hostname'] = platform.node()       
        config['uuid'] = str(uuid4())
        if not os.path.exists('/etc/nhfw'):
            os.mkdir('/etc/nhfw')
        try:
            fd = open(CONFIG_FILE, 'w')
            yaml.dump(config, fd)
            fd.close()
            self._parseConfig()
        except:
            print("[Error] Generate configuration file : {}".format(CONFIG_FILE))

    @property
    def hostname(self):
        return self._config['hostname']
    
    @property
    def hostuuid(self):
        return self._config['uuid']

    @property
    def domain(self):
        return self._config['domain']




