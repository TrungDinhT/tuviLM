from src.refactored.component.cung import Cung
from src.refactored.component.elementary import ComponentBase
from src.refactored.component.sao import Sao, TuHoa
from src.refactored.component.tuan_triet import TuanTriet


Component = Cung | Sao | TuHoa | TuanTriet | ComponentBase
