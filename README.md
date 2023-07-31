# CTA

## Install Instructions

To install the library run the following:
```bash
pip install .
```

To create API requests to the following:
```python
from cta import SimpleAPI

tracker = SimpleAPI(key="my_secret_key")
tracker.getroutes()
```

## Finished
- Completed implementing simpleapi.py

## TODO:
- Finish implementing typedapi.py


## Generate Documentation

Run the following:
```python
pip install pdoc3

pdoc --html cta
```

Open `./html/index.html`