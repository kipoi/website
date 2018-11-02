from flask_frozen import Freezer
from app import app
import os
import kipoi
from tqdm import tqdm

from app.models.cache import cache
from app.models.views import get_view

# override the database memcache
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

# always use relative URL's
if os.environ.get('FREEZER_RELATIVE_URLS'):
    app.config['FREEZER_RELATIVE_URLS'] = eval(os.environ.get('FREEZER_RELATIVE_URLS'))

# http://pythonhosted.org/Frozen-Flask/#api-reference
freezer = Freezer(app,
                  # with_no_argument_rules=False
                  # ignore all other url's
                  log_url_for=False)


@freezer.register_generator
def all_urls():
    df = kipoi.get_source("kipoi").list_models()
    model = df.model
    urls = set()
    for m in model:
        while m:
            urls.add(m)
            m = os.path.dirname(m)
    groups = {x for x in urls if get_view(x, df)[0] == "group_list"}
    # exclude the final models
    groups = groups - set(model)

    return ["/", "/groups/"] + ["/groups/{0}/".format(x) for x in groups] + ["/models/{0}/".format(x) for x in urls]


if __name__ == '__main__':
    urls = list(freezer.all_urls())
    for x in tqdm(freezer.freeze_yield(), total=len(urls)):
        pass
    print("Done!")
