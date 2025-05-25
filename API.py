import pandas as pd
import openai
import json
import re
import time

# 这里不要改，我已经开好了对应的api key了
API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = "sk-8e64d4093070449d88bc3ccd91d40992"  # 请替换为你的 API 密钥
client = openai.OpenAI(api_key=api_key, base_url=API_BASE)

# 这里需要根据自己的数据路径进行更改，其实只要能够读到对应的菌株名称就好了
excel_file = "dataset\问答\菌株问答机器人数据库模板.xlsx"
try:
    df = pd.read_excel(excel_file)
    strains = df["菌株名称"].dropna().unique().tolist()
except Exception as e:
    print(f"无法读取Excel文件: {e}")
    exit()


def extract_json_from_response(response: str) -> dict:
    try:
        cleaned = re.sub(r"```json|```", "", response).strip()
        
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace == -1 or last_brace == -1:
            raise ValueError("未找到有效的 JSON 内容")
        json_str = cleaned[first_brace:last_brace + 1]

        return json.loads(json_str)
    except Exception as e:
        return {"error": "无法解析模型输出", "原始输出": response}


def query_strain_info(strain_name: str) -> dict:
    prompt = f"请以结构化 JSON 格式详细介绍菌株 {strain_name} 的全部专业信息"
    prompt = prompt + "，字段包括：菌株名称、可治疗疾病、生长特性、存活能力评级、粘附/留存能力评级、外形特征、与其他菌种协同情况、是否影响肠道健康、产生的代谢物、潜在致病性/副作用、代谢途径及优势劣势、微生物相互作用、竞争性抑制情况、疾病关联性、培养周期、培养成本、基因表达变化情况、遗传稳定性、临床实验/使用案例、文献链接/专家推荐。请返回标准JSON字符串。"
    print(f"正在提问：{strain_name}")
    print(f"当前的prompt是{prompt}") # 这两个是调试的，也不用改，到时候会看到很明显的输出
    try:
        completion = client.chat.completions.create(
            model="qwen-plus", # 这里需要改，我是随便用的
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        response = completion.choices[0].message.content
        return extract_json_from_response(response)
    except Exception as e:
        return {"error": str(e)}

results = {}
for name in strains:
    if name == "Azospirillum lipoferum": #这里改成需要停止的菌株名字就好了
        break
    print('-'*80)
    info = query_strain_info(name)
    results[name] = info
    print(f"{name}的答案：{results[name]}")
    print('-'*80)
    time.sleep(2)  # 这里是防止他过快的提问，如果后面确定了模型就可以直接去掉了

with open("菌株详细信息汇总.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ 所有菌株信息已完成提问并保存为 JSON。")
