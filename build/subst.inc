.in:
	if sed \
		-e 's#[@]bindir_POST@#$(bindir)#g' \
		-e 's#[@]consoledir_POST@#$(consoledir)#g' \
		-e 's#[@]localstatedir_POST@#$(localstatedir)#g' \
		-e 's#[@]pkgemptydir_POST@#$(pkgemptydir)#g' \
		-e 's#[@]pkgdatadir_POST@#$(pkgdatadir)#g' \
		-e 's#[@]pkghostdatadir_POST@#$(pkghostdatadir)#g' \
		-e 's#[@]pkghostsysconfdir_POST@#$(pkghostsysconfdir)#g' \
		-e 's#[@]pkgpkidir_POST@#$(pkgpkidir)#g' \
		-e 's#[@]pkgproxydatadir_POST@#$(pkgproxydatadir)#g' \
		-e 's#[@]pkgproxysysconfdir_POST@#$(pkgproxysysconfdir)#g' \
		-e 's#[@]pkgsysconfdir_POST@#$(pkgsysconfdir)#g' \
		-e 's#[@]sbindir_POST@#$(sbindir)#g' \
		-e 's#[@]sysconfdir_POST@#$(sysconfdir)#g' \
		$< > $@.tmp; then \
		mv "$@.tmp" "$@"; \
	else \
		rm -f "$@.tmp"; \
		false; \
	fi
