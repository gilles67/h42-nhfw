from datetime import datetime
from tinydb import Query
from uuid import uuid4
from nhfw.models.firewallrule import NhfwFirewallRule

class NhfwContainer:
    _db = None
    _table = None
    _node = None

    _fwrules = None

    uuid = None
    #node = None

    name = None
    image = None
    status = None

    ip = None
    bridge = None
    
    dns = None
    cnames = None

    heartbeat = None

    @property
    def node(self):
        return self._node

    @property
    def fqdn(self):
        if self.node:
            return self.hostname + '.' + self.domain
        return None

    @property
    def hostname(self):
        if self.node:
            return self.name + "." + self.node.name
        return None
    
    @property
    def domain(self):
        if self.node:
            return self.node.domain
        return None

    @property
    def firewallRules(self):
        return self._fwrules
    
    def clearFirewallRules(self):
        self._fwrules = None

    def addFirewallRule(self, rule):
        if not self._fwrules:
            self._fwrules = []

        if not self._checkFirewallRule(rule.name):
            rule.link(self)
            self._fwrules.append(rule)

    def _checkFirewallRule(self, name):
        for rule in self._fwrules:
            if rule.name == name:
                return True
        return False

    def _deserialize(self, data, db=None, node=None):
        self._db = db
        if db:
            self._table = db.containers
        if node: 
            self._node = node
        self.name = data['name']
        self.uuid = data['uuid']
        self.ip = data['ip']
        self.bridge = data['bridge']
        self.dns = data['dns']
        self.cnames = data['cnames']
        self.image = data['image']
        self.status = data['status']
        if 'heartbeat' in data:
            self.heartbeat = data['heartbeat']
        
        self._fwrules = []
        for fwitem in data['fwrules']:
            self._fwrules.append(NhfwFirewallRule.createFromData(fwitem, parent=self))
        
        return self
    
    def _serialize(self):
        if not self.uuid:
            self.uuid = str(uuid4())

        fwrules = []
        if self._fwrules:
            for rule in self._fwrules:
                fwrules.append(rule._serialize())

        return { 
            'name': self.name,
            'uuid': self.uuid,
            'node': self._node.uuid,
            'ip': self.ip,
            'bridge': self.bridge,
            'dns': self.dns,
            'cnames': self.cnames,
            'image': self.image,
            'status': self.status,
            'fwrules': fwrules,
            'heartbeat': self.heartbeat
             }

    @property
    def isNew(self):
        return self._db == None

    @property
    def isRunning(self):
        return self.status == 'running'

    def saveToDB(self, db=None, node=None):
        self.heartbeat = str(datetime.utcnow().timestamp())
        if node: 
            self._node = node
        if self._table == None:
            self._db = db
            self._table = db.containers
            self._table.insert(self._serialize())
        else:
            qn = Query()    
            self._table.update(self._serialize(), qn.uuid == self.uuid)

    def __repr__(self):
        return "NhfwContainer name={}, uuid={}".format(self.name, self.uuid)

    @classmethod
    def listFromDB(cls, db, node=None):
        list = None        
        if node:
            qc = Query()
            list = db.containers.search(qc.node == node.uuid)
        else:        
            list = db.containers.all()
        return map(lambda data: cls()._deserialize(data, db=db), list)

    @classmethod
    def getFromDB(cls, db, node, name=None, uuid=None):
        data = None
        qc = Query()
        if uuid:
            data = db.containers.get(qc.node == node.uuid and qc.uuid == uuid)
        elif name:
            data = db.containers.get(qc.node == node.uuid and qc.name == name)
        if data: 
            return cls()._deserialize(data,db=db,node=node)
        return None