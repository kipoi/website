""" Main app view containing app instance and root view.
It also contains all template filters and context processors
that are available across whole webapp. 
"""
import os
import base64
from datetime import datetime
import kipoi
from flask import Flask, redirect, url_for
from kipoi.external import flatten_json

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
    if isinstance(schema, kipoi.components.ArraySchema):
        return {"list": [schema],
                "type": "Single numpy array"}
    elif isinstance(schema, list):
        return {"list": schema,
                "type": "List of numpy arrays"}
    elif isinstance(schema, dict):
        flattened_schema = flatten_json.flatten(dd=schema, separator='/')
        schema_list = []
        for key, value in flattened_schema.items():
            value = value.get_config()
            value["name"] = key
            schema_list.append(value)
        return {"list": schema_list,
                "type": "Dictionary of numpy arrays"}


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
        return u'http://kipoi.org'

    return dict(YEAR=year(),
                APP_NAME=app_name(),
                APP_URL=app_url())


from app.models.views import mod
app.register_blueprint(mod)


from app.models.cache import cache
cache.init_app(app)
