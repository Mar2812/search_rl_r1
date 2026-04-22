import argparse
import json
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from urllib import request as urlrequest

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Retrieve Gateway")


class SearchRequest(BaseModel):
    queries: List[str]
    topk_retrieval: int = 10
    topk_rerank: int = 3
    return_scores: bool = False
    batch_size: int | None = None


BACKEND_URLS: List[str] = []
HTTP_TIMEOUT = 3600


def split_round_robin(items: List[str], shards: int) -> List[List[tuple[int, str]]]:
    buckets: List[List[tuple[int, str]]] = [[] for _ in range(shards)]
    for i, q in enumerate(items):
        buckets[i % shards].append((i, q))
    return buckets


def call_backend(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


@app.post("/retrieve")
def retrieve(request: SearchRequest):
    total = len(request.queries)
    if total == 0:
        return {"result": []}
    if not BACKEND_URLS:
        raise HTTPException(status_code=500, detail="No backend configured.")

    shards = split_round_robin(request.queries, len(BACKEND_URLS))
    merged_results: List[Any] = [None] * total

    futures = []
    with ThreadPoolExecutor(max_workers=len(BACKEND_URLS)) as pool:
        for idx, shard in enumerate(shards):
            if not shard:
                continue
            original_indices = [x[0] for x in shard]
            shard_queries = [x[1] for x in shard]
            payload = {
                "queries": shard_queries,
                "topk_retrieval": request.topk_retrieval,
                "topk_rerank": request.topk_rerank,
                "return_scores": request.return_scores,
            }
            if request.batch_size is not None:
                payload["batch_size"] = request.batch_size

            future = pool.submit(call_backend, BACKEND_URLS[idx], payload)
            futures.append((future, original_indices, BACKEND_URLS[idx]))

        for future, original_indices, backend in futures:
            try:
                resp = future.result()
            except Exception as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Backend request failed: {backend}, error: {exc}",
                ) from exc
            shard_result = resp.get("result", [])
            if len(shard_result) != len(original_indices):
                raise HTTPException(
                    status_code=502,
                    detail=f"Invalid backend response length from {backend}",
                )
            for pos, item in zip(original_indices, shard_result):
                merged_results[pos] = item

    if any(x is None for x in merged_results):
        raise HTTPException(status_code=502, detail="Incomplete merged response.")
    return {"result": merged_results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Single-port retrieve gateway")
    parser.add_argument(
        "--backend_urls",
        type=str,
        required=True,
        help="Comma-separated backend URLs, e.g. http://127.0.0.1:7001/retrieve,...",
    )
    parser.add_argument("--port", type=int, default=6008, help="Gateway listen port")
    parser.add_argument("--timeout", type=int, default=3600, help="Backend request timeout in seconds")
    args = parser.parse_args()

    BACKEND_URLS = [x.strip() for x in args.backend_urls.split(",") if x.strip()]
    HTTP_TIMEOUT = args.timeout

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=args.port)
