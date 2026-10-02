"""Keyword search over the chunks, to complement the embedding search.

Embeddings are good at meaning but poor at names: "What is Starter Company Plus?" or
"digital main street" may not land near the one sentence that mentions them. This finds
chunks that contain the *rare* words of the question. It is deliberately conservative: a
chunk is only returned if it matches a rare word (one that appears in at most RARE_DF chunks)
AND covers most of the question's meaningful words, so common words like "business" or "tax"
never trigger it and off-topic questions match nothing.
"""
import math
import re

STOPWORDS = set(
    """a about above after again all also am an and any are as at be because been before being below
    between both but by can could did do does doing down during each few for from further get had has
    have having he her here hers him his how i if in into is it its just me more most my no nor not now
    of off on once only or other our out over own same she should so some such than that the their them
    then there these they this those through to too under until up us very was we were what when where
    which while who whom why will with would you your yours yes need needs want tell please give
    help know one""".split()
)

RARE_DF = 3          # a word is "rare" if it appears in at most this many chunks (or 3% of all chunks,
                     # whichever is larger, so the rule still means something as the knowledge base grows)
MIN_COVERAGE = 0.75  # share of the question's (weighted) words the chunk must contain


def tokens(text: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]  # crude plural handling: loans -> loan
        out.append(w)
    return out


def content_terms(text: str) -> list[str]:
    return [t for t in tokens(text) if t not in STOPWORDS and not t.isdigit()]


class LexicalIndex:
    def __init__(self, texts: list[str]):
        self.sets = [set(content_terms(t)) for t in texts]
        self.n = len(texts)
        self.rare = max(RARE_DF, int(0.03 * self.n))
        self.df: dict[str, int] = {}
        for s in self.sets:
            for t in s:
                self.df[t] = self.df.get(t, 0) + 1

    def _idf(self, term: str) -> float:
        df = self.df[term]
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def _weight(self, term: str) -> float:
        # A word the pages never use ("France", "lasagna", "trademark") can never be matched.
        # It still counts against coverage, so a question that is mostly about something the
        # pages do not cover cannot be rescued by one stray shared word like "capital".
        return self._idf(term) if term in self.df else math.log(1 + (self.n - 0.5) / 1.5)

    def search(self, query: str, max_hits: int = 3) -> list[tuple[int, float]]:
        """[(chunk index, coverage)] best first."""
        terms = list(dict.fromkeys(content_terms(query)))
        known = [t for t in terms if t in self.df]
        if not known or not any(self.df[t] <= self.rare for t in known):
            return []
        total = sum(self._weight(t) for t in terms)
        hits = []
        for i, s in enumerate(self.sets):
            matched = [t for t in known if t in s]
            if not any(self.df[t] <= self.rare for t in matched):
                continue
            coverage = sum(self._idf(t) for t in matched) / total
            if coverage >= MIN_COVERAGE:
                hits.append((i, coverage))
        hits.sort(key=lambda h: -h[1])
        return hits[:max_hits]
