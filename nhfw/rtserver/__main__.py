from nhfw.logging import nhfwlog_name
nhfwlog_name("nhfw.rtserver")
from nhfw.logging import nhfwlog

from flask import Flask
app = Flask(__name__)

from nhfw.rtserver.api.api10 import apilib
app.register_blueprint(apilib)

from nhfw.rtserver.config import RouterConfig
conf = RouterConfig()
app.config['router'] = conf

from nhfw.database import NhfwDatabase
app.db = NhfwDatabase()

nhfwlog.debug("Environement loaded")

if __name__ == '__main__':
    nhfwlog.debug("Starting flask server")
    app.run(debug=True, host='::', port=80)
