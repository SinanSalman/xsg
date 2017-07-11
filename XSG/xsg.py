import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import json
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , xsg.py
app.debug = True

# Load default config and override config from an environment variable
with open('./xsg/config.json') as config_file:
    config_data = json.load(config_file)
config_data['DATABASE'] = os.path.join(app.instance_path, config_data['DATABASE'])
app.config.update(config_data)
app.config.from_envvar('XSG_SETTINGS', silent=True)

toolbar = DebugToolbarExtension(app)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
