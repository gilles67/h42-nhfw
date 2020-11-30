import os
import jinja2
import ipaddress
from flask import Blueprint, Response, request, current_app
from pystemd.systemd1 import Unit

dnsapib = Blueprint('dns', __name__)

tloader = jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates'))
tenv = jinja2.Environment(loader=tloader)


@dnsapib.route('/dns/<hostuuid>/docker/<name>', methods=['POST'])
def docker_dns_update(hostuuid, name):
    data = request.get_json()
    filename = "/var/lib/nhfw/dnsmasq/{}-{}.conf".format(data['hostname'], data['name'])
    data['reverse_ip'] = ipaddress.ip_address(data['ip']).reverse_pointer
    data['fqdn'] = "{}.{}.{}".format(data['name'], data['hostname'], current_app.config['router'].domain)
    try:
        render_file(filename, 'docker-host.j2', data)
        reload_dnsmasq()
        return {'state': 'Ok', 'fqdn': data['fqdn'], 'data': data}, 200
    except:
        return {'state': 'Failed', 'data': data}, 500

@dnsapib.route('/dns/<hostuuid>/docker/<name>', methods=['DELETE'])
def docker_dns_delete(hostuuid, name):
    data = request.get_json()
    filename = "/var/lib/nhfw/dnsmasq/{}-{}.conf".format(data['hostname'], data['name'])
    try:
        os.remove(filename)
        reload_dnsmasq()
        return {'state': 'Deleted', 'data': data}, 200
    except:
        return {'state': 'Failed', 'data': data}, 500

def reload_dnsmasq():
    unit = Unit(b'dnsmasq.service')
    unit.load()
    unit.Unit.Reload(b'replace')

def render_file(file, tname, data):
    folder = os.path.dirname(file)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    template = tenv.get_template(tname)
    with open(file, 'w') as fd:
        fd.write(template.render(data))

