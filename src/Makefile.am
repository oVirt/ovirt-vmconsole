MAINTAINERCLEANFILES = \
	$(srcdir)/Makefile.in \
	$(NULL)

dirs =
if ENABLE_HOST
dirs += \
	ovirt-vmconsole-host \
	$(NULL)
endif
if ENABLE_PROXY
dirs += \
	ovirt-vmconsole-proxy \
	$(NULL)
endif

SUBDIRS = \
	$(dirs) \
	ovirt_vmconsole \
	$(NULL)

nodist_sbin_SCRIPTS = \
	$(NULL)

pkgpki_DATA = \
	.keep \
	$(NULL)


dist_pkgempty_DATA = \
	.keep \
	$(NULL)
