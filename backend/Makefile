install:
	@poetry install

reformat:
	@poetry run black .
	@poetry run isort .

lint:
	@poetry run flakehell lint . --count
	@poetry run mypy .

clean:
	@rm -rf build dist .eggs *.egg-info
	@rm -rf .benchmarks .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -rf {} +

test:
	@poetry run pytest --cov=evalserver --typeguard-packages=evalserver -n=auto tests/ -s

tox:
	@poetry run tox -q

build:
	@poetry build

wheel:
	@poetry build -v

publish:
	@poetry publish

sync-version:
	@poetry version -s | xargs -I % sed -i 's#".\+"#"%"#g' evalserver/version.py

start:
	@poetry run python ./evalserver/main.py

run:
	@poetry run python ./evalserver/main.py