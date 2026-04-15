from core.chunker import chunk_sections
from models.section import Section


def test_chunk_sections_skips_empty_sections():
    sections = [
        Section(
            section_id="paper_1_sec_0",
            paper_id="paper_1",
            title="Empty",
            section_type="unknown",
            text="   ",
        )
    ]

    assert chunk_sections(sections) == []


def test_chunk_sections_preserves_overlap_and_metadata():
    text = "abcdefghij" * 3
    sections = [
        Section(
            section_id="paper_1_sec_0",
            paper_id="paper_1",
            title="Intro",
            section_type="introduction",
            text=text,
        )
    ]

    chunks = chunk_sections(sections, max_char=10, overlap=3)

    assert len(chunks) == 4

    first, second = chunks[0], chunks[1]
    assert first.chunk_id == "paper_1_sec_0_chunk_0"
    assert first.paper_id == "paper_1"
    assert first.section_id == "paper_1_sec_0"
    assert first.char_start == 0
    assert first.char_end == 10
    assert first.text == text[0:10]

    assert second.chunk_id == "paper_1_sec_0_chunk_1"
    assert second.char_start == 7
    assert second.char_end == 17
    assert second.text == text[7:17]


def test_chunk_sections_handles_multiple_sections():
    sections = [
        Section(
            section_id="paper_1_sec_0",
            paper_id="paper_1",
            title="Abstract",
            section_type="abstract",
            text="one two three",
        ),
        Section(
            section_id="paper_1_sec_1",
            paper_id="paper_1",
            title="Method",
            section_type="method",
            text="four five six",
        ),
    ]

    chunks = chunk_sections(sections, max_char=50, overlap=5)

    assert [chunk.section_id for chunk in chunks] == ["paper_1_sec_0", "paper_1_sec_1"]
