# fancy-dict

[![Build Status](https://travis-ci.org/stefanhoelzl/fancy-dict.svg?branch=master)](https://travis-ci.org/stefanhoelzl/fancy-dict)

**Extends python dictionaries with merging, loading and querying functions**

## Key Features
* Load data from various sources (dicts, Files, HTTP)
* Customize the merging behavior on `update()`
* Querying data from nested dictionaries

## Installation
```bash
pip install git+https://github.com/stefanhoelzl/fancy-dict.git
````

## Usage
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

## Documentation
in progess...

## Development


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
