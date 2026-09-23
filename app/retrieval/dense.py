class DenseRetriever:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None
        self.embeddings = None

    def build(self, standards):
        """Returns True on success, False if sentence_transformers is unavailable.
        CON-08: Caller must check this return value and log appropriately."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return False
        try:
            import numpy as np
            self.model = SentenceTransformer(self.model_name)
            texts = [f"{s.standard_id} {s.title} {s.scope} {' '.join(s.keywords)}" for s in standards]
            self.embeddings = self.model.encode(texts, normalize_embeddings=True)
            return True
        except Exception:
            return False

    def search(self, query, top_k=8):
        if self.model is None:
            return []
        import numpy as np
        q = self.model.encode([query], normalize_embeddings=True)[0]
        sims = self.embeddings @ q
        idx = np.argsort(-sims)[:top_k]
        return [(int(i), float(sims[i])) for i in idx]
