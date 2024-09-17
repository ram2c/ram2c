import os
from RAG import process_docs
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from zhipuai import ZhipuAI
from openai import OpenAI
from api_key import *
from prompts import rag_fusion_prompt, rag_fusion_system_prompt

def vector_search(db:Chroma, query:str, filter:dict[str,str]| None=None, retrieval_k:int=4):
    '''
    Vector search based on one query and filter, return search results with certainty score
    return:
        search_results={page_content: certainty}
    '''
    search_results = {}
    
    # retrieved_docs=List[Tuple[Document, float]]
    retrieved_docs = db.similarity_search_with_score(
        query, 
        k=retrieval_k,
        filter=filter,
        )
    # print('len of retrieved_docs: ', len(retrieved_docs))
    for i in retrieved_docs:
        search_results[i[0].page_content] = i[1]
    return search_results


def reciprocal_rank_fusion(
    search_results_dict:dict[str,dict[str,float]], 
    verbose=False,
    ):
    '''
    implementation of reciprocal rank fusion (RRF) algorithm
    input: 
        search_results_dict={query: {doc: score}}
        HS_vector: np.ndarray, historical sampling vector, 数据库中所有文档的历史采样次数
        每一个查询语句对应一个字典，字典里是该查询语句对应的文档和对应的分数
    
    return: reranked_results={doc: score}
    '''
    fused_scores = {}
    # query是一条查询语句, doc_and_scores是对应的docs和对应的scores
    for query, doc_and_scores in search_results_dict.items():
        
        # rank是文档的排序, doc是文档内容, score是文档的分数
        for rank, (doc, score) in enumerate(sorted(doc_and_scores.items(), key=lambda x: x[1], reverse=True)):
            if doc not in fused_scores:
                fused_scores[doc] = 0
            previous_score = fused_scores[doc]
            fused_scores[doc] += 1 / (rank + 60)
            if verbose: 
                print(f"Updating score for {doc} from {previous_score} to {fused_scores[doc]} based on rank {rank} in query '{query}'")

    reranked_results = {doc: score for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)}
    if verbose: print("Final reranked results:", reranked_results)
    return reranked_results

def rewritings_rrf(db: Chroma, query:str, model_name='glm-4-plus'):
    '''
    return {doc: score}
    '''
    if 'glm-4' in model_name: client = ZhipuAI(api_key=glm_key)
    else:                     client = OpenAI(api_key=gpt_key)
    response = client.chat.completions.create(
        model=model_name, #   gpt-4-turbo-preview
        messages=[
            {"role": "system", "content": rag_fusion_system_prompt},
            {"role": "user", "content": rag_fusion_prompt.format(original_query=query)},
            {"role": "user", "content": f"OUTPUT (3 queries):"}
            ]
        )
    generated_queries = response.choices[0].message.content.strip().split("\n") # response.choices[0]["message"]["content"].strip().split("\n")
    generated_queries.append(query)
    # print(generated_queries)
    all_results = {}
    for query in generated_queries:
        search_results = vector_search(db, query, filter=None, retrieval_k=3) # {'role': 'teacher-record'}
        all_results[query] = search_results
    
    reranked_results = reciprocal_rank_fusion(
        all_results,
        verbose=False,
        )
    return reranked_results

def get_vec_db(path='./textdata/psy_db/') -> Chroma:
    ef = HuggingFaceEmbeddings(model_name= '/mnt/d/LLM/bge-m3/', model_kwargs={'device': 'cuda'})

    if len(os.listdir(path)) == 0:
        split_docs = process_docs()
        db = Chroma.from_documents(
            collection_name='RAM2C', 
            documents=split_docs, 
            embedding=ef, 
            persist_directory=path,
            )
    else:
        print(f'Load existing db from {path}')
        db = Chroma(
            collection_name='RAM2C',
            persist_directory=path, 
            embedding_function=ef,
            )
    return db