# coding: utf-8

import itertools
from collections import OrderedDict
import copy
from typing import Union, Optional, List
# from abc import ABC, abstractmethod

from pymatgen.core.structure import Structure

from cuivesta.template.vesta.sbond_default_dict import sbond_default_dict
# from cuivesta.template.vesta.sbond_middle_dict import sbond_middle_dict
# from cuivesta.template.vesta.sbond_large_dict import sbond_large_dict
from cuivesta.utils.func_tools import (val_to_str_line,
                                       structure_to_dict_for_vesta)
from cuivesta.options import actual_options


def replace_dummy_to_xx(target_str: str) -> str:
    return target_str.replace("X0+", "XX", -1)


class VestaFile:
    """construct VESTA file object and from pymatgen Structure instance"""

    def __init__(self, structure: Structure,
                 visible_bond: set = None,
                 vectors: dict = None,
                 boundary: Optional[Union[list, tuple]] = None,
                 planes: list = None,
                 styles: dict = None):
        """
        Args:
            structure: pymatgen Structure instance
            visible_bond: e.g., {('Ba', 'O'), ('Ti', 'O')}
                          if None is set, sbond_default_dict will be used
            vectors: e.g., {1: [[x.xx], [x.xx], [x.xx]], 2:[[x.xx], ..], ..}
            boundary: control range of plot
                      e.g., "-0.5 0.5 -0.5 0.5 -0.5 0.5" means center to origin
            styles: control options such as radii of element
        """
        s = copy.deepcopy(structure)
        d = structure_to_dict_for_vesta(s)
        self.blocks = OrderedDict()
        self.blocks["title"] = Title(d["formula"])
        self.blocks["cellp"] = Cellp(d["cell_parameters"])
        self.blocks["struc"] = Struc(s)
        if boundary is not None:
            self.blocks["boundary"] = Bound(boundary)
        self.blocks["sbond"] = SBond(d["composition"], visible_bond)
        if vectors is not None:
            # default_vct_size = s.volume/s.num_sites**1/3
            self.blocks["vectr"] = Vectr(vectors)
            self.blocks["vectt"] = Vectt(len(vectors))
        if planes is not None:
            self.blocks["splan"] = Splan(s, planes)
        if styles is not None:
            self.blocks["style"] = Style(styles)

    def __iter__(self):
        return self.blocks.values().__iter__()  # return iter(dict.values())

    def __repr__(self):
        outs = []
        for block in self.blocks.values():
            outs.append(repr(block))
        return "\n".join(outs)

    def write_file(self, filename: str):
        with open(filename + ".vesta", 'w') as poscar_vesta:
            poscar_vesta.write(repr(self))
        print(f"<vesta_io>: generated {filename}.vesta.")


class Title:
    """
    This is class object of TITLE block in *.vesta files.
    """

    vesta_version = "#VESTA_FORMAT_VERSION 3.3.0"
    header = "TITLE"

    def __init__(self, formula: str):
        """
        Args:
            formula: e.g., 'Ba1 Ti1 O3'
        """
        self.formula = formula

    def __repr__(self):
        outs = [f'{self.vesta_version}',
                f'{self.header}',
                f'{self.formula}',
                f'']
        return "\n".join(outs)


class Cellp:
    """
    This is class object of CELLP block in *.vesta files.
    # e.g.) 3.992878   3.992878   3.992878  90.000000  90.000000  90.000000
    """

    header = "CELLP"

    def __init__(self, cell_parameters: tuple):
        """
        Args:
            cell_parameters: e.g., (3.992,3.992, 3.992, 90.0, 90.0, 90.0)
        :param cell_parameters:
        """
        self.cell_parameters = cell_parameters

    def __repr__(self):
        cellp = val_to_str_line(self.cell_parameters)
        outs = [f'{self.header}',
                f'{cellp}',
                f'']
        return "\n".join(outs)


class Struc:
    """
    This is class object of STRUC block in *.vesta files.
    e.g. "index" "element" "element+index" + "occupation" + "coords"
          1       Ba        Ba1               1.0000         0.500  0.500  0.500
    """

    header = "STRUC"
    separator = " 0 0 0 0 0 "
    zero_coord = " 0.0 0.0 0.0 "

    def __init__(self, structure: Structure, occupation: int = 1.0):
        """
        Args:
            structure: pymatgen Structure instance
        """
        self.occupation = f" {occupation} "
        self.structure = structure

    def __repr__(self):
        coords = []
        for site, c in enumerate(self.structure, 1):
            specifies = f'{site} {c.species_string} ' \
                        f'{c.species_string}{site} {self.occupation} '
            coord = val_to_str_line(c.frac_coords)
            coords.append(specifies + coord)
            coords.append(self.zero_coord)
        # replace "X0+" (pmg dummy species) -> "XX" (vesta dummy species)
        str_coords = replace_dummy_to_xx('\n'.join(coords))
        outs = [f'{self.header}',
                f'{str_coords}',
                f'{self.separator}',
                f'']
        return replace_dummy_to_xx('\n'.join(outs))


class Bound:
    """control range of plot"""

    header = "BOUND"
    separator = " 0 0 0 0 0 "

    def __init__(self,
                 boundary: Optional[Union[tuple, list]] = (0, 1, 0, 1, 0, 1)):
        """

        Args:
            boundary (tuple or list): a_min, a_max, b_min, b_max, c_min, c_max
        """
        if len(boundary) != 6:
            raise ValueError("length of boundary must be 6")
        self.boundary = boundary

    def __repr__(self):
        outs = [f'{self.header}',
                f'{val_to_str_line(self.boundary)}',
                f'{self.separator}',
                f'']
        return "\n".join(outs)


class SBond:
    """
    This is class object of SBOND block in *.vesta files.
    e.g. "index" "element" "element+index" + "occupation" + "coords"
          1       Ba        Ba1               1.0000         0.500  0.500  0.500
    """

    header = "SBOND"
    separator = " 0 0 0 0 "

    def __init__(self, composition: tuple, user_define: set):
        """
        Args:
            composition: e.g., ('Ba', 'Ti', 'O')
            user_define: e.g., {('Ti', 'O')}
        """
        # pairs_in_composition = set(itertools.combinations(composition, 2))
        pairs_in_composition = \
            set(itertools.combinations_with_replacement(composition, 2))
        if not user_define:
            user_define = pairs_in_composition
        self.pairs_of_bond = sorted(pairs_in_composition & user_define)

    def __repr__(self):
        visible_bonds = []
        _idx = 1
        for _key in self.pairs_of_bond:
            if _key in sbond_default_dict:
                visible_bond = f'{_idx} {_key[0]} {_key[1]} ' \
                               f'{sbond_default_dict[_key]}'
                visible_bonds.append(visible_bond)  # + '\n'
                _idx += 1
        str_visible_bonds = '\n'.join(visible_bonds)
        outs = [f'{self.header}',
                f'{str_visible_bonds}',
                f'{self.separator}',
                f'']
        return "\n".join(outs)


class Vectr:
    """
    This is class object of VECTR block in *.vesta files.
    VECTR (specify vector object)
    e.g)  1(vct_index)   -0.16519    0.00000    0.00000  <-- e.g., disp data
          1(atm_index)   0           0          0        <-- options
    """

    header = "VECTR"
    separator = " 0 0 0 0 0 "

    def __init__(self, vectors: dict):
        """
        Args:
            vectors (dict): dict of site index and vector.
                            e.g., {1: [[x.xx],[x.xx],[x.xx]], ..}
        """
        self.default_vct_options = " 0 0 0 0 "
        self.vectors = vectors

    def __repr__(self):
        vectors = []
        for _key in self.vectors:
            vector = f'{val_to_str_line(self.vectors[_key])}'
            option = f'{_key} {self.default_vct_options}'
            vectors.append(f'{_key} ' + vector)
            vectors.append(option + self.separator)
            vectors.append(self.separator)
        str_vectors = '\n'.join(vectors)
        outs = [f'{self.header}',
                f'{str_vectors}',
                f'']
        return "\n".join(outs)


class Vectt:
    """
    This is class object of VECTR block in *.vesta files.
    generate vesta vector object from differences between structures
     as ([[x.xx(float), x.xx. x.xx], [x.xx, x.xx, x.xx],...])
    """

    header = "VECTT"

    def __init__(self,
                 num_of_vectors: int,
                 size: float = 0.50,
                 color: str = "1 1 1"):
        """
        Args:
            num_of_vectors: number of vector objects
        """
        self.num_of_vectors = num_of_vectors
        self.size = size
        self.color = color  # default black
        # self.length = length
        self.type = 2

    def __repr__(self):
        vector_option = f"{self.size} {self.color} {self.type}"
        vector_types = []
        for _ in range(self.num_of_vectors):
            vector_types.append(f'{_ + 1} {vector_option}')
        str_vector_types = '\n'.join(vector_types)
        outs = [f'{self.header}',
                f'{str_vector_types}',
                f'']
        return "\n".join(outs)


class Splan:
    """
    This is class object of SPLAN block in *.vesta files.
    e.g. "index" "h" "k" "l" + "coords"
        1 1.000000E+00 1.000000E+00 1.000000E+00 3.92182 255   0 255 192
    """

    header = "SPLAN"
    footer = "  0   0   0   0"

    def __init__(self, s: Structure, hklds: List[list]):
        """
        Args:
            s: pymatgen Structure class
            hkls: list of h, k, l (reflection) index
        """
        hklds_copy = copy.deepcopy(hklds)
        for _hkl in hklds_copy:
            if len(_hkl) == 3:
                _hkl.append(s.lattice.reciprocal_lattice.d_hkl(_hkl))
        self.hklds = hklds_copy
        self.plane_color = "255 0 255 80"  # default pink
        # self.plane_color = "1 1 1 80"  # black

    def __repr__(self):
        splanes = []
        for _idx, hkld in enumerate(self.hklds, 1):
            splanes.append(f'{_idx} {val_to_str_line(hkld)} {self.plane_color}')
        str_splnes = '\n'.join(splanes)
        outs = [f'{self.header}',
                f'{str_splnes}',
                f'{self.footer}',
                f'']
        return "\n".join(outs)


class Style:
    """
    This is class object of STYLE block in *.vesta files.
    generate vesta vector object from differences between structures
     as ([[x.xx(float), x.xx. x.xx], [x.xx, x.xx, x.xx],...])
    """

    header = "STYLE"
    amp_prefix = "VECTS "
    atoms_prefix = "ATOMS "
    ucolp_prefix = "UCOLP \n"

    def __init__(self, styles: dict):
        """
        Args:
            styles: dict of optional style
        """
        self.amplitude = styles["amplitude"]
        self.atoms = styles["atoms"]
        # self.ucolp = styles["ucolp"]

    def __repr__(self):
        vct = f'{self.amp_prefix} {self.amplitude}'
        atom = f'{self.atoms_prefix} {actual_options[self.atoms]}'
        ucol = f'{self.ucolp_prefix} {actual_options["all_bold_cell"]}'
        outs = [f'{self.header}',
                f'{vct}',
                f'{ucol}',
                f'{atom}',
                f'']
        return "\n".join(outs)

