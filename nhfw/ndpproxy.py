from nhfw.logging import nhfwlog_name
nhfwlog_name('nhfw.ndpproxy')
from nhfw.daemon import fork_magic

def ndpproxy_loop():
    import os, time, netifaces
    from netaddr import IPNetwork
    from nhfw.logging import nhfwlog

    nhfwlog.info("Started")

    ifip_lan = netifaces.ifaddresses('br0')[netifaces.AF_INET6][0]
    lan = IPNetwork( ifip_lan['addr'] + '/' + ifip_lan['netmask'])
    lannet = str(lan.network)[:-1]

    nhfwlog.info("Detect LAN side network if={}, network={}".format('br0', lan.network))

    ifip_wan = netifaces.ifaddresses('enp4s0')[netifaces.AF_INET6][0]
    wan = IPNetwork( ifip_wan['addr'] + '/' + ifip_wan['netmask'])
    wannet = str(wan.network)[:-1]

    nhfwlog.info("Detect WAN side network if={}, network={}".format('enp4s0', wan.network))

    cache_ip = []
    try:
        while True:
            ps = os.popen('ip -6 neigh show dev br0 nud reachable')
            while True:
                line = ps.readline() 
                if line == "":
                    break
                ip = line.split(' ')[0]
                ipn = IPNetwork(ip + '/64')
                if ipn.network == lan.network:
                    if ip in cache_ip:
                        nhfwlog.debug("IP in cache ip={}".format(ip))
                        continue
                    else:
                        cache_ip.append(ip)
                        wanip = ip.replace(lannet, wannet)
                        cmdret = os.system('ip -6 neigh add proxy {} dev enp4s0'.format(wanip))
                        nhfwlog.info("Add IP in proxy, wanif={}, wanip={}, lanip={}, return={}".format('enp4s0', wanip, ip, cmdret))

            ps.close()
            time.sleep(5)
    except KeyboardInterrupt:
        nhfwlog.info("Stopped")
        exit(0)

if __name__ == "__main__":
    fork_magic('/run/nhfw.ndpproxy.pid', ndpproxy_loop)