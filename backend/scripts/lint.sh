#!/bin/sh

set -e
set -x

mypy app
ruff check app
ruff format app --check
