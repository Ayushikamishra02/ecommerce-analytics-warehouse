#!/usr/bin/env bash
# run dbt from the repo root: ./dbt.sh build | test | docs generate
DIR="$(cd "$(dirname "$0")" && pwd)"
DBT_PROFILES_DIR="$DIR/warehouse" OLIST_DB="$DIR/warehouse/olist.duckdb" dbt "$@" --project-dir "$DIR/warehouse"
