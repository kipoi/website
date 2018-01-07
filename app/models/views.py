""" This is a model view, containing all views related to the
KIPOI models. First is the model list that shows all available
models and the second is the models detail view that describes
selected model. """

import os
import base64
import kipoi
from flask import Blueprint, render_template

models = Blueprint('models', __name__, template_folder='templates')

@models.route("/models/")
def list_models():
    """ Model list view """
    # Retrieve model list
    model_df = kipoi.list_models()

    # Convert dataframe to dictionary of records
    model_list = model_df.to_dict(orient='records')

    return render_template("models/index.html", models=model_list)

@models.route("/model/<source>/<model_name>")
def model_details(source, model_name):
    """ Model detail view """
    # Model name parsed from url
    model_name = (base64.b64decode(model_name)).decode("utf-8")

    # Model info retrieved from kipoi
    model = kipoi.get_model_descr(model_name, source=source)

    # Model dataloaders info retrieved from kipoi
    dataloader = kipoi.get_dataloader_descr(os.path.join(model_name, model.default_dataloader))

    return render_template("models/model_details.html",
                           model_name=model_name,
                           model=model,
                           dataloader=dataloader)
