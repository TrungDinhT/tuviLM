from src.tuvi.element.types import TYPE_DIA_CHI, LIST_DIA_CHI


def get_position_by_move(
    begin_position: TYPE_DIA_CHI | int,
    offset: int,
    direction: int,
) -> TYPE_DIA_CHI:
    if isinstance(begin_position, str):
        begin_position = LIST_DIA_CHI.index(begin_position)

    return LIST_DIA_CHI[(begin_position + direction * offset) % 12]
