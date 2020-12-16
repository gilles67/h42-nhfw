import os
from tinydb import TinyDB, Query

DB_FILE="/etc/nhfw/db.json"

class NhfwDatabase:
    _db = None

    def __init__(self):
        self._opendb()

    def _opendb(self):
        dir = os.path.dirname(DB_FILE)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self._db = TinyDB(DB_FILE)

    @property
    def nodes(self):
        return self._db.table('node')
    
    @property
    def containers(self):
        return self._db.table('container')
