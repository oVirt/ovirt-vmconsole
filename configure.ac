AC_PREREQ(2.60)

define([VERSION_MAJOR], [1])
define([VERSION_MINOR], [0])
define([VERSION_FIX], [5])
define([VERSION_NUMBER], VERSION_MAJOR[.]VERSION_MINOR[.]VERSION_FIX)
define([VERSION_SUFFIX], [3])

AC_INIT([ovirt-vmconsole], VERSION_NUMBER[-]VERSION_SUFFIX)
PACKAGE_RPM_VERSION="VERSION_NUMBER"
PACKAGE_RPM_RELEASE="VERSION_SUFFIX"
PACKAGE_MAVEN_VERSION="VERSION_MAJOR.VERSION_MINOR.VERSION_SUFFIX"
AC_SUBST([PACKAGE_RPM_VERSION])
AC_SUBST([PACKAGE_RPM_RELEASE])
AC_SUBST([PACKAGE_MAVEN_VERSION])

AC_CONFIG_AUX_DIR([.])
AC_CONFIG_SRCDIR([src/ovirt_vmconsole/common/base.py])
AC_CONFIG_MACRO_DIR([m4])
AM_INIT_AUTOMAKE([tar-pax])
AM_GNU_GETTEXT_VERSION([0.17])
AM_GNU_GETTEXT([external])

AC_ARG_ENABLE(
	[ovirt-vmconsole-host],
	[AS_HELP_STRING([--disable-ovirt-vmconsole-host], [disable ovirt-vmconsole-host @<:@default=enabled@:>@])],
	,
	[enable_ovirt_vmconsole_host="yes"]
)
AC_ARG_ENABLE(
	[ovirt-vmconsole-proxy],
	[AS_HELP_STRING([--disable-ovirt-vmconsole-proxy], [disable ovirt-vmconsole-proxy @<:@default=enabled@:>@])],
	,
	[enable_ovirt_vmconsole_proxy="yes"]
)
AC_ARG_ENABLE(
	[python-syntax-check],
	[AS_HELP_STRING([--disable-python-syntax-check], [disable python syntax check @<:@default=enabled@:>@])],
	,
	[enable_python_syntax_check="yes"]
)
AC_ARG_WITH(
	[local-version],
	[AS_HELP_STRING([--with-local-version], [local version to use])],
	[LOCAL_VERSION="${withval}"],
	[LOCAL_VERSION=""]
)
AC_ARG_WITH(
	[pkgpkidir],
	[AS_HELP_STRING([--with-pkgpkidir], [pki directory to use @<:@SYSCONFDIR/pki/ovirt-vmconsole@:>@])],
	[pkgpkidir="${withval}"],
	[pkgpkidir="\$(sysconfdir)/pki/ovirt-vmconsole"]
)
AC_ARG_WITH(
	[vmconsole-user],
	[AS_HELP_STRING([--with-vmconsole-user], [user to use @<:@ovirt-vmconsole@:>@])],
	[VMCONSOLE_USER="${withval}"],
	[VMCONSOLE_USER="ovirt-vmconsole"]
)
AC_ARG_WITH(
	[vmconsole-group],
	[AS_HELP_STRING([--with-vmconsole-group], [group to use @<:@ovirt-vmconsole@:>@])],
	[VMCONSOLE_GROUP="${withval}"],
	[VMCONSOLE_GROUP="ovirt-vmconsole"]
)
AC_ARG_WITH(
	[ovirt-vmconsole-host-principal],
	[AS_HELP_STRING([--with-ovirt-vmconsole-host-principal], [principal to use for host @<:@ovirt-vmconsole-host@:>@])],
	[OVIRT_VMCONSOLE_HOST_PRINCIPAL="${withval}"],
	[OVIRT_VMCONSOLE_HOST_PRINCIPAL="ovirt-vmconsole-host"]
)
AC_ARG_WITH(
	[ovirt-vmconsole-proxy-principal],
	[AS_HELP_STRING([--with-ovirt-vmconsole-proxy-principal], [principal to use for proxy @<:@ovirt-vmconsole-proxy@:>@])],
	[OVIRT_VMCONSOLE_PROXY_PRINCIPAL="${withval}"],
	[OVIRT_VMCONSOLE_PROXY_PRINCIPAL="ovirt-vmconsole-proxy"]
)
AC_ARG_WITH(
	[ovirt-vmconsole-host-sshd-port],
	[AS_HELP_STRING([--with-ovirt-vmconsole-host-sshd-port], [remote principal to use @<:@2223@:>@])],
	[OVIRT_VMCONSOLE_HOST_SSHD_PORT="${withval}"],
	[OVIRT_VMCONSOLE_HOST_SSHD_PORT="2223"]
)
AC_ARG_WITH(
	[ovirt-vmconsole-proxy-sshd-port],
	[AS_HELP_STRING([--with-ovirt-vmconsole-proxy-sshd-port], [remote principal to use @<:@2222@:>@])],
	[OVIRT_VMCONSOLE_PORXY_SSHD_PORT="${withval}"],
	[OVIRT_VMCONSOLE_PROXY_SSHD_PORT="2222"]
)
AC_ARG_WITH(
	[ovirt-vmconsole-host-consoledir],
	[AS_HELP_STRING([--with-ovirt-vmconsole-host-consoledir], [console directory @<:@LOCALSTATEDIR/run/ovirt-vmconsole-console@:>@])],
	[consoledir="${withval}"],
	[consoledir="\$(localstatedir)/run/ovirt-vmconsole-console"]
)

AC_PROG_INSTALL
AC_PROG_SED
AC_PROG_MAKE_SET
AC_PROG_MKDIR_P
AC_PROG_LN_S

AM_PATH_PYTHON([2.6],, [AC_MSG_ERROR([Cannot find python])])

AC_ARG_VAR([PYFLAKES], [path to pyflakes utility])
AC_CHECK_PROGS([PYFLAKES], [pyflakes])
AC_ARG_VAR([PEP8], [path to pep8 utility])
AC_CHECK_PROGS([PEP8], [pep8])
AC_ARG_VAR([SSH], [full path to ssh])
AC_PATH_PROGS([SSH], [ssh],, [/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin])
AC_ARG_VAR([SSHD], [full path to sshd])
AC_PATH_PROGS([SSHD], [sshd],, [/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin])

test -n "${SSHD}" || AC_MSG_ERROR([sshd cannot be found])
if test "${enable_ovirt_vmconsole_host}" = "yes"; then
	test -n "${SSH}" || AC_MSG_ERROR([ssh cannot be found])
fi

AC_SUBST([consoledir])
AC_SUBST([pkgemptydir], ["\$(pkgdatadir)/empty"])
AC_SUBST([mypythonlibdir], ["\$(pythondir)/ovirt_vmconsole"])
AC_SUBST([pkghostdatadir], ["\$(pkgdatadir)/ovirt-vmconsole-host"])
AC_SUBST([pkgpkidir])
AC_SUBST([pkgproxydatadir], ["\$(pkgdatadir)/ovirt-vmconsole-proxy"])
AC_SUBST([pkgsysconfdir], ["\$(sysconfdir)/ovirt-vmconsole"])
AC_SUBST([pkghostsysconfdir], ["\$(sysconfdir)/ovirt-vmconsole/ovirt-vmconsole-host"])
AC_SUBST([pkgproxysysconfdir], ["\$(sysconfdir)/ovirt-vmconsole/ovirt-vmconsole-proxy"])
AC_SUBST([LOCAL_VERSION])
AC_SUBST([VMCONSOLE_USER])
AC_SUBST([VMCONSOLE_GROUP])
AC_SUBST([OVIRT_VMCONSOLE_HOST_PRINCIPAL])
AC_SUBST([OVIRT_VMCONSOLE_PROXY_PRINCIPAL])
AC_SUBST([OVIRT_VMCONSOLE_HOST_SSHD_PORT])
AC_SUBST([OVIRT_VMCONSOLE_PROXY_SSHD_PORT])
AM_CONDITIONAL([ENABLE_HOST], [test "${enable_ovirt_vmconsole_host}" = "yes"])
AM_CONDITIONAL([ENABLE_PROXY], [test "${enable_ovirt_vmconsole_proxy}" = "yes"])
AM_CONDITIONAL([PYTHON_SYNTAX_CHECK], [test "${enable_python_syntax_check}" = "yes"])

AC_CONFIG_FILES([
	Makefile
	ovirt-vmconsole.spec
	po/Makefile.in
	selinux-ovirt_vmconsole/Makefile
	selinux-ovirt_vmconsole/ovirt_vmconsole.fc.in
	src/Makefile
	src/ovirt-vmconsole-host/Makefile
	src/ovirt-vmconsole-host/ovirt-vmconsole-host-sshd/Makefile
	src/ovirt-vmconsole-host/ovirt-vmconsole-host-sshd/authorized_principals
	src/ovirt-vmconsole-host/ovirt-vmconsole-host-sshd/ovirt-vmconsole-host-sshd
	src/ovirt-vmconsole-host/ovirt-vmconsole-host-sshd/ovirt-vmconsole-host-sshd.systemd.in
	src/ovirt-vmconsole-host/ovirt-vmconsole-host-sshd/ovirt-vmconsole-host-sshd.sysv.in
	src/ovirt-vmconsole-host/ovirt-vmconsole-host-sshd/sshd_config.in
	src/ovirt-vmconsole-host/ovirt-vmconsole-host.conf.in
	src/ovirt-vmconsole-proxy/Makefile
	src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-sshd/Makefile
	src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-sshd/ovirt-vmconsole-proxy-sshd
	src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-sshd/ovirt-vmconsole-proxy-sshd.systemd.in
	src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-sshd/ovirt-vmconsole-proxy-sshd.sysv.in
	src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-sshd/sshd_config.in
	src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy.conf.in
	src/ovirt-vmconsole-proxy/ssh_config.in
	src/ovirt_vmconsole/Makefile
	src/ovirt_vmconsole/common/Makefile
	src/ovirt_vmconsole/common/config.py.in
	src/ovirt_vmconsole/ovirt_vmconsole_host_shell/Makefile
	src/ovirt_vmconsole/ovirt_vmconsole_proxy_keys/Makefile
	src/ovirt_vmconsole/ovirt_vmconsole_proxy_shell/Makefile
])
AC_CONFIG_FILES(
	[src/ovirt-vmconsole-host/ovirt-vmconsole-host-shell:src/spawn.in],
	[chmod a+x src/ovirt-vmconsole-host/ovirt-vmconsole-host-shell]
)
AC_CONFIG_FILES(
	[src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-keys:src/spawn.in],
	[chmod a+x src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-keys]
)
AC_CONFIG_FILES(
	[src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-shell:src/spawn.in],
	[chmod a+x src/ovirt-vmconsole-proxy/ovirt-vmconsole-proxy-shell]
)
AC_OUTPUT
