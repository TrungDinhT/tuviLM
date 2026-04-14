from src.refactored.component.elementary import CircleDirection, DiaChi


def get_xung_chieu(position: DiaChi) -> DiaChi:
    return position + 6


def mirror_across(position: DiaChi, axis: tuple[DiaChi, DiaChi]) -> DiaChi:
    """Mirror a position across an axis defined by opposite DiaChi."""
    axis_start, axis_end = axis
    if axis_start + 6 != axis_end:
        raise ValueError(
            "Mirror axis must be defined by opposite DiaChi positions."
        )
    return DiaChi.from_index(2 * axis_start.index - position.index)


def get_nhi_hop(position: DiaChi) -> DiaChi:
    index = position.index
    return DiaChi.from_index(13 - index)


def get_luc_hai(position: DiaChi) -> DiaChi:
    index = position.index
    return DiaChi.from_index(7 - index)


def get_tam_hop(position: DiaChi, direction: CircleDirection) -> DiaChi:
    return position + 4 * direction
