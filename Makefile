# Repository entry points. Run `make` (or `make help`) from the repository root.
#
# The specification keeps its own Makefile in docs/spec/ — it carries the LaTeX rules and
# knows its sources. This file only collects the tasks you actually run day to day, so the
# commands are discoverable without reading docs.
#
# Nothing here writes tracked files: the spec's PDF and LaTeX auxiliaries are ignored by
# docs/spec/.gitignore, and experiment output belongs in runs/ (ignored as well).

UV ?= uv
SPEC_DIR := docs/spec

.DEFAULT_GOAL := help
.PHONY: help sync spec spec-check spec-audit selftest lint format notebooks check clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "; printf "\nUsage: make <target>\n\n"} \
	      /^[a-zA-Z_-]+:.*?## / { printf "  %-12s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@printf "\n"

sync: ## Create/refresh the environment from uv.lock
	$(UV) sync

spec: ## Build the technical specification PDF (docs/spec/technical-spec.pdf)
	$(MAKE) -C $(SPEC_DIR)

spec-check: ## Check that the specification's names match the implementation
	$(UV) run python scripts/check_glossary.py

spec-audit: ## Build the spec PDF and audit the artifact (notation, headings, standalone, margins)
	@if command -v latexmk >/dev/null 2>&1; then \
	  $(UV) run python scripts/check_spec.py; \
	else \
	  printf 'skipping spec audit: latexmk is not installed (see docs/spec/README.md)\n'; \
	fi

selftest: ## Fail if a gate has stopped rejecting what it exists to reject
	$(UV) run python scripts/selftest_gates.py

lint: ## Ruff errors only — the same scope the pre-commit hook blocks on
	$(UV) run ruff check .

format: ## Apply ruff formatting to Python sources
	$(UV) run ruff format src scripts

notebooks: ## Fail if a notebook would be committed with outputs (judges the stored form)
	$(UV) run python scripts/check_notebook_outputs.py --stored-form

check: lint selftest spec-check spec-audit notebooks ## Everything that must pass before a commit
	@printf "\nAll checks passed.\n"

clean: ## Remove build artifacts (spec PDF, LaTeX auxiliaries, caches)
	$(MAKE) -C $(SPEC_DIR) clean
	rm -rf .ruff_cache .pytest_cache
	find . -type d -name '__pycache__' -not -path './.venv/*' -prune -exec rm -rf {} +
