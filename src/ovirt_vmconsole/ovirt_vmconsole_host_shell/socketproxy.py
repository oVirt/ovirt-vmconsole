#
# Copyright 2016-2017 Red Hat, Inc.
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

import errno
import fcntl
import os
import select
import signal
import socket
import sys
import termios
import tty


from ..common import base


class Proxy(base.Base):

    _socket = None
    _oldattr = []
    _oldfl = []
    _oldsignals = []

    def _trace(self, *args):
        if self._dotrace:
            self.logger.debug(*args)

    def __init__(
        self,
        socket,
        timeout=-1,
        bufsize=1024,
        trace=False,
    ):
        super(Proxy, self).__init__()

        self._socketname = socket
        self._timeout = timeout
        self._bufsize = bufsize
        self._dotrace = trace

        self.logger.debug(
            "start socket='%s' timeout=%s bufsize=%s",
            self._socketname,
            self._timeout,
            self._bufsize,
        )

    def __enter__(self):
        try:
            for s in (signal.SIGPIPE, signal.SIGHUP, signal.SIGINT):
                self._oldsignals += (
                    (
                        s,
                        signal.signal(s, signal.SIG_IGN),
                    ),
                )

            self.logger.debug('opening socket')
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.connect(self._socketname)
            self._socket.setblocking(False)

            self.logger.debug('setup stdin/stdout')
            sys.stdin.flush()
            sys.stdout.flush()

            try:
                self._oldattr += (
                    (
                        sys.stdin,
                        termios.tcgetattr(sys.stdin.fileno()),
                    ),
                )
                tty.setraw(sys.stdin.fileno())
            except Exception:
                # not tty
                pass

            for x in (sys.stdin, sys.stdout):
                fl = fcntl.fcntl(x.fileno(), fcntl.F_GETFL)
                self._oldfl += ((x, fl),)
                fcntl.fcntl(x.fileno(), fcntl.F_SETFL, fl | os.O_NDELAY)

        except Exception:
            self.logger.debug('initialization error', exc_info=True)
            self.__exit__(None, None, None)
            raise

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug('cleanup')

        if self._socket is not None:
            self._socket.close()
            self._socket = None

        for x in self._oldfl:
            try:
                fcntl.fcntl(x[0].fileno(), fcntl.F_SETFL, x[1])
            except Exception:
                self.logger.debug('fcntl failed', exc_info=True)
        self._oldfl = []

        for x in self._oldattr:
            try:
                termios.tcsetattr(x[0].fileno(), termios.TCSAFLUSH, x[1])
            except Exception:
                self.logger.debug('tcsetattr failed', exc_info=True)
        self._oldattr = []

        for x in self._oldsignals:
            signal.signal(x[0], x[1])
            self._oldsignals = []

    def run(self):
        from_socket = b''
        to_socket = b''
        stdin_closed = False
        stdout_closed = False
        socket_closed = False
        timeout = False
        while True:
            self._trace(
                (
                    'timeout=%s stdin_closed=%s stdout_closed=%s '
                    'socket_closed=%s len(to_socket)=%s len(from_socket)=%s'
                ),
                timeout,
                stdin_closed,
                stdout_closed,
                socket_closed,
                len(to_socket),
                len(from_socket),
            )
            if timeout:
                self.logger.debug('exit due to timeout')
                break
            if stdin_closed and len(to_socket) == 0:
                self.logger.debug('exit due to stdin closed')
                break
            if socket_closed and len(from_socket) == 0:
                self.logger.debug('exit due to socket closed')
                break

            p = select.poll()
            if not stdin_closed:
                p.register(
                    sys.stdin.fileno(),
                    select.POLLIN if (
                        len(to_socket) < self._bufsize and
                        not socket_closed
                    ) else 0,
                )
            if not stdout_closed:
                p.register(
                    sys.stdout.fileno(),
                    select.POLLOUT if len(from_socket) > 0 else 0
                )
            if not socket_closed:
                p.register(
                    self._socket.fileno(),
                    (
                        (
                            select.POLLIN if (
                                len(from_socket) < self._bufsize and
                                not stdout_closed
                            ) else 0
                        ) |
                        (
                            select.POLLOUT if len(to_socket) > 0 else 0
                        )
                    )
                )

            self._trace('poll')
            r = p.poll(self._timeout)
            if not r:
                timeout = True
            for x in r:
                if x[0] == sys.stdin.fileno():
                    if (x[1] & select.POLLIN) != 0:
                        self._trace('poll: stdin read')
                        buf = os.read(x[0], self._bufsize - len(to_socket))
                        if len(buf) == 0:
                            stdin_closed = True
                        else:
                            to_socket += buf
                    elif (x[1] & (select.POLLERR | select.POLLHUP)) != 0:
                        self._trace('poll: stdin err')
                        if len(to_socket) < self._bufsize:
                            stdin_closed = True
                if x[0] == sys.stdout.fileno():
                    if (x[1] & select.POLLOUT) != 0:
                        self._trace('poll: stdout write')
                        try:
                            from_socket = from_socket[
                                os.write(x[0], from_socket):
                            ]
                        # TODO: we should use BrokenPipeError once
                        # we can drop compatibility with python2
                        except EnvironmentError as e:
                            if e.errno != errno.EPIPE:
                                raise
                            stdout_closed = True
                    elif (x[1] & (select.POLLERR | select.POLLHUP)) != 0:
                        self._trace('poll: stdout err')
                        stdout_closed = True
                if x[0] == self._socket.fileno():
                    if (x[1] & select.POLLOUT | select.POLLIN) != 0:
                        if (x[1] & select.POLLOUT) != 0:
                            self._trace('poll: socket write')
                            try:
                                to_socket = to_socket[
                                    os.write(x[0], to_socket):
                                ]
                            # TODO: we should use BrokenPipeError once
                            # we can drop compatibility with python2
                            except EnvironmentError as e:
                                if e.errno != errno.EPIPE:
                                    raise
                                socket_closed = True
                        if (x[1] & select.POLLIN) != 0:
                            self._trace('poll: socket read')
                            buf = os.read(
                                x[0],
                                self._bufsize - len(from_socket),
                            )
                            if len(buf) == 0:
                                socket_closed = True
                            else:
                                from_socket += buf
                    elif (x[1] & (select.POLLERR | select.POLLHUP)) != 0:
                        self._trace('poll: socket err')
                        if len(from_socket) < len(from_socket):
                            socket_closed = True


def _main(socketname):
    with Proxy(socketname, trace=True) as p:
        p.run()


if __name__ == '__main__':
    import logging

    logging.basicConfig(filename='socketproxy.log', level=logging.DEBUG)

    if len(sys.argv[1:]) != 1:
        sys.stderr.write("usage: %s socketname\n" % sys.argv[0])
        sys.exit(1)

    _main(sys.argv[1])


# vim: expandtab tabstop=4 shiftwidth=4
