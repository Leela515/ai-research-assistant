from abc import ABC, abstractmethod
from typing import List
from models.paper import Paper
from models.section import Section

class DocumentParser(ABC):
    @abstractmethod
    def parse(self, paper: Paper) -> List[Section]:
        """Given a paper (with pdf_url or local pdf path), return strucutred sections.
        must preserve provenance (paper_id, pages if possible).
        """

        raise NotImplementedError