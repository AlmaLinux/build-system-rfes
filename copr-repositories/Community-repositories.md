# [RFE] Implement community repositories support in the AlmaLinux Build System


## Introduction

This document describes an AlmaLinux Build System community repositories feature implementation proposal.


### The problem

Although our Build System allows a user building packages for different distributions/platforms there is no easy way to share such packages with the community.

Internally every build contains the following yum repositories for each target (platform + architecture combination):

  * sources - contains source RPMs. That repository is shared across multiple architectures of a single platform.
  * binaries - contains binary RPM packages built from source RPMs for each architecture of a platform.
  * debug - contains debuginfo and debugsource packages generated from binary RPMs. As a binary repository, that repository is unique for each architecture and platform combination.

Currently, the Build System doesn't generate a yum repository configuration file for a build so a user should create it manually for each build he wants to deploy on a computer.

Another point is that a user's project may contain multiple builds/iterations and that turns manual repository configuration file management into a serious problem for a regular (not a professional package maintiainer) user.

**So, we need to provide a maintainer or a SIG a way to create his own public repository, release one or multiple builds to it and share the repository with other community members.**

**Also, it would be nice if we can integrate our solution to the existent CentOS/Fedora/RHEL ecosystem with minimal modifications required from the upstream side.**


### The resolution

On the AlmaLinux Build System side we need to implement the following:

  1. Make possible for users creating their own public repositories (community repositories). That process should be very similar to creating a GitHub repository.
  2. For each community repository it should be possible to create a dedicated "channel" (it is called "chroot" in Fedora's CoPr terminology) for different platforms (e.g. EL8 or EL9). Each "channel" should have a public yum/dnf repository accessible via HTTPs.
  3. Allow community repository owners to release packages from a Build System build to their repositories.
  4. All publicly released packages should be signed by a dedicated PGP key (e.g. AlmaLinux CoPr Key).
  5. Allow community repository owners to remove packages from their repositories.
  6. Allow users or system administrators to create organizations (SIGs) that can include multiple users and own community repositories. An organization members (at least some of them) should be able to manage organization repositories.

There is the [copr](https://dnf-plugins-core.readthedocs.io/en/latest/copr.html) DNF core plugin that provides integration with the [Fedora COPR](https://copr.fedorainfracloud.org/) Build System. It can be easily configured to work with our Build System (it's called "hub" in Fedora's CoPr terminology), see the integration section below.


## Requirements

### First milestone

* A user should be able to select EPEL as a default build flavor for his further builds.
* The backend should always match `epel-${releasever}-${basearch}` platforms to AlmaLinux platforms even if EPEL is not enabled. This is because the COPR DNF plugin doesn't support other EL targets.
* We are not going to sign packages in community repositories in the first (alpha) release. This will be implemented in the next iteration.
* A user can use a github-like form to create a new community repository: owner (either this user or one of his teams), name/title, description, list of target platform (currently we support only AlmaLinux 8 and 9).
* A user can release one or more projects from a build to a community repository owned by him or his team.
* A user can delete a project (and all its RPMs. A project here is a unique NEVR) from a community repository. In the next iteration we will add support for an individual RPM deletion.
* A user can select a community repo as a build flavor.

### Second milestone

TBD in middle July.


## The implementation


### DNF copr plugin integration

The [copr](https://dnf-plugins-core.readthedocs.io/en/latest/copr.html) DNF plugin supports multiple hubs (repository sources) of the box. All we need is to create a configuration file for our Build System in the `/etc/dnf/plugins/copr.d/` directory (e.g. `almalinux.conf`):

```toml
[almalinux]
hostname = build.almalinux.org
protocol = https
port = 443
```

After creating the configuration file a user specifies a hub name using the `--hub` command line argument:

```bash
# find a repository by name
$ dnf copr --hub almalinux search project-name

# enable a repository
$ dnf copr --hub almalinux enable user/project-name
```

Alternavely, a hub can be specified as a part of a repository path:

```bash
# enable a repository "user/project-name" from an "almalinux" hub
$ dnf copr enable almalinux/user/project-name
```


### API endpoints

This section contains a list of API endpoints that should be implemented for integration with the copr DNF plugin.


#### Search repositories

The `/api_3/project/search` API endpoint returns a list of repositories by name.

Query string parameters:

  * `query` - a repository (project) name.

Minimal workable output:

```json
{
    // list of found repositories
    "items": [
        {
            // repository name
            "name": "emacs-goodies",
            // full repository name (including a user name)
            "full_name": "test_user/emacs-goodies",
            // repository description
            "description": "Extra GNU/Emacs packages",
            // owner (user) name
            "ownername": "test_user",
            "chroot_repos": {
                "epel-9-x86_64": "http://build.almalinux.org/repositories/test_user/emacs-goodies/epel-9-x86_64/",
                "epel-9-aarch64": "http://build.almalinux.org/repositories/test_user/emacs-goodies/epel-9-aarch64/"
            }
        }
    ]
}
```

Relevant DNF copr command:

```bash
$ dnf copr search emacs
================================= Matched: emacs =================================
test_user/emacs-goodies : Extra GNU/Emacs packages
```


#### List user's repositories

The `/api_3/project/list` API endpoint returns a list of repositories by a specified user.

Query string parameters:

  * `ownername` - a username.

The endpoint output has the same format as the `/api_3/project/search` format:

```json
{
    // list of found repositories
    "items": [
        {
            // repository name
            "name": "emacs-goodies",
            // full repository name (including a user name)
            "full_name": "test_user/emacs-goodies",
            // repository description
            "description": "Extra GNU/Emacs packages",
            // owner (user) name
            "ownername": "test_user",
            "chroot_repos": {
                "epel-9-x86_64": "http://build.almalinux.org/repositories/test_user/emacs-goodies/epel-9-x86_64/",
                "epel-9-aarch64": "http://build.almalinux.org/repositories/test_user/emacs-goodies/epel-9-aarch64/"
            }
        }
    ]
}
```

Relevant DNF copr command:

```bash
$ dnf copr --hub almalinux list --available-by-user=test_user
============================= List of test_user coprs =============================
test_user/emacs-goodies : Extra GNU/Emacs packages
```


#### Generate repository config

The `/coprs/{ownername}/{name}/repo/{platform}/dnf.repo` API endpoint generates a yum/dnf repository configuration file for a specified repository.

URL parameters:

  * `ownername` - a username.
  * `name` - a repository name.
  * `platform` - a target platform (e.g. `epel-9`).

Query string parameters:

  * `arch` - a target architecture (e.g.  `x86_64`).

The endpoint output is a yum/dnf repository configuration file text:

```toml
[copr:127.0.0.1:test_user:emacs-goodies]
name=Copr repo for emacs-goodies owned by test_user
baseurl=http://127.0.0.1:8000/repositories/test_user/emacs-goodies/epel-9-$basearch/
type=rpm-md
skip_if_unavailable=True
gpgcheck=0
enabled=1
enabled_metadata=1
```

Relevant DNF copr command:

```bash
$ dnf copr --hub almalinux enable test_user/emacs-goodies
...
Do you really want to enable 127.0.0.1:8000/test_user/emacs-goodies? [y/N]: y
Repository successfully enabled.
```


## References

  * [DNF copr plugin documentation](https://dnf-plugins-core.readthedocs.io/en/latest/copr.html)
  * [Fedora copr project documentation](https://docs.pagure.org/copr.copr/)
  * [Fedora copr project sources](https://pagure.io/copr/copr)

## Authors

  * [Eugene Zamriy](ezamriy@almalinux.org)
