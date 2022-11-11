SHELL := /bin/bash
VENV_NAME := .env
SRC := $(shell find . -name "*.py" -print -o -path ./.env -prune)
UNAME := $(shell uname)

all: build

build: .build.ts

install_linux_deps:
	sudo apt install python3.10-dev python3.10-venv gcc libmysqlclient-dev

.build.ts:
	python3.10 -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/pip install wheel
	$(VENV_NAME)/bin/pip install -r requirements.txt
	@touch $@

distclean:
	rm -vrf $(VENV_NAME)
	rm -v .*.ts

clean_pyc:
	find . -name "*.pyc" -delete

dump_prod_db:
	source ./set_env_prod.sh && \
	./manage.py dumpdata \
	--exclude auth.permission \
	--exclude contenttypes \
	--exclude auth.user \
	--exclude sessions.session \
	--exclude adminplus \
	--exclude admin.logentry \
	--indent 2 > db.json

load_data:
	rm -fv db.sqlite3
	source ./set_env_local.sh && \
	./manage.py migrate && \
	./manage.py loaddata db.json

rebuild_db_from_prod: dump_prod_db load_data

run: build
	source ./set_env_local.sh && source ./set_env_local_secret.sh && \
	./manage.py runserver
