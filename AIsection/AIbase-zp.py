import requests
import json
import tkinter as tk
#视频理解示例、上传视频URL
from zhipuai import ZhipuAI

print("开始")
client = ZhipuAI(api_key="783620bfceb1a3a8766a383954f23c32.BVqhPrWuaWF2F8jg") # 填写您自己的APIKey
response = client.chat.completions.create(
    model="glm-z1-flash",  # 填写需要调用的模型名称
    messages=[
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "你好，请问你是谁？"
          }
        ]
      }
    ]
)
print(response.choices[0].message)