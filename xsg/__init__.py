from flask import Flask

app = Flask(__name__)
import xsg.views
import random

#  debugging JS code; force reload of JS code with every html refresh for debugging
def js_debug():
    if app.debug:
        return '?v=' + str(random.randint(1,9999))
    else:
        return ''

app.jinja_env.globals.update(js_debug=js_debug)
