from flask_frozen import Freezer
from app import app
import os
import kipoi
from tqdm import tqdm

from app.models.cache import cache

# override the database memcache
cache.init_app(app, config={'CACHE_TYPE': 'simple'})
# http://pythonhosted.org/Frozen-Flask/#api-reference
freezer = Freezer(app,
                  # with_no_argument_rules=False
                  # ignore all other url's
                  log_url_for=False)


@freezer.register_generator
def all_urls():
    model = kipoi.get_source("kipoi").list_models().model
    # model = model[~model.str.startswith("tf-binding")]
    # model = model[~model.str.startswith("rbp_eclip")]
    urls = set()
    for m in model:
        while m:
            urls.add(m)
            m = os.path.dirname(m)
    return ["/", "/groups/"] + [f"/models/kipoi/{x}/" for x in urls]


if __name__ == '__main__':
    urls = list(freezer.all_urls())
    for x in tqdm(freezer.freeze_yield(), total=len(urls)):
        pass
    print("Done!")
