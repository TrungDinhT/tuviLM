from src.refactored.component.cung import Cung
from src.refactored.component.sao import Sao, TuanTriet, TuHoa, VongTrangSinh


Component = (
    Cung
    | Sao
    | VongTrangSinh
    | TuHoa
    | TuanTriet
)
