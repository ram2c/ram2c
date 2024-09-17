'''
generate student answers for the topic.
2024.9.15
'''
from prompts import *
import re
from zhipuai import ZhipuAI
from openai import OpenAI
from api_key import *
from t1_generate_topics import get_novel_chunks

def generate_student_answer(question, related_content, client, model_name):
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": student_sys.format(
                gender='boy',
                char1=student_characters_english[0],
                char2=student_characters_english[2],
                book='Robinson Crusoe')
             },
            {"role": "user", "content": student_answer_prompt.format(
                related_content=related_content,
                question=question)
             }
            ],
        temperature=0.8)
    return completion.choices[0].message.content

if __name__ == '__main__':

    glm4_client = ZhipuAI(api_key=glm_key)
    openai_client = OpenAI(api_key=gpt_key)
    with open('/home/hhy/RAM2C/generated_data/questions_20240915.txt', 'r', encoding='utf-8') as f:
        questions = re.split('\d+ \d ', ''.join(f.readlines()))[1:]
        question_related_chunks = get_novel_chunks(chunk_size=300, chunk_overlap=50)

    for i, (ques, related_content) in enumerate(zip(questions, question_related_chunks)):
        answer = generate_student_answer(ques, related_content, glm4_client, model_name='glm-4-plus') # "gpt-4-turbo-preview" gpt-4o-mini
        print(i, answer, '\n\n')
    # answer = generate_student_answer(
    #     questions, 
    #     question_related_contents[375], 
    #     openai_client,                 # glm4_client, 
    #     model_name='gpt-3.5-turbo'
    #     ) # "gpt-4-turbo-preview"
    # print(answer)