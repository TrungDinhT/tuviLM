from src.tuvi.tinh_ban import TinhBan
from src.tuvi.element.types import TYPE_DIA_CHI
from src.tuvi.database.star_composition import ElementComposition
from src.tuvi.transform import get_tam_hop, get_xung_chieu

# TODO : Must improve this
def search_element(tinhBan : TinhBan, element_name : str) -> TYPE_DIA_CHI:
    for position, cung in tinhBan.map_cung.items():
        list_sao_name = [ele.name for ele in cung.all_element]
        if element_name in list_sao_name:
            return position
    raise ValueError(f"Can not find {element_name}")

# TODO : should search on element name ?
def search_elements(tinhBan : TinhBan, list_search_names : set[str]) -> list[TYPE_DIA_CHI]:
    returned_position = []

    for position, cung in tinhBan.map_cung.items():
        list_elements_names = set([ele.name for ele in cung.all_element])
        if list_search_names & list_elements_names:
            returned_position.append(position)

    return returned_position


def check_composition(
    tinhBan : TinhBan,
    composition : ElementComposition
) -> bool:

    list_ele_positions = search_elements(tinhBan, composition.list_elements)

    if (target_position := composition.target_position):
        if target_position not in list_ele_positions:
            return False
        if (role := composition.role):
            for position, cung in tinhBan.map_cung.items():
                # TODO : Difficult to search for role position, should save in tinhban
                if cung.role == role:
                    position_role = position
                    break
            if position_role != target_position:
                return False

        considered_positions = [target_position]

        if composition.relation == "tam phuong":
            considered_positions += list(get_tam_hop(position_role))
        if composition.relation == "tu chinh":
            considered_positions += list(get_tam_hop(position_role)) + [get_xung_chieu(position_role)]

        return all(p in considered_positions for p in list_ele_positions)


    if (role := composition.role):
        for position, cung in tinhBan.map_cung.items():
            # TODO : Difficult to search for role position, should save in tinhban
            if cung.role == role:
                position_role = position
                break

        considered_positions = [position_role]

        if composition.relation == "tam phuong":
            considered_positions += list(get_tam_hop(position_role))
        if composition.relation == "tu chinh":
            considered_positions += list(get_tam_hop(position_role)) + [get_xung_chieu(position_role)]

        return all(p in considered_positions for p in list_ele_positions)
    else:
        if composition.relation == "cung":
            return len(list_ele_positions) == 1
        if composition.relation == "tam phuong":
            considered_position = [list_ele_positions[0], *get_tam_hop(list_ele_positions[0])]
            return all(p in considered_position for p in list_ele_positions)
        if composition.relation == "tu chinh":
            if len(list_ele_positions) != 4:
                return False
            for considered_position in list_ele_positions:
                if get_xung_chieu(considered_position) in list_ele_positions and all(
                    p in [considered_position, *get_tam_hop(considered_position)] for p in list_ele_positions
                ):
                    return True
            return False
