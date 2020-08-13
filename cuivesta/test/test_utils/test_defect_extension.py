# coding: utf-8

from pathlib import Path
import unittest
import copy

from pymatgen.core.structure import Structure

from monty.serialization import loadfn

from cuivesta.utils.defect_extension import (SDefect,
                                             add_vacancy_to_structure,
                                             replace_dummy_to_xx,
                                             defect_induced_displacement_vectors)

parent_dir = Path(__file__).parent

defect_dir = parent_dir / "Va_Se1_0"


class DefectExtensionTest(unittest.TestCase):
    def test_sdefect(self):
        s = Structure.from_file(defect_dir / "CONTCAR-finish")
        de = loadfn(defect_dir / "defect_entry.json")
        sd = SDefect(s, de)
        print(sd)
        self.assertEqual(len(repr(sd)), 7462)

    def test_add_vacancy_to_structure(self):
        s = Structure.from_file(defect_dir / "CONTCAR-finish")
        s_copy = copy.deepcopy(s)
        de = loadfn(defect_dir / "defect_entry.json")
        sd = SDefect(s, de)
        add_vacancy_to_structure(s_copy, sd)
        self.assertEqual(len(s_copy), (len(s) + 1))

    def test_replace_dummy_to_xx(self):
        before_replace = '64 X0+ X0+64  1.0  0.250000 0.000000 0.000000'
        after_replace = replace_dummy_to_xx(before_replace)
        expected = '64 XX XX64  1.0  0.250000 0.000000 0.000000'
        self.assertEqual(after_replace, expected)

    def test_defect_induced_displacement_vectors(self):
        s = Structure.from_file(defect_dir / "CONTCAR-finish")
        de = loadfn(defect_dir / "defect_entry.json")
        sd = SDefect(s, de)
        actual = defect_induced_displacement_vectors(sd, False)
        expected = {1: [0.135544575238062, 0.1328422727231546, 0.13580732052833855],
                    9: [-0.12598887820809024, -0.1299492678927452, 0.1303079120927934],
                    17: [-0.15074928879118676, 0.1521800279487935, -0.14457211955231042],
                    25: [0.1220996954162643, -0.12347033953810893, -0.11863793386708155]}
        self.assertEqual(actual, expected)
