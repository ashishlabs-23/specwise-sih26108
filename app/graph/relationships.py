def expand(seed_ids, relationships, max_hops=2):
    """
    CON-09: Each returned Relationship now carries its hop distance (1 or 2).
    Only verified relationships are traversed.
    """
    adjacency = {}
    for rel in relationships:
        if rel.verified:
            adjacency.setdefault(rel.from_standard, []).append(rel)

    seen = set(seed_ids)
    queue = [(x, 0) for x in seed_ids]
    result = []

    while queue:
        current, hop = queue.pop(0)
        if hop >= max_hops:
            continue
        for rel in adjacency.get(current, []):
            # Create a copy with hop distance set
            rel_with_hop = rel.model_copy(update={"hop": hop + 1})
            result.append(rel_with_hop)
            if rel.to_standard not in seen:
                seen.add(rel.to_standard)
                queue.append((rel.to_standard, hop + 1))
    return result
