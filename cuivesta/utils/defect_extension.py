# coding: utf-8

from pymatgen.core.structure import Structure

from pydefect.analysis.defect import Defect
from pydefect.core.defect_entry import DefectEntry
from pydefect.analysis.defect_structure import DefectStructure
from pydefect.util.structure_tools import get_displacements


def defect_entry_loader(s: Structure, filename="defect_entry.json"):
    defect_entry = DefectEntry.load_json(filename)
    print(f"<vesta_io>: defect_entry.json found.")
    return SDefect(s, defect_entry)


def defect_loader():
    defect = Defect.load_json("defect.json")
    print(f"<vesta_io>: defect.json found.")
    return DefectStructure.from_defect(defect)


class SDefect:
    """
    This is simplified version of Defect class.
    Reconstructing from DefectEntry.
    SDefect excludes information related to electronic structure.
    """
    def __init__(self,
                 final_structure: Structure,
                 defect_entry: DefectEntry):
        de = defect_entry
        # self.initial_structure = de.initial_structure
        self.final_structure = final_structure
        self.defect_center = de.defect_center_coords
        self.neighboring_sites = de.neighboring_sites
        self.displacements = get_displacements(self.final_structure,
                                               de.initial_structure,
                                               de.defect_center_coords)

    def __repr__(self):
        outs = [f"final structure: {self.final_structure}",
                "",
                f"defect_center: {self.defect_center}",
                f"neighboring sites: {self.neighboring_sites}",
                f"displacements: {self.displacements}"]
        return "\n".join(outs)


def add_vacancy_to_structure(s: Structure, d: Defect or SDefect) -> Structure:
    """ Load atomic coordinates: [x.xx(float), x.xx. x.xx] """
    # vacancy_notation = " XX"
    vacancy_notation = "X"  # will be interpreted as dummy specie "X0+"
    vac_position = d.defect_center
    s.append(vacancy_notation, vac_position)
    return s


def replace_dummy_to_xx(target_str: str) -> str:
    return target_str.replace("X0+", "XX", -1)


def defect_induced_displacement_vectors(defect: DefectStructure or SDefect,
                                        all_site: bool) -> dict:
    """
    Args:
        defect (DefectStructure or SDefect):
        all_site(bool) : flag to show all sites
    Return:
        vectors(dict):
    """
    displacement_vectors = defect.displacements["displacement_vectors"]
    vectors_dict = {key: val for key, val in enumerate(displacement_vectors, 1)}
    if all_site:
        visible_vectors = vectors_dict
    else:
        visible_sites = defect.neighboring_sites
        visible_vectors = {ns+1: vectors_dict[ns+1] for ns in visible_sites}
    return visible_vectors

