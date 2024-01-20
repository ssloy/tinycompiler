SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

VENV := $(shell echo $${VIRTUAL_ENV-.venv})
PY3 := $(shell command -v python3 2>/dev/null)
PYTHON := $(VENV)/bin/python
INSTALL_STAMP := $(VENV)/.install.stamp

BUILDDIR=build
WENDDIR=test-data
TESTS = $(patsubst $(WENDDIR)/%.wend, $(BUILDDIR)/%.wend, $(wildcard $(WENDDIR)/*.wend))

.PHONY: test run clean

$(PYTHON):
	@if [ -z $(PY3) ]; then echo "Python 3 could not be found."; exit 2; fi
	echo $(PY3) -m venv $(VENV)
	$(PY3) -m venv $(VENV)

$(INSTALL_STAMP): $(PYTHON) requirements.txt
	$(PYTHON) -m pip install -r requirements.txt
	touch $(INSTALL_STAMP)

test: $(INSTALL_STAMP)
	$(PYTHON) -m pytest --cov . -v --cov-report term-missing ./tests/

run: $(INSTALL_STAMP)
	@mkdir -p $(BUILDDIR)
	@cp -r $(WENDDIR)/* $(BUILDDIR)/
	@for WEND in $(TESTS) ; do \
		echo $$WEND ; \
		EXP=$$(echo $$WEND|sed s/\.wend/\.expected/) ; \
		ASM=$$(echo $$WEND|sed s/\.wend/\.s/) ; \
		OBJ=$$(echo $$WEND|sed s/\.wend/\.o/) ; \
		ELF=$$(echo $$WEND|sed s/\.wend//) ; \
		$(PYTHON) compiler.py $$WEND > $$ASM ; \
		as --march=i386 --32 -gstabs -o $$OBJ $$ASM ; \
		ld -m elf_i386 $$OBJ  -o $$ELF ; \
		$$ELF | diff $$EXP - ; \
	done



clean:
	@rm -rf $(BUILDDIR)
	rm -rf $(VENV) .pytest_cache .coverage
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete

