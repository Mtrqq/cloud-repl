FROM python:3.8.12-slim-bullseye as builder

WORKDIR /usr/app

RUN python -m pip install -U pip setuptools wheel --user --no-cache-dir && \
    python -m pip install poetry==1.1.10 --user --no-cache-dir

COPY . .

RUN python -m poetry export -f requirements.txt -o ./requirements.txt && \
    python -m pip download -r ./requirements.txt -d --prefer-binary -d ./dist && \
    python -m poetry build -f wheel


FROM python:3.8.12-slim-bullseye

WORKDIR /usr/app

COPY --from=builder /usr/app/dist ./dist
COPY --from=builder /usr/app/requirements.txt ./requirements.txt

RUN python -m pip install -r ./requirements.txt -f ./dist && \
    python -m pip install evalserver -f ./dist

ENTRYPOINT [ "python" ]
CMD ["-m", "evalserver"]