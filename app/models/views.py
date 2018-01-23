""" This is a model view, containing all views related to the
KIPOI models. First is the model list that shows all available
models and the second is the models detail view that describes
selected model. """

import os
import kipoi
from flask import Blueprint, render_template, redirect, url_for
from models.code_snippets import get_snippets

models = Blueprint('models', __name__, template_folder='templates')

def get_view(model_path, df):
    """Test if the queried string is a model

    Args:
      relative path to the model: i.e. "" for the root, "rbp_eclip" for 
      accessing the rbp_eclip data subset
      df: pd.DataFrame returned by `kipoi.get_source("kipoi").list_models()`

    to be used in combination with:
    ```
    df = kipoi.get_source("kipoi").list_models()
    vtype_path = get_view(model_path, df)
    if vtype_path is None:
       # run 404
    else:
       vtype, path = vtype_path
    if vtype == "model":
        # render the normal model view
        pass
    elif vtype == "model_list":
        # run the normal model list view on a subseted table
        df_subset = df[df.model.str.contains("^" + path)]
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

@models.route("/groups/")
def list_groups():
    """ Group list view """

    group_df = kipoi.get_source("kipoi").list_models_by_group()
    group_list = group_df.to_dict(orient='records')
    return render_template("models/index_groups.html", groups=group_list)

@models.route('/models/<source>/<path:model_name>')
def model_list(source, model_name):
    """ Models list view """
    model_name = model_name.rstrip('/')
    df = kipoi.get_source("kipoi").list_models()
    vtype_path = get_view(model_name, df)
    print(vtype_path)
    if vtype_path is None:
       # run 404
        pass
    else:
        vtype, path = vtype_path

    # render the model detail view
    if vtype == "model":
        # Model info retrieved from kipoi
        model = kipoi.get_model_descr(model_name, source=source)

        # Model dataloaders info retrieved from kipoi
        dataloader = kipoi.get_dataloader_descr(os.path.join(model_name, model.default_dataloader))
        title = model_name.split('/')
        # obtain snippets
        code_snippets = get_snippets(model_name)
        
        return render_template("models/model_details.html",
                               model_name=model_name,
                               model=model,
                               dataloader=dataloader,
                               title=title,
                               code_snippets=code_snippets)

    # run the normal model list view on a subsetted table
    elif vtype == "model_list":
        model_df = kipoi.list_models()
        # Filter the results
        model_df = model_df[model_df.model.str.contains("^" + path)]

        filtered_models = model_df.to_dict(orient='records')
        return render_template("models/index.html", models=filtered_models)

    # redirect to the group list
    elif vtype == "group_list":
        return redirect(url_for('models.list_groups'))

# @models.route("/model/<source>/<path:model_name>")
# def model_details(source, model_name):
#     """ Model detail view """
#     # Model name parsed from url
#     # model_name = (base64.b64decode(model_name)).decode("utf-8")

#     # Model info retrieved from kipoi
#     model = kipoi.get_model_descr(model_name, source=source)

#     # Model dataloaders info retrieved from kipoi
#     dataloader = kipoi.get_dataloader_descr(os.path.join(model_name, model.default_dataloader))

#     return render_template("models/model_details.html",
#                            model_name=model_name,
#                            model=model,
#                            dataloader=dataloader)
