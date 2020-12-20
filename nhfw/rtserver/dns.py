from netaddr import IPAddress
from nhfw.dnstools import NamedServer
from nhfw.logging import nhfwlog
log = nhfwlog

def container_records(container, app):
    
    rconfig = app.config['router']
    nserver = NamedServer('::1', rconfig.dnstsig)

    delete_ip = None

    # AAAA Record
    log.info("DNS Update rdtype=AAAA, fqdn={}, ip={}".format(container.fqdn, container.ip))

    if container.isRunning:
        nserver.update_record(container.domain, container.hostname, 'AAAA', container.ip)
    else:
        delete_ip = nserver.query_record(container.fqdn, 'AAAA')
        nserver.delete_record(container.domain, container.hostname, 'AAAA')

    # PTR
    log.info("DNS Update rdtype=PTR, fqdn={}, ip={}".format(container.fqdn, container.ip))
    
    if container.isRunning:
        arpa = IPAddress(container.ip).reverse_dns
        nserver.update_record('1.0.0.6.f.a.c.0.7.4.0.1.0.0.2.ip6.arpa', arpa, 'PTR', container.fqdn + '.')
    elif delete_ip: 
        arpa = IPAddress(delete_ip).reverse_dns
        nserver.delete_record('1.0.0.6.f.a.c.0.7.4.0.1.0.0.2.ip6.arpa', arpa, 'PTR')
