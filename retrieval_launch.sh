
file_path=/root/autodl-tmp/data
index_file=$file_path/e5_Flat.index
corpus_file=$file_path/wiki-18.jsonl
retriever_name=e5
retriever_path=intfloat/e5-base-v2

python search_r1/search/retrieval_server.py --index_path $index_file \
                                            --corpus_path $corpus_file \
                                            --topk 3 \
                                            --retriever_name $retriever_name \
                                            --retriever_model $retriever_path
                                            # --faiss_gpu

# export HF_ENDPOINT=https://hf-mirror.com
# export HUGGINGFACE_HUB_BASE_URL=https://hf-mirror.com
# export HF_HOME=/root/autodl-tmp/hf
# export HF_DATASETS_CACHE=/root/autodl-tmp/hf/datasets
# export TRANSFORMERS_CACHE=/root/autodl-tmp/hf/transformers
# export TMPDIR=/root/autodl-tmp/tmp
# mkdir -p "$HF_HOME" "$HF_DATASETS_CACHE" "$TRANSFORMERS_CACHE" "$TMPDIR"
# bash retrieval_launch.sh