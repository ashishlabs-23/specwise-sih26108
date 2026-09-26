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


def has_corpus_product_signal(text: str, standards) -> bool:
    """Check for a meaningful corpus term or explicit IS reference in the input.

    Candidate retrieval alone is not a domain signal: BM25 can return lexical
    matches for unrelated technical tenders. Terms are derived from the loaded
    standard records, so this gate follows the existing corpus without changing it.
    """
    normalized = text.lower()
    if re.search(r"\bis\s*[:\-]?\s*\d{3,6}\b", normalized):
        return True

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
