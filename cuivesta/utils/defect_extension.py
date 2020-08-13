# coding: utf-8
from typing import Union

import numpy as np

from pymatgen.core.structure import Structure
from monty.serialization import loadfn
from pymatgen.util.coord import pbc_shortest_vectors

try:
    from pydefect.core.defect_entry import DefectEntry
    _pydefect_version = "legacy"
except ImportError:
    from pydefect.input_maker.defect_entry import DefectEntry
    _pydefect_version = "current"


def get_displacements(final_structure: Structure,
                      initial_structure: Structure,
                      anchor_atom_index: int = None) -> list:
    """
    Note: this function is copied and modified
          from legacy pydefect.util.structure_tool.py
    """
    if anchor_atom_index:
        drift_frac_coords = final_structure[anchor_atom_index].frac_coords - \
                             initial_structure[anchor_atom_index].frac_coords
    else:
        drift_frac_coords = np.zeros(3)

    displacement_vectors = []
    for final_site, initial_site in zip(final_structure, initial_structure):
        displacement_vector, _ = \
            pbc_shortest_vectors(lattice=initial_structure.lattice,
                                 fcoords1=initial_site.frac_coords,
                                 fcoords2=(final_site.frac_coords
                                           - drift_frac_coords),
                                 return_d2=True)
        displacement_vectors.append(list(displacement_vector[0][0]))

    return displacement_vectors


class SDefect:
    """
    This is simplified version of Defect class.
    Reconstructing from DefectEntry.
    SDefect excludes information related to electronic structure.
    """
    def __init__(self,
                 final_structure: Structure,
                 defect_entry: DefectEntry):
        self.final_structure = final_structure
        self.de = defect_entry
        if _pydefect_version == "legacy":
            self._legacy_constructor()
        elif _pydefect_version == "current":
            self._current_constructor()

    def _legacy_constructor(self):
        self.defect_center = self.de.defect_center_coords
        self.neighboring_sites = self.de.neighboring_sites
        self.initial_structure = self.de.initial_structure

    def _current_constructor(self):
        self.defect_center = self.de.defect_center
        self.neighboring_sites = self.de.perturbed_site_indices
        self.initial_structure = self.de.structure

    @property
    def displacements(self, anchor_atom_index=None):
        disp_info = get_displacements(self.final_structure,
                                      self.initial_structure,
                                      anchor_atom_index)
        return {key: val for key, val in enumerate(disp_info, 1)}

    @classmethod
    def from_defect_entry(cls, s: Structure, filename="defect_entry.json"):
        defect_entry = loadfn(filename)
        print(f"<vesta_io>: defect_entry.json found.")
        return cls(s, defect_entry)

    def __repr__(self):
        outs = [f"final structure: {self.final_structure}",
                "",
                f"defect_center: {self.defect_center}",
                f"neighboring sites: {self.neighboring_sites}",
                f"displacements: {self.displacements}"]
        return "\n".join(outs)


def add_vacancy_to_structure(s: Structure, vac_position) -> Structure:
    """ Load atomic coordinates: [x.xx(float), x.xx. x.xx] """
    # vacancy_notation = " XX"
    vacancy_notation = "X"  # will be interpreted as dummy specie "X0+"
    s.append(vacancy_notation, vac_position)
    return s


def replace_dummy_to_xx(target_str: str) -> str:
    return target_str.replace("X0+", "XX", -1)


def defect_induced_displacement_vectors(sdefect: SDefect,
                                        all_site: bool) -> dict:
    """
    Args:
        sdefect: SDefect
        all_site(bool) : flag to show all sites
    Return:
        vectors(dict):
    """
    if all_site:
        visible_vectors = sdefect.displacements
    else:
        visible_sites = sdefect.neighboring_sites
        visible_vectors = {ns+1: sdefect.displacements[ns+1]
                           for ns in visible_sites}
    return visible_vectors

