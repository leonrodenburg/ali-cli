#!/bin/bash
pipenv shell

# Bump version
VERSION_PART=$1
VERSION=$(bumpversion --list $VERSION_PART | grep 'new_version\=' | tr '=' '\n' | grep '[0-9.]')

# Push new commit and tag
git push
git push --tags

# Create distribution package and upload to PyPI
python setup.py sdist bdist_wheel
twine upload dist/*$VERSION*
