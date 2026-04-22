#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"

# Internal worker ports (not exposed externally)
PORTS=(7001 7002 7003 7004)
GPUS=(0 1 2 3)

echo "Starting 4 backend workers..."
for i in "${!GPUS[@]}"; do
  gpu="${GPUS[$i]}"
  port="${PORTS[$i]}"
  log_file="${LOG_DIR}/worker_gpu${gpu}.log"
  echo "  GPU ${gpu} -> port ${port} (log: ${log_file})"
  CUDA_VISIBLE_DEVICES="${gpu}" PORT="${port}" nohup bash "${ROOT_DIR}/retrieval_launch_bm25_rerank.sh" > "${log_file}" 2>&1 &
done

sleep 2

backend_urls="http://127.0.0.1:7001/retrieve,http://127.0.0.1:7002/retrieve,http://127.0.0.1:7003/retrieve,http://127.0.0.1:7004/retrieve"
gateway_log="${LOG_DIR}/gateway_6008.log"
echo "Starting gateway on port 6008 (log: ${gateway_log})"
nohup python "${ROOT_DIR}/search_r1/search/retrieve_gateway.py" \
  --backend_urls "${backend_urls}" \
  --port 6008 \
  > "${gateway_log}" 2>&1 &

echo ""
echo "All services launched."
echo "Gateway URL: http://127.0.0.1:6008/retrieve"
echo "Check logs:"
echo "  tail -f ${LOG_DIR}/gateway_6008.log"
echo "  tail -f ${LOG_DIR}/worker_gpu0.log"
echo "  tail -f ${LOG_DIR}/worker_gpu1.log"
echo "  tail -f ${LOG_DIR}/worker_gpu2.log"
echo "  tail -f ${LOG_DIR}/worker_gpu3.log"
