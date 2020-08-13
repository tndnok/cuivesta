# coding: utf-8

from pathlib import Path
import unittest
import copy

from pymatgen.core.structure import Structure

from pydefect.analysis.defect import Defect
from pydefect.core.defect_entry import DefectEntry

from cuivesta.utils.defect_extension import (SDefect,
                                             add_vacancy_to_structure,
                                             replace_dummy_to_xx,
                                             defect_induced_displacement_vectors)

parent_dir = Path(__file__).parent

defect_dir = parent_dir / "Va_O1_2"


class DefectExtensionTest(unittest.TestCase):
    def test_sdefect(self):
        s = Structure.from_file(defect_dir / "CONTCAR")
        de = DefectEntry.load_json(defect_dir / "defect_entry.json")
        sd = SDefect(s, de)
        print(sd)
        self.assertEqual(len(repr(sd)), 13773)

    def test_add_vacancy_to_structure(self):
        s = Structure.from_file(defect_dir / "CONTCAR")
        s_copy = copy.deepcopy(s)
        d = Defect.load_json(defect_dir / "defect.json")
        add_vacancy_to_structure(s_copy, d)
        self.assertEqual(len(s_copy), (len(s) + 1))

    def test_replace_dummy_to_xx(self):
        before_replace = '64 X0+ X0+64  1.0  0.250000 0.000000 0.000000'
        after_replace = replace_dummy_to_xx(before_replace)
        expected = '64 XX XX64  1.0  0.250000 0.000000 0.000000'
        self.assertEqual(after_replace, expected)

    def test_defect_induced_displacement_vectors(self):
        d = Defect.load_json(defect_dir / "defect.json")
        actual = defect_induced_displacement_vectors(d, False)
        expected = {1: [-0.16518775913396233, 0.0, 0.0],
                    5: [0.16518775913396233, 0.0, 0.0],
                    17: [0.0, 0.0, 0.16518775913396233],
                    18: [0.0, 0.0, -0.16518775913396233],
                    25: [0.0, 0.16518775913396233, 0.0],
                    27: [0.0, -0.16518775913396233, 0.0]}
        self.assertEqual(actual, expected)
