file_path=/home/machao123/data
index_file=$file_path/bm25
corpus_file=$file_path/wiki18_extracted/data00/jiajie_jin/flashrag_indexes/wiki_dpr_100w/wiki_dump.jsonl
retriever_name=bm25

python search_r1/search/retrieval_server.py --index_path $index_file \
                                            --corpus_path $corpus_file \
                                            --topk 3 \
                                            --retriever_name $retriever_name

# export HF_ENDPOINT=https://hf-mirror.com
# export HUGGINGFACE_HUB_BASE_URL=https://hf-mirror.com
# save_path=/home/machao123/data
# hf download PeterJinGo/wiki-18-bm25-index --repo-type dataset --local-dir $save_path

# export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(which javac)")")")"
# export PATH="$JAVA_HOME/bin:$PATH"
# bash retrieval_launch_bm25.sh