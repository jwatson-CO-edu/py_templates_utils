# Dependencies
## Python 3.11
## PMD, Static Analysis
1. `cd /tmp/`
1. `wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.10.0/pmd-dist-7.10.0-bin.zip`
1. `unzip pmd-dist-7.10.0-bin.zip`
1. `sudo mv pmd-bin-7.10.0 /opt/`
1. Add to "~/.bashrc": `alias pmd="/opt/pmd-bin-7.10.0/bin/pmd"`

# `DEV_PLAN`
* `[ ]` Fetch most recent branch: `git for-each-ref --sort=-authordate`
    - `[ ]` Global flag for whether to do this


# Nice Features?
## Static Analysis
* [PMD - source code analyzer](https://github.com/pmd/pmd)
    - `[ ]` Build
    - `[ ]` Test CLI from student project
    - `[ ]` Test CLI from root folder
