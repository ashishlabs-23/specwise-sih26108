import re


# These words describe procurement activity or generic infrastructure and do not
# identify an item represented by a standard in the loaded corpus.
_GENERIC_TERMS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with",
    "supply", "installation", "install", "equipment", "system", "water", "distribution",
    "procurement", "tender", "work", "works", "provide", "providing", "testing", "commissioning",
    "specification", "specifications", "requirement", "requirements", "standard", "standards",
}
_TOKEN = re.compile(r"[a-z0-9]+")
_CORE_ITEM_NOUNS = {"pump", "pumps", "pumpset", "pumpsets", "cable", "cables"}
_PROCUREMENT = re.compile(r"(?<!water )\b(?:supply|procure(?:ment)?|purchase|provide)\b", re.I)


def _primary_procurement_text(text: str) -> str | None:
    """Return the stated procurement heads, excluding attached accessories.

    Tender language commonly lists accessory mentions after a lead item using
    commas, "including", or "with". Explicit item clauses are kept separately
    so genuine multi-item packages retain each primary procurement item.
    """
    heads = []
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+(?=(?:item\s+\d+\s*[:.)-]|\d+[.)]\s))", "\n", text, flags=re.I)
    for line in re.split(r"[\r\n]+", text):
        line = re.sub(r"\[PAGE\s+\d+\]", " ", line, flags=re.I).strip()
        if not line:
            continue
        item = re.match(r"\s*(?:item\s+\d+\s*[:.)-]|\d+[.)])\s*(.*)", line, re.I)
        if item:
            line = item.group(1)
            # In enumerated lists each item begins with the item label and has
            # its own procurement status; retain product-first item clauses.
            candidate = re.split(r"[,;.]|\b(?:including|with|along with)\b", line, maxsplit=1, flags=re.I)[0]
            if re.search(r"\b(?:pump|pumps|pumpset|pumpsets|cable|cables)\b", candidate, re.I):
                heads.append(candidate)
            continue
        if _PROCUREMENT.search(line):
            tail = _PROCUREMENT.split(line, maxsplit=1)[-1]
            candidate = re.split(r"[,;.]|\b(?:including|with|along with)\b", tail, maxsplit=1, flags=re.I)[0]
            heads.append(candidate)
    return " ".join(heads) if heads else None


def has_corpus_product_signal(text: str, standards) -> bool:
    """Check for a meaningful corpus term or explicit IS reference in the input.

    Candidate retrieval alone is not a domain signal: BM25 can return lexical
    matches for unrelated technical tenders. Terms are derived from the loaded
    standard records, so this gate follows the existing corpus without changing it.
    """
    # An explicit IS citation is itself a verifiable requirement, even when the
    # stated procurement head is otherwise outside the product corpus.
    if re.search(r"\bis\s*[:\-]?\s*\d{3,6}\b", text, re.I):
        return True
    normalized = text.lower()
    primary_text = _primary_procurement_text(text)
    # When procurement structure is explicit, only product nouns in the stated
    # procurement head count. This keeps accessory mentions from driving routing.
    if primary_text is not None:
        normalized = primary_text.lower()
    corpus_phrases = set()
    for standard in standards:
        for field in standard.product_terms:
            phrase = " ".join(_TOKEN.findall(field.lower()))
            if phrase and not all(token in _GENERIC_TERMS for token in phrase.split()):
                corpus_phrases.add(phrase)

    # The corpus also contains general standards for pumps and cables. A bare
    # item noun is enough to keep an ambiguous pump/cable query in-domain, while
    # generic materials such as steel or pipe cannot turn an unrelated tender
    # into a corpus match.
    has_item_noun = any(
        re.search(rf"\b{re.escape(noun)}\b", normalized)
        for noun in _CORE_ITEM_NOUNS
    )
    has_product_phrase = any(
        re.search(rf"\b{re.escape(phrase)}\b", normalized)
        for phrase in corpus_phrases
    )
    return has_item_noun or has_product_phrase
