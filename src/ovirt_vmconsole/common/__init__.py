#
# Copyright 2015 Red Hat, Inc.
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

import sys


def _pythonModulesCompat():
    """Rename modules to match python3 names."""
    if sys.version_info[0] >= 3:
        import builtins
        setattr(builtins, 'unicode', str)
    else:
        import ConfigParser
        sys.modules['configparser'] = ConfigParser
        import __builtin__
        sys.modules['builtins'] = __builtin__

        class COMPAT_BlockingIOError(OSError):
            pass

        setattr(__builtin__, 'BlockingIOError', COMPAT_BlockingIOError)


_pythonModulesCompat()


__all__ = []


# vim: expandtab tabstop=4 shiftwidth=4
