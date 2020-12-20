from nhfw.logging import nhfwlog_name
nhfwlog_name('nhfw.nodelib')
from nhfw.daemon import fork_magic

def main():
    from nhfw.logging import nhfwlog
    from nhfw.nodelib.config import NodelibConfig
    from nhfw.nodelib.docker import updateInventory, containerChange, updateFirewallRules
    from nhfw.nodelib.client import NodelibClient
    from nhfw.database import NhfwDatabase

    nhfwlog.info('Starting Docker monitor')

    config = NodelibConfig()
    client = NodelibClient(config)
    db = NhfwDatabase()
    mynode = config.getLocalNode(db)
    client.routerUpdateNode(mynode)

    updateInventory(mynode, client)

    updateFirewallRules(mynode)
    
    nhfwlog.info('Started Docker monitor')

    try:
        containerChange(mynode, client)
    except KeyboardInterrupt:
        nhfwlog.info('Stopped Docker monitor')
        exit(0)

if __name__ == "__main__":
    fork_magic('/run/nhfw.nodelib.pid', main)