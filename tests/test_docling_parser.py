import pytest

docling = pytest.importorskip("docling")

from models.section import Section
from parsers.docling_parser import DoclingParser


def make_parser_without_init():
    return DoclingParser.__new__(DoclingParser)


@pytest.mark.parametrize(
    ("heading", "expected"),
    [
        ("Abstract", "abstract"),
        ("1 Introduction", "introduction"),
        ("Related Work", "related_work"),
        ("Materials and Methods", "method"),
        ("Conclusion and Future Work", "conclusion"),
        ("Appendix A", "appendix"),
        ("Unexpected Heading", "unknown"),
    ],
)
def test_infer_section_type(heading, expected):
    parser = make_parser_without_init()

    assert parser._infer_section_type(heading) == expected


def test_split_frontmatter_abstract_splits_first_unknown_section():
    parser = make_parser_without_init()
    sections = [
        Section(
            section_id="paper_1_sec_0",
            paper_id="paper_1",
            title=None,
            section_type="unknown",
            text="Conference 2025\nAuthors\nAbstract This is the abstract.",
        ),
        Section(
            section_id="paper_1_sec_1",
            paper_id="paper_1",
            title="Introduction",
            section_type="introduction",
            text="Intro text",
        ),
    ]

    split_sections = parser._split_frontmatter_abstract(sections)

    assert [section.section_type for section in split_sections] == [
        "frontmatter",
        "abstract",
        "introduction",
    ]
    assert split_sections[0].text == "Conference 2025\nAuthors"
    assert split_sections[1].title == "Abstract"
    assert split_sections[1].text.startswith("Abstract")
