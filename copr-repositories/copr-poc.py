#!/usr/bin/env python3
# author: Eugene Zamriy <eugene@zamriy.info>
# created: 2022-05-27

"""
Fedora COPR-compatible service proof-of-concept implementation.
"""

import typing

from fastapi import FastAPI, Response, status
from fastapi.responses import PlainTextResponse


repositories = [
    {
        # repository name
        'name': 'emacs-goodies',
        # full repository name (incl. user name)
        'full_name': 'test_user/emacs-goodies',
        # repository description
        'description': 'Extra GNU/Emacs packages',
        # repository owner's username
        'ownername': 'test_user',
        # yum/dnf repository URLs for each supported platforms.
        # AlmaLinux 9 is detected as "epel-9" by the copr plugin.
        # See the `_guess_chroot` function in the `dnf-plugins/copr.py` sources.
        'chroot_repos': {
            'epel-9-x86_64': 'http://127.0.0.1:8000/repositories/test_user/emacs-goodies/epel-9-x86_64/',
            'epel-9-aarch64': 'http://127.0.0.1:8000/repositories/test_user/emacs-goodies/epel-9-aarch64/'
        }
     }
]

app = FastAPI()


def generate_repo_config(repo: typing.Dict, platform: str) -> str:
    """
    Generates a yum/dnf repository configuration file.

    Args:
        repo: repository for which a configuration file should be generated.
        platform: target platform.

    Returns:
        Yum/dnf repository configuration file.

    Notes:
        A hostname/IP address should be the same in a repo id and baseurl,
        otherwise the copr plugin will fail.
    """
    return (f'[copr:127.0.0.1:{repo["ownername"]}:{repo["name"]}]\n'
            f'name=Copr repo for {repo["name"]} owned by {repo["ownername"]}\n'
            f'baseurl=http://127.0.0.1:8000/repositories/{repo["ownername"]}/{repo["name"]}/{platform}-$basearch/\n'
            'type=rpm-md\n'
            'skip_if_unavailable=True\n'
            'gpgcheck=0\n'
            'enabled=1\n'
            'enabled_metadata=1\n')


@app.get('/api_3/project/search')
def search_repos(query: str) -> typing.Dict:
    """
    Searches repositories by a name.

    Args:
        query: repository name.

    Returns:
        A list of repositories with matching names.
    """
    reply = {'items': []}
    for repo in repositories:
        if query in repo['name']:
            reply['items'].append(repo)
    return reply


@app.get('/api_3/project/list')
def list_repos(ownername: str) -> typing.Dict:
    """
    Finds repositories owned by a specified user.

    Args:
        ownername: username.

    Returns:
        A list of repositories owned by a specified user.
    """
    return {
        'items': [p for p in repositories if p['ownername'] == ownername]
    }


@app.get('/coprs/{ownername}/{name}/repo/{platform}/dnf.repo',
         response_class=PlainTextResponse)
def get_dnf_repo_config(ownername: str, name: str, platform: str, arch: str,
                        response: Response) -> str:
    """
    Generates a yum/dnf repository configuration file for a specified copr repo.

    Args:
        ownername: username.
        name: repository name.
        platform: target platform.
        arch: target architecture.
        response: FastAPI response object.

    Returns:
        Yum/dnf repository configuration file.
    """
    full_name = f'{ownername}/{name}'
    chroot = f'{platform}-{arch}'
    for repo in repositories:
        if repo['ownername'] == ownername and repo['name'] == name:
            if chroot in repo['chroot_repos']:
                return generate_repo_config(repo, platform)
            response.status_code = status.HTTP_404_NOT_FOUND
            return f'Chroot {chroot} does not exist in {full_name}.'
    response.status_code = status.HTTP_404_NOT_FOUND
    return f'copr dir {full_name} does not exist.'
