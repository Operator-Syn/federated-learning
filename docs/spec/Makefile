# Build the technical specification. Run `make` in this directory, or `make -C docs/spec`.
#
# The PDF is a build artifact: it is not committed. What is committed is the LaTeX, the
# shared sections and the glossary.

LATEXMK ?= latexmk
MAIN := technical-spec.tex
PDF := $(MAIN:.tex=.pdf)
SECTIONS := $(wildcard sections/*.tex)

.PHONY: all pdf check clean

all: pdf

pdf: $(PDF)

$(PDF): $(MAIN) $(SECTIONS) glossary.yml
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error $(MAIN)

# Names in the document must match the names the code registers.
check:
	cd ../.. && uv run python scripts/check_glossary.py

clean:
	$(LATEXMK) -C $(MAIN)
