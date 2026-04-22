#!/usr/bin/env python3
import argparse
import json
import threading
import time
import urllib.request


def build_payload(n: int, topk_retrieval: int, topk_rerank: int, batch_size: int):
    return {
        "queries": [f"测试查询 {i}: 北京是中国的首都吗？" for i in range(n)],
        "topk_retrieval": topk_retrieval,
        "topk_rerank": topk_rerank,
        "batch_size": batch_size,
        "return_scores": False,
    }


def post_once(url: str, payload: dict, timeout_s: int):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, body


def run_case(url: str, n: int, topk_retrieval: int, topk_rerank: int, batch_size: int, timeout_s: int):
    payload = build_payload(n, topk_retrieval, topk_rerank, batch_size)

    stop = threading.Event()
    t0 = time.perf_counter()

    def ticker():
        while not stop.wait(2.0):
            elapsed = time.perf_counter() - t0
            print(f"[client] n={n} still waiting... elapsed={elapsed:.1f}s", flush=True)

    th = threading.Thread(target=ticker, daemon=True)
    th.start()

    try:
        code, body = post_once(url, payload, timeout_s)
    finally:
        stop.set()
        th.join(timeout=1.0)

    elapsed = time.perf_counter() - t0
    result_count = -1
    try:
        parsed = json.loads(body)
        result_count = len(parsed.get("result", []))
    except Exception:
        pass

    print(
        f"[client] n={n} done status={code} elapsed={elapsed:.3f}s result_count={result_count}",
        flush=True,
    )

    return elapsed


def main():
    parser = argparse.ArgumentParser(description="Benchmark /retrieve latency with live progress.")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:6006/retrieve")
    parser.add_argument("--cases", type=str, default="256,512", help="Comma separated query counts, e.g. 256,512")
    parser.add_argument("--topk_retrieval", type=int, default=40)
    parser.add_argument("--topk_rerank", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=64, help="Pass through to server for batch progress.")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--timeout_s", type=int, default=7200)
    args = parser.parse_args()

    cases = [int(x.strip()) for x in args.cases.split(",") if x.strip()]
    print(f"[client] target={args.url} cases={cases} repeat={args.repeat}", flush=True)

    for n in cases:
        times = []
        for r in range(1, args.repeat + 1):
            print(f"[client] case n={n} run={r}/{args.repeat} start", flush=True)
            t = run_case(
                url=args.url,
                n=n,
                topk_retrieval=args.topk_retrieval,
                topk_rerank=args.topk_rerank,
                batch_size=args.batch_size,
                timeout_s=args.timeout_s,
            )
            times.append(t)

        avg = sum(times) / len(times)
        print(
            f"[client] summary n={n} avg={avg:.3f}s min={min(times):.3f}s max={max(times):.3f}s",
            flush=True,
        )


if __name__ == "__main__":
    main()

