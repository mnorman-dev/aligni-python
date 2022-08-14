# Aligni Python

[![PyPI](https://img.shields.io/pypi/v/aligni-python?style=flat-square)](https://pypi.python.org/pypi/aligni-python/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aligni-python?style=flat-square)](https://pypi.python.org/pypi/aligni-python/)
[![PyPI - License](https://img.shields.io/pypi/l/aligni-python?style=flat-square)](https://pypi.python.org/pypi/aligni-python/)

---

**Source Code**: [https://github.com/mnorman-dev/aligni-python](https://github.com/mnorman-dev/aligni-python)

**PyPI**: [https://pypi.org/project/aligni-python/](https://pypi.org/project/aligni-python/)

---

Python library for interfacing to the Aligni (PLM/MRP) API v2

Full documentation of the underlying API is available at: [https://api.aligni.com/v2/index.html](https://api.aligni.com/v2/index.html)

**WARNING** This code should be considered beta level at best.  A good understanding of the underlying api is required to understand the data available for each datatype.

## Usage

Below is a simple example of how to use this interface to query the parts in a library.  This example uses the demo Aligni site at [https://demo.aligni.com/](https://demo.aligni.com/).
```python
import aligni.api

if __name__ == "__main__":
  sitename = "demo"  # Replace with sitename of Aligni account
  apikey = "oid3vLgynoy_Yl1gZkrgkLEq3J"  # Replace with API Key created from Aligni account

  aligni_api = aligni.api.API(sitename, apikey)
  aligni_parts = aligni_api.parts.get_list()
  aligni_total_part_count = len(aligni_parts)
  print("Aligni Part Count =", aligni_total_part_count)
```

Refer to tests to see further examples.

## Installation

```sh
pip install aligni-python
```

## Development

- Clone this repository
- Requirements:
  - [Poetry](https://python-poetry.org/)
  - Python 3.7+
- Create a virtual environment and install the dependencies

```sh
poetry install
```

- Activate the virtual environment

```sh
poetry shell
```

### Testing

```sh
pytest
```

### Pre-commit

Pre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality
checks to make sure the changeset is in good shape before a commit/push happens.

You can install the hooks with (runs for each commit):

```sh
pre-commit install
```

Or if you want them to run only for each push:

```sh
pre-commit install -t pre-push
```

Or if you want e.g. want to run all checks manually for all files:

```sh
pre-commit run --all-files
```
