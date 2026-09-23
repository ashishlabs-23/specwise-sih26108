from app.retrieval.bm25 import BM25

def test_bm25():
    b = BM25(["openwell submersible pumpset","monoset pump","transformer"])
    assert b.search("openwell submersible",1)[0].doc_index == 0
