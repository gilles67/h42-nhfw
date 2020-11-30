from flask import Flask
app = Flask(__name__)

from nhfw.dnslib.dnsapi import dnsapib
app.register_blueprint(dnsapib)

from nhfw.rtserver.config import RouterConfig
conf = RouterConfig()

app.config['router'] = conf


if __name__ == '__main__':
    app.run(debug=True, host='::', port=80)
