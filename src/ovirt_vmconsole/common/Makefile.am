include $(top_srcdir)/build/subst.inc
include $(top_srcdir)/build/python.inc

MAINTAINERCLEANFILES = \
	$(srcdir)/Makefile.in \
	$(NULL)
CLEANFILES = \
	config.py \
	$(NULL)

SUFFIXES = .in

mypythonmoduledir = $(mypythonlibdir)/common

mypythonmodule_PYTHON = \
	__init__.py \
	base.py \
	utils.py \
	$(NULL)

nodist_mypythonmodule_PYTHON = \
	config.py \
	$(NULL)

clean-local: \
	python-clean \
	$(NULL)

all-local: \
	$(DISTFILES) \
	python-syntax-check \
	$(NULL)
