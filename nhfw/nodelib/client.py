import requests


class NodelibClient:
    _config = None
    def __init__(self, config):
        self._config = config

    def get(self, uri, payload):
        return self._makeRequest(uri, payload, 'get')
        
    def post(self, uri, payload):
        return self._makeRequest(uri, payload, 'post')

    def delete(self, uri, payload):
        return self._makeRequest(uri, payload, 'delete')

    def routerUpdateNode(self, mynode):
        payload = mynode._serialize()
        uri = '/api/1.0/node/{}'.format(mynode.uuid)
        try:
            self.post(uri, payload)
        except:
            pass

    def routerUpdateContainer(self, mycontainer):
        payload = mycontainer._serialize()
        uri  = 'api/1.0/container/{}'.format(mycontainer.uuid)
        try:
            self.post(uri, payload)
        except: 
            pass

    def _makeRequest(self, uri, payload, method):
        data = {}
        data['node_name'] = self._config.name
        data['node_uuid'] = self._config.uuid
        data['payload']  = payload
        url = requests.compat.urljoin(self._config.router, uri)
        r = None
        if method == 'get':
            r = requests.get(url, json=data)
        elif method == 'post':
            r = requests.post(url, json=data)
        elif method == 'delete':
            r = requests.delete(url, json=data)
        return r






    