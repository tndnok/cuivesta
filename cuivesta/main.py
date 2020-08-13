#!/usr/bin/env python
# coding: utf-8

import argparse
import sys
from pathlib import Path

import numpy as np

from pymatgen.core.structure import Structure

import cuivesta.utils.defect_extension as dex
from cuivesta.blocks import VestaFile
from cuivesta.utils.func_tools import (
    structure_diff_vectors,
    make_visible_bond_set,
    make_plane_list,
    plane_option_parse,
    vector_option_parse,
    centering_atom,
    boundary_option_preparse)

# command line option
parser = argparse.ArgumentParser()
parser.add_argument(
    "-p", "--poscar", type=str, default="POSCAR",
    help="POSCAR file name.", metavar="FILE")
parser.add_argument(
    "-v", "--vectors", type=str, default=None,
    help="vector set to be visible.", metavar="FILE")
parser.add_argument(
    "--diff", type=str, default=False,
    help="2nd POSCAR file name for comparison.", metavar="FILE")
parser.add_argument(
    "--defect", action="store_true", default=False,
    help="show defect-induced displacements as vector "
         "(need defect.json or defect_entry.json)")
parser.add_argument(
    "--vacancy", action="store_true", default=False,
    help="add the vacancy site to be visible as XX element")
parser.add_argument(
    "--all_sites", action="store_true", default=False,
    help="force vectors at all sites to be visible")
parser.add_argument(
    "-m", "--amplitude", type=float, default=1.0,
    help="amount of displacement")
parser.add_argument(
    "-b", "--bonds", type=str, default=None, nargs="+",
    help="customize bonds to be visible")
parser.add_argument(
    "--atoms", type=str, default="atomic",
    help="customize radii of element: "
         "choose one from atomic, ionic, and vdw")
parser.add_argument(
    "--boundary", type=str, default="0 1 0 1 0 1",
    help="customize range of plot: " 
         "specify as 0 1 0 .. (x_min x_max y_min ..)")
parser.add_argument(
    "--centering", type=int, default=None,
    help="centering the specified atom: " 
         "specify atom index")
parser.add_argument(
    "--planes", type=str, default=None, nargs="+",
    help="specify index of plane: " 
         "e.g., '100' for hkl index or '100-3.0' for hkl-d "
         "-3 means d=3.0 A for inter-plane distance"
         "default d is determined by reciprocal_lattice.d_hkl() of pmg")
parser.add_argument(
    "-f", "--filename", type=str, default=None,
    help="output file name.", metavar="FILE")
# args = parser.parse_args()

# style_dict = {"amplitude": args.amplitude,
#               "atoms": args.atoms}


# WRITE *.vesta
def main():
    args = parser.parse_args()
    s = Structure.from_file(args.poscar)

    # manual vectors
    if args.diff and args.defect:
        print('diff and defect options are exclusive')
        sys.exit()

    vectors_dict = None
    if args.vectors:
        vectors_dict = vector_option_parse(args.vectors, s.num_sites)

    if args.diff:
        s1 = s
        s2 = Structure.from_file(args.diff)
        vectors_dict = structure_diff_vectors(s1, s2)

    # defect extension
    defect = None
    if args.defect:
        defect = dex.SDefect.from_defect_entry(s)
        vectors_dict = dex.defect_induced_displacement_vectors(defect,
                                                               args.all_sites)
    if args.vacancy:
        if defect is None:
            defect = dex.SDefect.from_defect_entry(s)
        if isinstance(defect.defect_center, int):
            raise TypeError("defect is not vacancy")
        dex.add_vacancy_to_structure(s, defect.defect_center)

    # plane
    plane_list = None
    if args.planes:
        planes = plane_option_parse(args.planes, path=Path.cwd())
        plane_list = [make_plane_list(plane) for plane in planes]

    # bond
    if args.bonds:
        bond_set = make_visible_bond_set(args.bonds)
    else:
        bond_set = args.bonds

    # boundary
    boundary = boundary_option_preparse(args.boundary)
    if args.centering is not None:  # To use 0 index
        center_site = s[args.centering-1]  # pmg Site object
        center_frac_coord = center_site.frac_coords
        shift = centering_atom(center_frac_coord, boundary)
    else:
        shift = np.array([0, 0, 0, 0, 0, 0])
    boundary = boundary + shift

    # misc
    amplitude = args.amplitude * ((s.volume/s.num_sites)**1/3)
    style_dict = {"amplitude": amplitude,
                  "atoms": args.atoms}

    vf = VestaFile(s, bond_set, vectors_dict, boundary, plane_list, style_dict)
    filename = args.filename or args.poscar
    vf.write_file(filename=filename)


if __name__ == "__main__":
    main()
