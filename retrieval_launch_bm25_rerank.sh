file_path=/root/autodl-tmp/data
index_file=$file_path/bm25
corpus_file=$file_path/wiki-18.jsonl

retriever_name=bm25
reranker_path=/root/autodl-tmp/models/BAAI_bge-reranker-base
server_port=${PORT:-6006}

export HF_HOME=/root/autodl-tmp/hf
export HF_DATASETS_CACHE=/root/autodl-tmp/hf/datasets
export TRANSFORMERS_CACHE=/root/autodl-tmp/hf/transformers
export TMPDIR=/root/autodl-tmp/tmp
mkdir -p "$HF_HOME" "$HF_DATASETS_CACHE" "$TRANSFORMERS_CACHE" "$TMPDIR"

python search_r1/search/retrieval_rerank_server.py --index_path $index_file \
                                                   --corpus_path $corpus_file \
                                                   --retrieval_topk 40 \
                                                   --retriever_name $retriever_name \
                                                   --reranking_topk 3 \
                                                   --reranker_model $reranker_path \
                                                   --reranker_batch_size 32 \
                                                   --port $server_port

