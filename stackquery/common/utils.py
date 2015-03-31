import json
import os


def get_repos(filename):
    if os.path.exists(filename):
        repos = json.load(open(filename))
        return repos.get('repos', [])
    return []


def get_repos_by_module(filename, module):
    repos = get_repos(filename)
    _module = module
    if '/' in _module:
        _module = _module.split('/')[-1]
    for repo in repos:
        if _module in repo['module']:
            return repo

    # Let's give a try and check if we will be able to download from git
    uri = 'git://git.openstack.org/%s.git' % module
    return {
        'uri': uri, 'module': _module,
        'releases': [{'release_name': 'Kilo', 'tag_to': 'HEAD'}]}


def make_range(start, stop, step):
    last_full = stop - ((stop - start) % step)
    for i in range(start, last_full, step):
        yield range(i, i + step)
    if stop > last_full:
        yield range(last_full, stop)
