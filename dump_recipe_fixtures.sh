#!/usr/bin/env bash
set -e

python plannatalerzu/manage.py dump_recipe_fixtures --output recipes/fixtures/recipe_data.json
