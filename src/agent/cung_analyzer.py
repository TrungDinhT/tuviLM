import httpx
from typing import Iterable

from src.agent.prompt import CUNG_AGENT_INSTRUCTION
from src.retrieval.search.tool import search_role_info, search_start_info, search_start_role_info
from src.tuvi.cung import Cung
from src.tuvi.tinh_ban import TinhBan
from pydantic_ai import Agent


class CungAnalyzer:
    def __init__(self, model: str = "gpt-4.1-mini", timeout: httpx.Timeout = None):
        self.timeout = timeout or httpx.Timeout(connect=5.0, timeout=60.0)
        self.agent: Agent[str] = Agent(
            model=model,
            system_prompt=CUNG_AGENT_INSTRUCTION,
            output_type=str,
        )

    @staticmethod
    def _format_docs(items: Iterable[dict[str, str]]) -> list[str]:
        docs: list[str] = []
        for item in items:
            title = item.get("title", "")
            content = item.get("content", "")
            docs.append(f"{title}: {content}")
        return docs

    def _build_cung_context(self, position: str, cung: Cung) -> str:
        """Build structured user context for a specific cung."""
        chinh_tinh = ", ".join(
            f"{star.name} {star.get_status(position)}" for star in cung.chinhTinh
        ) or "Không có"

        phu_tinh = ", ".join(star.name for star in cung.phuTinh) or "Không có"

        tu_hoa = ", ".join(star.name for star in cung.tuhoa) or "Không có"

        trang_sinh = cung.trang_sinh.name if cung.trang_sinh else "Không có"

        flags: list[str] = []
        if cung.is_tuan:
            flags.append("Có Tuần")
        if cung.is_triet:
            flags.append("Có Triệt")
        tinh_trang = ", ".join(flags) if flags else "Không có Tuần/Triệt"

        return "\n".join(
            [
                f"Vị trí cung: {position}",
                f"Vai trò cung: {cung.role}",
                f"Chính tinh: {chinh_tinh}",
                f"Phụ tinh: {phu_tinh}",
                f"Tràng sinh: {trang_sinh}",
                f"Tứ hóa: {tu_hoa}",
                f"Đặc điểm bổ sung: {tinh_trang}",
            ]
        )

    def _gather_documents(self, cung: Cung) -> list[str]:
        """Gather relevant documents for a cung."""
        documents: list[str] = []

        # Search role information
        documents.extend(self._format_docs(search_role_info(cung.role)))

        # Search main stars information
        for star in cung.chinhTinh:
            documents.extend(self._format_docs(search_start_role_info(star.name, cung.role)))

        # Search transformation stars information
        for tuhoa in cung.tuhoa:
            documents.extend(self._format_docs(search_start_info(tuhoa.name)))

        # Search longevity star information
        if cung.trang_sinh:
            documents.extend(self._format_docs(search_start_info(cung.trang_sinh.name)))

        # Search auxiliary stars information
        for star in cung.phuTinh:
            documents.extend(self._format_docs(search_start_info(star.name)))

        # De-duplicate while preserving order
        seen = set()
        unique_documents: list[str] = []
        for doc in documents:
            if doc not in seen:
                seen.add(doc)
                unique_documents.append(doc)

        return unique_documents

    def analyze_cung(self, position: str, cung: Cung) -> str:
        """Analyze a single cung and return the agent's response."""
        cung_context = self._build_cung_context(position, cung)
        documents = self._gather_documents(cung)

        prompt = (
            "Hãy phân tích cung sau dựa trên thông tin đầu vào và tài liệu tham khảo.\n\n"
            "## Thông tin cung\n"
            f"{cung_context}\n\n"
            "## Tài liệu tham khảo\n"
            f"{'\n\n'.join(documents) if documents else 'Không có tài liệu tham khảo phù hợp.'}"
        )

        return self.agent.run_sync(prompt).output

    def run(self, tinh_ban: TinhBan) -> dict:
        """Analyze all cungs in a tinh_ban and return results."""
        results = {}

        for position, cung in tinh_ban.map_cung.items():
            analysis = self.analyze_cung(position, cung)
            results[position] = {
                "role": cung.role,
                "analysis": analysis
            }

        return results
