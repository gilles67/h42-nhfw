import os, platform
from uuid import uuid4
from nhfw.config import NhfwConfigBase
from nhfw.models.node import NhfwNode
from tinydb import Query

class NodelibConfig(NhfwConfigBase):
    CONFIG_FILE="/etc/nhfw/node.yml"

    def __init__(self):
        super().__init__(initial=self._initialConfig)

    def _initialConfig(self):
        config = {}
        config['hostname'] = platform.node()       
        config['uuid'] = str(uuid4())
        return config

    def getLocalNode(self, db):
        node = NhfwNode.getFromDB(self.uuid, db)
        if node: 
            return node
        else:
            node = NhfwNode()
            node.name = self.name
            node.uuid = self.uuid
            node.domain = self.domain
            node.saveToDB(db=db)
            return node
    @property
    def config(self):
        return self._config

    @property
    def name(self):
        return self._config['hostname']
    
    @property
    def uuid(self):
        return self._config['uuid']

    @property
    def domain(self):
        return self._config['domain']

    @property
    def router(self):
        return self._config['router']
