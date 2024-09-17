import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import OpenAI
from zhipuai import ZhipuAI
from api_key import gpt_key, glm_key
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

class ChatQwen:
    def __init__(self, model_path="/mnt/d/LLM/Qwen2-0.5B-Instruct/", top_p:float=0.9, dtype=torch.bfloat16):
        '''bf16 和 fp16 差距不大, 推理速度比全精度稍慢, 8bit占用显存最低, 但推理速度慢6倍
        '''
        self.model_path = model_path
        self.change_generation_config(top_p)
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, 
            device_map="cuda",
            torch_dtype=dtype,
            )
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=model_path, 
            device_map="cuda",
            )
    
    def change_generation_config(self, top_p: float):
        import json
        with open(self.model_path + 'generation_config.json', 'r') as file:
            data = json.load(file)
            if 'top_p' in data: data['top_p'] = top_p
        with open(self.model_path + 'generation_config.json', 'w') as file:
            json.dump(data, file, indent=4)
    
    def completion(self, prompt, system_prompt="You are a helpful assistant."):
        '''return string'''
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            )
        model_inputs = self.tokenizer([text], return_tensors="pt").to('cuda')
        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=5000,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response


class ChatvLLM:
    def __init__(self, model_path, temperature=0.7, max_tokens=1024) -> None:
        self.model_path = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.sampling_params = SamplingParams(top_p=0.7, temperature=temperature, max_tokens=max_tokens, repetition_penalty=1.02)
        self.llm = LLM(
            model=model_path,
            trust_remote_code=True,
            tensor_parallel_size=1,
            gpu_memory_utilization=0.95,
            max_model_len=2048,
            )
    def completion(self, prompt:str, system_prompt:str) -> str:
        prompt = [{"role": "system", "content": system_prompt},
                  {"role": "user", "content": prompt}]
        input_text = self.tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
        outputs = self.llm.generate(prompts=input_text, sampling_params=self.sampling_params)
        return outputs[0].outputs[0].text

if __name__ == '__main__':
    # local Qwen models
    qwen_client = ChatQwen(
        model_path='/mnt/d/LLM/Qwen2-0.5B-Instruct/',
        # model_path='D:/LLM models/Qwen1.5-1.8B-Chat/',
        # model_path='D:/LLM models/Qwen1.5-4B-Chat/',
        # model_path='D:/LLM models/qwen1.5-4B-dpo/',
        # model_path='D:/LLM models/Qwen1.5-7B-Chat/',
        # model_path='D:/LLM models/Qwen1.5-7B-Chat-GPTQ-Int8/',
        top_p=0.8,
        dtype=torch.bfloat16,
        )

    # response = qwen_client.completion('我睡不着觉')
    # response = qwen_client.completion('北京和三亚哪个城市纬度更高？Think step by step')
    # print(response)