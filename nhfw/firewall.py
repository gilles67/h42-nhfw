import iptc, socket

from netaddr import IPAddress, IPNetwork
from nhfw.models.firewallrule import *

# Filter Rule
def addFilterRule(rule, table='ufw6-user-forward'):
    iptable = iptc.Table6(iptc.Table6.FILTER)
    chain = iptc.Chain(iptable, table)
    chain_rule = iptc.Rule6()
    
    if not rule.type in [FWR_DOCK_CLIENT, FWR_DOCK_SERVER]:
        return None

    if rule.type == FWR_DOCK_CLIENT:
        chain_rule.in_interface = rule.inif
        chain_rule.out_interface = rule.outif
        chain_rule.src = rule._parent.ip
        chain_rule.dst = validate_address(rule.dst)

    elif rule.type == FWR_DOCK_SERVER:
        chain_rule.in_interface = rule.inif
        chain_rule.out_interface = rule.outif
        chain_rule.src = validate_address(rule.src)
        chain_rule.dst = rule._parent.ip

    chain_rule.target = chain_rule.create_target("ACCEPT")

    if rule.protocol in ['tcp', 'udp']:
        chain_rule.protocol = rule.protocol
        if rule.type in [FWR_DOCK_CLIENT, FWR_DOCK_SERVER]:
            match_proto = iptc.Match(chain_rule, rule.protocol)
            match_proto.dport = rule.port
            chain_rule.add_match(match_proto)

    if rule.fullname:
        match_txt = iptc.Match(chain_rule, "comment")
        match_txt.comment = rule.fullname
        chain_rule.add_match(match_txt)

    chain.insert_rule(chain_rule)
    iptable.commit()


def deleteFilterRule(name, table='ufw6-user-forward'):
    iptable = iptc.Table6(iptc.Table6.FILTER)
    iptable.autocommit = False
    chain = iptc.Chain(iptable, table)
    count = 0
    for rule in chain.rules:
        for match in rule.matches:
            if match.name == 'comment':
                if match.comment == name:
                    chain.delete_rule(rule)
                    count += 1
                    break
    iptable.commit()
    iptable.autocommit = True
    return count

def checkFilterRule(name, table='ufw6-user-forward'):
    iptable = iptc.Table6(iptc.Table6.FILTER)
    chain = iptc.Chain(iptable, table)
    for rule in chain.rules:
        for match in rule.matches:
            if match.name == 'comment':
                if match.comment == name:
                    return True
    return False


def validate_address(addr):
    if is_ipv6(addr):
        return addr
    elif is_network(addr):
        return addr
    else:
        return resolve_hostname(addr)

def is_ipv6(addr):
    try:
        IPAddress(addr)
        return True
    except:
        return False

def is_network(addr):
    try:
        IPNetwork(addr)
        return True
    except:
        return False

def resolve_hostname(fqdn): 
    hosts = socket.getaddrinfo(fqdn, 80, family=socket.AF_INET6, type=socket.SOCK_STREAM)
    for (family, type, proto, canonname, (address, port, flowinfo, scope_id)) in hosts:
        return address
    return None