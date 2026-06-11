from pathlib import Path
import unittest

from spectaskai.rag_indexer import index_markdown_file
from spectaskai.rag_search import search_chunks


class RagPipelineTest(unittest.TestCase):
    def test_index_markdown_file_extracts_sections(self) -> None:
        chunks = index_markdown_file(Path("data/home-specs/router-demo.md"), spec_id="router-demo")

        sections = {chunk.section for chunk in chunks}
        self.assertIn("GNSS", sections)
        self.assertIn("Timing", sections)
        self.assertTrue(all(chunk.spec_id == "router-demo" for chunk in chunks))

    def test_search_chunks_returns_relevant_gnss_chunk(self) -> None:
        chunks = index_markdown_file(Path("data/home-specs/router-demo.md"), spec_id="router-demo")
        results = search_chunks("GNSS timing priority", chunks, limit=2)

        self.assertTrue(results)
        self.assertIn(results[0].chunk.section, {"GNSS", "Timing"})
        self.assertIn("gnss", results[0].matched_terms)


if __name__ == "__main__":
    unittest.main()
