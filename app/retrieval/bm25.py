import math
import re
from collections import Counter
from dataclasses import dataclass

TOKEN = re.compile(r"[A-Za-z0-9]+", re.UNICODE)

def tokenize(text):
    return [x.lower() for x in TOKEN.findall(text)]

@dataclass
class Hit:
    doc_index: int
    score: float

class BM25:
    def __init__(self, documents, k1=1.5, b=0.75):
        self.docs = [tokenize(x) for x in documents]
        self.n = len(self.docs)
        self.k1, self.b = k1, b
        self.avgdl = sum(map(len, self.docs))/max(self.n, 1)
        self.tf = [Counter(x) for x in self.docs]
        self.df = Counter()
        for d in self.docs:
            for t in set(d):
                self.df[t] += 1

    def search(self, query, top_k=8):
        q = tokenize(query)
        out = []
        for i, tf in enumerate(self.tf):
            dl = len(self.docs[i])
            score = 0.0
            for term in q:
                if term not in tf:
                    continue
                df = self.df[term]
                idf = math.log(1 + (self.n - df + 0.5)/(df + 0.5))
                f = tf[term]
                denom = f + self.k1*(1-self.b+self.b*dl/max(self.avgdl, 1))
                score += idf * ((f*(self.k1+1))/denom)
            if score > 0:
                out.append(Hit(i, score))
        return sorted(out, key=lambda x:x.score, reverse=True)[:top_k]
