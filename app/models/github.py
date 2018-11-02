import os


def github_https_page_root(remote_url):
    if remote_url.startswith("git@github.com:"):
        return remote_url.replace("git@github.com:", "https://github.com/").replace(".git", "/")
    else:
        return remote_url.replace(".git", "/")


def github_dir_tree(remote_url, relative_path):
    return os.path.join(github_https_page_root(remote_url), "tree/master", relative_path)
