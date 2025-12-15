SHELL := /bin/bash
VENV_NAME := .env
SRC := $(shell find . -name "*.py" -print -o -path ./.env -prune)
UNAME := $(shell uname)

all: build

build: .build.ts

install_linux_deps:
	sudo apt install python3.12-dev python3.12-venv gcc

.build.ts:
	python3.12 -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/pip install wheel
	$(VENV_NAME)/bin/pip install -r requirements.txt
	@touch $@

distclean:
	rm -vrf $(VENV_NAME)
	rm -v .*.ts

clean_pyc:
	find . -name "*.pyc" -delete

dump_prod_db:
	mkdir -p backup
	scp stmknights:/mnt/db/db.sqlite3 backup/db.sqlite3

load_data:
	rm -fv db.sqlite3
	source ./set_env_local.sh && \
	./manage.py migrate && \
	./manage.py loaddata db.json

# rebuild_db_from_prod: dump_prod_db load_data

run: build
	source ./set_env_local.sh && source ./set_env_local_secret.sh && \
	./manage.py runserver
