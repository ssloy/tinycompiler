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
GFXASM = $(patsubst $(GFXDIR)/%.wend, $(BUILDDIR)/%.s,   $(wildcard $(GFXDIR)/*.wend))
GFXOBJ = $(patsubst $(GFXDIR)/%.wend, $(BUILDDIR)/%.o,   $(wildcard $(GFXDIR)/*.wend))
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
		OBJ=$$DSTDIR/$$(basename $$WEND|sed s/\.wend/\.o/) ; \
		ELF=$$DSTDIR/$$(basename $$WEND|sed s/\.wend//) ; \
		python3 compiler.py $$WEND > $$LL ; \
		llc $$LL ; \
		gcc $$ASM -o $$ELF ; \
		$$ELF | diff $$EXP - ; \
		echo ' ok' ; \
	done

$(BUILDDIR)/%.exe: $(BUILDDIR)/%.o
	ld -m elf_i386 $< -o $@

$(BUILDDIR)/%.o: $(BUILDDIR)/%.s
	as --march=i386 --32 -o $@ $<

$(BUILDDIR)/%.s: $(GFXDIR)/%.wend
	python3 compiler.py $< > $@

gfx: $(BUILDDIR) $(GFXASM) $(GFXOBJ) $(GFXEXE)

clean:
	rm -rf $(BUILDDIR)
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
