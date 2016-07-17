#!/bin/mksh

git commit -m "Update www submodule.

$(git submodule summary www)" www
