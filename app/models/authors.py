import kipoi
import logging
from app.models.cache import cache


def parse_cite_as_url(url):
    # import re
    # in case multiple urls are provided,
    # take the first one
    # url = re.split(' |; |, |\*|\n|,|;',cite_as)[0]
    
    replace_dict = {
        "https://doi.org/": "doi:",
        "https://arxiv.org/pdf/": "arxiv:",
        "https://arxiv.org/abs/": "arxiv:",
    }
    
    for k,v in replace_dict.items():
        if url.startswith("https://arxiv.org/pdf/"):
            return url.replace("https://arxiv.org/pdf/", "arxiv:").replace(".pdf", "")
        if url.startswith(k):
            return url.replace(k,v)
    return None


def parse_author(author_dict):
    def clean_name(name):
        return name.replace("\xa0", " ")
    
    if "given" in author_dict and "family" in author_dict:
        name = author_dict['given'] + " " + author_dict['family']
        return kipoi.specs.Author(clean_name(name))
    elif "literal" in author_dict:
        name = author_dict['literal']
        return kipoi.specs.Author(clean_name(name))
    else:
        raise ValueError("Author name not found")

@cache.memoize()
def get_authors(cite_as):
    """Given a doi, get a list of Authors
    """
    from manubot import cite
    try:
        citation = cite.citation_to_citeproc(parse_cite_as_url(cite_as))
        
        authors = [parse_author(d) for d in citation['author']]
        return authors
    except Exception as e:
        logging.warning("Unable to get the authors for: {}\n{}".format(cite_as, e))
        return []