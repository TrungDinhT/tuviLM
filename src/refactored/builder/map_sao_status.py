from src.refactored.component.map_star_status import (
    MAP_START_STATUS,
)
from src.refactored.component.elementary import DiaChi
from src.refactored.component.sao import Status as SaoStatus

MAP_SAO_STATUS: dict[str, dict[DiaChi, SaoStatus]] = {
    sao_name: {
        DiaChi(dia_chi_text): SaoStatus(status_text)
        for dia_chi_text, status_text in status_dict.items()
    }
    for sao_name, status_dict in MAP_START_STATUS.items()
}
