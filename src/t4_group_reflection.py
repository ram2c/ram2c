'''
Group reflection implementation
2024.9.14
'''
from tqdm import tqdm
from prompts import group_reflection_prompt, group_reflection_system
from chat_models import ChatQwen
from openai import OpenAI
from zhipuai import ZhipuAI
from api_key import glm_key, gpt_key


fields_3 = [
    'teaching language style', 
    'content and knowledge', 
    'logic and reasoning'
    ] # 3 agents

fields_5 = [
    'teaching language style', 
    'teaching language style', 
    'content and knowledge', 
    'emotional support',
    'logic and reasoning',
    ] # 5 agents

fields_7 = [
    'teaching language style', 
    'teaching language style', 
    'content and knowledge', 
    'content and knowledge',
    'logic and reasoning',
    'logic and reasoning',
    'emotional support',
    ] # 7 agents

def group_reflection(question:str, answer:str, reranked_results:list[str], field: str) -> list[str]:
    '''
    调用一个智能体, 对若干文档进行reflection, 返回decision_list
    '''
    glm4_client = ZhipuAI(api_key=glm_key)
    decision_list = []
    for retr in tqdm(reranked_results):
        response = glm4_client.chat.completions.create(
            model='glm-4-plus', # glm-4  gpt-4-turbo-preview
            messages=[
                {"role": "system", "content": group_reflection_system},
                {"role": "user", "content": group_reflection_prompt.format(
                    question=question,
                    answer=answer,
                    document=retr,
                    field=field,
                    )
                 },
                ]
            )
        decision_list.append(response.choices[0].message.content)
        
    return decision_list

def group_reflection_gpt(question:str, answer:str, reranked_results:dict, field: str) -> list[str]:
    '''
    调用一个智能体, 对`reranked_results`进行reflection, 返回decision_list
    '''
    openai_client = OpenAI(api_key=gpt_key)
    decision_list = []
    for retr in tqdm(list(reranked_results.keys())):
        response = openai_client.chat.completions.create(
            model='gpt-4o-mini-2024-07-18', # glm-4  gpt-4-turbo-preview gpt-3.5-turbo
            messages=[
                {"role": "system", "content": group_reflection_system},
                {"role": "user", "content": group_reflection_prompt.format(
                    question=question,
                    answer=answer,
                    document=retr,
                    field=field,
                    )
                 },
                ]
            )
        decision_list.append(response.choices[0].message.content)
        # print(response.usage.total_tokens)
    print(decision_list)
    return decision_list

def group_reflection_qwen(qwen_client:ChatQwen, question: str, answer:str, reranked_results:dict, field: str) -> list[str]:
    
    decision_list = []
    for retr in tqdm(list(reranked_results.keys())):
        response = qwen_client.completion(
            prompt=group_reflection_prompt.format(
                question=question,
                answer=answer,
                document=retr,
                field=field,
                ),
            system_prompt=group_reflection_system,
            )
        decision_list.append(response)
    print(decision_list)
    return decision_list