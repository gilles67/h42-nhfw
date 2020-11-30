import docker
from yaml import load, dump
from nhfw.dockerlib.container import get_containers, DockContainer
from nhfw.apiclient.client import ApiClient 

api = ApiClient()
client = docker.DockerClient(base_url='unix://var/run/docker.sock')

containers = get_containers(client)
for item in containers:
    if item.isRunning:
        item.addToDnsAuthority(api)
    else:
        item.removeFromDnsAuthority(api)

try:
    for event in client.events(decode=True):
        if 'status' in event:
            container = None
            if 'Actor' in event:
                name = event['Actor']['Attributes']['name']
                container = DockContainer(name=name,client=client)
            if container and event['status'] == "start":
                if container.isDnsRegister:
                    container.addToDnsAuthority(api)
            if container and event['status'] == "stop":
                if container.isDnsRegister:
                    container.removeFromDnsAuthority(api)
except KeyboardInterrupt:
    pass

