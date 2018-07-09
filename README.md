# fancy-dict

[![Build Status](https://travis-ci.org/stefanhoelzl/fancy-dict.svg?branch=master)](https://travis-ci.org/stefanhoelzl/fancy-dict)
[![Build Status](https://fancy-dict.readthedocs.io/en/latest/?badge=latest)](http://fancy-dict.readthedocs.io/)
[![Coverage Status](https://coveralls.io/repos/github/stefanhoelzl/fancy-dict/badge.svg?branch=master)](https://coveralls.io/github/stefanhoelzl/fancy-dict?branch=master)
[![Test Status](https://raw.githubusercontent.com/stefanhoelzl/ci-results/fancy-dict/master/tests.png)](https://github.com/stefanhoelzl/ci-results/blob/fancy-dict/master/testresults.tap)

**Extends python dictionaries with merge, load and filter functions**

## Key Features
* Load data from various sources (dicts, Files, HTTP)
* Customize the merging behavior on `update()`
* Filter data of dictionaries

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
...     base_file.write('{"counter[add]": 0, "settings": {"skip": True}}')
47

# write custom settings
>>> with open("config.yml", "w+") as config_file:
...     config_file.write('{"include": ["base.yml"], "counter": 1, "settings": {"+skip": False, "?merge": True}}')
85

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
>>> annotated_dict["not_existing"]  # value was updated, because it was existing before
True

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
http://fancy-dict.readthedocs.io/

## Contribution
* **There is a bug?** Write an [Issue](https://github.com/stefanhoelzl/fancy-dict/issues)
* **Feedback or Questions?** Write an [Issue](https://github.com/stefanhoelzl/fancy-dict/issues)
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
$ make tests.lint       # runs only linter
$ make tests.coverage  # runs only code coverage
```
Before making a pull request, check if still everythinig builds
```bash
$ make       # runs all tests, builds the docs and creates a package
$ make clean # cleans the repository
```
Create a pull request!

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/stefanhoelzl/fancy-dict/blob/master/LICENSE) file for details
