include $(top_srcdir)/build/python.inc

MAINTAINERCLEANFILES = \
	$(srcdir)/Makefile.in \
	$(NULL)

mypythonmoduledir = $(mypythonlibdir)/ovirt_vmconsole_host_shell

mypythonmodule_PYTHON = \
	__init__.py \
	__main__.py \
	socketproxy.py \
	$(NULL)

clean-local: \
	python-clean \
	$(NULL)

all-local: \
	$(DISTFILES) \
	python-syntax-check \
	$(NULL)
