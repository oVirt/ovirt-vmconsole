import argparse
import gettext
import logging
import os
import pwd
import shlex
import sys
import termios


from ..common import base
from ..common import config
from ..common import utils


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-vmconsole')


class UserVisibleRuntimeError(RuntimeError):
    pass


class Main(base.Base):

    NAME = 'ovirt-vmconsole-host-shell'

    def _fileContent(self, name):
        with open(name, 'r') as f:
            return f.read()

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

    def doInfo(self):
        sys.stdout.write(
            (
                'package=%s\n'
                'ssh-ca-key=%s\n'
                'ssh-host-cert=%s\n'
            ) % (
                self.NAME,
                self._fileContent(
                    os.path.join(
                        config.pkgpkidir,
                        'ca.pub',
                    )
                ).rstrip('\n'),
                self._fileContent(
                    os.path.join(
                        config.pkgpkidir,
                        'host-ssh_host_rsa-cert.pub',
                    )
                ).rstrip('\n'),
            )
        )

    def doConnect(self):

        try:
            termios.tcgetattr(sys.stdin.fileno())
        except:
            raise UserVisibleRuntimeError(
                _('No pty support, please enable at client side')
            )

        if os.path.basename(self._args.console) != self._args.console:
            raise UserVisibleRuntimeError(
                _('Invalid console name')
            )

        socket = os.path.join(
            self._config.get('host', 'consoledir'),
            self._args.console,
        )

        self.logger.debug("socket: %s", socket)

        if not os.access(socket, os.F_OK):
            self.logger.debug('exists')

        if not os.access(socket, os.F_OK | os.R_OK | os.W_OK):
            raise UserVisibleRuntimeError(
                _("Console '{console}' is not available").format(
                    console=self._args.console,
                )
            )

        self.logger.info(
            _(
                "Opening console '{console}' on behalf of "
                "'{entity}'[{entityid}]"
            ).format(
                console=self._args.console,
                entity=self._args.entity if self._args.entity else 'N/A',
                entityid=self._args.entityid if self._args.entityid else 'N/A',
            ),
        )

        cmd = self._config.get('host', 'console_attach').format(
            socket=socket,
        )
        self.logger.debug('Executing: %s', cmd)
        os.execv(
            self._config.get('host', 'shell'),
            [
                self._config.get('host', 'shell'),
                '-c', cmd,
            ],
        )
        raise RuntimeError('Cannot execute socat')

    def parse_args(self, cmdline):
        parser = argparse.ArgumentParser(
            prog=self.NAME,
            description=_('oVirt VM console host shell'),
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help=_('enable debug log'),
        )
        parser.add_argument(
            '--entityid',
            help=_('original entity id'),
        )
        parser.add_argument(
            '--entity',
            help=_('original entity'),
        )

        subparsers = parser.add_subparsers(
            help=_('sub-command help'),
        )

        helpParser = subparsers.add_parser(
            'help',
            help=_('present help'),
        )
        helpParser.set_defaults(
            func=lambda: parser.print_help(),
        )

        infoParser = subparsers.add_parser(
            'info',
            help=_('present information'),
        )
        infoParser.set_defaults(
            func=lambda: self.doInfo(),
        )

        connectParser = subparsers.add_parser(
            'connect',
            help=_('connect to console'),
        )
        connectParser.add_argument(
            '--console',
            required=True,
            help=_('console to use'),
        )
        connectParser.set_defaults(
            func=lambda: self.doConnect(),
        )

        return parser.parse_args(cmdline)

    def main(self):
        ret = 1
        try:
            self._config = utils.loadConfig(
                defaults=os.path.join(
                    config.pkghostdatadir,
                    'ovirt-vmconsole-host.conf',
                ),
                location=os.path.join(
                    config.pkghostsysconfdir,
                    'conf.d',
                ),
            )

            utils.setupLogger(processName=self.NAME)

            self._args = self.parse_args(
                shlex.split(os.environ.get('SSH_ORIGINAL_COMMAND', ''))
            )

            if self._config.getboolean('host', 'debug') or self._args.debug:
                logging.getLogger(base.Base.LOG_PREFIX).setLevel(logging.DEBUG)

            self.logger.debug(
                '%s: %s-%s (%s)',
                self.NAME,
                config.PACKAGE_NAME,
                config.PACKAGE_VERSION,
                config.LOCAL_VERSION,
            )
            self.logger.debug(
                'SSH_ORIGINAL_COMMAND=%s args=%s config=%s',
                os.environ.get('SSH_ORIGINAL_COMMAND'),
                self._args,
                self._config,
            )
            self.validations()
            self._args.func()
            ret = 0
        except UserVisibleRuntimeError as e:
            self.logger.error('%s', str(e))
            self.logger.debug('Exception', exc_info=True)
            sys.stderr.write(_('ERROR: {error}\n').format(error=e))
        except Exception as e:
            self.logger.error('%s', str(e))
            self.logger.debug('Exception', exc_info=True)
            sys.stderr.write(_('ERROR: Internal error\n'))
        return ret


if __name__ == '__main__':
    os.umask(0o022)
    sys.exit(Main().main())
