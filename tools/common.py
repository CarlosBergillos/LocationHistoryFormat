import yaml


def _get_from_config(key, configpath="./mkdocs.yml"):
    noop = lambda loader, suffix, node: None
    yaml.add_multi_constructor("tag:yaml.org,2002:python/name", noop, Loader=yaml.SafeLoader)
    yaml.add_multi_constructor("!ENV", noop, Loader=yaml.SafeLoader)

    with open(configpath, "r") as f:
        config = yaml.safe_load(f)

    return config.get(key)


def site_url(configpath="./mkdocs.yml"):
    return _get_from_config("site_url", configpath=configpath)


def repo_url(configpath="./mkdocs.yml", file_path=None, line_start=None, line_end=None):
    url = _get_from_config("repo_url", configpath=configpath)

    if file_path is not None:
        url += "/tree/main" + file_path

        if line_start is not None:
            url += "#L" + str(line_start)

            if line_end is not None:
                url += "-L" + str(line_end)

    return url
