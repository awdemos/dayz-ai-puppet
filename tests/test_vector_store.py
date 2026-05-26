from dayz_ai_puppet.memory.vector_store import Document, SimpleVectorStore


class TestSimpleVectorStore:
    def test_add_and_len(self):
        store = SimpleVectorStore()
        store.add(Document(doc_id="1", position=(0, 0, 0)))
        assert len(store) == 1

    def test_query_by_position(self):
        store = SimpleVectorStore()
        store.add(Document(doc_id="near", position=(100, 0, 100)))
        store.add(Document(doc_id="far", position=(5000, 0, 5000)))

        results = store.query_by_position((110, 0, 110), k=5, max_distance=200)
        assert len(results) == 1
        assert results[0][0].doc_id == "near"

    def test_query_by_position_max_distance(self):
        store = SimpleVectorStore()
        store.add(Document(doc_id="1", position=(100, 0, 100)))
        results = store.query_by_position((1000, 0, 1000), max_distance=10)
        assert len(results) == 0

    def test_query_by_features(self):
        store = SimpleVectorStore()
        store.add(Document(doc_id="a", position=(0, 0, 0), features={"danger": 0.9, "loot": 0.1}))
        store.add(Document(doc_id="b", position=(0, 0, 0), features={"danger": 0.1, "loot": 0.9}))

        results = store.query_by_features({"danger": 1.0}, k=2)
        assert results[0][0].doc_id == "a"

    def test_query_by_features_empty(self):
        store = SimpleVectorStore()
        results = store.query_by_features({"key": 1.0})
        assert len(results) == 0

    def test_query_by_position_sorted_by_distance(self):
        store = SimpleVectorStore()
        store.add(Document(doc_id="mid", position=(50, 0, 50)))
        store.add(Document(doc_id="close", position=(10, 0, 10)))
        store.add(Document(doc_id="far", position=(200, 0, 200)))

        results = store.query_by_position((0, 0, 0), k=3, max_distance=500)
        assert results[0][0].doc_id == "close"
        assert results[1][0].doc_id == "mid"
        assert results[2][0].doc_id == "far"
