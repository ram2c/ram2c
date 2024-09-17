import os, json
import numpy as np

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langchain_chroma import Chroma

def load_docs(splitter:RecursiveCharacterTextSplitter, role:str, type:str, file_dir:str):
    '''
    load raw documents from file_dir
    
    role: 'teacher', 'psychologist', 'ethics'
    type: book, record, theory
    retern: list of Document objects
    '''
    split_docs = []
    if role != 'ethics':
        file_list = os.listdir(file_dir)
        for file_name in file_list:
            document = TextLoader(file_dir+file_name, encoding='utf-8').load()
            split_doc = splitter.split_documents(document)
            
            # assign metadata 'role' and 'file_name' to each split document
            for item in split_doc:
                item.metadata['role'] = role
                item.metadata['type'] = type
                item.metadata['file_name'] = file_name.split('.txt')[0]
            
            # merge split documents from different txt into one list
            split_docs.extend(split_doc)
    else:
        with open(file_dir+'typical_safety_scenarios.json', 'r', encoding='utf-8') as json_file:
            prompts = json.load(json_file)
            for key in prompts.keys():
                for item in prompts[key]:
                    split_docs.append(Document(page_content='prompt:' + item['prompt'] + 'response:' + item['response'] + 'type:',
                                                metadata={'source':'typical_safety_scenarios.json',
                                                            'role': role,
                                                            'type': key,
                                                            'file_name': 'typical_safety_scenarios.json',
                                                            })
                                      )
    return split_docs

def process_docs():
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50) 
    split_docs = []
    # Chinese language teachers
    split_docs.extend(load_docs(splitter, role='teacher-record', type='teacher-record', file_dir='/home/hhy/RAM2C/textdata/teacher/record/text/'))
    # split_docs.extend(load_docs(splitter, role='teacher-books-robinson', type='teacher-books', file_dir='/home/hhy/RAM2C/textdata/teacher/books/robinson/'))
    # split_docs.extend(load_docs(splitter, role='teacher-theory', type='teacher-theory', file_dir='/home/hhy/RAM2C/textdata/teacher/theory/text/'))
    # educational psychologists
    # split_docs.extend(load_docs(splitter, role='psychologist', type='psychologist-theory', file_dir='/home/hhy/RAM2C/textdata/psycho/text/'))
    # ethical safety experts
    # split_docs.extend(load_docs(splitter, role='ethics', type='prompt', file_dir='./textdata/ethics/'))

    tmp = [doc for doc in split_docs if len(doc.page_content) > 15]

    print('number of raw documents:', len(split_docs))
    print('number of filtered documents:', len(tmp))
    print('Too short documents:', len(split_docs) - len(tmp))
    split_docs = tmp
    return split_docs

# from FlagEmbedding import FlagReranker
# reranker = FlagReranker(
#     model_name_or_path='D:/LLM models/embed_models/BAAI_bge-reranker-v2-m3/', 
#     use_fp16=True,
#     device='cuda',
#     )

# reranker = CrossEncoder(
#     model_name='D:/LLM models/embed_models/maidalun1020_bce-reranker-base_v1/', 
#     max_length=512,
#     )

if __name__ == '__main__':
    db = get_vec_db(path='/home/hhy/RAM2C/textdata/edu_theory_db/')
    print(db._collection.count())

    db = get_vec_db(path='/home/hhy/RAM2C/textdata/novel_db/')
    print(db._collection.count())

    db = get_vec_db(path='/home/hhy/RAM2C/textdata/psy_theory_db/')
    print(db._collection.count())

    db = get_vec_db(path='/home/hhy/RAM2C/textdata/record_db/')
    print(db._collection.count())
    db.search()