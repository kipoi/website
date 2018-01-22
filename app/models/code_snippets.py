"""Generate code snippets
"""
import os
import kipoi
import pprint


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


# python specific snippets
def py_set_example_kwargs(model_name):
    example_kwargs = get_example_kwargs(model_name)
    return "\nkwargs = " + pprint.pformat(example_kwargs)


def py_snippet(model_name):
    """Generate the python code snippet
    """
    ctx = {"model_name": model_name,
           "example_kwargs": get_example_kwargs(model_name)}
    return [("Get the model", """import kipoi
model = kipoi.get_model('{model_name}')""".format(**ctx)),
            ("Make a prediction the example files",
             """# setup the example dataloader kwargs
import os
dl_kwargs = {example_kwargs}
os.chdir(os.path.expanduser('~/.kipoi/models/{model_name}'))

# predict
pred = model.pipeline.predict(**dl_kwargs)""".format(**ctx)
             ),
            ("Use dataloader and model separately",
             """# Get the dataloader
Dl = kipoi.get_dataloader_factory('{model_name}')
# instantiate it
dl = Dl(**dl_kwargs)
# get a batch iterator
it = dl.batch_iter(batch_size=4)
# predict for a batch
batch = next(it)
model.predict_on_batch(batch)""".format(**ctx))]


def get_snippets(model_name):
    snp = py_snippet(model_name)
    return {"cli": snp, "python": snp, "R": snp}
# print(py_snippet("DeepSEA")[2][1])
