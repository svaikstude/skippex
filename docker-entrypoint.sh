#!/bin/sh
set -e
. /app/venv/bin/activate
exec python -m skippex $@
