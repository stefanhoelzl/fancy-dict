# fancy-dict

[![Build Status](https://travis-ci.org/stefanhoelzl/fancy-dict.svg?branch=master)](https://travis-ci.org/stefanhoelzl/fancy-dict)
[![Coverage Status](https://coveralls.io/repos/github/stefanhoelzl/fancy-dict/badge.svg?branch=master)](https://coveralls.io/github/stefanhoelzl/fancy-dict?branch=master)
[![Test Status](data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMzMiIGhlaWdodD0iMjAiPgogICAgPGxpbmVhckdyYWRpZW50IGlkPSJiIiB4Mj0iMCIgeTI9IjEwMCUiPgogICAgICAgIDxzdG9wIG9mZnNldD0iMCIgc3RvcC1jb2xvcj0iI2JiYiIgc3RvcC1vcGFjaXR5PSIuMSIvPgogICAgICAgIDxzdG9wIG9mZnNldD0iMSIgc3RvcC1vcGFjaXR5PSIuMSIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxtYXNrIGlkPSJhIj4KICAgICAgICA8cmVjdCB3aWR0aD0iMTMzIiBoZWlnaHQ9IjIwIiByeD0iMyIgZmlsbD0iI2ZmZiIvPgogICAgPC9tYXNrPgogICAgPGcgbWFzaz0idXJsKCNhKSI+CiAgICAgICAgPHBhdGggZmlsbD0iIzU1NSIgZD0iTTAgMGg0NXYyMEgweiIvPgogICAgICAgIDxwYXRoIGZpbGw9IiM0YzEiIGQ9Ik00NSAwaDg4djIwSDQ1eiIvPgogICAgICAgIDxwYXRoIGZpbGw9InVybCgjYikiIGQ9Ik0wIDBoMTMzdjIwSDB6Ii8+CiAgICA8L2c+CiAgICA8ZyBmaWxsPSIjZmZmIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMsVmVyZGFuYSxHZW5ldmEsc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxMSI+CiAgICAgICAgPHRleHQgeD0iMjMuNSIgeT0iMTUiIGZpbGw9IiMwMTAxMDEiIGZpbGwtb3BhY2l0eT0iLjMiPnRlc3RzPC90ZXh0PgogICAgICAgIDx0ZXh0IHg9IjIyLjUiIHk9IjE0Ij50ZXN0czwvdGV4dD4KICAgIDwvZz4KICAgIDxnIGZpbGw9IiNmZmYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyxWZXJkYW5hLEdlbmV2YSxzYW5zLXNlcmlmIiBmb250LXNpemU9IjExIj4KICAgICAgICA8dGV4dCB4PSI5MC4wIiB5PSIxNSIgZmlsbD0iIzAxMDEwMSIgZmlsbC1vcGFjaXR5PSIuMyI+cGFzc2VkIDEwMzwvdGV4dD4KICAgICAgICA8dGV4dCB4PSI4OS4wIiB5PSIxNCI+cGFzc2VkIDEwMzwvdGV4dD4KICAgIDwvZz4KPC9zdmc+)](https://github.com/stefanhoelzl/fancy-dict/blob/ci-results/master/testresults.tap)

**Extends python dictionaries with merging, loading and querying functions**

## Key Features
* Load data from various sources (dicts, Files, HTTP)
* Customize the merging behavior on `update()`
* Querying data from nested dictionaries

Currently only tested on Python 3.6

## Installation
```bash
$ pip install git+https://github.com/stefanhoelzl/fancy-dict.git
````

## Usage
Basics
```python
>>> from fancy_dict import FancyDict

# Load data form GitHub-API
>>> repo = FancyDict.load("https://api.github.com/repos/stefanhoelzl/fancy-dict")

# Access like plain python dicts
>>> repo["owner"]["avatar_url"]
'https://avatars0.githubusercontent.com/u/1478183?v=4'

# Nested updates
>>> repo.update({"owner": {"avatar_url": "https://avatars0.githubusercontent.com/u/254659"}})

# Other values in repo["owner"] are still present
>>> repo["owner"]["html_url"]
'https://github.com/stefanhoelzl'

# Get nested values with query
>>> list(repo.query("owner.avatar_url"))
['https://avatars0.githubusercontent.com/u/254659']
```
Load and merge annotated yaml/json files.
```python
# Create directories later needed
>>> import os
>>> os.makedirs("inc")

# Import used fancy_dict classes
>>> from fancy_dict import FancyDict
>>> from fancy_dict.loader import KeyAnnotationsConverter

# write settings defaults
>>> with open("inc/base.yml", "w+") as base_file:
>>>     base_file.write('{"counter[add]": 0, "settings": {"skip": True}}')

# write custom settings
>>> with open("config.yml", "w+") as config_file:
>>>     config_file.write('{"include": ["base.yml"], "counter": 1, "settings": {"+skip": False, "?merge": True}}')

# merge custom and default settings
>>> FancyDict.load("config.yml", include_paths=("inc",), include_key="include", annotations_decoder=KeyAnnotationsConverter)
{'counter': 1, 'settings': {'skip': True}}
```
Annotate keys to control updating behavior
```python
>>> from fancy_dict import FancyDict
>>> from fancy_dict.merger import add
>>> from fancy_dict.conditions import if_existing, if_not_existing

# Set a custom merge method (defines how old and new value get merged)
>>> annotated_dict = FancyDict({"counter": 0})
# sets an annotation that the key "counter" should be updated by adding old and new value
>>> annotated_dict.annotate("counter", merge_method=add)
>>> annotated_dict.update({"counter": 1})
>>> annotated_dict["counter"]
1
>>> annotated_dict.update({"counter": 1})
>>> annotated_dict["counter"]
2

# Finalizes a value for a given key, so updates dont change this value
>>> annotated_dict.annotate("counter", finalized=True)
>>> annotated_dict.update({"counter": 1})
>>> annotated_dict["counter"]
2
# direct changes of this key are still possible
>>> annotated_dict["counter"] = 0
>>> annotated_dict["counter"]
0

# set annotations so that updates only apply under certain conditions
>>> annotated_dict.annotate("not_existing", condition=if_existing)
>>> annotated_dict.update({"not_existing": False})
>>> annotated_dict.keys()
dict_keys(['counter'])
>>> annotated_dict["not_existing"] = False
>>> annotated_dict.update({"not_existing": True})
>>> annotated_dict["not_existing"]
True  # value was updated, because it was existing before

# same for if_not_existing condition
>>> annotated_dict.annotate("existing", condition=if_not_existing)
>>> annotated_dict["existing"] = False
>>> annotated_dict.update({"existing": True})
>>> annotated_dict["existing"]
False
>>> del annotated_dict["existing"]
>>> annotated_dict.update({"existing": True})
>>> annotated_dict["existing"]
True
```
## Development status
Alpha

working towards the first release and better documentation!

## Documentation
in progess...

## Contribution
* **There is a bug?** Write an [Issue](https://github.com/stefanhoelzl/fancy-dict/issues)
* **You like it?** Great!! Spread the news :)

### Submit changes
_tested on macOS and Linux (will be different on Windows)_

Fork it and check out:
``` bash
$ git checkout https://github.com/<YourUsername>/fancy-dict.git
```
setup the development environment
```bash
$ cd fancy-dict
$ virtualenv venv
$ source venv/bin/activate
$ make env.install
```
Write a failing test, make your changes until all tests pass
```bash
$ make tests           # runs all tests
$ make tests.unit      # runs only unit tests
$ make test.lint       # runs only linter
$ make tests.coverage  # runs only code coverage
```
Before making a pull request, check if still everythinig builds
```bash
$ make       # runs all tests, builds the docs and creates a package
$ make clean # cleans the repository
```
Create a pull request!

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
