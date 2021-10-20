FROM mtrqq/repl-backend:0.0.5-base

RUN apt update && apt install rustc -y

ENV EVAL_LANGUAGE=rust