PYTHON_SYNTAX_CHECK_FILES = $(srcdir)/*.py

python-syntax-check:
if PYTHON_SYNTAX_CHECK
	FILES="$(AM_PYTHON_SYNTAX_CHECK_FILES)"; \
	FILES="$${FILES:-$(PYTHON_SYNTAX_CHECK_FILES)}"; \
	if [ -n "$(PYFLAKES)" ]; then \
		$(PYFLAKES) $${FILES}; \
	fi
	FILES="$(AM_PYTHON_SYNTAX_CHECK_FILES)"; \
	FILES="$${FILES:-$(PYTHON_SYNTAX_CHECK_FILES)}"; \
	if [ -n "$(PEP8)" ]; then \
		$(PEP8) $${FILES}; \
	fi
endif

python-clean:
	rm -rf $(srcdir)/__pycache__ __pycache__
	rm -f $(srcdir)/*.pyc $(srcdir)/*.pyo *.pyc *.pyo
