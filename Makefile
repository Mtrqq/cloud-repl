build-all:
	docker build ./backend/ -t mtrqq/repl-backend:0.0.5-base
	docker build ./frontend/ -t mtrqq/repl-frontend:0.0.4
	cd backend/docker && docker build . -t mtrqq/repl-backend:0.0.4-python -f python.dockerfile
	cd backend/docker && docker build . -t mtrqq/repl-backend:0.0.7-rust -f rust.dockerfile
	cd backend/docker && docker build . -t mtrqq/repl-backend:0.0.1-nodejs -f nodejs.dockerfile

push-all:
	docker push mtrqq/repl-backend:0.0.5-base
	docker push mtrqq/repl-frontend:0.0.4
	docker push mtrqq/repl-backend:0.0.4-python
	docker push mtrqq/repl-backend:0.0.7-rust
	docker push mtrqq/repl-backend:0.0.1-nodejs