""" This is a model view, containing all views related to the
KIPOI models. First is the model list that shows all available
models and the second is the models detail view that describes
selected model. """

import re
import os
import pandas as pd
import kipoi
from flask import Blueprint, render_template, redirect, url_for, current_app, Markup
import logging
from collections import OrderedDict

from app.models.code_snippets import get_snippets
from app.models.cache import cache
from app.models.authors import get_authors
from app.models.github import github_dir_tree
from app.models.markdown import render_markdown
mod = Blueprint('models', __name__, template_folder='templates')


@cache.memoize()
def get_model_groups(source, group_filter):
    """ Cache for list model groups """
    group_df = kipoi.remote.list_models_by_group(get_model_list(source), group_filter=group_filter)

    if group_df is None:
        raise ValueError("Unable to handle group_filter: {0}".format(group_filter))
    # add the information about the absolute path
    if group_filter == "":
        group_df["abs_group"] = group_df['group']
    else:
        group_df["abs_group"] = group_filter + "/" + group_df['group']
    return group_df


# @cache.cached(key_prefix='model_list')
@cache.memoize()
def get_model_list(source):
    """ Cache for kipoi's list models """
    df = kipoi.get_source(source).list_models()
    return df


def get_view(model_path, df):
    """Test if the queried string is a model

    Args:
      relative path to the model: i.e. "" for the root, "rbp_eclip" for
      accessing the rbp_eclip data subset
      df: pd.DataFrame returned by `kipoi.get_source(source).list_models()`

    to be used in combination with:
    ```
    df = kipoi.get_source(source).list_models()
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
        df_groups = kipoi.get_source(source).list_models_by_group(path)
        # render the normal path
        # render the group view
    ```

    Returns:
       a tuple: (type, path), where type can be "model", "model_list" or "group_list"
    """
    if (df.model == model_path).any():
        # a model matches exactly model_path
        return ("model", model_path)
    names = df.model[df.model.str.contains("^" + model_path + "/")]
    if model_path is not "":
        sub_names = names.str.replace("^" + model_path + "/", "")
    else:
        sub_names = names

    if len(sub_names) == 0:
        # error - no right string was found
        return None
    elif sub_names.str.contains("/").any():
        # some names contain further slashed in the name
        return ("group_list", model_path)
    else:
        # remain just regular models in the list
        return ("model_list", model_path)
    # Don't jump over
    # elif len(sub_names) == 1:
    #     # we have found a single one
    #     name = sub_names.iloc[0]
    #     if name == "":
    #         return ("model", model_path)
    #     else:
    #         return ("model", model_path + "/" + name)
    # elif len(names) >= 1:
    #     # there is more than one element in the list
    #     if sub_names.str.contains("/").any():
    #         # some names contain further slashed in the name -
    #         return ("group_list", model_path)
    #     else:
    #         # remain just regular models in the list
    #         return ("model_list", model_path)


def update_cite_as(cite_as):
    if cite_as is None:
        return None
    if isinstance(cite_as, str):
        return re.split(' |; |, |\*|\n|,|;', cite_as.strip())
    else:
        return [v for c in cite_as for v in update_cite_as(c)]


def update_cite_as_dict(d):
    """Parses comma-separated values in cite_as
    """
    d['cite_as'] = update_cite_as(d['cite_as'])
    return d


def update_authors(authors, cite_as):
    """Given a list of authors, augment it
    Args:
      authors: a list of kipoi.specs.Author
      cite_as: cite_as field of a model
    """
    if cite_as is not None and cite_as:
        cite_as = update_cite_as(cite_as)[0]  # take the first cite_as entry
        scraped_authors = get_authors(cite_as)
    else:
        scraped_authors = []

    # now we need to merge the existing authors in the model.yaml file
    # with the scraped ones.

    def find_orig_author(author, orig_authors):
        for orig_author in orig_authors:
            # dots are ignored
            if orig_author.name.replace(".", "") == author.name.replace(".", ""):
                return orig_author
        return None

    if scraped_authors:
        # sanity check. No additional authors
        for orig_author in authors:
            if find_orig_author(orig_author, scraped_authors) is None:
                logging.warning("specified author: {} not found in parsed authors:\n {}".format(orig_author, scraped_authors))
        out = []
        for author in scraped_authors:
            orig_author = find_orig_author(author, authors)
            if orig_author is not None:
                out.append(orig_author)
            else:
                out.append(author)
        return out
    else:
        return authors


def update_authors_as_dict(d):
    if d['cite_as'] is not None and d['cite_as']:
        d['authors'] = update_authors(d['authors'], d['cite_as'])
    return d


def update_contributors(contributors, authors):
    if contributors:
        return contributors
    else:
        return authors

def update_contributors_as_dict(d):
    d['contributors'] = update_contributors(d['contributors'], d['authors'])
    return d


@mod.route("/groups")
@mod.route("/groups/")
@mod.route("/groups/<path:group_name>")
def list_groups(group_name=None):
    """ Group list view """
    source = current_app.config['SOURCE']
    if group_name is None:
        group_name = ""
    group_name = group_name.rstrip('/')
    group_df = get_model_groups(source, group_name)
    group_list = group_df.to_dict(orient='records')
    # parse cite_as
    group_list = [update_cite_as_dict(x) for x in group_list]

    # update contributors
    group_list = [update_contributors_as_dict(x) for x in group_list]

    # update authors
    group_list = [update_authors_as_dict(x) for x in group_list]

    # get readme file
    readme_dir = os.path.join(kipoi.get_source(current_app.config['SOURCE']).local_path, group_name)
    try:
        # python doesnt handle case sensetive path. so:
        filelists = os.listdir(readme_dir)
        readmeindx = [x.lower() for x in filelists].index("readme.md")
        filecontent = open(os.path.join(readme_dir, filelists[readmeindx]), "r").read()
        readmecontent = render_markdown(filecontent)
    except IOError:
        readmecontent = ""
    except ValueError:
        readmecontent = ""

    return render_template("models/index_groups.html", groups=group_list, readmecontent=readmecontent)


@mod.route("/")
def main():
    """Main view
    """
    source = current_app.config['SOURCE']
    GENOMICS_TAGS = ["DNA binding",
                     "Transcription",
                     "DNA accessibility",
                     "RNA binding",
                     "DNA methylation",
                     "Replication timing",
                     "Genotyping",
                     "3D chromatin structure",
                     "Proteomics",
                     "RNA structure",
                     "DNA sequencing",
                     "RNA splicing",
                     "RNA expression",
                     "Histone modification"]
    # Get the following numbers:
    #
    # - Total number of models
    # - number of models supporting variant effect prediction
    # - Number of models by framework
    # - Total number of output dimensions for a variant
    df = get_model_list(source)
    dfg = get_model_groups(source, "")

    # models_by_framework = dict(df.type.value_counts())
    # models_by_license = dict(df.license.value_counts())
    models_by_genomics_tag = pd.Series([x for model_groups in dfg.tags
                                        for x in model_groups]).value_counts()
    models_by_genomics_tag = models_by_genomics_tag[models_by_genomics_tag.index.isin(GENOMICS_TAGS)]

    models_by_framework = dfg.type.apply(lambda x: list(x)[0]).value_counts()
    models_by_license = dfg.license.apply(lambda x: list(x)[0]).value_counts()

    # framework_colors = {
    #     "keras": "#d70000",
    #     "tensorflow": "#fa9400",
    #     "pytorch": "#9e529f",  # alternatively "#f05732"
    #     "sklearn": "#1c97d1",
    #     "custom": "#18CC5A"}

    framework_colors = {
        "tensorflow": "#ffd92f",
        "keras": "#ff8f5a",
        "pytorch": "#8da0cb",
        "sklearn": "#e78ac3",
        "custom": "#66c2a5",
    }
    models_by_framework_colors = [framework_colors[x] for x in models_by_framework.index]
    # TODO - put the chart colors also here:
    return render_template("models/main.html",
                           n_models=len(df),
                           n_groups=len(dfg),
                           n_contributors=len({x.name for contributors in df.contributors for x in contributors}),
                           n_postproc_score_variants=dfg.veff_score_variants.sum(),
                           models_by_framework_keys=list(models_by_framework.index),
                           models_by_framework_values=list(models_by_framework),
                           models_by_framework_colors=models_by_framework_colors,
                           models_by_license_keys=list(models_by_license.index),
                           models_by_license_values=list(models_by_license),
                           models_by_genomics_tag_keys=list(models_by_genomics_tag.index)[:7],
                           models_by_genomics_tag_values=list(models_by_genomics_tag)[:7])


@mod.route("/about/")
def about():
    """About page
    """
    return render_template("models/about.html")

@mod.route("/seminar/")
def seminar():
    """Seminar page
    """
    return render_template("models/seminar.html")


dl_skip_arguments = {
    "kipoiseq.dataloaders.SeqIntervalDl": ['alphabet_axis', 'dummy_axis', 'alphabet', 'dtype']
}


@mod.route('/models/<path:model_name>')
def model_list(model_name):
    """ Models list view """
    from kipoi.utils import cd
    source = current_app.config['SOURCE']
    df = get_model_list(source)
    model_name = model_name.rstrip('/')
    vtype_path = get_view(model_name, df)

    if vtype_path is None:
        # run 404
        return
        # pass
    else:
        vtype, path = vtype_path

    # render the model detail view
    if vtype == "model":
        # Model info retrieved from kipoi
        model = kipoi.get_model_descr(model_name, source=source)

        src = kipoi.get_source(source)
        model_dir = kipoi.utils.relative_path(src.get_model_dir(model_name), src.local_path)
        model_url = github_dir_tree(src.remote_url, model_dir)
        # Model dataloaders info retrieved from kipoi
        if model.default_dataloader:
            if isinstance(model.default_dataloader, str):
                dl_rel_path = True
                dataloader = kipoi.get_dataloader_descr(os.path.join(model_name, model.default_dataloader),
                                                        source=source)
                dataloader_name = model.default_dataloader
                dataloader_args = dataloader.args
            else:
                dl_rel_path = False
                with cd(src.get_model_dir(model_name)):
                    dataloader = model.default_dataloader.get()
                dataloader_name = model.default_dataloader.defined_as
                dataloader_args = OrderedDict([(k, v)
                                            for k, v in dataloader.args.items()
                                            if k not in list(model.default_dataloader.default_args) +
                                            dl_skip_arguments.get(dataloader_name, [])])

                if model.default_dataloader.defined_as == 'kipoiseq.dataloaders.SeqIntervalDl':
                    # HACK - cleanup some values for SeqIntervalDl
                    if model.default_dataloader.default_args.get("ignore_targets", False):
                        dataloader_args.pop('label_dtype', None)
        else:
            dataloader = None
            dataloader_name = ''
            dataloader_args = {}
            dl_rel_path = False

        title = model_name.split('/')
        # obtain snippets
        code_snippets = get_snippets(model_name, source)
        if model_name == "SeqVec/embedding2structure":
            code_snippets["docker"] = ''
            code_snippets["singularity"] = ''
            code_snippets["cli"] = '' 
            code_snippets["python"] = ''
            code_snippets["R"] = ''

        # reading the README content
        readme_dir = kipoi.get_source(current_app.config['SOURCE']).get_model_dir(model_name)
        try:
            # python doesnt handle case sensetive path. so:
            filelists = os.listdir(readme_dir)
            readmeindx = [x.lower() for x in filelists].index("readme.md")
            filecontent = open(os.path.join(readme_dir, filelists[readmeindx]), "r").read()
            readmecontent = render_markdown(filecontent)
            # remove the title because already there is a title
            readmecontent = re.sub("<[hH][12]>.*</[hH][12]>", "", readmecontent, count=1)
            readmecontent = Markup(readmecontent)
        except IOError:
            readmecontent = ""
        except ValueError:
            readmecontent = ""

        return render_template("models/model_details.html",
                               model_name=model_name,
                               model=model,
                               contributors=update_contributors(model.info.contributors, model.info.authors),
                               authors=update_authors(model.info.authors, model.info.cite_as),
                               dataloader=dataloader,
                               dataloader_args=dataloader_args,
                               dataloader_name=dataloader_name,
                               model_url=model_url,
                               dl_rel_path=dl_rel_path,
                               cite_as=update_cite_as(model.info.cite_as),
                               title=title,
                               code_snippets=code_snippets,
                               readmecontent=readmecontent)

    # run the normal model list view on a subsetted table
    elif vtype == "model_list":
        model_df = get_model_list(source)

        # TODO - augment the results

        # Filter the results
        model_df = model_df[model_df.model.str.contains("^" + path + "/")]

        filtered_models = model_df.to_dict(orient='records')
        filtered_models = [update_cite_as_dict(x) for x in filtered_models]

        # update contributors
        filtered_models = [update_contributors_as_dict(x) for x in filtered_models]

        # update authors
        filtered_models = [update_authors_as_dict(x) for x in filtered_models]

        # get readme file
        readme_dir = os.path.join(kipoi.get_source(current_app.config['SOURCE']).local_path, model_name)
        try:
            filelists = os.listdir(readme_dir)
            readmeindx = [x.lower() for x in filelists].index("readme.md")
            filecontent = open(os.path.join(readme_dir, filelists[readmeindx]), "r").read()
            readmecontent = render_markdown(filecontent)
        except IOError:
            readmecontent = ""
        except ValueError:
            readmecontent = ""

        return render_template("models/index.html", models=filtered_models, readmecontent=readmecontent)

    # redirect to the group list
    elif vtype == "group_list":
        return redirect(url_for('models.list_groups', group_name=path))
