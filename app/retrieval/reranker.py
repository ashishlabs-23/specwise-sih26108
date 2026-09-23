class CrossEncoderReranker:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None

    def load(self):
        try:
            from sentence_transformers import CrossEncoder
        except ImportError:
            return False
        self.model = CrossEncoder(self.model_name)
        return True

    def rerank(self, query, candidates, top_k=8):
        if self.model is None:
            return candidates[:top_k]
        pairs = [[query, f"{x['standard_id']} {x['title']} {x['scope']}"] for x in candidates]
        scores = self.model.predict(pairs)
        for item, score in zip(candidates, scores):
            item["rerank_score"] = float(score)
        return sorted(candidates, key=lambda x:x["rerank_score"], reverse=True)[:top_k]
