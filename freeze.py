from flask_frozen import Freezer
from app import app
import os
import kipoi
from tqdm import tqdm
freezer = Freezer(app)


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
    # freezer.freeze()

    urls = all_urls()
    for x in tqdm(freezer.freeze_yield(), total=len(urls)):
        pass
    print("Done!")
