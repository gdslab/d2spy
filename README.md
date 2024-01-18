# Building with poetry

Run the following from the root directory to build the source and wheels archives: `poetry build`

This will create a `dist` directory containing a `.tar.gz` archive of the source code and a `.whl` file.

# Installing d2spy package with pip

The d2spy package can be installed with pip using the `.whl` in the build's `dist` directory. Inside a Python virtual environment, run `python -m pip install d2spy_pkg-VERSION-py3-none-any.whl` to install d2spy.
