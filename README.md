# dockfiletographviz
Python package for converting Dockerfile into input for Graphviz

# Development

## Code Checks
```bash
black ./src -l 120 && flake8 --max-line-length 120 && mypy . && coverage run --source=src -m pytest -v && coverage html
```