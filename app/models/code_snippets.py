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
        "DeepCpG_DNA": "kipoi/kipoi-docker:sharedpy3keras1.2",
        "CpGenie": "kipoi/kipoi-docker:sharedpy3keras1.2",
        "Divergent421": "kipoi/kipoi-docker:sharedpy3keras1.2",
        "Basenji": "kipoi/kipoi-docker:sharedpy3keras2",
        "Basset": "kipoi/kipoi-docker:sharedpy3keras2",
        "HAL": "kipoi/kipoi-docker:sharedpy3keras2",
        "DeepSEA": "kipoi/kipoi-docker:sharedpy3keras2",
        "Optimus_5Prime": "kipoi/kipoi-docker:sharedpy3keras2",
        "labranchor": "kipoi/kipoi-docker:sharedpy3keras2",
        "CleTimer": "kipoi/kipoi-docker:sharedpy3keras2",
        "SiSp": "kipoi/kipoi-docker:sharedpy3keras2",
        "FactorNet": "kipoi/kipoi-docker:sharedpy3keras2",
        "pwm_HOCOMOCO": "kipoi/kipoi-docker:sharedpy3keras2",
        "MaxEntScan": "kipoi/kipoi-docker:sharedpy3keras2",
        "DeepBind": "kipoi/kipoi-docker:sharedpy3keras2",
        "lsgkm-SVM": "kipoi/kipoi-docker:sharedpy3keras2",
        "rbp_eclip": "kipoi/kipoi-docker:sharedpy3keras2",
        "MPRA-DragoNN": "kipoi/kipoi-docker:mpra-dragonn",
        "extended_coda": "kipoi/kipoi-docker:extended_coda",
        "MMSplice/pathogenicity": "kipoi/kipoi-docker:mmsplice",
        "MMSplice/splicingEfficiency": "kipoi/kipoi-docker:mmsplice",
        "MMSplice/deltaLogitPSI": "kipoi/kipoi-docker:mmsplice",
        "MMSplice/modularPredictions": "kipoi/kipoi-docker:mmsplice",
        "MMSplice/mtsplice": "kipoi/kipoi-docker:mmsplice-mtsplice",
        "DeepMEL": "kipoi/kipoi-docker:deepmel",
        "Framepool": "kipoi/kipoi-docker:framepool",
        "KipoiSplice": "kipoi/kipoi-docker:kipoisplice",
        "deepTarget": "kipoi/kipoi-docker:deeptarget",
        "AttentiveChrome": "kipoi/kipoi-docker:attentivechrome",
        "BPNet-OSKN": "kipoi/kipoi-docker:bpnet-oskn",
        "SeqVec": "kipoi/kipoi-docker:seqvec",
        "Xpresso": "kipoi/kipoi-docker:sharedpy3keras2",
        "epidermal_basset": "kipoi/kipoi-docker:sharedpy3keras1.2",
        "DeepFlyBrain": "kipoi/kipoi-docker:deepflybrain",
        "APARENT/site_probabilities": "kipoi/kipoi-docker:aparent-site_probabilities",
        "APARENT/veff": "kipoi/kipoi-docker:aparent-veff"
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
           "model_name_no_slash": model_name.replace("/", "_"),
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
    test_snippet = "Test the model", "docker run {docker_image_name} kipoi test {model_name} --source={source}".format(**ctx)
    predict_snippet = "Make prediction for custom files directly", """# Create an example directory containing the data
mkdir -p $PWD/kipoi-example 
# You can replace $PWD/kipoi-example with a different absolute path containing the data 
docker run -v $PWD/kipoi-example:/app/ {docker_image_name} \\
kipoi get-example {model_name} -o /app/{output_dir} 
docker run -v $PWD/kipoi-example:/app/ {docker_image_name} \\
kipoi predict {model_name} \\
--dataloader_args='{example_kwargs}' \\
-o '/app/{model_name_no_slash}.example_pred.tsv' 
# check the results
head $PWD/kipoi-example/{model_name_no_slash}.example_pred.tsv
""".format(**ctx)
    if model_name == "Basenji":
        test_snippet = "Test the model", "docker run {docker_image_name} kipoi test {model_name} --batch_size=2 --source={source}".format(**ctx)
        predict_snippet = "Make prediction for custom files directly", """# Create an example directory containing the data
mkdir -p $PWD/kipoi-example 
# You can replace $PWD/kipoi-example with a different absolute path containing the data 
docker run -v $PWD/kipoi-example:/app/ {docker_image_name} \\
kipoi get-example {model_name} -o /app/{output_dir} 
docker run -v $PWD/kipoi-example:/app/ {docker_image_name} \\
kipoi predict {model_name} \\
--dataloader_args='{example_kwargs}' \\
--batch_size=2 -o '/app/{model_name_no_slash}.example_pred.tsv' 
# check the results
head $PWD/kipoi-example/{model_name_no_slash}.example_pred.tsv
""".format(**ctx)
    return [("Get the docker image", """docker pull {docker_image_name}""".format(**ctx)),
            ("Get the activated conda environment inside the container",
             """docker run -it {docker_image_name}""".format(**ctx)
             ),
        (test_snippet),
        (predict_snippet),
]

# --------------------------------------------
# Singularity

def singularity_snippet(model_name, source="kipoi"):
    """
    Generate the snippet for the docker containers  

    Args:
        model_name (str): Name of the model the description being generated for
        source (str, optional): Where the model is residing. Defaults to "kipoi".
    """
    # TODO: read from kipoi-donctainer repo directly. Need an SSH key
    model_group_to_image_dict = {
        "DeepCpG_DNA": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "CpGenie": {
            "url": "https://zenodo.org/api/files/909c448f-0740-44bb-959a-21e643e0440a/kipoi-docker_sharedpy3keras1.2.sif?versionId=ef87d9b5-da51-49ec-9661-0a30ae59a20f",
            "name": "kipoi-docker_sharedpy3keras1.2.sif"
        },
        "Divergent421": {
            "url": "https://zenodo.org/api/files/909c448f-0740-44bb-959a-21e643e0440a/kipoi-docker_sharedpy3keras1.2.sif?versionId=ef87d9b5-da51-49ec-9661-0a30ae59a20f",
            "name": "kipoi-docker_sharedpy3keras1.2.sif"
        },
        "Basenji": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "Basset": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "HAL": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "DeepSEA": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "Optimus_5Prime": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "labranchor": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "CleTimer": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "SiSp": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "FactorNet": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "pwm_HOCOMOCO": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "MaxEntScan": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "DeepBind": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "lsgkm-SVM": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "rbp_eclip": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "MPRA-DragoNN": {
            "url": "https://zenodo.org/record/5643980/files/kipoi-docker_mpra-dragonn.sif?download=1",
            "name": "kipoi-docker_mpra-dragonn.sif"
        },
        "extended_coda": {
            "url": "https://zenodo.org/api/files/e48e60fa-544a-4721-821c-37450be3cf5c/kipoi-docker_extended_coda.sif?versionId=88d8d2a2-9bbf-46b4-a802-0c4534405ade",
            "name": "kipoi-docker_extended_coda.sif"
        },
        "MMSplice/pathogenicity": {
            "url": "https://zenodo.org/api/files/9474d673-ac4a-47b3-b6ba-6c6581db479a/kipoi-docker_mmsplice.sif?versionId=9ca56f66-8535-4179-a7cc-3817dcaf9b9b",
            "name": "kipoi-docker_mmsplice.sif"
        },
        "MMSplice/splicingEfficiency": {
            "url": "https://zenodo.org/api/files/9474d673-ac4a-47b3-b6ba-6c6581db479a/kipoi-docker_mmsplice.sif?versionId=9ca56f66-8535-4179-a7cc-3817dcaf9b9b",
            "name": "kipoi-docker_mmsplice.sif"
        },
        "MMSplice/deltaLogitPSI": {
            "url": "https://zenodo.org/api/files/9474d673-ac4a-47b3-b6ba-6c6581db479a/kipoi-docker_mmsplice.sif?versionId=9ca56f66-8535-4179-a7cc-3817dcaf9b9b",
            "name": "kipoi-docker_mmsplice.sif"
        },
        "MMSplice/modularPredictions": {
            "url": "https://zenodo.org/api/files/9474d673-ac4a-47b3-b6ba-6c6581db479a/kipoi-docker_mmsplice.sif?versionId=9ca56f66-8535-4179-a7cc-3817dcaf9b9b",
            "name": "kipoi-docker_mmsplice.sif"
        },
        "MMSplice/mtsplice": {
            "url": "https://zenodo.org/record/5643967/files/kipoi-docker_mmsplice-mtsplice.sif?download=1",
            "name": "kipoi-docker_mmsplice-mtsplice.sif"
        },
        "DeepMEL": {
            "url": "https://zenodo.org/record/5643863/files/kipoi-docker_deepmel.sif?download=1",
            "name": "kipoi-docker_deepmel.sif"
        },
        "Framepool": {
            "url": "https://zenodo.org/record/5643942/files/kipoi-docker_framepool.sif?download=1",
            "name": "kipoi-docker_framepool.sif"
        },
        "KipoiSplice": {
            "url": "https://zenodo.org/record/5643955/files/kipoi-docker_kipoisplice.sif?download=1",
            "name": "kipoi-docker_kipoisplice.sif"
        },
        "deepTarget": {
            "url": "https://zenodo.org/record/5643929/files/kipoi-docker_deeptarget.sif?download=1",
            "name": "kipoi-docker_deeptarget.sif"
        },
        "AttentiveChrome": {
            "url": "https://zenodo.org/record/5638781/files/kipoi-docker_attentivechrome.sif?download=1",
            "name": "kipoi-docker_attentivechrome.sif"
        },
        "BPNet-OSKN": {
            "url": "https://zenodo.org/record/5643831/files/kipoi-docker_bpnet-oskn.sif?download=1",
            "name": "kipoi-docker_bpnet-oskn.sif"
        },
        "SeqVec": {
            "url": "https://zenodo.org/record/5643982/files/kipoi-docker_seqvec.sif?download=1",
            "name": "kipoi-docker_seqvec.sif"
        },
        "Xpresso": {
            "url": "https://zenodo.org/record/5644007/files/kipoi-docker_sharedpy3keras2.sif?download=1",
            "name": "kipoi-docker_sharedpy3keras2.sif"
        },
        "epidermal_basset": {
            "url": "https://zenodo.org/api/files/909c448f-0740-44bb-959a-21e643e0440a/kipoi-docker_sharedpy3keras1.2.sif?versionId=ef87d9b5-da51-49ec-9661-0a30ae59a20f",
            "name": "kipoi-docker_sharedpy3keras1.2.sif"
        },
        "DeepFlyBrain": {
            "url": "https://zenodo.org/record/5643854/files/kipoi-docker_deepflybrain.sif?download=1",
            "name": "kipoi-docker_deepflybrain.sif"
        },
        "APARENT/site_probabilities": {
            "url": "https://zenodo.org/record/5643783/files/kipoi-docker_aparent-site_probabilities.sif?download=1",
            "name": "kipoi-docker_aparent-site_probabilities.sif"
        },
        "APARENT/veff": {
            "url": "https://zenodo.org/record/5643822/files/kipoi-docker_aparent-veff.sif?download=1",
            "name": "kipoi-docker_aparent-veff.sif"
        },
    }

    try:
        kw = get_example_kwargs(model_name, source)
    except Exception:
        kw = "Error"
    ctx = {"model_name": model_name,
           "example_kwargs": kw,
           "batch_size": get_batch_size(model_name, source),
           "source": source,
           "model_name_no_slash": model_name.replace("/", "_"),
           "output_dir" : "$PWD/kipoi-example/"
           }
    try:
        if model_name in model_group_to_image_dict: # Special provision for MMSplice
            singularity_image_name =  model_group_to_image_dict[model_name]["name"]
        else:
            singularity_image_name = model_group_to_image_dict[model_name.split('/')[0]]["name"]
    except Exception:
        singularity_image_name = ""
    try:
        if model_name in model_group_to_image_dict: # Special provision for MMSplice
            singularity_image_url =  model_group_to_image_dict[model_name]["url"]
        else:
            singularity_image_url = model_group_to_image_dict[model_name.split('/')[0]]["url"]
    except Exception:
        singularity_image_url = ""
    ctx["singularity_image_name"] = singularity_image_name
    ctx["singularity_image_url"] = singularity_image_url
    test_snippet = "Test the model", "singularity exec {singularity_image_name} kipoi test {model_name} --source={source}".format(**ctx)
    predict_snippet = "Make prediction for custom files directly", """# Create an example directory containing the data
mkdir -p $PWD/kipoi-example 
# You can replace $PWD/kipoi-example with a different absolute path containing the data 
singularity exec {singularity_image_name} \\
kipoi get-example {model_name} -o {output_dir} 
singularity exec {singularity_image_name} \\
kipoi predict {model_name} \\
--dataloader_args='{example_kwargs}' \\
-o '{model_name_no_slash}.example_pred.tsv' 
# check the results
head $PWD/kipoi-example/{model_name_no_slash}.example_pred.tsv
""".format(**ctx)
    if model_name == "Basenji":
        test_snippet = "Test the model", "singularity exec {singularity_image_name} kipoi test {model_name} --batch_size=2 --source={source}".format(**ctx)
        predict_snippet = "Make prediction for custom files directly", """# Create an example directory containing the data
mkdir -p $PWD/kipoi-example 
# You can replace $PWD/kipoi-example with a different absolute path containing the data 
singularity exec {singularity_image_name} \\
kipoi get-example {model_name} -o {output_dir} 
singularity exec {singularity_image_name}  \\
kipoi predict {model_name} \\
--dataloader_args='{example_kwargs}' \\
--batch_size=2 -o '{model_name_no_slash}.example_pred.tsv' 
# check the results
head $PWD/kipoi-example/{model_name_no_slash}.example_pred.tsv
""".format(**ctx)
    return [("Get the singularity image", """{singularity_image_url}""".format(**ctx)),
        (test_snippet),
        (predict_snippet),
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
             """pred = model.pipeline.predict_example(batch_size={batch_size})""".format(**ctx)
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
    test_snippet = "Test the model", "kipoi test {model_name} --source={source}".format(**ctx)
    predict_snippet =  "Make a prediction", """kipoi get-example {model_name} -o {output_dir}
kipoi predict {model_name} \\
  --dataloader_args='{example_kwargs}' \\
  -o '/tmp/{model_name_no_slash}.example_pred.tsv'
# check the results
head '/tmp/{model_name_no_slash}.example_pred.tsv'
""".format(**ctx)
    if model_name == "Basenji":
        test_snippet = "Test the model", "kipoi test {model_name} --batch_size=2 --source={source}".format(**ctx)
        predict_snippet =  "Make a prediction", """kipoi get-example {model_name} -o {output_dir}
kipoi predict {model_name} \\
  --dataloader_args='{example_kwargs}' \\
  --batch_size=2 -o '/tmp/{model_name_no_slash}.example_pred.tsv'
# check the results
head '/tmp/{model_name_no_slash}.example_pred.tsv'
""".format(**ctx)
    return [
        ("Create a new conda environment with all dependencies installed", "kipoi env create {group_name}\nsource activate {env_name}".format(**ctx)),
        ("Install model dependencies into current environment", "kipoi env install {group_name}".format(**ctx)),
        (test_snippet),  
        (predict_snippet),
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
            "docker": docker_snippet(model_name, source),
            "singularity": singularity_snippet(model_name, source)}



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
