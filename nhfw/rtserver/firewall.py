import time
from nhfw.models.firewallrule import *
from nhfw.firewall import checkFilterRule, addFilterRule, deleteFilterRule
from nhfw.logging import nhfwlog


def container_rules(container, app):
    zones = ['br0', 'wg42']

    if not container.firewallRules:
        return 

    for rule in container.firewallRules:
        if rule.type == FWR_DOCK_SERVER:
            nhfwlog.debug(rule)
            for zone in zones:
                zrule = rule.clone()
                zrule.name = zrule.name + '.' + zone
                zrule.inif = zone
                zrule.outif = 'wg0'
                if container.isRunning:
                    while not checkFilterRule(zrule.fullname):
                        addFilterRule(zrule)
                        nhfwlog.debug("Add try {}".format(zrule))
                        time.sleep(1)
                    nhfwlog.info("Add Firewall rule, {}".format(zrule))
                else:
                    while checkFilterRule(zrule.fullname):
                        deleteFilterRule(zrule.fullname)
                        nhfwlog.debug("Delete try {}".format(zrule))
                    nhfwlog.info("Delete Firewall rule, {}".format(zrule))
                nhfwlog.debug(zrule._serialize())
