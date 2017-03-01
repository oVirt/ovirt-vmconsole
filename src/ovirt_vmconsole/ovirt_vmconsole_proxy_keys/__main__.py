#
# Copyright 2015-2017 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

import argparse
import gettext
import logging
import os
import pwd
import string
import sys


from ..common import base
from ..common import config
from ..common import utils


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-vmconsole')


class Main(base.Base):

    NAME = 'ovirt-vmconsole-proxy-keys'

    def validations(self):
        ent = pwd.getpwnam(config.VMCONSOLE_USER)
        if not ent:
            raise RuntimeError(
                _("Cannnot resolve user '{user}'").format(
                    user=config.VMCONSOLE_USER,
                )
            )

        if ent.pw_uid != os.geteuid():
            self.logger.debug("User: %s %s", ent.pw_uid, os.geteuid())
            raise RuntimeError(
                _("Must run under user '{user}'").format(
                    user=config.VMCONSOLE_USER,
                )
            )

    def doList(self):
        def _escape(s):
            VALID_CHARS = set(
                string.digits +
                string.ascii_letters +
                ' _-{}'
            )
            r = ''
            for c in str(s):
                r += c if c in VALID_CHARS else '_'
            return r

        out = utils.ProcessUtils().executeJson(
            what=_('Key list'),
            command=self._config.get('proxy', 'key_list').format(
                version=1,
                keyfp='',
                keytype='',
                key='',
            ),
        )
        if out.get('content') != 'key_list':
            raise RuntimeError(_('Invalid key list output'))
        if out.get('version') != 1:
            raise RuntimeError(_('Invalid key list version'))

        for entry in out.get('keys', []):
            if 'entityid' not in entry or 'key' not in entry:
                raise RuntimeError(_('Malformed key entry'))

            if not (
                set(entry['key'].strip().split(' ', 2)[0]) <=
                set(
                    string.ascii_letters +
                    string.digits +
                    '-'
                )
            ):
                raise RuntimeError(
                    _("Invalid key: '{key}'").format(
                        key=entry['key'],
                    )
                )

            if '\n' in entry['key']:
                raise RuntimeError(
                    _("Invalid key: '{key}'").format(
                        key=entry['key'],
                    )
                )

            sys.stdout.write(
                '%s\n' % self._config.get(
                    'proxy',
                    'authorized_keys_entry'
                ).format(
                    entityid=_escape(entry['entityid']),
                    entity=_escape(
                        entry.get('entity', entry['entityid'])
                    ),
                    key=entry['key'].strip(),
                )
            )

    def parse_args(self, cmdline):
        parser = argparse.ArgumentParser(
            prog=self.NAME,
            description=_('oVirt VM console keys'),
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help=_('enable debug log'),
        )

        subparsers = parser.add_subparsers(
            dest='command',
            help=_('sub-command help'),
        )
        subparsers.required = True

        helpParser = subparsers.add_parser(
            'help',
            help=_('present help'),
        )
        helpParser.set_defaults(
            func=lambda: parser.print_help(),
        )

        listParser = subparsers.add_parser(
            'list',
            help=_('list keys'),
        )
        listParser.set_defaults(
            func=lambda: self.doList(),
        )

        # ssh execute with hardcoded user name
        listParser = subparsers.add_parser(
            config.VMCONSOLE_USER,
            help=_('list keys'),
        )
        listParser.set_defaults(
            func=lambda: self.doList(),
        )

        return parser.parse_args(cmdline)

    def main(self):
        ret = 1
        try:
            self._config = utils.loadConfig(
                defaults=os.path.join(
                    config.pkgproxydatadir,
                    'ovirt-vmconsole-proxy.conf',
                ),
                location=os.path.join(
                    config.pkgproxysysconfdir,
                    'conf.d',
                ),
            )

            utils.setupLogger(processName=self.NAME)

            self._args = self.parse_args(sys.argv[1:])

            if self._config.getboolean('proxy', 'debug') or self._args.debug:
                logging.getLogger(base.Base.LOG_PREFIX).setLevel(logging.DEBUG)

            self.logger.debug(
                '%s: %s-%s (%s)',
                self.NAME,
                config.PACKAGE_NAME,
                config.PACKAGE_VERSION,
                config.LOCAL_VERSION,
            )
            self.logger.debug(
                'cmdline=%s args=%s, config=%s',
                sys.argv,
                self._args,
                self._config,
            )
            self.validations()
            self._args.func()
            ret = 0
        except Exception as e:
            self.logger.error('%s', str(e))
            self.logger.debug('Exception', exc_info=True)
            sys.stderr.write(_('ERROR: Internal error\n'))
        return ret


if __name__ == '__main__':
    os.umask(0o022)
    sys.exit(Main().main())


# vim: expandtab tabstop=4 shiftwidth=4
