from src.refactored.component.elementary import DiaChi


def get_xung_chieu(position: DiaChi) -> DiaChi:
    return position + 6


def get_nhi_hop(position: DiaChi) -> DiaChi:
    index = position.index
    return DiaChi.from_index(13 - index)


def get_luc_hai(position: DiaChi) -> DiaChi:
    index = position.index
    return DiaChi.from_index(7 - index)


def get_tam_hop_thuan(position: DiaChi) -> DiaChi:
    # Increase clockwise
    return position + 4


def get_tam_hop_nghich(position: DiaChi) -> DiaChi:
    # Decrease counter-clockwise
    return position - 4


def get_tam_hop(position: DiaChi) -> tuple[DiaChi, DiaChi]:
    return get_tam_hop_thuan(position), get_tam_hop_nghich(position)
