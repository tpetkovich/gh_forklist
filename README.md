# gh_forklist.py

A very simple python wrapper script to get the inclusive list of "interesting" forks (to a csv file) for a target repository and provide means to skim through forks which have commits and are ahead, behind or diverged from the target repository. The only dependency is [pandas](https://pandas.pydata.org/) for the .csv output.  
It does not do the API calls by itself, rather uses the [Github CLI](https://cli.github.com/), as this seemed to be the smoothest one, - assuming the user has that anyway set up - rather than fiddling around with the authentication, API keys and such.  
There are much more worked out tools than this, for example [Useful Forks](https://useful-forks.github.io/), but I just wanted to avoid messing around with API keys.
Additionally this script is slow and sucks, but due to Github REST API limited anyway and the Microsoft infrastructure constantly on the brink of collapse, I am not sure what else can be done. Additionally, the GraphQL based Github API does not have the required cross-repository compare object at all, although that would seem to be the logical way to provide this data.

Usage with [uv](https://github.com/astral-sh/uv):

```shell
uv run gh_forklist.py {target_repo}
```

CLI usage help output:

```shell
❯ uv run gh_forklist.py -h
usage: Github fork list to CSV. [-h] [-b BRANCH] [--include-identical] REPO

Simple Github CLI wrapper to list the forks of a target Github repository with commit divergence details saved to a .csv file.
Requires Github CLI executable `gh` in path with authentication set up.

positional arguments:
  REPO                 The target Github repository in owner/repo format

options:
  -h, --help           show this help message and exit
  -b BRANCH            The relevant branch of the target repository. If unspecified, uses the default one.
  --include-identical  Include identical/unchanged forks in the list, which are by default discarded.
```
