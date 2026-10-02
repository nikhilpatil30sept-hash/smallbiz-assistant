"""Quick command-line test:  python ask.py "How do I register a business name in Ontario?" """
import sys

from rag import answer_stream, format_sources


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('usage: python ask.py "your question"')
    sources, tokens = answer_stream(" ".join(sys.argv[1:]))
    for t in tokens:
        print(t, end="", flush=True)
    print("\n\n--- Sources ---")
    print(format_sources(sources) or "(none found above the relevance threshold)")


if __name__ == "__main__":
    main()
