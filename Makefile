.PHONY: install build test report powerbi sql dashboard all docs clean

install:        ## editable install with dashboard + test extras
	pip install -e ".[app,dev]"

build:          ## download data, load DuckDB, dbt build (models + tests)
	olist build

test:           ## python tests (needs `make build` first)
	pytest

report:         ## figures + reports/metrics.json
	olist report

powerbi:        ## Parquet export for Power BI
	olist powerbi

sql:            ## run the 22 SQL questions, regenerate the lesson
	olist sql

dashboard:      ## Streamlit app on http://localhost:8501
	olist dashboard

docs:           ## dbt docs site (lineage + column docs) on http://localhost:8080
	./dbt.sh docs generate && ./dbt.sh docs serve

all: build report powerbi sql test

clean:
	rm -rf warehouse/olist.duckdb warehouse/target warehouse/logs powerbi/data
