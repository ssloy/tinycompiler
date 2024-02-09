SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

BUILDDIR=build
WENDDIR=test-data
TESTS = $(patsubst $(WENDDIR)/%.wend, $(BUILDDIR)/%.wend, $(wildcard $(WENDDIR)/*.wend))

GFXDIR=gfx
GFXASM = $(patsubst $(GFXDIR)/%.wend, $(BUILDDIR)/%.s,   $(wildcard $(GFXDIR)/*.wend))
GFXOBJ = $(patsubst $(GFXDIR)/%.wend, $(BUILDDIR)/%.o,   $(wildcard $(GFXDIR)/*.wend))
GFXEXE = $(patsubst $(GFXDIR)/%.wend, $(BUILDDIR)/%.exe, $(wildcard $(GFXDIR)/*.wend))

.PHONY: run clean

run:
	@mkdir -p $(BUILDDIR)
	@cp -r $(WENDDIR)/* $(BUILDDIR)/
	@for WEND in $(TESTS) ; do \
		echo $$WEND ; \
		EXP=$$(echo $$WEND|sed s/\.wend/\.expected/) ; \
		ASM=$$(echo $$WEND|sed s/\.wend/\.s/) ; \
		OBJ=$$(echo $$WEND|sed s/\.wend/\.o/) ; \
		ELF=$$(echo $$WEND|sed s/\.wend//) ; \
		python3 compiler.py $$WEND > $$ASM ; \
		as --march=i386 --32 -gstabs -o $$OBJ $$ASM ; \
		ld -m elf_i386 $$OBJ  -o $$ELF ; \
		$$ELF | diff $$EXP - ; \
	done

$(BUILDDIR):
	@mkdir -p $(BUILDDIR)

$(BUILDDIR)/%.exe: $(BUILDDIR)/%.o
	ld -m elf_i386 $< -o $@

$(BUILDDIR)/%.o: $(BUILDDIR)/%.s
	as --march=i386 --32 -o $@ $<

$(BUILDDIR)/%.s: $(GFXDIR)/%.wend
	python3 compiler.py $< > $@

gfx: $(BUILDDIR) $(GFXASM) $(GFXOBJ) $(GFXEXE)

clean:
	@rm -rf $(BUILDDIR)
