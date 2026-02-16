import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.memory.config import MemoryRetrievalConfig
from modules.memory.service import MemoryService
from modules.storage.in_memory import InMemoryStore


class MemoryRetrievalServiceUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.service = MemoryService(self.store)

    def test_index_summary_persists_vector_records(self) -> None:
        self.service.index_summary("u1", "I felt anxious before a work presentation.")

        summaries = self.store.list_memory_summaries("u1")
        vectors = self.store.list_memory_vectors("u1")

        self.assertEqual(len(summaries), 1)
        self.assertEqual(len(vectors), 1)
        self.assertEqual(vectors[0].text, summaries[0])
        self.assertGreater(len(vectors[0].embedding), 0)

    def test_retrieve_relevant_returns_work_related_memory(self) -> None:
        self.service.index_summary("u1", "Work anxiety rises before every presentation with my manager.")
        self.service.index_summary("u1", "Sleep improved after evening breathing exercises.")
        self.service.index_summary("u1", "Conflict with my partner made me feel distant.")

        results = self.service.retrieve_relevant("u1", "I feel anxious before work presentations", limit=2)
        self.assertEqual(len(results), 2)
        self.assertIn("Work anxiety rises before every presentation", results[0])

    def test_blank_query_falls_back_to_recent(self) -> None:
        self.service.index_summary("u1", "first")
        self.service.index_summary("u1", "second")
        self.service.index_summary("u1", "third")

        results = self.service.retrieve_relevant("u1", "   ", limit=2)
        self.assertEqual(results, ["second", "third"])

    def test_openai_embedder_without_key_raises_on_index(self) -> None:
        service = MemoryService(
            self.store,
            config=MemoryRetrievalConfig(embedder_provider="openai", openai_api_key=""),
        )
        with self.assertRaises(ValueError):
            service.index_summary("u1", "any summary")


if __name__ == "__main__":
    unittest.main()
