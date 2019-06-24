SHELL := /bin/bash
VENV_NAME := .env
SRC := $(shell find . -name "*.py" -print -o -path ./.env -prune)
UNAME := $(shell uname)

all: build

build: .build.ts

.build.ts:
	python3.7 -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/pip install -r requirements.txt
	@touch $@

distclean:
	rm -rf $(VENV_NAME)

clean_pyc:
	find . -name "*.pyc" -delete
