""" This is a model view, containing all views related to the
KIPOI models. First is the model list that shows all available
models and the second is the models detail view that describes
selected model. """

import os
import base64
import kipoi
from flask import Blueprint, render_template

models = Blueprint('models', __name__, template_folder='templates')


def get_view(model_path, df):
    """Test if the queried string is a model

    Args:
      relative path to the model: i.e. "" for the root, "rbp_eclip" for accessing the rbp_eclip data subset
      df: pd.DataFrame returned by `kipoi.get_source("kipoi").list_models()`

    to be used in combination with:
    ```
    df = kipoi.get_source("kipoi").list_models()
    vtype, path = get_view(model_path, df)
    if vtype == "model":
        # render the normal model view
        pass
    elif vtype == "model_list":
        # run the normal view and subset the table via javascript using `path`
        pass
    elif vtype == "group_list":
        df_groups = kipoi.get_source("kipoi").list_models_by_group(path)
        # render the normal path
        # render the group view
    ```

    Returns:
       a tuple: (type, path), where type can be "model", "model_list" or "group_list"
    """
    names = df.model[df.model.str.contains("^" + model_path)]
    sub_names = names.str.replace("^" + model_path, "")
    # sub_models = sub_names[~sub_names.str.contains("^/")]
    sub_groups = sub_names[sub_names.str.contains("^/")].str.replace("^/", "")

    if len(sub_names) == 0:
        # error - no right string was found
        return None
    elif len(sub_names) == 1:
        # we have found a single one
        name = sub_names.iloc[0]
        if name == "":
            return ("model", model_path)
        else:
            return ("model", model_path + "/" + name)
    elif len(names) > 1:
        # there is more than one element in the list
        if sub_groups.str.contains("/").any():
            # some names contain further slashed in the name -
            return ("group_list", model_path)
        else:
            # remain just regular models in the list
            return ("model_list", model_path)


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
