# coding: utf-8

from pathlib import Path
import unittest

from pymatgen.core.structure import Structure

from cuivesta.blocks import (VestaFile,
                             Title,
                             Cellp,
                             Struc,
                             Bound,
                             SBond,
                             Vectr,
                             Vectt,
                             Splan,
                             Style)

parent_dir = Path(__file__).parent


class VestaBlockTest(unittest.TestCase):
    def setUp(self) -> None:
        self.poscar = parent_dir / "POSCAR_BaTiO3"

    def test_title(self):
        title = Title("Ba1 Ti1 O3")
        actual = repr(title)
        expected = '#VESTA_FORMAT_VERSION 3.3.0\nTITLE\nBa1 Ti1 O3\n'
        self.assertEqual(actual, expected)

    def test_cellp(self):
        cellp = Cellp((3.992, 3.992, 3.992, 90.0, 90.0, 90.0))
        actual = repr(cellp)
        expected = 'CELLP\n3.992000 3.992000 3.992000 90.000000 90.000000 90.000000\n'
        self.assertEqual(actual, expected)

    def test_struc(self):
        poscar = parent_dir / "POSCAR_BaTiO3"
        s = Structure.from_file(poscar)
        struc = Struc(s)
        actual = repr(struc)
        expected = 'STRUC\n1 Ba Ba1  1.0  0.500000 0.500000 0.500000\n 0.0 0.0 0.0 \n2 Ti Ti2  1.0  0.000000 0.000000 0.000000\n 0.0 0.0 0.0 \n3 O O3  1.0  0.500000 0.000000 0.000000\n 0.0 0.0 0.0 \n4 O O4  1.0  0.000000 0.000000 0.500000\n 0.0 0.0 0.0 \n5 O O5  1.0  0.000000 0.500000 0.000000\n 0.0 0.0 0.0 \n 0 0 0 0 0 \n'
        self.assertEqual(actual, expected)

    def test_bound(self):
        bound = Bound((0, 2, 0, 2, 0, 2))
        actual = repr(bound)
        expected = 'BOUND\n0.000000 2.000000 0.000000 2.000000 0.000000 2.000000\n 0 0 0 0 0 \n'
        self.assertEqual(actual, expected)

    def test_sbond(self):
        sbond = SBond(('Ba', 'Ti', 'O'), {('Ti', 'O')})
        actual = repr(sbond)
        expected = 'SBOND\n1 Ti O 0.00000  \t2.707\t 0  1  1  0  1\n 0 0 0 0 \n'
        self.assertEqual(actual, expected)

    def test_vectr(self):
        vectr = Vectr({1: [0., 0., 0.],
                       2: [0., 0., -0.1],
                       3: [0., 0., 0.],
                       4: [0., 0., 0.],
                       5: [0., 0., 0.]})
        actual = repr(vectr)
        expected = 'VECTR\n1 0.000000 0.000000 0.000000\n1  0 0 0 0  0 0 0 0 0 \n 0 0 0 0 0 \n2 0.000000 0.000000 -0.100000\n2  0 0 0 0  0 0 0 0 0 \n 0 0 0 0 0 \n3 0.000000 0.000000 0.000000\n3  0 0 0 0  0 0 0 0 0 \n 0 0 0 0 0 \n4 0.000000 0.000000 0.000000\n4  0 0 0 0  0 0 0 0 0 \n 0 0 0 0 0 \n5 0.000000 0.000000 0.000000\n5  0 0 0 0  0 0 0 0 0 \n 0 0 0 0 0 \n'
        self.assertEqual(actual, expected)

    def test_vectt(self):
        vectt = Vectt(3)
        actual = repr(vectt)
        expected = 'VECTT\n1 0.5 1 1 1 2\n2 0.5 1 1 1 2\n3 0.5 1 1 1 2\n'
        self.assertEqual(actual, expected)

    def test_splan(self):
        poscar = parent_dir / "POSCAR_BaTiO3"
        s = Structure.from_file(poscar)
        splan = Splan(s, [[1, 0, 0, 3.0], [1, 1, 1]])
        actual = repr(splan)
        expected = 'SPLAN\n1 1.000000 0.000000 0.000000 3.000000 255 0 255 80\n2 1.000000 1.000000 1.000000 0.908517 255 0 255 80\n  0   0   0   0\n'
        self.assertEqual(actual, expected)

    def test_style(self):
        style = Style({"amplitude": 5.0,
                       "atoms": "ionic"})
        actual = repr(style)
        expected = 'STYLE\nVECTS  5.0\nUCOLP \n 0  2  3.000   0   0   0\nATOMS  1  0  1\n'
        self.assertEqual(actual, expected)

    def test_vesta_file(self):
        poscar = parent_dir / "POSCAR_BaTiO3"
        poscar_vesta = parent_dir / "POSCAR_BaTiO3.vesta"
        s = Structure.from_file(poscar)
        amplitude = 1.0 * ((s.volume / s.num_sites) ** 1 / 3)
        style_dict = {"amplitude": amplitude, "atoms": "atomic"}
        vf = VestaFile(s, styles=style_dict)
        actual = repr(vf)
        with open(poscar_vesta, 'r') as expected_file:
            expected = expected_file.read()
        self.assertEqual(actual, expected)
