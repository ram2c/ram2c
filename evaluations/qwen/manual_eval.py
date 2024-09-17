import re, os
import numpy as np
import random

####################################################
# change the seed to evaluate on H/T/S dimension
# 42: humanized communication
# 45: teaching expertise
# 48: safety and ethics
####################################################
random.seed(42) # 保证每个人题目相同,do not change
np.random.seed(42) # 保证每个人题目相同, do not change


# negative response samples
with open('/home/hhy/RAM2C/evaluations/qwen/dpo_eval_res_qwen.txt', 'r', encoding='utf-8') as f:
    dpo_eval_res_qwen = ''.join(f.readlines())
    qwen_response = re.split(r'\d+, ', dpo_eval_res_qwen)[1:]

# positive response samples
with open('/home/hhy/RAM2C/evaluations/qwen/dpo_eval_res_qwen_dpo.txt', 'r', encoding='utf-8') as f:
    dpo_eval_res_qwen_dpo = ''.join(f.readlines())
    qwen_dpo_response = re.split(r'\d+, ', dpo_eval_res_qwen_dpo)[1:]
# print(len(qwen_response), len(qwen_dpo_response))

num_samples = 25

random_index = list(range(len(qwen_dpo_response)))
np.random.shuffle(random_index)
random_index = random_index[:num_samples] # 题目组,每个志愿者都一样

np.random.seed()
random.seed()
np.random.shuffle(random_index) # 题目顺序,每个志愿者都不一样

count = 0
rating_log = []
for i, index in enumerate(random_index[:num_samples]):
    os.system('cls')
    if i % 10 == 0: print(count/(i+1))
    if np.random.random() > 0.5: # 正样本放在A选项
        flag = input(f'{i}/{num_samples}: \n文本1:\n'+qwen_dpo_response[index]+'\n\n文本2:\n'+qwen_response[index]+'\n\n\n\n\n')
        if flag == "": # 输入回车，选择第一段文字
            count += 1
            rating_log.append([index, 4])
        elif flag == "  ": # 输入2个空格，表示中立
            count += 0.5
            rating_log.append([index, 2])
        else:
            rating_log.append([index, 0])
    else: # 负样本放在A选项
        flag = input(f'{i}/100: \n文本1:\n'+qwen_response[index]+'\n\n文本2:\n'+qwen_dpo_response[index]+'\n\n\n\n\n')
        if flag == " ": # 输入空格，选择第二段文字
            count += 1
            rating_log.append([index, 4])
        elif flag == "  ": # 输入2个空格，表示中立
            count += 0.5
            rating_log.append([index, 2])
        else:
            rating_log.append([index, 0])
    if i % 10 == 0:
        print(count/(i+1))

print(rating_log)

with open('./manual_rating.txt', 'w', encoding='utf-8') as file:
    # 遍历列表，将每个元素写入文件
    for item in rating_log:
        file.write(str(item[0])+','+str(item[1])+'\n')  # 在每个元素后添加换行符，以确保写入文件时每个元素占一行

print("列表已成功写入'manual_rating.txt'")
print(count)