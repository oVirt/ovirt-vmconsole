include $(top_srcdir)/build/python.inc

MAINTAINERCLEANFILES = \
	$(srcdir)/Makefile.in \
	$(NULL)

dirs =
if ENABLE_HOST
dirs += \
	ovirt_vmconsole_host_shell \
	$(NULL)
endif
if ENABLE_PROXY
dirs += \
	ovirt_vmconsole_proxy_keys \
	ovirt_vmconsole_proxy_shell \
	$(NULL)
endif

SUBDIRS = \
	common \
	$(dirs) \
	$(NULL)

mypythonmoduledir = $(mypythonlibdir)

mypythonmodule_PYTHON = \
	__init__.py \
	$(NULL)

clean-local: \
	python-clean \
	$(NULL)

all-local: \
	$(DISTFILES) \
	python-syntax-check \
	$(NULL)
