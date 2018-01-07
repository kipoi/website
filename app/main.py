""" Main app view containing app instance and root view.
It also contains all template filters and context processors
that are available across whole webapp. """

import os
import base64
from datetime import datetime
from flask import Flask
from models.views import models, list_models


def get_app_base_path():
    """ Get app base path. """
    return os.path.dirname(os.path.realpath(__file__))

def get_instance_folder_path():
    """ Get instance folder path. """
    return os.path.join(get_app_base_path(), 'instance')

app = Flask(__name__,
            instance_path=get_instance_folder_path(),
            instance_relative_config=True,
            template_folder='templates')

# Debug settings
app.config.update(
    DEBUG=True,
    EXPLAIN_TEMPLATE_LOADING=False
)

@app.template_filter('b64encode')
def base64encode(text):
    """Convert a string to base64."""
    return base64.b64encode(str.encode(text))

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

@app.route("/")
def entry():
    """ For root url redirect to model list. """
    return list_models()

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

if __name__ == "__main__":
    app.register_blueprint(models)
    app.run()
