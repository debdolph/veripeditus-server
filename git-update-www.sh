#!/bin/sh

git commit -m "Update www submodule.\n\n$(git submodule summary www)" www
