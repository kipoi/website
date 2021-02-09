"""Generate code snippets
"""
import json
import os
import kipoi
import pprint
from kipoi.cli.env import conda_env_name


def get_dataloader_descr(model_name, source):
    from kipoi.utils import cd
    src = kipoi.get_source(source)
    md = kipoi.get_model_descr(model_name, source=source)
    if isinstance(md.default_dataloader, str):
        dl_path = os.path.join(model_name, md.default_dataloader)
        return kipoi.get_dataloader_descr(dl_path, source=source)
    else:
        with cd(src.get_model_dir(model_name)):
            return md.default_dataloader.get()


def get_example_kwargs(model_name, source='kipoi', output_dir='example'):
    """Get the example kwargs from the dataloader
    """
    dl = get_dataloader_descr(model_name, source=source)
    return dl.download_example(output_dir=output_dir, absolute_path=False, dry_run=True)


def get_batch_size(model_name, source):
    # HACK
    if source == "kipoi" and model_name == "Basenji":
        return 2
    else:
        return 4


def get_group_name(model_name, source):
    group = kipoi.get_source(source).get_group_name(model_name)
    if group is None:
        return model_name
    else:
        return group
# --------------------------------------------
# Docker

def docker_snippet(model_name, source="kipoi"):
    """
    Generate the snippet for the docker containers  

    Args:
        model_name (str): Name of the model the description being generated for
        source (str, optional): Where the model is residing. Defaults to "kipoi".
    """
    # TODO: read from kipoi-donctainer repo directly. Need an SSH key
    model_group_to_image_dict = {
    "DeepCpG_DNA": "haimasree/kipoi-docker:sharedpy3keras1.2",
    "CpGenie": "haimasree/kipoi-docker:sharedpy3keras1.2",
    "Divergent421": "haimasree/kipoi-docker:sharedpy3keras1.2",
    "Basenji": "haimasree/kipoi-docker:sharedpy3keras2",
    "Basset": "haimasree/kipoi-docker:sharedpy3keras2",
    "HAL": "haimasree/kipoi-docker:sharedpy3keras2",
    "DeepSEA": "haimasree/kipoi-docker:sharedpy3keras2",
    "Optimus_5Prime": "haimasree/kipoi-docker:sharedpy3keras2",
    "labranchor": "haimasree/kipoi-docker:sharedpy3keras2",
    "CleTimer": "haimasree/kipoi-docker:sharedpy3keras2",
    "SiSp": "haimasree/kipoi-docker:sharedpy3keras2",
    "FactorNet": "haimasree/kipoi-docker:sharedpy3keras2",
    "pwm_HOCOMOCO": "haimasree/kipoi-docker:sharedpy3keras2",
    "MaxEntScan": "haimasree/kipoi-docker:sharedpy3keras2",
    "DeepBind": "haimasree/kipoi-docker:sharedpy3keras2",
    "lsgkm-SVM": "haimasree/kipoi-docker:sharedpy3keras2",
    "rbp_eclip": "haimasree/kipoi-docker:sharedpy3keras2",
    "MPRA-DragoNN": "haimasree/kipoi-docker:mpra-dragonn",
    "extended_coda": "haimasree/kipoi-docker:extended_coda",
    "MMSplice/pathogenicity": "haimasree/kipoi-docker:mmsplice",
    "MMSplice/splicingEfficiency": "haimasree/kipoi-docker:mmsplice",
    "MMSplice/deltaLogitPSI": "haimasree/kipoi-docker:mmsplice",
    "MMSplice/modularPredictions": "haimasree/kipoi-docker:mmsplice",
    "MMSplice/mtsplice": "haimasree/kipoi-docker:mmsplice-mtsplice",
    "DeepMEL": "haimasree/kipoi-docker:deepmel",
    "Framepool": "haimasree/kipoi-docker:framepool",
    "KipoiSplice": "haimasree/kipoi-docker:kipoisplice",
    "deepTarget": "haimasree/kipoi-docker:deeptarget",
    "AttentiveChrome": "haimasree/kipoi-docker:attentivechrome",
    "BPNet-OSKN": "haimasree/kipoi-docker:bpnet-oskn",
    "SeqVec": "haimasree/kipoi-docker:seqvec",
    "Xpresso": "haimasree/kipoi-docker:sharedpy3keras2"
    }

    try:
        kw = get_example_kwargs(model_name, source)
    except Exception:
        kw = "Error"
    if isinstance(kw, dict):
        for key, value in kw.items():
            if isinstance(value, str):
                kw[key] = value.replace('example', '/app/example')
    ctx = {"model_name": model_name,
           "example_kwargs": kw,
           "batch_size": get_batch_size(model_name, source),
           "source": source,
           "model_name_no_slash": model_name.replace("/", "|"),
           "output_dir" : "example"
           }
    try:
        if model_name in model_group_to_image_dict: # Special provision for MMSplice
            docker_image_name =  model_group_to_image_dict[model_name]
        else:
            docker_image_name = model_group_to_image_dict[model_name.split('/')[0]]
    except Exception:
        docker_image_name = ""
    ctx["docker_image_name"] = docker_image_name
    print("docker image name {}".format(docker_image_name))
    return [("Get the docker image", """docker pull {docker_image_name}""".format(**ctx)),
            ("Get the activated conda environment inside the container",
             """docker run -it {docker_image_name}""".format(**ctx)
             ),
        ("Test the model", "docker run {docker_image_name} kipoi test {model_name} --source={source}".format(**ctx)),
        ("Make prediction for custom files directly", """mkdir -p <absolute path to your data dir>/output \\
docker run -v <absolute path to your data dir>:/app/ {docker_image_name} \\
kipoi get-example {model_name} -o /app/{output_dir} \\
docker run -v <absolute path to your data dir>:/app/ {docker_image_name} \\
kipoi predict {model_name} \\
--dataloader_args='{example_kwargs}' \\
-o '/app/output/{model_name_no_slash}.example_pred.tsv'
# check the results
head '<absolute path to your data dir>/output/{model_name_no_slash}.example_pred.tsv'
""".format(**ctx)),
]

# --------------------------------------------
# Python


# python specific snippets
# def py_set_example_kwargs(model_name, source):
#     example_kwargs = get_example_kwargs(model_name, source)
#     return "\nkwargs = " + pprint.pformat(example_kwargs)

def py_snippet(model_name, source="kipoi"):
    """Generate the python code snippet
    """
    try:
        kw = get_example_kwargs(model_name, source)
    except Exception:
        kw = "Error"
    ctx = {"model_name": model_name,
           "example_kwargs": kw,
           "batch_size": get_batch_size(model_name, source)}
    return [("Get the model", """import kipoi
model = kipoi.get_model('{model_name}')""".format(**ctx)),
            ("Make a prediction for example files",
             """pred = model.pipeline.predict_example()""".format(**ctx)
             ),
            ("Use dataloader and model separately",
             """# Download example dataloader kwargs
dl_kwargs = model.default_dataloader.download_example('example')
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

def bash_snippet(model_name, source="kipoi"):
    output_dir = 'example'
    try:
        kw = json.dumps(get_example_kwargs(model_name, source, output_dir=output_dir))
        group_name = get_group_name(model_name, source)
        env_name = conda_env_name(group_name, group_name, source)
    except Exception:
        kw = "Error"
        env_name = "Error"
        group_name = "Error"
    ctx = {"model_name": model_name,
           "model_name_no_slash": model_name.replace("/", "|"),
           "group_name": group_name,
           "env_name": env_name,
           "source": source,
           "output_dir": output_dir,
           "example_kwargs": kw}
    return [
        ("Create a new conda environment with all dependencies installed", "kipoi env create {group_name}\nsource activate {env_name}".format(**ctx)),
        ("Install model dependencies into current environment", "kipoi env install {group_name}".format(**ctx)),
        ("Test the model", "kipoi test {model_name} --source={source}".format(**ctx)),
        ("Make a prediction", """kipoi get-example {model_name} -o {output_dir}
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


def R_snippet(model_name, source="kipoi"):
    """Generate the python code snippet
    """
    try:
        kw = format_R_kwargs(get_example_kwargs(model_name, source))
    except Exception:
        kw = "Error"
    ctx = {"model_name": model_name,
           "example_kwargs": kw,
           "batch_size": get_batch_size(model_name, source)}
    return [("Get the model", """library(reticulate)
kipoi <- import('kipoi')
model <- kipoi$get_model('{model_name}')""".format(**ctx)),
            ("Make a prediction for example files",
             "predictions <- model$pipeline$predict_example()".format(**ctx)
             ),
            ("Use dataloader and model separately",
             """# Download example dataloader kwargs
dl_kwargs <- model$default_dataloader$download_example('example')
# Get the dataloader
dl <- model$default_dataloader(dl_kwargs)
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

def get_snippets(model_name, source="kipoi"):
    return {"cli": bash_snippet(model_name, source),
            "python": py_snippet(model_name, source),
            "R": R_snippet(model_name, source),
            "docker": docker_snippet(model_name, source)}


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
