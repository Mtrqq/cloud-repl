FROM mtrqq/repl-backend:0.0.5-base

RUN apt update && apt install nodejs -y

ENV EVAL_SERVER_LANG=nodejs