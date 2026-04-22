import argparse
from typing import Any, Dict, List, Tuple

import requests


DEFAULT_QUERIES = [
    "Who wrote the novel Pride and Prejudice?",
    "What is the capital city of Japan?",
    "Which planet is known as the Red Planet?",
    "What is photosynthesis?",
    "When did World War II end?",
]


def _as_text(doc: Any) -> str:
    if isinstance(doc, dict):
        return (doc.get("contents") or doc.get("text") or "").strip()
    return str(doc).strip()


def _as_title(doc: Any) -> str:
    if isinstance(doc, dict):
        if doc.get("title"):
            return str(doc["title"])
        contents = doc.get("contents")
        if isinstance(contents, str) and contents.strip():
            return contents.splitlines()[0].strip().strip('"')
    text = _as_text(doc)
    if text.startswith('"') and '"\n' in text:
        return text.split("\n", 1)[0].strip().strip('"')
    return ""


def call_bm25(url: str, queries: List[str], topk: int) -> List[List[Dict[str, Any]]]:
    payload = {"queries": queries, "topk": topk, "return_scores": True}
    r = requests.post(url, json=payload, timeout=180)
    r.raise_for_status()
    return r.json()["result"]


def call_rerank(url: str, queries: List[str], topk_retrieval: int, topk_rerank: int) -> List[List[Dict[str, Any]]]:
    payload = {
        "queries": queries,
        "topk_retrieval": topk_retrieval,
        "topk_rerank": topk_rerank,
        "return_scores": True,
    }
    r = requests.post(url, json=payload, timeout=180)
    r.raise_for_status()
    return r.json()["result"]


def topk_preview(items: List[Dict[str, Any]], k: int) -> List[Tuple[float, str, str]]:
    out = []
    for it in items[:k]:
        score = float(it.get("score", 0.0))
        doc = it.get("document")
        title = _as_title(doc) or "N/A"
        text = _as_text(doc).replace("\n", " ")
        out.append((score, title, text[:160]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bm25_url", type=str, default="http://127.0.0.1:8000/retrieve")
    ap.add_argument("--rerank_url", type=str, default="http://127.0.0.1:8001/retrieve")
    ap.add_argument("--bm25_topk", type=int, default=40)
    ap.add_argument("--rerank_topk_retrieval", type=int, default=40)
    ap.add_argument("--rerank_topk", type=int, default=3)
    ap.add_argument("--preview_k", type=int, default=3)
    ap.add_argument("--query", action="append", default=[])
    args = ap.parse_args()

    queries = args.query or DEFAULT_QUERIES

    print("BM25 URL:", args.bm25_url, "topk=", args.bm25_topk)
    bm25 = call_bm25(args.bm25_url, queries, args.bm25_topk)

    print("Rerank URL:", args.rerank_url, "retrieval_topk=", args.rerank_topk_retrieval, "rerank_topk=", args.rerank_topk)
    rr = call_rerank(args.rerank_url, queries, args.rerank_topk_retrieval, args.rerank_topk)

    for q, bm_items, rr_items in zip(queries, bm25, rr):
        print("\n====================")
        print("Q:", q)
        print("\n[BM25 top{} preview]".format(args.preview_k))
        for i, (s, t, snip) in enumerate(topk_preview(bm_items, args.preview_k), 1):
            print(f"{i}. score={s:.3f} title={t} snip={snip}")

        print("\n[BM25+Rerank top{} preview]".format(args.preview_k))
        for i, (s, t, snip) in enumerate(topk_preview(rr_items, args.preview_k), 1):
            print(f"{i}. score={s:.3f} title={t} snip={snip}")


if __name__ == "__main__":
    main()

