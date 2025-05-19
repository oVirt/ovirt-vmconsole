.PHONY: installdeps git_cfg_safe srpm

installdeps:
	dnf -y install git autoconf automake make gettext-devel openssh-clients openssh-server python3-devel gcc

git_cfg_safe: installdeps
	# From git 2.35.2 we need to mark temporary directory, where the project is cloned to, as safe, otherwise
	# git commands won't work because of the fix for CVE-2022-24765
	git config --global --add safe.directory "$(shell pwd)"

srpm: git_cfg_safe
	$(eval SUFFIX=$(shell sh -c " echo '.$$(date -u +%Y%m%d%H%M%S).git$$(git rev-parse --short HEAD)'"))
	sed "s:%{?release_suffix}:${SUFFIX}:" -i ovirt-vmconsole.spec.in
	mkdir -p tmp.repos/SOURCES
	autopoint
	autoreconf -ivf
	./configure
	make dist
	rpmbuild \
		-D "_topdir tmp.repos" \
		-ts ./*.tar.gz
	cp tmp.repos/SRPMS/*.src.rpm $(outdir)
