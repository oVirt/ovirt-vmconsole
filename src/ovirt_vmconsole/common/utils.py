import configparser
import gettext
import glob
import json
import logging
import logging.handlers
import os
import subprocess
import sys


from . import base


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-vmconsole')


def setupLogger(processName=None):
    class _MyFormatter(logging.Formatter):
        """Needed as syslog will truncate any lines after first."""

        def __init__(
            self,
            fmt=None,
            datefmt=None,
        ):
            logging.Formatter.__init__(self, fmt=fmt, datefmt=datefmt)

        def format(self, record):
            return logging.Formatter.format(self, record).replace('\n', ' | ')

    logger = logging.getLogger(base.Base.LOG_PREFIX)
    logger.propagate = False
    if os.environ.get('OVIRT_SERVICE_DEBUG', '0') != '0':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    try:
        h = logging.handlers.SysLogHandler(
            address='/dev/log',
            facility=logging.handlers.SysLogHandler.LOG_DAEMON,
        )
        h.setLevel(logging.DEBUG)
        h.setFormatter(
            _MyFormatter(
                fmt=(
                    '{process}[{pid}]: '
                    '%(levelname)s '
                    '%(message)s'
                ).format(
                    process=(
                        processName if processName
                        else os.path.splitext(os.path.basename(sys.argv[0]))[0]
                    ),
                    pid=os.getpid(),
                ),
            ),
        )
        logger.addHandler(h)
    except IOError:
        logging.debug('Cannot open syslog logger', exc_info=True)


def loadConfig(defaults, location):
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(
        (
            [defaults] +
            sorted(glob.glob(os.path.join(location, '*.conf')))
        ),
    )
    return parser


class ProcessUtils(base.Base):

    def simpleDaemon(self, main, *args, **kwargs):
        # Default maximum for the number of available file descriptors.
        MAXFD = 1024

        import resource  # Resource usage information.
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = MAXFD

        pid = os.fork()
        if pid == 0:
            try:
                os.chdir('/')
                os.setsid()
                for fd in range(0, maxfd):
                    try:
                        os.close(fd)
                    except OSError:
                        # ERROR, fd wasn't open to begin with (ignored)
                        pass

                os.open(os.devnull, os.O_RDWR)  # standard input (0)
                os.dup2(0, 1)  # standard output (1)
                os.dup2(0, 2)  # standard error (2)

                if os.fork() != 0:
                    os._exit(0)

                try:
                    main(*args, **kwargs)
                except:
                    import traceback
                    traceback.print_exc()
            finally:
                os._exit(1)

        pid, status = os.waitpid(pid, 0)

        if not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
            raise RuntimeError(_('Daemon not exited properly'))

    def executeJson(self, what, command):

        self.logger.debug(
            'Executing: %s',
            command,
        )
        p = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            self.logger.debug(
                '%s execution failed: rc=%s stdout=%s',
                what,
                p.returncode,
                stderr.decode('utf-8', 'replace') if stderr else '',
            )
            raise RuntimeError(
                _('{what} execution failed rc={rc}').format(
                    what=what,
                    rc=p.returncode,
                )
            )

        stdout = stdout.decode('utf-8', 'replace') if stdout else ''
        ret = json.loads(stdout)
        if not ret:
            self.logger.debug('stdout: %s', stdout)
            raise RuntimeError(
                _('{what} malformed output').format(
                    what=what,
                )
            )

        return ret


# vim: expandtab tabstop=4 shiftwidth=4
