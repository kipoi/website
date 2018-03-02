"""Generate code snippets
"""
import os
import kipoi
import pprint
from app.config import SOURCE
from kipoi.cli.env import conda_env_name


def get_model_dir(model_name):
    """Get the model directory name
    """
    return os.path.join("~/.kipoi/models", model_name)


def get_dataloader_descr(model_name):
    dl_path = os.path.join(model_name, kipoi.get_model_descr(model_name).default_dataloader)
    return kipoi.get_dataloader_descr(dl_path)


def get_example_kwargs(model_name):
    """Get the example kwargs from the dataloader
    """
    dl = get_dataloader_descr(model_name)
    return dl.get_example_kwargs()


def get_batch_size(model_name):
    # HACK
    if SOURCE == "kipoi" and model_name == "Basenji":
        return 2
    else:
        return 4

# --------------------------------------------
# Python


# python specific snippets
def py_set_example_kwargs(model_name):
    example_kwargs = get_example_kwargs(model_name)
    return "\nkwargs = " + pprint.pformat(example_kwargs)


def py_snippet(model_name):
    """Generate the python code snippet
    """
    try:
        kw = get_example_kwargs(model_name)
    except Exception:
        kw = "Error"
    ctx = {"model_name": model_name,
           "example_kwargs": kw,
           "batch_size": get_batch_size(model_name)}
    return [("Get the model", """import kipoi
model = kipoi.get_model('{model_name}')""".format(**ctx)),
            ("Make a prediction for example files",
             """pred = model.pipeline.predict_example()""".format(**ctx)
             ),
            ("Use dataloader and model separately",
             """# setup the example dataloader kwargs
dl_kwargs = {example_kwargs}
import os; os.chdir(os.path.expanduser('~/.kipoi/models/{model_name}'))
# Get the dataloader and instantiate it
dl = model.default_dataloader(**dl_kwargs)
# get a batch iterator
it = dl.batch_iter(batch_size={batch_size})
# predict for a batch
batch = next(it)
model.predict_on_batch(batch['inputs'])""".format(**ctx)),
            ("Make predictions for custom files directly",
             """pred = model.pipeline.predict(dl_kwargs, batch_size={batch_size})""".format(**ctx)
             ),
            ]


# --------------------------------------------
# Bash / CLI

def bash_snippet(model_name):
    try:
        kw = get_example_kwargs(model_name)
        env_name = conda_env_name(model_name, model_name, SOURCE)
    except Exception:
        kw = "Error"
        env_name = "Error"
    ctx = {"model_name": model_name,
           "model_name_no_slash": model_name.replace("/", "|"),
           "env_name": env_name,
           "example_kwargs": kw}
    return [
        ("Create a new conda environment with all dependencies installed", "kipoi env create {model_name}\nsource activate {env_name}".format(**ctx)),
        ("Install model dependencies into current environment", "kipoi env install {model_name}".format(**ctx)),
        ("Test the model", "kipoi test {model_name} --source=kipoi".format(**ctx)),
        ("Make a prediction", """cd ~/.kipoi/models/{model_name}
kipoi predict {model_name} \\
  --dataloader_args='{example_kwargs}' \\
  -o '/tmp/{model_name_no_slash}.example_pred.tsv'
# check the results
head '/tmp/{model_name_no_slash}.example_pred.tsv'
""".format(**ctx)),
    ]


# TODO - add kipoi postproc score variants example

# --------------------------------------------
# R


def render_dict_as_R(d):
    ["{k}={v}".format(k=k, v=pprint.pformat(v)) + ""for k, v in d.items()]


def format_R_kwargs(obj):
    assert isinstance(obj, dict)
    return ", ".join([str(k) + "=" + format_R_obj(v)
                      for k, v in obj.items()])


def format_R_obj(obj):
    if isinstance(obj, list):
        return "list(" + ", ".join([format_R_obj(x)
                                    for x in obj]) + ")"
    elif isinstance(obj, dict):
        return "list(" + format_R_kwargs(obj) + ")"
    elif isinstance(obj, tuple):
        return format_R_obj(list(obj))
    else:
        return pprint.pformat(obj)


def R_snippet(model_name):
    """Generate the python code snippet
    """
    try:
        kw = format_R_kwargs(get_example_kwargs(model_name))
    except Exception:
        kw = "Error"
    ctx = {"model_name": model_name,
           "example_kwargs": kw,
           "batch_size": get_batch_size(model_name)}
    return [("Get the model", """library(reticulate)
kipoi <- import('kipoi')
model <- kipoi$get_model('{model_name}')""".format(**ctx)),
            ("Make a prediction for example files",
             "predictions <- model$pipeline$predict_example()".format(**ctx)
             ),
            ("Use dataloader and model separately",
             """# Get the dataloader
setwd('~/.kipoi/models/{model_name}')
dl <- model$default_dataloader({example_kwargs})
# get a batch iterator
it <- dl$batch_iter(batch_size={batch_size})
# predict for a batch
batch <- iter_next(it)
model$predict_on_batch(batch$inputs)""".format(**ctx)),
            ("Make predictions for custom files directly",
             """pred <- model$pipeline$predict(dl_kwargs, batch_size={batch_size})""".format(**ctx)
             ),
            ]


# --------------------------------------------

def get_snippets(model_name):
    return {"cli": bash_snippet(model_name),
            "python": py_snippet(model_name),
            "R": R_snippet(model_name)}


# --------------------------------------------
# Tests

def test_single_snippet():
    get_snippets("HAL")
    get_snippets("DeepSEA")


def test_get_snippets():
    models = kipoi.list_models().model.unique()
    for model_name in models:
        assert isinstance(get_snippets(model_name), dict)


def test_print(model_name):
    """Test the printed snippets
    """
    snippets = get_snippets(model_name)
    for lang, l in snippets.items():
        print("---------------")
        print("Language: {0}".format(lang))
        print("---------------")
        for k, v in l:
            print("--> " + k + "\n" + v + "\n")
