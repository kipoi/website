""" This is a model view, containing all views related to the
KIPOI models. First is the model list that shows all available
models and the second is the models detail view that describes
selected model. """

import os
import kipoi
from flask import Blueprint, render_template, redirect, url_for

from app.models.code_snippets import get_snippets
from app.models.cache import cache

mod = Blueprint('models', __name__, template_folder='templates')


@cache.cached(key_prefix='model_groups')
def get_model_groups():
    """ Cache for list model groups """
    group_df = kipoi.get_source("kipoi").list_models_by_group()
    return group_df


@cache.cached(key_prefix='model_list')
def get_model_list():
    """ Cache for kipoi's list models """
    df = kipoi.get_source("kipoi").list_models()
    return df


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


@mod.route("/")
@mod.route("/groups/")
def list_groups():
    """ Group list view """
    group_df = get_model_groups()
    group_list = group_df.to_dict(orient='records')
    return render_template("models/index_groups.html", groups=group_list)


@mod.route("/main")
def main():
    """Main view
    """
    # TODO - get the following numbers:
    #
    # - Total number of models
    # - number of models supporting variant effect prediction
    # - Number of models by framework
    # - Total number of output dimensions for a variant
    models_by_framework = {"Pytorch": 2, "Tensorflow": 1, "Keras": 3, "Custom": 3, "Scikit-learn": 0}

    df = get_model_list()
    dfg = get_model_groups()

    # models_by_framework = dict(df.type.value_counts())
    # models_by_license = dict(df.license.value_counts())
    models_by_framework = dict(dfg.type.apply(lambda x: list(x)[0]).value_counts())
    models_by_license = dict(dfg.license.apply(lambda x: list(x)[0]).value_counts())

    # TODO - postprocessing functionality barplot ...

    # TODO - put the colors also here:
    return render_template("models/main.html",
                           n_models=len(df),
                           n_groups=len(dfg),
                           n_contributors=len({x.name for contributors in df.contributors for x in contributors}),
                           models_by_framework_keys=list(models_by_framework),
                           models_by_framework_values=list(models_by_framework.values()),
                           models_by_license_keys=list(models_by_license),
                           models_by_license_values=list(models_by_license.values()))


@mod.route('/models/<source>/<path:model_name>')
def model_list(source, model_name):
    """ Models list view """
    df = get_model_list()
    model_name = model_name.rstrip('/')
    vtype_path = get_view(model_name, df)

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
        model_df = get_model_list()
        # Filter the results
        model_df = model_df[model_df.model.str.contains("^" + path)]

        filtered_models = model_df.to_dict(orient='records')
        return render_template("models/index.html", models=filtered_models)

    # redirect to the group list
    elif vtype == "group_list":
        return redirect(url_for('models.list_groups'))
