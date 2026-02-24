# # Load model directly
# from transformers import AutoTokenizer, AutoModelForCausalLM

# tokenizer = AutoTokenizer.from_pretrained("Doctor-Shotgun/MS3.2-24B-Magnum-Diamond")
# model = AutoModelForCausalLM.from_pretrained("Doctor-Shotgun/MS3.2-24B-Magnum-Diamond")
# messages = [
#     {"role": "user", "content": "Who are you?"},
# ]
# inputs = tokenizer.apply_chat_template(
# 	messages,
# 	add_generation_prompt=True,
# 	tokenize=True,
# 	return_dict=True,
# 	return_tensors="pt",
# ).to(model.device)

# outputs = model.generate(**inputs, max_new_tokens=40)
# print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))

import requests
import json

def test_raw_ollama():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gemma3:27b",
        "prompt": "Say hello world in one word.",
        "stream": False
    }
    print("Sending request to Ollama... wait for it.")
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json().get('response')}")
    except Exception as e:
        print(f"Error: {e}")

test_raw_ollama()