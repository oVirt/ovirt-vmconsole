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
