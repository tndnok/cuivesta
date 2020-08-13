# coding: utf-8

from typing import Union
from fractions import Fraction

import numpy as np

from pymatgen.core.structure import Structure, StructureError
# from utils.defect_json_generator import SDefect
from pathlib import Path

format_str = "{{:.{0}f}}".format(6)


def val_to_str_line(val_line: list or tuple) -> str:
    str_list = f'{" ".join([format_str.format(c) for c in val_line])}'
    return str_list


def structure_to_dict_for_vesta(s: Structure):
    dict_for_vesta = dict()
    dict_for_vesta["formula"] = s.composition.formula
    dict_for_vesta["cell_parameters"] = s.lattice.abc + s.lattice.angles
    dict_for_vesta["num_sites"] = s.num_sites
    # dict_for_vesta["composition"] = s.symbol_set
    # periodic table order
    dict_for_vesta["composition"] = tuple(s.composition.as_dict().keys())
    return dict_for_vesta


def structure_diff_vectors(s1: Structure, s2: Structure) -> dict:
    """
    generate vesta vector object from diff between POSCAR1 and POSCAR2
     as ([[x.xx(float), x.xx. x.xx], [x.xx, x.xx, x.xx],...])
    """
    if len(s1) != len(s2):
        raise StructureError("The number of atoms are different between two "
                             "input structures.")
    # elif s1.lattice != s2.lattice:
    #     logger.warning("The lattice constants are different between two input"
    #                    "structures. Anchoring the farthest atom is switched "
    #                    "off as it bears erroneous result.")
    #     anchor_atom_index = None
    displacement_vectors = s1.frac_coords - s2.frac_coords
    vectors_dict = {key: val for key, val in enumerate(displacement_vectors, 1)}
    return vectors_dict


def make_visible_bond_set(pairs: list) -> set:
    """
    :arg string pairs: e.g., "Ti-O"
    :return: Return set of bonds
    """
    return set(tuple(bond.split("-")) for bond in pairs)


def make_plane_list(plane: str) -> list:
    hkl = plane.split('-')[0]
    d = plane.split('-')[-1]
    hkl_list = [float(_) for _ in hkl]
    if not hkl == d:
        hkl_list.append(float(d))
    return hkl_list


def plane_option_parse(cl_args: list, path: Path) -> list:
    current_path = path
    str_args = []
    for cl_arg in cl_args:
        assume_file_path = current_path / cl_arg
        # allow only *.txt file as args of --plane option
        if Path.exists(assume_file_path) and (cl_arg.split(".")[-1] == "txt"):
            with open(str(assume_file_path), "r") as file:
                str_args += file.read().split()
        else:  # do nothing if args is not *txt file
            str_args.append(cl_arg)
    return str_args


def vector_option_parse(arg: str, num_sites: int) -> dict:
    with open(arg, "r") as vct_file:
        vectors_list = [vct.strip().split() for vct in vct_file.readlines()]
    # add vectors for all sites
    if (len(vectors_list) == num_sites) and (len(vectors_list[0]) == 3):
        vectors_dict = {_i: [float(_) for _ in vct]
                        for _i, vct in enumerate(vectors_list, 1)}
    # add vectors for specified site
    elif len(vectors_list[0]) == 4:
        vectors_dict = {int(vct[0]): [float(_) for _ in vct[1:]]
                        for vct in vectors_list}
    else:
        raise StructureError("The number of vectors are different from number"
                             "of atoms.")
    return vectors_dict


def centering_atom(atom_at_center: np.ndarray,
                   scale_of_range: np.ndarray) -> np.ndarray:
    center_of_plot = (scale_of_range.reshape(3, 2)[:, 0]
                      + scale_of_range.reshape(3, 2)[:, 1]) / 2.0
    total_shift = atom_at_center - center_of_plot
    return np.array([total_shift[0], total_shift[0],
                     total_shift[1], total_shift[1],
                     total_shift[2], total_shift[2]])


def boundary_option_preparse(sys_arg: str,
                             base_boundary: list = None) -> np.ndarray:
    base_boundary = base_boundary or [0, 1, 0, 1, 0, 1]
    boundary = sys_arg.split()
    if len(boundary) == 6:
        return np.array([float(_) for _ in boundary])
    elif len(boundary) == 1:
        return np.array(base_boundary) * float(Fraction(boundary[0]))




