import syslog
from nhfw.nodelib.config import NodelibConfig
from nhfw.nodelib.docker import updateInventory, containerChange, updateFirewallRules
from nhfw.nodelib.client import NodelibClient
from nhfw.database import NhfwDatabase

syslog.openlog('nhfw.nodelib')

def main():

    syslog.syslog('Starting Docker monitor')

    config = NodelibConfig()
    client = NodelibClient(config)
    db = NhfwDatabase()
    mynode = config.getLocalNode(db)
    client.routerUpdateNode(mynode)

    updateInventory(mynode, client)

    updateFirewallRules(mynode)
    
    syslog.syslog('Started Docker monitor')

    try:
        containerChange(mynode, client)
    except KeyboardInterrupt:
        syslog.syslog('Stopped Docker monitor')
        exit(0)

if __name__ == "__main__":
    main()