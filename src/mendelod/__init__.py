from flask import Flask
from flask_bootstrap import Bootstrap

from mendeley import Mendeley
from mendeley.session import MendeleySession

import yaml

with open('config.yml') as f:
    config = yaml.load(f)
    


REDIRECT_URI = 'http://localhost:5000/redirect'

app = Flask(__name__)
Bootstrap(app)
app.debug = True
app.secret_key = config['clientSecret']

if 'token' in config:
    app.config['token'] =  config['token']

mendeley = Mendeley(config['clientId'], config['clientSecret'], REDIRECT_URI)


import views