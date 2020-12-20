import os, platform
from uuid import uuid4
from nhfw.config import NhfwConfigBase

class RouterConfig(NhfwConfigBase):
    CONFIG_FILE="/etc/nhfw/router.yml"

    def __init__(self):
        super().__init__(initial=self._initialConfig)

    def _initialConfig(self):
        config = {}
        config['hostname'] = platform.node()       
        config['uuid'] = str(uuid4())
        return config

    @property
    def config(self):
        return self._config

    @property
    def hostname(self):
        return self._config['hostname']
    
    @property
    def hostuuid(self):
        return self._config['uuid']

    @property
    def domain(self):
        return self._config['domain']

    @property
    def dnstsig(self):
        return self._config['dnstsig']


