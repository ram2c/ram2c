'''
calculate the inter-annotator agreement (IAA) score
'''

import os
import numpy as np
from statsmodels.stats.inter_rater import fleiss_kappa

# 初始化一个25x3的矩阵，每行对应一道题目，每列对应一个选项
matrix = np.zeros((25, 3), dtype=int)

# 读取每份问卷
files = os.listdir('/home/hhy/RAM2C/evaluations/qwen/results')
for file_name in files:
    with open(os.path.join('/home/hhy/RAM2C/evaluations/qwen/results', file_name), 'r') as f:
        lines = f.readlines()
        for line in lines:
            idx = int(line.split(', ')[0]) # 题目编号
            if '1' in line.split(', ')[1]: # 答案A
                matrix[idx, 0] += 1
            elif '0.5' in line.split(', ')[1]: # 答案B
                matrix[idx, 1] += 1
            else: # 答案C
                matrix[idx, 2] += 1
print(matrix.sum(1))
# 假设数据为以下格式：每个志愿者的答案（题目编号: 答案）
# 0表示选A，1表示选B
# 这里只是一个示例，实际数据需要根据你的情况填充
# answers = {
#     1: {1: 0, 2: 1, 3: 0, 4: 1, 5: 0},  # 志愿者1的答案
#     2: {6: 1, 7: 0, 8: 0, 9: 1, 10: 0}, # 志愿者2的答案
#     3: {11: 0, 12: 0, 13: 1, 14: 0, 15: 1}, # 志愿者3的答案
#     4: {16: 1, 17: 1, 18: 0, 19: 0, 20: 1}, # 志愿者4的答案
#     5: {21: 0, 22: 1, 23: 1, 24: 0, 25: 0}, # 志愿者5的答案
# }


# Fleiss' Kappa要求每道题目必须有相同的评估人数
kappa = fleiss_kappa(matrix, method='uniform')
print(f"Fleiss' Kappa: {kappa}")
