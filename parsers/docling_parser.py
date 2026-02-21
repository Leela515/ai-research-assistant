from __future__ import annotations

from typing import List, Optional
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from models.paper import Paper
from models.section import Section
from parsers.base_parser import DocumentParser
from utils.logger import get_logger
import re

logger = get_logger(__name__)

class DoclingParser(DocumentParser):
    """
    Thin adapter:
    Paper(pdf_path)-> Docling Document-> Markdown-> Section objects.
    """

    def __init__(self):
        pdf_opts = PdfPipelineOptions()
        pdf_opts.do_ocr = False
        pdf_opts.force_backend_text = True

        pdf_opts.do_table_structure = False
        pdf_opts.do_picture_description = False
        pdf_opts.do_picture_classification = False
        self._converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_opts)
            }
        )

    def parse(self, paper: Paper) -> List[Section]:
        if not paper.pdf_path:
            raise ValueError(f"Paper {paper.paper_id} has no pdf_path. Download first.")

        
        pdf_path = Path(paper.pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found at: {paper.pdf_path}")
        
        logger.info(f"Parsing PDf with Docling: {paper.pdf_path}")

        # Convert PDF to Docling Document
        result = self._converter.convert(str(pdf_path))
        doc = result.document # quickstart pattern

        # Export to Markdown (Docling supports Markdown export in docs/quickstart)
        md: Optional[str] = None

        if hasattr(doc, "export_to_markdown"):
            md = doc.export_to_markdown()
        elif hasattr(doc, "export"):
            try:
                md = doc.export("markdown")
            except Exception:
                md = None
        
        if not md or not md.strip():
            raise RuntimeError("Docling produced empty Markdown output.")
        
        # Map Markdown -> Sections

        sections = self._markdown_to_sections(paper_id=paper.paper_id, markdown=md)
        sections = self._split_frontmatter_abstract(sections)
        return sections
        
    def _markdown_to_sections(self, paper_id: str, markdown: str) -> List[Section]:
        """Simple Sectioner:
        - every heading starts a new section
        - Text unit next heading belongs to that section
        """

        lines = markdown.splitlines()

        sections: List[Section] = []
        current_title: Optional[str] = None
        current_type: str = "unknown"
        buffer: List[str] = []
        idx = 0

        def flush():
            nonlocal idx, buffer, current_title, current_type
            text = "\n".join(buffer).strip()
            if not text:
                return
            section_id = f"{paper_id}_sec_{idx}"
            sections.append(
                Section(
                    section_id=section_id,
                    paper_id=paper_id,
                    title=current_title,
                    section_type=current_type,
                    text=text,
                    page_start=None,
                    page_end=None,
                )
            )
            idx += 1
            buffer = []
        
        for line in lines:
            if line.startswith("#"):
                # New section
                flush()
                heading = line.lstrip("#").strip()
                current_title = heading if heading else None
                current_type = self._infer_section_type(heading)
            else:
                buffer.append(line)

        flush()

        if not sections:
            # Worst case: no headings in markdown, store as one section
            sections.append(
                Section(
                    section_id=f"{paper_id}_sec_0",
                    paper_id=paper_id,
                    title=None,
                    section_type="unknown",
                    text=markdown.strip(),
                    page_start=None,
                    page_end=None,
                )
            )
        
        return sections
    
    def _infer_section_type(self, heading: str) -> str:
        if not heading:
            return "unknown" 
        h = heading.strip().lower()

        h = re.sub(r"^\s*(\d+(\.\d+)*|[ivxlcdm]+)\.?\s+", "", h)

        h = re.sub(r"[\-–—:|/]", " ", h)
        h = re.sub(r"\s+", " ", h).strip()

        prefix_rules = [
            ("abstract", "abstract"),
            ("introduction", "introduction"),
            ("background", "background"),
            ("related work", "related_work"),
            ("literature review", "related_work"),
            ("preliminaries", "background"),
            ("method", "method"),
            ("methods", "method"),
            ("materials and methods", "method"),
            ("methodology", "method"),
            ("approach", "method"),
            ("experimental setup", "experiments"),
            ("experiments", "experiments"),
            ("results", "results"),
            ("evaluation", "results"),
            ("discussion", "discussion"),
            ("conclusion", "conclusion"),
            ("conclusions", "conclusion"),
            ("future work", "conclusion"),
            ("acknowledgement", "acknowledgements"),
            ("acknowledgement", "acknowledgements"),
            ("acknowledgments", "acknowledgements"),
            ("references", "references"),
            ("bibliography", "references"),
            ("appendix", "appendix"),
            ("supplementary", "appendix"),
        ]

        for prefix, label in prefix_rules:
            if h.startswith(prefix):
                return label

        # Secondary keyword checks (covers headings like "Conclusion and Future Work")
        keyword_rules = [
            ("related work", "related_work"),
            ("literature", "related_work"),
            ("method", "method"),
            ("experiment", "experiments"),
            ("result", "results"),
            ("evaluation", "results"),
            ("discussion", "discussion"),
            ("conclusion", "conclusion"),
            ("reference", "references"),
            ("bibliograph", "references"),
            ("appendix", "appendix"),
        ]

        for kw, label in keyword_rules:
            if kw in h:
                return label

        return "unknown"
    
    def _split_frontmatter_abstract(self, sections: List[Section]) -> List[Section]:
        if not sections:
            return sections

        first = sections[0]
        if first.section_type != "unknown":
            return sections

        text = first.text or ""
        m = re.search(r"\babstract\b", text, flags=re.IGNORECASE)
        if not m:
            return sections

        cut = m.start()
        front = text[:cut].strip()
        rest = text[cut:].strip()

        out: List[Section] = []
        base_id = first.section_id

        if front:
            out.append(first.model_copy(update={
                "section_id": f"{base_id}_front",
                "section_type": "frontmatter",
                "title": first.title,
                "text": front,
            }))       

        if rest:
            out.append(first.model_copy(update={
                "section_id": f"{base_id}_abstract",
                "section_type": "abstract",
                "title": "Abstract",
                "text": rest,
            }))

        out.extend(sections[1:])
        return out