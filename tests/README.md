# Unit Tests

This folder implements unit tests for testing that the files in `./examples/` parse as expected, and to serve as regression tests to ensure that any output changes in the future are intentional.

````bash
# run tests (from root of project or tests folder):
pytest

# run tests with verbose output / logging
pytest -v -s --log-cli-level=DEBUG
````