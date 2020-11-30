
class DockContainer:
    
    def __init__(self, name=None, client=None, objdata=None):
        if objdata:
            self._container = objdata
        if name and client:
            self._container = client.containers.get(name)
        if self._container == None:
            raise Exception("[DockContainer] Invalide data")

    @property
    def name(self):
        return self._container.name

    @property
    def isDnsRegister(self):
        if 'one.h42.nhfw.dns.register' in self._container.labels: 
            return _check_bool(self._container.labels['one.h42.nhfw.dns.register'])
        return False

    @property
    def isRunning(self):
        return self._container.status == 'running'

    @property
    def containerIp(self):
        if self.isRunning: 
            return self._container.attrs['NetworkSettings']['GlobalIPv6Address']
        return None

    @property
    def additionnalName(self):
        names = []
        for item in self._container.labels:
            if item.startswith('one.h42.nhfw.dns.name'):
                names.append(self._container.labels[item])
        return names


    def _init_data(self):
        return {
            'type': 'docker',
            'name': self.name,
            'ip': self.containerIp
        }

    def addToDnsAuthority(self, api):
        dns_data = self._init_data()
        dns_data['cname'] = self.additionnalName
        return api.post('/dns/{}/docker/{}'.format(api.hostuuid, self.name), dns_data)

    def removeFromDnsAuthority(self, api):
        dns_data = self._init_data()
        return api.delete('/dns/{}/docker/{}'.format(api.hostuuid, self.name), dns_data)

    def notifyGreatFirewall(self, api):
        fw_data = self._init_data()
    
    def applyFirewallRules(self):
        pass


def _check_bool(value):
    return value.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly']
        

def get_containers(client):
    list = client.containers.list(all=True)
    return map(lambda item: DockContainer(objdata=item), list)
