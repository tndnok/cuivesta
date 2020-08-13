# coding: utf-8

from pathlib import Path
import unittest

import numpy as np

from numpy import array, testing

from pymatgen.core.structure import Structure

from cuivesta.utils.func_tools import (val_to_str_line,
                                       structure_to_dict_for_vesta,
                                       make_visible_bond_set,
                                       make_plane_list,
                                       plane_option_parse,
                                       vector_option_parse,
                                       structure_diff_vectors,
                                       centering_atom,
                                       boundary_option_preparse)

parent_dir = Path(__file__).parent


class FuncToolsTest(unittest.TestCase):
    def test_val_to_str_line(self):
        actual = val_to_str_line((3.992, 3.992, 3.992, 90.0, 90.0, 90.0))
        expected = '3.992000 3.992000 3.992000 90.000000 90.000000 90.000000'
        self.assertEqual(actual, expected)

    def test_structure_to_dict_for_vesta(self):
        s = Structure.from_file("POSCAR_BaTiO3")
        actual = structure_to_dict_for_vesta(s)
        expected = {'formula': 'Ba1 Ti1 O3',
                    'cell_parameters': (3.9928776341656214,
                                        3.9928776341656214,
                                        3.9928776341656214,
                                        90.0,
                                        90.0,
                                        90.0),
                    'num_sites': 5,
                    'composition': ('Ba', 'Ti', 'O')}
        self.assertEqual(actual, expected)

    def test_make_visible_bond_set(self):
        actual = make_visible_bond_set(["Ti-O"])
        expected = {("Ti", "O")}
        self.assertEqual(actual, expected)

    def test_make_plane_list(self):
        actual = make_plane_list("111-3.3")
        expected = [1, 1, 1, 3.3]
        self.assertEqual(actual, expected)

    def test_multi_plane_option_parse(self):
        path = parent_dir
        actual = plane_option_parse(["test_plane.txt", "111"], path)
        expected = ['111', '222-4.0', '111']
        self.assertEqual(actual, expected)

    def test_multi_vector_option_parse_1(self):
        path = parent_dir / "test_vector_1.txt"
        actual = vector_option_parse(path, 2)
        expected = {2: [1.0, 1.0, 1.0], 3: [1.0, 0.0, 0.0]}
        self.assertEqual(actual, expected)

    def test_multi_vector_option_parse_2(self):
        path = parent_dir / "test_vector_2.txt"
        actual = vector_option_parse(path, 2)
        expected = {1: [3.0, 3.0, 3.0], 2: [2.0, 2.0, 2.0]}
        self.assertEqual(actual, expected)


# using numpy.testing
def test_structure_diff_vectors():
    test_dir = parent_dir / "diff"
    s1 = Structure.from_file(test_dir / "POSCAR1")
    s2 = Structure.from_file(test_dir / "POSCAR2")
    actual = structure_diff_vectors(s1, s2)
    expected = {1: array([0., 0., 0.]),
                2: array([0., 0., -0.1]),
                3: array([0., 0., 0.]),
                4: array([0., 0., 0.]),
                5: array([0., 0., 0.])}
    for _key in actual:
        testing.assert_array_equal(actual[_key], expected[_key])


def test_centering_atom():
    actual = centering_atom(np.array([0.25, 0.25, 0.25]),
                            np.array([0, 2, 0, 2, 0, 2]))
    expected = np.array([-0.75, -0.75, -0.75, -0.75, -0.75, -0.75])
    testing.assert_array_equal(actual, expected)


def test_boundary_option_preparse1():
    actual = boundary_option_preparse("1/2")
    expected = np.array([0.0, 0.5, 0.0, 0.5, 0.0, 0.5])
    testing.assert_array_equal(actual, expected)


def test_boundary_option_preparse2():
    actual = boundary_option_preparse("0 2 0 2 0 2")
    expected = np.array([0.0, 2.0, 0.0, 2.0, 0.0, 2.0])
    testing.assert_array_equal(actual, expected)


