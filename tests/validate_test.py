from ovirt_vmconsole.common import validate

import unittest


class TestConsoleList(unittest.TestCase):

    def setUp(self):
        self.out = {
            'version': 1,
            'content': 'console_list',
            'consoles': [],
        }

    def test_bad_version(self):
        self.out['version'] = 0
        self.assertInvalid()

    def test_bad_content(self):
        self.out['content'] = 'something else'
        self.assertInvalid()

    def test_missing_version(self):
        del self.out['version']
        self.assertInvalid()

    def test_missing_content(self):
        del self.out['content']
        self.assertInvalid()

    def test_reorder_already_ordered(self):
        cons = [
            {'vmid': 1, 'vm': 'c'},
            {'vmid': 2, 'vm': 'a'},
            {'vmid': 3, 'vm': 'b'},
        ]
        expected = [
            {'vmid': 2, 'vm': 'a'},
            {'vmid': 3, 'vm': 'b'},
            {'vmid': 1, 'vm': 'c'},
        ]
        data = dict(self.out)
        data['consoles'] = cons
        consoles = validate.console_list(data)
        self.assertEquals(consoles['consoles'], expected)

    def test_reorder_empty(self):
        data = dict(self.out)
        consoles = validate.console_list(data)
        self.assertEquals(consoles, self.out)
        self.assertEquals(consoles['consoles'], [])

    def test_reorder_does_not_change_other_keys(self):
        cons = [
            {'vmid': 1, 'vm': 'a'},
            {'vmid': 2, 'vm': 'b'},
            {'vmid': 3, 'vm': 'c'},
        ]
        data = dict(self.out)
        data['consoles'] = cons
        consoles = validate.console_list(data)
        del consoles['consoles']
        del self.out['consoles']
        self.assertEquals(consoles, self.out)

    def assertInvalid(self):
        self.assertRaises(RuntimeError,
                          validate.console_list,
                          self.out)
