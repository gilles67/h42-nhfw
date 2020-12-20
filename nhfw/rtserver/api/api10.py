import os
import jinja2
import ipaddress
from nhfw.models.node import NhfwNode
from nhfw.models.container import NhfwContainer
from nhfw.rtserver.dns import container_records
from nhfw.rtserver.firewall import container_rules

from flask import Blueprint, Response, request, current_app, jsonify
from pystemd.systemd1 import Unit

apilib = Blueprint('api', __name__)

tloader = jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates'))
tenv = jinja2.Environment(loader=tloader)


@apilib.route('/api/1.0/node/<nodeuuid>', methods=['POST'])
def node_update(nodeuuid):
    data = request.get_json()
    dbnode = current_app.db.getNode(nodeuuid)
    if dbnode:
        dbnode._deserialize(data['payload'])
    else:
        dbnode = NhfwNode()._deserialize(data['payload'])
    dbnode.saveToDB(db=current_app.db)

    return jsonify({'result': 'Ok'}), 200


@apilib.route('/api/1.0/container/<containeruuid>', methods=['POST'])
def container_update(containeruuid):
    data = request.get_json()
    dbnode = current_app.db.getNode(data['node_uuid'])
    dbcontainer = dbnode.getContainer(uuid=containeruuid)
    if dbcontainer:
        dbcontainer._deserialize(data['payload'])
        dbcontainer.saveToDB()
    else:
        dbcontainer = NhfwContainer()._deserialize(data['payload'])
        dbnode.addContainer(dbcontainer)

    # Update DNS
    container_records(dbcontainer, current_app)

    # Update Firewall
    container_rules(dbcontainer, current_app)

    return jsonify({'result': 'Ok'}), 200


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

