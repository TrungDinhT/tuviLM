from src.refactored.builder.legacy.map_star_status import (
    MAP_START_STATUS as _MAP_START_STATUS_TEXT,
)
from src.refactored.component.elementary import DiaChi
from src.refactored.component.sao import Status as SaoStatus

MAP_SAO_STATUS: dict[str, dict[DiaChi, SaoStatus | None]] = {
    sao_name: {
        DiaChi(dia_chi_text): SaoStatus(status_text)
        for dia_chi_text, status_text in status_dict.items()
    }
    for sao_name, status_dict in _MAP_START_STATUS_TEXT.items()
}
