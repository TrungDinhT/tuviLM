import httpx
from typing import List

from src.agent.agent import BaseAgent, LLMMessage
from src.agent.prompt import CUNG_AGENT_INSTRUCTION
from src.retrieval.search.tool import search_role_info, search_start_info, search_start_role_info
from src.tuvi.cung import Cung
from src.tuvi.tinh_ban import TinhBan


class CungAnalyzer:
    def __init__(self, model: str = "gpt-4.1-mini", timeout: httpx.Timeout = None):
        if timeout is None:
            timeout = httpx.Timeout(connect=5.0, timeout=60.0)
        self.agent = BaseAgent(
            system_prompt=CUNG_AGENT_INSTRUCTION,
            model=model,
            timeout=timeout
        )

    def _build_cung_messages(self, position: str, cung: Cung) -> List[LLMMessage]:
        """Build messages for a specific cung (palace)."""
        messages: List[LLMMessage] = []

        messages.append({
            "role": "user",
            "content": f"Vị trí của cung là {position}, vai trò của cung là {cung.role}.",
        })

        messages.append({
            "role": "user",
            "content": f"Các sao chính trong cung là : {', '.join([f'{star.name} {star.get_status(position)}' for star in cung.chinhTinh])}.",
        })

        messages.append({
            "role": "user",
            "content": f"Các sao phụ trong cung là : {', '.join([star.name for star in cung.phuTinh])}.",
        })

        messages.append({
            "role": "user",
            "content": f"Sao Tràng Sinh trong cung là : {cung.trang_sinh.name}.",
        })

        messages.append({
            "role": "user",
            "content": f"Các sao hóa trong cung là : {', '.join([star.name for star in cung.tuhoa])}.",
        })

        if cung.is_tuan:
            messages.append({
                "role": "user",
                "content": "Cung có Tuần.",
            })

        if cung.is_triet:
            messages.append({
                "role": "user",
                "content": "Cung có Triệt.",
            })

        return messages

    def _gather_documents(self, cung: Cung) -> List[str]:
        """Gather relevant documents for a cung."""
        documents = []

        # Search role information
        doc = search_role_info(cung.role)
        for d in doc:
            documents.append(f"{d['title']}: {d['content']}")

        # Search main stars information
        for star in cung.chinhTinh:
            doc = search_start_role_info(star.name, cung.role)
            for d in doc:
                documents.append(f"{d['title']}: {d['content']}")

        # Search transformation stars information
        for tuhoa in cung.tuhoa:
            doc = search_start_info(tuhoa.name)
            for d in doc:
                documents.append(f"{d['title']}: {d['content']}")

        # Search longevity star information
        if cung.trang_sinh:
            doc = search_start_info(cung.trang_sinh.name)
            for d in doc:
                documents.append(f"{d['title']}: {d['content']}")

        # Search auxiliary stars information
        for star in cung.phuTinh:
            doc = search_start_info(star.name)
            for d in doc:
                documents.append(f"{d['title']}: {d['content']}")

        return documents

    def analyze_cung(self, position: str, cung) -> str:
        """Analyze a single cung and return the agent's response."""
        messages = self._build_cung_messages(position, cung)
        documents = self._gather_documents(cung)

        messages.append({
            "role": "system",
            "content": "\n\n".join(documents),
        })

        return self.agent.run(messages)

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
