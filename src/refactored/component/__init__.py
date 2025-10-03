from src.refactored.component.cung import Cung
from src.refactored.component.elementary import ComponentBase
from src.refactored.component.sao import Sao, TuHoa


Component = Cung | Sao | TuHoa | ComponentBase
