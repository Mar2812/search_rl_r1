file_path=/home/machao123/data
index_file=$file_path/bm25
corpus_file=$file_path/wiki18_extracted/data00/jiajie_jin/flashrag_indexes/wiki_dpr_100w/wiki_dump.jsonl

retriever_name=bm25
reranker_path=/home/machao123/models/BAAI_bge-reranker-base

python search_r1/search/retrieval_rerank_server.py --index_path $index_file \
                                                   --corpus_path $corpus_file \
                                                   --retrieval_topk 40 \
                                                   --retriever_name $retriever_name \
                                                   --reranking_topk 3 \
                                                   --reranker_model $reranker_path \
                                                   --reranker_batch_size 32 \
                                                   --port 8001

