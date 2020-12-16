import docker, syslog, time
from nhfw.models.container import NhfwContainer
from nhfw.models.firewallrule import *
from nhfw.firewall import *


## update inventory

def updateInventory(mynode, client):
    # Connect to docker
    dock = docker.DockerClient(base_url='unix://var/run/docker.sock')
    
    # List container
    list = dock.containers.list(all=True)
    for item in list:
        # Check if container can be monitor by nodelib
        if not 'one.h42.nhfw.enable' in item.labels:
            continue
        else:
            if not _checkBool(item.labels['one.h42.nhfw.enable']):
                syslog.syslog("Skip Docker container name={}".format(name))
                continue;

        mycontainer = _updateContainer(mynode, dock, item.name)
        
        client.routerUpdateContainer(mycontainer)

    dock.close()

## monitor status change

def containerChange(mynode, client):
    dock = docker.DockerClient(base_url='unix://var/run/docker.sock')
    for event in dock.events(decode=True):
        if 'status' in event:
            if 'Actor' in event:
                name = event['Actor']['Attributes']['name']
            
            dtainer = dock.containers.get(name)
            if not 'one.h42.nhfw.enable' in dtainer.labels:
                continue
            if not event['status'] in ["start", "stop"]:
                continue

            mycontainer = _updateContainer(mynode, dock, dtainer.name)
            
            print("Update Docker container, name={}, status={}, tigger={}".format(mycontainer.name, mycontainer.status, event['status']))
            _applyFirewallRules(mycontainer)
            syslog.syslog("Update Docker container, name={}, status={}, tigger={}".format(mycontainer.name, mycontainer.status, event['status']))
            client.routerUpdateContainer(mycontainer)
            print("End")

    dock.close()


def _updateContainer(mynode, dock, name):

        networks_bridge = _getNetworkBridge(dock)        

        #update information

        item = dock.containers.get(name)

        mycontainer = mynode.getContainer(name=item.name)
        if not mycontainer: 
           mycontainer = NhfwContainer()
        
        mycontainer.name = item.name
        mycontainer.status = item.status
        mycontainer.image = item.image.tags[0]
        
        if item.status == 'running':
            mycontainer.ip = item.attrs['NetworkSettings']['GlobalIPv6Address']
            net = [*item.attrs['NetworkSettings']['Networks'].keys()][0]
            if net in networks_bridge:
                mycontainer.bridge = networks_bridge[net]
            else:
                mycontainer.bridge = None
        else:
            mycontainer.ip = None
            mycontainer.bridge = None

        if 'one.h42.nhfw.dns.register' in item.labels:
            mycontainer.dns = _checkBool(item.labels['one.h42.nhfw.dns.register'])
              
        # Transforme labels to dictionnary
        labels = _labelsTree(item.labels)

        try:
            mycontainer.cnames = [*labels['nhfw']['dns']['name'].values()]
        except:
            mycontainer.cnames = None

        for fwitem in labels['nhfw']['firewall']['rule']:
            myfwrule = _createFirewallRule(fwitem, labels['nhfw']['firewall']['rule'][fwitem])
            mycontainer.addFirewallRule(myfwrule)

        # Save Container to DB
        if mycontainer.isNew:
            mynode.addContainer(mycontainer)
            syslog.syslog("New Docker container, name={}".format(mycontainer.name))
        else:
            mycontainer.saveToDB()
            syslog.syslog("Update Docker container, name={}".format(mycontainer.name))
        
        return mycontainer


def _getNetworkBridge(dock): 
    nets = dock.networks.list()
    networks_bridge={}
    for net in nets:
        if net.attrs['Name']:
            if 'com.docker.network.bridge.name' in net.attrs['Options']:
                networks_bridge[net.attrs['Name']] =  net.attrs['Options']['com.docker.network.bridge.name']
    return networks_bridge


## Convert Labels to dict

def _labelsTree(labels):
    dlabel = {}
    for label in labels:
        value = labels[label]
        if label.startswith('one.h42.nhfw'):
            label = label.replace('one.h42.nhfw', 'nhfw')
        indexes = label.split('.')
        _labelsTreeRecurse(dlabel, indexes, value)
    return dlabel

def _labelsTreeRecurse(dict, indexes, value):
    index = indexes.pop(0)
    if len(indexes) == 0:
        dict[index] = value
    else:       
        if not index in dict:
            dict[index] = {}
        _labelsTreeRecurse(dict[index], indexes, value)

# Check bool

def _checkBool(value):
    return value.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly']



# Firewall

# Create Firewall rules
def _createFirewallRule(name, data):
    fwrule = NhfwFirewallRule()
    fwrule.name = name
    topo = None
    if 'server' in data:
        topo = data['server']
        fwrule.type = FWR_DOCK_SERVER
        if 'client' in topo:
            fwrule.src = topo['client']
    elif 'client' in data:
        topo = data['client']
        fwrule.type = FWR_DOCK_CLIENT
        if 'server' in topo:
            fwrule.dst = topo['server']
    else: 
        fwrule = None

    if topo:
        if 'tcp' in topo:
            fwrule.protocol = 'tcp'
            fwrule.port = topo['tcp']
        if 'udp' in topo:             
            fwrule.protocol = 'udp'
            fwrule.port = topo['udp']

    return fwrule

def updateFirewallRules(mynode):
    for container in mynode.containers:
        _applyFirewallRules(container)

def _applyFirewallRules(container):
    for rule in container.firewallRules:
        if container.isRunning:
            while not checkFilterRule(rule.fullname):
                addFilterRule(rule)
                print("Add try {}".format(rule))
                time.sleep(1)
            syslog.syslog("Add Firewall rule, {}".format(rule))
        else:
            while checkFilterRule(rule.fullname):
                deleteFilterRule(rule.fullname)
                print("Delete try {}".format(rule))
            syslog.syslog("Delete Firewall rule, {}".format(rule))
