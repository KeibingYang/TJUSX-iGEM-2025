import base64
from openai import OpenAI
import os
import random
import json
import requests

API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = ""

client = OpenAI(
    api_key=api_key,
    base_url=API_BASE,  # 关键：指定自定义 API 地址
)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# 一共是5个选项，这部分专门针对good选项，就按照之前设计的几个选项，最后加入no defect即可。
def random_options():
    options = ["color","scratch","crush","texture","dirty"]
    selected = random.sample(options, 4)
    selected.append("no defect")
    random.shuffle(selected)
    return selected


# 因为存在combined，所以这里就是以异常文件夹为最小单位，每次跑之前都需要需要大家手动修改一下，
folder_path = r"Defect_Spectrum\DS-DAGM\good"
# 自定义就可以，不需要别的，最后返回给我一个该文件夹目录下总的cot json文件即可。
output_path = os.path.join(folder_path, "noqa_results.jsonl")  # 写成 .jsonl

for root, dirs, files in os.walk(folder_path):

    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            num, _ = os.path.splitext(filename)
            image_path = os.path.join(folder_path, filename)
            image_path = image_path.replace(os.sep, '/')
            json_path = os.path.join(folder_path, num + '.json')
            json_path = json_path.replace(os.sep, '/')
            base64_image = encode_image(image_path)

            select_options = random_options()
            answer_index = select_options.index("no defect")
            answer_letter = chr(65 + answer_index)

            defect_options = "(A)" + select_options[0] + "(B)" + select_options[1] + \
                             "(C)" + select_options[2] + "(D)" + select_options[3] + "(E)" + select_options[4]

            prompt = "Which of the following options correctly identifies the defects in the image?"
            prompt = prompt + "(A)" + select_options[0]
            prompt = prompt + "(B)" + select_options[1]
            prompt = prompt + "(C)" + select_options[2]
            prompt = prompt + "(D)" + select_options[3]
            prompt = prompt + "(E)" + select_options[4]
            prompt = prompt + ",The correct answer is " + answer_letter + "."
            prompt += " Begin with \"The answer is " + "\"(X = option), then immediately "
            prompt += "state \"The defect type is " + "no defect" + "\", appending an explanation.Analyze the entire image to support your judgment.For each incorrect option, provide a rejection reason citing specific missing features and append \"Likely cause:\" with a explanation.No paragraph breaks, and avoid connectors."

            print(prompt)

            completion = client.chat.completions.create(
                model="qwen-vl-max",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
            )

            results = {
                "image_path": image_path,
                "coordinates": "NULL",
                "type": "no defect",
                "conversation": {
                    "Question": prompt,
                    "options": {
                        "A": select_options[0],
                        "B": select_options[1],
                        "C": select_options[2],
                        "D": select_options[3],
                        "E": select_options[4],
                    },
                    "Reasoning": completion.choices[0].message.content,
                    "Answer": "(" + answer_letter + ")" + "no defect"
                },
            }
            print(results)
            # ✅ 写入 JSONL（每行为一个 JSON 对象）
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(results, ensure_ascii=False) + "\n")