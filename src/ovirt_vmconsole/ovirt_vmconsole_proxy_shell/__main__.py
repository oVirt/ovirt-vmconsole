import argparse
import gettext
import json
import logging
import os
import pwd
import shlex
import sys
import tempfile
import termios
import time


from ..common import base
from ..common import config
from ..common import utils


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-vmconsole')


class UserVisibleRuntimeError(RuntimeError):
    pass


class UserExit(RuntimeError):
    pass


class Main(base.Base):

    NAME = 'ovirt-vmconsole-proxy-shell'

    _consoles = []

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
                'ssh-proxy-cert=%s\n'
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
                        'proxy-ssh_host_rsa-cert.pub',
                    )
                ).rstrip('\n'),
            )
        )

    def doAccept(self):
        out = utils.ProcessUtils().executeJson(
            _('Console list'),
            self._config.get('proxy', 'console_list').format(
                version=1,
                entityid=self._args.entityid,
            ),
        )
        if out.get('content') != 'console_list':
            raise RuntimeError(_('Invalid console list output'))
        if out.get('version') != 1:
            raise RuntimeError(_('Invalid console list version'))
        out.setdefault('consoles', [])
        self._consoles = out

    def doConnect(self):

        try:
            termios.tcgetattr(sys.stdin.fileno())
        except:
            raise UserVisibleRuntimeError(
                _('No pty support, please enable at client side')
            )

        consoles = self._consoles['consoles']
        entry = None
        if self._userargs.vm_id:
            for e in consoles:
                if self._userargs.vm_id == e['vmid']:
                    entry = e
                    break
            else:
                raise UserVisibleRuntimeError(
                    _("VM with id '{vmid}' is unavailable").format(
                        vmid=self._userargs.vm_id,
                    )
                )
        elif self._userargs.vm_name:
            for e in consoles:
                if self._userargs.vm_name == e['vm']:
                    entry = e
                    break
            else:
                raise UserVisibleRuntimeError(
                    _("VM with name '{vm}' is unavailable").format(
                        vm=self._userargs.vm_name,
                    )
                )
        elif len(consoles) == 1:
            entry = consoles[0]
        else:
            menu = self._config.get('proxy', 'console_menu_title')
            if not menu:
                menu = _('Available Serial Consoles:\n')
            for i, e in enumerate(consoles):
                menu += '{index:02} {vm}[{vmid}]\n'.format(
                    index=i,
                    vmid=e['vmid'],
                    vm=e['vm'],
                )
            menu += 'SELECT> '

            while not entry:
                sys.stdout.write(menu)
                sys.stdout.flush()
                l = sys.stdin.readline()
                if not l:
                    raise UserVisibleRuntimeError('EOF')
                l = l.rstrip('\r\n')
                if l == 'exit':
                    raise UserExit()
                try:
                    i = int(l)
                    if i < 0 or i >= len(consoles):
                        sys.stderr.write(_('Invalid selection\n'))
                    else:
                        entry = consoles[i]
                except ValueError:
                    sys.stderr.write(_('Invalid selection\n'))

        self.logger.debug('Reading CA key')
        with open(os.path.join(config.pkgpkidir, 'ca.pub')) as f:
            cakey = f.read().decode('utf-8').rstrip('\n')

        self.logger.debug('Creating known_hosts')
        fd, known_hosts = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as f:
            f.write(
                '@cert-authority {host},{alias} {key}'.format(
                    host=entry['host'],  # openssh bug (principal)
                    alias=self._config.get(
                        'proxy',
                        'ovirt_vmconsole_host_principal'
                    ),
                    key=cakey,
                )
            )

        self.logger.debug('Cleanup daemon')

        def delayedUnlink(timeout, name):
            time.sleep(timeout)
            os.unlink(name)

        utils.ProcessUtils().simpleDaemon(
            delayedUnlink,
            timeout=self._config.getint('proxy', 'known_hosts_close_delay'),
            name=known_hosts,
        )

        self.logger.info(
            _(
                "Opening console '{console}@{host}' on behalf of "
                "'{entity}'[{entityid}]"
            ).format(
                host=entry['host'],
                console=entry['console'],
                entityid=self._args.entityid,
                entity=self._args.entity,
            )
        )

        cmd = self._config.get('proxy', 'console_attach').format(
            host=entry['host'],
            console=entry['console'],
            entityid=self._args.entityid,
            entity=self._args.entity,
            known_hosts_file=known_hosts,
        )
        self.logger.debug('Executing: %s', cmd)
        os.execv(
            self._config.get('proxy', 'shell'),
            [
                self._config.get('proxy', 'shell'),
                '-c', cmd,
            ],
        )
        raise RuntimeError('Cannot execute ssh')

    def doList(self):
        if self._userargs.format == 'plain':
            for entry in self._consoles['consoles']:
                sys.stdout.write(
                    '{vmid}\t{vm}\n'.format(
                        vmid=entry['vmid'],
                        vm=entry['vm'],
                    )
                )
        elif self._userargs.format == 'json':
            sys.stdout.write(
                '%s\n' % (
                    json.dumps(
                        self._consoles,
                        sort_keys=True,
                        indent=4,
                    )
                )
            )

    def parse_args(self, cmdline):
        parser = argparse.ArgumentParser(
            prog=self.NAME,
            description=_('oVirt VM console proxy shell'),
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help=_('enable debug log'),
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

        acceptParser = subparsers.add_parser(
            'accept',
            help=_('accept to console'),
        )
        acceptParser.add_argument(
            '--entityid',
            required=True,
            help=_('entity id'),
        )
        acceptParser.add_argument(
            '--entity',
            help=_('entity name'),
        )
        acceptParser.set_defaults(
            func=lambda: self.doAccept(),
        )

        args = parser.parse_args(cmdline)
        if not args.entity:
            args.entity = args.entityid

        return args

    def parse_user_args(self, cmdline):
        parser = argparse.ArgumentParser(
            prog=self.NAME,
            description=_('oVirt VM console proxy shell'),
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help=_('enable debug log'),
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
            help=_('connect to console [default]'),
        )
        connectParser.add_argument(
            '--vm-id',
            help=_('VM unique id to use'),
        )
        connectParser.add_argument(
            '--vm-name',
            help=_('VM name to use'),
        )
        connectParser.set_defaults(
            func=lambda: self.doConnect(),
        )

        listParser = subparsers.add_parser(
            'list',
            help=_('list consoles'),
        )
        listParser.add_argument(
            '--format',
            choices=[
                'plain',
                'json',
            ],
            default='plain',
            help=_('output format [%(default)s]'),
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
            self._userargs = self.parse_user_args(
                shlex.split(os.environ.get('SSH_ORIGINAL_COMMAND', 'connect'))
            )

            if (
                self._config.getboolean('proxy', 'debug') or
                self._args.debug or
                self._userargs.debug
            ):
                logging.getLogger(base.Base.LOG_PREFIX).setLevel(logging.DEBUG)

            self.logger.debug(
                '%s: %s-%s (%s)',
                self.NAME,
                config.PACKAGE_NAME,
                config.PACKAGE_VERSION,
                config.LOCAL_VERSION,
            )
            self.logger.debug(
                (
                    'argv=%s SSH_ORIGINAL_COMMAND=%s '
                    'args=%s userargs=%s config=%s'
                ),
                sys.argv,
                os.environ.get('SSH_ORIGINAL_COMMAND'),
                self._args,
                self._userargs,
                self._config,
            )
            self.validations()
            self._args.func()
            self._userargs.func()
            ret = 0
        except (UserExit, KeyboardInterrupt):
            pass
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
