import os, time, netifaces, syslog
from netaddr import IPNetwork
from nhfw.daemon import fork_magic

syslog.openlog('nhfw.ndpproxy')

def ndpproxy_loop():
    syslog.syslog("Started")

    ifip_lan = netifaces.ifaddresses('br0')[netifaces.AF_INET6][0]
    lan = IPNetwork( ifip_lan['addr'] + '/' + ifip_lan['netmask'])
    lannet = str(lan.network)[:-1]

    syslog.syslog("Detect LAN side network {} : {} ".format('br0', lan.network))

    ifip_wan = netifaces.ifaddresses('enp4s0')[netifaces.AF_INET6][0]
    wan = IPNetwork( ifip_wan['addr'] + '/' + ifip_wan['netmask'])
    wannet = str(wan.network)[:-1]

    syslog.syslog("Detect WAN side network {} : {} ".format('enp4s0', wan.network))

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
                        #syslog.syslog("New IP {} already in cache".format(ip))
                        continue
                    else:
                        cache_ip.append(ip)
                        wanip = ip.replace(lannet, wannet)
                        syslog.syslog("Add IP {} on {} for {}".format(wanip, 'enp4s0', ip))
                        os.system('ip -6 neigh add proxy {} dev enp4s0'.format(wanip))
            ps.close()
            time.sleep(5)
    except KeyboardInterrupt:
        syslog.syslog("Stopped")
        exit(0)

if __name__ == "__main__":
    fork_magic('/run/nhfw.ndpproxy.pid', ndpproxy_loop)