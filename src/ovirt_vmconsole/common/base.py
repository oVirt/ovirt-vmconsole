import logging


class Base(object):
    LOG_PREFIX = 'ovirt-vmconsole'

    @property
    def logger(self):
        return self._logger

    def __init__(self):
        self._logger = logging.getLogger(
            '%s.%s' % (
                self.LOG_PREFIX,
                self.__class__.__name__,
            )
        )


# vim: expandtab tabstop=4 shiftwidth=4
