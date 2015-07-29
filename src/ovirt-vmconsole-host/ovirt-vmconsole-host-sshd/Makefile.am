include $(top_srcdir)/build/subst.inc

MAINTAINERCLEANFILES = \
	$(srcdir)/Makefile.in \
	$(NULL)

CLEANFILES = \
	ovirt-vmconsole-host-sshd.systemd \
	ovirt-vmconsole-host-sshd.sysv \
	sshd_config \
	$(NULL)

SUFFIXES = .in

noinst_DATA = \
	ovirt-vmconsole-host-sshd.systemd \
	ovirt-vmconsole-host-sshd.sysv \
	$(NULL)

libexec_SCRIPTS = \
	ovirt-vmconsole-host-sshd \
	$(NULL)

mydir=$(pkghostdatadir)/ovirt-vmconsole-host-sshd
my_DATA = \
	authorized_principals \
	sshd_config \
	$(NULL)
