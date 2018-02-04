""" Main app view containing app instance and root view.
It also contains all template filters and context processors
that are available across whole webapp. """

import os
import base64
from datetime import datetime
from flask import Flask, redirect, url_for


def get_app_base_path():
    """ Get app base path. """
    return os.path.dirname(os.path.realpath(__file__))

def get_instance_folder_path():
    """ Get instance folder path. """
    return os.path.join(get_app_base_path(), 'instance')

app = Flask(__name__,
            instance_path=get_instance_folder_path(),
            template_folder='templates')

app.config.from_pyfile('config.py')

@app.template_filter('b64encode')
def base64encode(text):
    """Convert a string to base64."""
    return base64.b64encode(str.encode(text))

@app.template_filter('parse_cite_as')
def parse_cite_as(cite):
    """Convert set of strings to list of strings."""
    if isinstance(cite, set):
        if not cite:
            return []
        return cite.pop().split(',')
    elif isinstance(cite, str):
        return cite.split(',')

@app.template_filter('parse_schema')
def parse_schema(schema):
    """Parse model schema by removing unneeded fields and reordering them."""
    if isinstance(schema, object):
        return [schema]
    elif isinstance(schema, list):
        return schema
    elif isinstance(schema, dict):
        schema_list = []
        for key, value in schema.items():
            value["name"] = key
            schema_list.append(value)
        return schema_list

@app.context_processor
def app_processor():
    """ Default context processors. """
    def year():
        """ Current year. """
        return datetime.now().strftime("%Y")

    def app_name():
        """ App name. """
        return u'KIPOI project website'

    def app_url():
        """ App url. """
        return u'http://kipoi.in.tum.de'

    return dict(YEAR=year(),
                APP_NAME=app_name(),
                APP_URL=app_url())

from app.models.views import mod
app.register_blueprint(mod)

from app.models.cache import cache
cache.init_app(app)
