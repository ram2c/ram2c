import numpy as np
from prompts import *
from openai import OpenAI
from zhipuai import ZhipuAI
from api_key import *
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

openai_client = OpenAI(api_key=gpt_key)
glm4_client = ZhipuAI(api_key=glm_key)


def get_novel_chunks(chunk_size=300, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    novel = TextLoader('./textdata/author/robinson/robinson.txt', encoding='utf-8').load()
    question_related_chunks = splitter.split_documents(novel)
    print('number of novel chunks: ', len(question_related_chunks))
    return question_related_chunks


# teacher_system_prompt_english = '''
# You are a talented Chinese language teacher with a deep understanding of literature teaching.
# '''

question_revision_prompt = '''
You are going to check whether the question is relevant to the topic. Think step by step. Use Chinese.
Question: {ques}.
Topic: {topic}.
If so, copy the question as your rivision. If not, give your revision to the question.
Your revision:
'''

question_integration_prompt = '''
You are going to integrate the analyses of Chinese teachers, to make the final revision more relevant to the topic. Use Chinese.
Raw Question: {ques}.
Topic: {topic}.
Analysis1: {analysis1}.
Analysis2: {analysis2}.
Analysis3: {analysis3}.

Only output your final integration. ONLY INCLUDE ONE QUESTION IN REVISION. DO NOT output other content.
Your revision:
'''
def generate_questions(question_related_chunks):
    total_tokens = 0
    questions = []
    for i, doc in enumerate(question_related_chunks[628:]):
        topic_index = np.random.randint(0, 7)
        topic = learning_directions[topic_index]

        # raw_ques = openai_client.chat.completions.create(
        #     model="gpt-4o-mini-2024-07-18", #  gpt-4o-2024-08-06   gpt-4-turbo-2024-04-09
        #     messages=[
        #         {"role": "system", "content": teacher_system_prompt_english},
        #         {"role": "user", "content": teacher_question_prompt_new.format(context=doc.page_content, topic=topic)},
        #         ],
        #     temperature=0.7, seed=42, n=1,)
        raw_ques = glm4_client.chat.completions.create(
            model='glm-4-plus',
            messages=[
                {"role": "system", "content": teacher_system_prompt_english},
                {"role": "user", "content": teacher_question_prompt_new.format(context=doc.page_content, topic=topic)},
            ]
        )
        # analysis1 = glm4_client.chat.completions.create(
        #     model='glm-4-air',
        #     messages=[{"role": "system", "content": teacher_system_prompt_english},
        #               {"role": "user", "content": question_revision_prompt.format(ques=raw_ques.choices[0].message.content, topic=topic)}],
        #     temperature=1.0)

        # revision = glm4_client.chat.completions.create(
        #     model='glm-4-air',
        #     messages=[{"role": "system", "content": teacher_system_prompt_english},
        #               {"role": "user", "content": question_integration_prompt.format(ques=raw_ques.choices[0].message.content, topic=topic,
        #                                                                              analysis1=analysis1, analysis2=analysis2, analysis3=analysis3)}],
        #     temperature=1.0)
        
        total_tokens += raw_ques.usage.total_tokens
        # total_tokens += analysis1.usage.total_tokens
        # total_tokens += revision.usage.total_tokens
        print(i+628, topic_index, raw_ques.choices[0].message.content, '\n\n')
        
        questions.append(raw_ques.choices[0].message.content)
    print('total tokens: ', total_tokens, '\n\n\n')
    return questions

if __name__ == '__main__':

    question_related_chunks = get_novel_chunks()

    questions = generate_questions(question_related_chunks)