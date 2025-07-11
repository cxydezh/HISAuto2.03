import requests
import json
import tkinter as tk

response = requests.post(
    "http://172.17.40.16:11434/api/generate",
    json={
        "model": "deepseek-r1:32b",
        "prompt": "解释量子纠缠的基本概念",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "max_tokens": 512,
            "top_p": 0.95,
            "top_k": 0
            }
        }
    )
response.raise_for_status()
result = response.json()["response"]
print(result)
def ask_ollama(prompt, model="linux6200/bge-reranker-v2-m3:latest"):
    url = "http://172.17.40.16:11434/api/generate"
    payload = {
        "model": model, 
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    try:
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        return f"Error: {str(e)}"

# 示例使用


if __name__ == "__main__":
    root = tk.Tk()
    root.mainloop()
    answer = ask_ollama("解释量子纠缠的基本概念")
    print("模型回答:", answer)