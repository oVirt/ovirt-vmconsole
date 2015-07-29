include $(top_srcdir)/build/subst.inc

MAINTAINERCLEANFILES = \
	$(srcdir)/Makefile.in \
	$(NULL)

CLEANFILES = \
	ovirt-vmconsole-proxy-sshd.systemd \
	ovirt-vmconsole-proxy-sshd.sysv \
	sshd_config \
	$(NULL)

SUFFIXES = .in

noinst_DATA = \
	ovirt-vmconsole-proxy-sshd.systemd \
	ovirt-vmconsole-proxy-sshd.sysv \
	$(NULL)

libexec_SCRIPTS = \
	ovirt-vmconsole-proxy-sshd \
	$(NULL)

mydir=$(pkgproxydatadir)/ovirt-vmconsole-proxy-sshd
my_DATA = \
	sshd_config \
	$(NULL)
