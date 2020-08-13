# coding: utf-8

import unittest
from argparse import Namespace

from cuivesta import main


class CuiVestaMainTest(unittest.TestCase):
    def test_default_args(self):
        actual = main.parser.parse_args([])
        expected = Namespace(all_sites=False,
                             amplitude=1.0,
                             atoms='atomic',
                             bonds=None,
                             boundary='0 1 0 1 0 1',
                             centering=None,
                             defect=False,
                             diff=False,
                             filename=None,
                             planes=None,
                             poscar='POSCAR',
                             vacancy=False,
                             vectors=None)
        self.assertEqual(actual, expected)

