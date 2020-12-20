FWR_DOCK_CLIENT=1
FWR_DOCK_SERVER=2

class NhfwFirewallRule:
    _parent = None

    name = None
    type = None
    protocol = None
    port = None
    src = None
    dst = None
    trust = None
    inif = None
    outif = None

    def link(self, parent):
        self._parent = parent

    @property
    def fullname(self):
        if not self._parent:
            return None
        if self.type in [FWR_DOCK_CLIENT, FWR_DOCK_SERVER]:
            return "nhfw.container.{}.rule.{}".format(self._parent.name, self.name)
        return None

    def _serialize(self):
        return { 'name': self.name, 'type': self.type, 'protocol': self.protocol, 'port': self.port, 'src': self.src,  'dst': self.dst ,  'trust': self.trust, 'inif': self.inif, 'outif': self.outif }

    def _deserialize(self, data, parent=None):
        if parent:
            self.link(parent)
        self.name = data['name']
        self.type = data['type']
        self.protocol = data['protocol']
        self.port = data['port']
        self.src = data['src']
        self.dst = data['dst']
        self.trust = data['trust']
        if 'inif' in data:
            self.inif = data['inif']
        if 'outif' in data:
            self.outif = data['outif']
        return self

    def clone(self):
        return NhfwFirewallRule()._deserialize(self._serialize(), parent=self._parent)

    def __repr__(self):
        if self.type == FWR_DOCK_CLIENT:
            return "NhfwFirewallRule type=Docker Client, port={}/{}, to={}, name={}".format(self.port, self.protocol, self.dst, self.name)
        elif self.type == FWR_DOCK_SERVER:
            return "NhfwFirewallRule type=Docker Server, port={}/{}, from={}, name={}".format(self.port, self.protocol, self.src, self.name)
        else:
            return "<NhfwFirewallRule: Invalid rule>"

    @classmethod
    def createFromData(cls, data, parent=None):
        return cls()._deserialize(data, parent=parent)
