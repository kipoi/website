import pymdownx
from flask import Markup
import markdown


extensions = [
    'markdown.extensions.tables',
    'pymdownx.magiclink',
    'pymdownx.betterem',
    'pymdownx.tilde',
    # 'pymdownx.emoji',
    'pymdownx.tasklist',
    'pymdownx.superfences'
]

extension_config = {
    "pymdownx.magiclink": {
        "repo_url_shortener": True,
        "repo_url_shorthand": True,
        "provider": "github",
        "user": "facelessuser",
        "repo": "pymdown-extensions"
    },
    "pymdownx.tilde": {
        "subscript": False
    },
    # "pymdownx.emoji": {
    #     "emoji_index": pymdownx.emoji.gemoji,
    #     "emoji_generator": pymdownx.emoji.to_png,
    #     "alt": "short",
    #     "options": {
    #         "attributes": {
    #             "align": "absmiddle",
    #             "height": "20px",
    #             "width": "20px"
    #         },
    #         "image_path": "https://assets-cdn.github.com/images/icons/emoji/unicode/",
    #         "non_standard_image_path": "https://assets-cdn.github.com/images/icons/emoji/"
    #     }
    # }
}


def render_markdown(md):
    return Markup(markdown.markdown(md,
                                    extensions=extensions,
                                    extension_config=extension_config))
