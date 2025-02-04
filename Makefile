SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

BUILDDIR = build
WENDDIR = test-programs
TESTS = $(shell find $(WENDDIR) -name '*.wend' -not -path '*/gfx/*')

GFXDIR = $(WENDDIR)/gfx
GFXLL  = $(patsubst $(GFXDIR)/%.wend, $(BUILDDIR)/%.ll,  $(wildcard $(GFXDIR)/*.wend))
GFXASM = $(patsubst $(GFXDIR)/%.wend, $(BUILDDIR)/%.s,   $(wildcard $(GFXDIR)/*.wend))
GFXEXE = $(patsubst $(GFXDIR)/%.wend, $(BUILDDIR)/%.exe, $(wildcard $(GFXDIR)/*.wend))

.PHONY: all test clean

all: test gfx

$(BUILDDIR):
	@mkdir -p $(BUILDDIR)

test: $(BUILDDIR)
	for WEND in $(TESTS) ; do \
		SRCDIR=$$(dirname $$WEND) ; \
		DSTDIR=$$(dirname $$WEND | sed s/$(WENDDIR)/$(BUILDDIR)/) ; \
		mkdir -p $$DSTDIR ; \
		echo -n Testing $$WEND... ;\
		EXP=$$(echo $$WEND|sed s/\.wend/\.expected/) ; \
		LL=$$DSTDIR/$$(basename $$WEND|sed s/\.wend/\.ll/) ; \
		ASM=$$DSTDIR/$$(basename $$WEND|sed s/\.wend/\.s/) ; \
		ELF=$$DSTDIR/$$(basename $$WEND|sed s/\.wend//) ; \
		python3 compiler.py $$WEND > $$LL ; \
		llc $$LL ; \
		gcc $$ASM -o $$ELF ; \
		$$ELF | diff $$EXP - ; \
		echo ' ok' ; \
	done

$(BUILDDIR)/%.exe: $(BUILDDIR)/%.s
	gcc -o $@ $<

$(BUILDDIR)/%.s: $(BUILDDIR)/%.ll
	llc $<

$(BUILDDIR)/%.ll: $(GFXDIR)/%.wend
	python3 compiler.py $< > $@

gfx: $(BUILDDIR) $(GFXLL) $(GFXASM) $(GFXEXE)

clean:
	rm -rf $(BUILDDIR)
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
