# Custom Components

TODO.

## Testing
Test files written in the pytest idiom will be automatically picked up when the
test suite is run. In other words, to add tests for your component, simply
create a `test` folder inside your component folder, and add
`test_something.py` files inside it.

The import path for your module should be absolute, i.e.:
```python 
from lib.analysers.my_analyser import main as my_analyser
```

Special fixtures to help test lifecycle functions are on their way, but
currently don't exist. So you can only test pure functions.

