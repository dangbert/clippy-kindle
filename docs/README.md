# clippy-kindle Documentation
[![Documentation Status](https://readthedocs.org/projects/clippy-kindle/badge/?version=latest)](https://clippy-kindle.readthedocs.io/en/latest/?badge=latest)

View this project's documentation [here](https://clippy-kindle.readthedocs.io/en/latest/index.html).

### Or build the docs yourself:

````bash
cd <project_root_directory>/docs
# install python requirements (if not done previously):
virtualenv ../env
source ../env/bin/activate
pip3 install -r ../requirements.txt

make html
# now you can view the docs in your browser:
firefox build/html/index.html
````
