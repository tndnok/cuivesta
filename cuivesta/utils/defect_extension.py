# coding: utf-8

from pymatgen.core.structure import Structure
from monty.serialization import loadfn

try:
    from pydefect.core.defect_entry import DefectEntry
    _pydefect_version = "legacy"
except ImportError:
    from pydefect.input_maker.defect_entry import DefectEntry
    _pydefect_version = "current"


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
        if _pydefect_version == "legacy":
            self._legacy_constructor(defect_entry)
        elif _pydefect_version == "current":
            self._current_constructor(defect_entry)

    def _legacy_constructor(self, de):
        self.defect_center = de.defect_center_coords
        self.neighboring_sites = de.neighboring_sites
        displacement_vectors =\
            self.final_structure.frac_coords - de.initial_structure.frac_coords
        self.displacements = {key: val.tolist() for key, val in
                              enumerate(displacement_vectors, 1)}

    def _current_constructor(self, de):
        self.defect_center = de.defect_center
        self.neighboring_sites = de.perturbed_site_indices
        displacement_vectors = \
            self.final_structure.frac_coords - de.structure.frac_coords
        self.displacements = {key: val.tolist() for key, val in
                              enumerate(displacement_vectors, 1)}

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

