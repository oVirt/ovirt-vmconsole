from ovirt_vmconsole.common import utils

from contextlib import contextmanager
import io
import platform
import sys
import unittest


def _py2():
    ver = platform.python_version_tuple()
    return ver[0] == '2'


@contextmanager
def replace_io(new_stdin, new_stdout):
    old_stdin, old_stdout = sys.stdin, sys.stdout
    try:
        sys.stdin, sys.stdout = new_stdin, new_stdout
        yield
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout


class TestConsoleSelect(unittest.TestCase):

    def setUp(self):
        self.consoles = (
            {
                'vmid': 'vm0',
                'vm': 'test-vm-0',
            },
            {
                'vmid': 'vm1',
                'vm': 'test-vm-1',
            }
        )

    def test_menu_output(self):
        menu = ''
        new_stdin = io.StringIO(u'0\n')
        new_stdout = io.BytesIO() if _py2() else io.StringIO()

        with replace_io(new_stdin, new_stdout):
            entry = utils.selectConsole(menu, self.consoles)

        expected = """00 test-vm-0[vm0]
01 test-vm-1[vm1]

Please, enter the id of the Serial Console you want to connect to.
To disconnect from a Serial Console, enter the sequence: <Enter><~><.>
SELECT> """
        self.assertEqual(new_stdout.getvalue(), expected)

    def test_select_console(self):
        menu = ''
        new_stdin = io.StringIO(u'0\n')
        new_stdout = io.BytesIO() if _py2() else io.StringIO()

        with replace_io(new_stdin, new_stdout):
            entry = utils.selectConsole(menu, self.consoles)

        self.assertEqual(entry, self.consoles[0])
