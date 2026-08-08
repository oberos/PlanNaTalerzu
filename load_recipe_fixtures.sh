#!/usr/bin/env bash
set -e

python plannatalerzu/manage.py loaddata recipes/fixtures/recipe_data.json
