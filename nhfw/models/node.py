from tinydb import Query
from nhfw.models.container import NhfwContainer

class NhfwNode:
    _db = None
    _table = None

    name = None
    domain = None
    uuid = None

    heartbeat = None

    # Container Functions

    @property
    def containers(self):
        return NhfwContainer.listFromDB(self._db, node=self)
    
    def getContainer(self, name=None, uuid=None):
        return NhfwContainer.getFromDB(self._db, self, name=name, uuid=uuid)

    def addContainer(self, container):
        container.saveToDB(db=self._db, node=self)

    # Storage Function

    def _serialize(self):
        return { 'name': self.name, 'domain': self.domain, 'uuid': self.uuid, 'heartbeat': self.heartbeat }

    def _deserialize(self, data, db=None):
        self._db = db
        self._table = db.nodes
        self.name = data['name']
        self.domain = data['domain']
        self.uuid = data['uuid']
        if 'heartbeat' in data:
            self.heartbeat = data['heartbeat']
        return self

    def saveToDB(self, db=None):
        self.heartbeat = str(datetime.utcnow().timestamp())
        if db:
            self._db = db
            self._table = db.nodes
            self._table.insert(self._serialize())
        else:
            qn = Query()    
            self._table.update(self._serialize(), qn.uuid == self.uuid)

    @classmethod
    def getFromDB(cls, id, db):
        qn = Query()
        data = db.nodes.get(qn.uuid == id)
        if data: 
            return cls()._deserialize(data,db=db)
        return None
    
    @classmethod
    def listFromDB(cls, db):
        print("Not implemented")


    def __repr__(self):
        return "NhfwNode name={}, uuid={}".format(self.name, self.uuid)
