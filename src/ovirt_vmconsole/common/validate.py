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
# Refer to the README.md and COPYING files for full details of the license
#

import gettext
import operator


def console_list(out):
    if out.get('content') != 'console_list':
        raise RuntimeError(_('Invalid console list output'))
    if out.get('version') != 1:
        raise RuntimeError(_('Invalid console list version'))
    # sort consoles by vm name for userfriendliness
    consoles = out.pop('consoles', [])
    out['consoles'] = sorted(consoles, key=operator.itemgetter("vm"))
    return out


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-vmconsole')
