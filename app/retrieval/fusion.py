from collections import defaultdict

def rrf(rank_lists, k=60):
    scores = defaultdict(float)
    paths = defaultdict(list)
    for path, ids in rank_lists.items():
        for rank, sid in enumerate(ids, 1):
            scores[sid] += 1/(k+rank)
            paths[sid].append(path)
    rows = [(sid, scores[sid], paths[sid]) for sid in scores]
    return sorted(rows, key=lambda x:x[1], reverse=True)
