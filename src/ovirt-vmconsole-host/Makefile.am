include $(top_srcdir)/build/subst.inc

MAINTAINERCLEANFILES = \
	$(srcdir)/Makefile.in \
	$(NULL)
CLEANFILES = \
	README \
	ovirt-vmconsole-host.conf \
	$(NULL)

EXTRA_DIST = \
	README.in \
	$(NULL)

SUFFIXES = .in

SUBDIRS = \
	ovirt-vmconsole-host-sshd \
	$(NULL)

nodist_sbin_SCRIPTS = \
	ovirt-vmconsole-host-shell \
	$(NULL)

nodist_pkghostdata_DATA = \
	ovirt-vmconsole-host.conf \
	$(NULL)

confdir = $(pkghostsysconfdir)/conf.d

nodist_conf_DATA = \
	README \
	$(NULL)
