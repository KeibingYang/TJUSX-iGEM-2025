from pathlib import Path
from cobra.io import load_matlab_model  # 导入读取 MAT 文件的函数

# 定义文件路径
mat_file_path = Path("D:\_AAA原桌面\竞赛\iGEM2\dataset\AGORA2.0\AGORA2_annotatedMat_A_C.zip\Abiotrophia_defectiva_ATCC_49176.mat")  # 替换为实际文件路径

# 情况 1：MAT 文件包含多个模型变量，需指定变量名
# model = load_matlab_model(
#     str(mat_file_path.resolve()),  # 解析文件路径为字符串
#     variable_name="模型变量名"  # MAT 文件中存储模型的变量名（必填）
# )

# 情况 2：MAT 文件仅包含单个模型，无需指定变量名
model = load_matlab_model(str(mat_file_path.resolve()))

print("模型名称:", model.name)
print("代谢物数量:", len(model.metabolites))
print("反应数量:", len(model.reactions))
    # ====================== 1. 模型基本信息 ======================
print("\n===================== 模型基本信息 ======================")
print(f"模型名称: {model.name}")
print(f"模型 ID: {model.id}")
print(f"模型注释: {model.annotation}")
print(f" compartments: {', '.join(model.compartments)}")
print(f"代谢物数量: {len(model.metabolites)}")
print(f"反应数量: {len(model.reactions)}")
print(f"组数量: {len(model.groups)}")
print(f"目标函数表达式: {model.objective.expression}")
print(f"目标函数方向: {model.objective.direction}")
    
    # ====================== 2. 代谢物（Metabolites）详细信息 ======================
print("\n===================== 代谢物列表 ======================")
for i, metabolite in enumerate(model.metabolites):
    print(f"\n第 {i+1} 个代谢物:")
    print(f"ID: {metabolite.id}")
    print(f"名称: {metabolite.name}")
    print(f" compartment: {metabolite.compartment}")
    print(f"公式: {metabolite.formula}")
    print(f"电荷: {metabolite.charge}")
    print(f"初始浓度: {getattr(metabolite, '_initial_concentration', '未定义')}")
    print(f"注释: {metabolite.annotation}")
    # print(f"边界值: [{metabolite.lower_bound}, {metabolite.upper_bound}]")
    
    # ====================== 3. 反应（Reactions）详细信息 ======================
print("\n===================== 反应列表 ======================")
for i, reaction in enumerate(model.reactions):
    print(f"\n第 {i+1} 个反应:")
    print(f"ID: {reaction.id}")
    print(f"名称: {reaction.name}")
    print(f"方程式: {reaction.build_reaction_string()}")
    print(f"下界 (vmin): {reaction.lower_bound}")
    print(f"上界 (vmax): {reaction.upper_bound}")
    print(f"可逆性: {reaction.reversibility}")
    print(f"基因关联: {reaction.gene_reaction_rule}")
    print(f"目标函数权重: {reaction.objective_coefficient}")
    print(f"注释: {reaction.annotation}")
    print("涉及的代谢物:")
    for metabolite, coefficient in reaction.metabolites.items():
        print(f"- {metabolite.id}: {coefficient}")
    
    # ====================== 4. 目标函数详细信息 ======================
print("\n===================== 目标函数 ======================")
print("目标函数组成:")
for reaction, weight in model.objective.items():
    print(f"- {reaction.id}: 权重 {weight}")
    
    # ====================== 5. 组（Groups）和其他属性 ======================
if model.groups:
    print("\n===================== 组（Groups） ======================")
    for group in model.groups:
        print(f"组 ID: {group.id}, 名称: {group.name}, 类型: {group.type}")
    else:
        print("\n无组（Groups）信息")
    
print("\n===================== 模型完整信息输出结束 ======================")
# # print(model)

# # 获取所有代谢物对象
# metabolites = model.metabolites

# # 示例 1：打印第一个代谢物的 ID、名称和初始浓度（若有）
# first_met = metabolites[0]
# print(f"代谢物 ID: {first_met.id}")
# print(f"代谢物名称: {first_met.name}")
# # print(f"初始浓度: {first_met._initial_concentration}")  # 注意：部分模型可能未定义此属性

# # 示例 2：按 ID 查找特定代谢物（如 "glc__D_c"）并查看其边界值
# specific_met = model.metabolites.get_by_id("glc__D_c")
# print(f"代谢物 {specific_met.id} 的下界: {specific_met.lower_bound}")
# print(f"代谢物 {specific_met.id} 的上界: {specific_met.upper_bound}")

# # 获取所有反应对象
# reactions = model.reactions

# # 示例 1：打印第一个反应的 ID、名称和方程式
# first_reaction = reactions[0]
# print(f"反应 ID: {first_reaction.id}")
# print(f"反应名称: {first_reaction.name}")
# print(f"反应方程式: {first_reaction.build_reaction_string()}")

# # 示例 2：按 ID 查找特定反应（如 "ATPM"）并查看系数矩阵
# atpm_reaction = model.reactions.get_by_id("ATPM")
# print("反应系数矩阵（代谢物: 系数）:")
# for met, coeff in atpm_reaction.metabolites.items():
#     print(f"{met.id}: {coeff}")

# # 查看当前目标函数表达式
# print("目标函数表达式:", model.objective.expression)

# # 查看目标函数中各反应的权重系数
# print("目标函数权重:")
# for reaction, weight in model.objective.items():
#     print(f"{reaction.id}: {weight}")

# import numpy as np

# # 获取代谢物-反应矩阵（S 矩阵），形状为 (代谢物数, 反应数)
# S_matrix = model.metabolites.matrix
# print("S 矩阵形状:", S_matrix.shape)
# print("前 5 行 5 列数据:\n", S_matrix[:5, :5])

# # 获取反应的下界和上界（数组形式）
# lower_bounds = model.reactions.lower_bound
# upper_bounds = model.reactions.upper_bound
# print("前 5 个反应的下界:", lower_bounds[:5])
# print("前 5 个反应的上界:", upper_bounds[:5])


# from scipy.io import loadmat

# # 加载 MAT 文件（返回字典，键为变量名）
# data = loadmat("D:\_AAA原桌面\竞赛\iGEM2\dataset\AGORA2.0\AGORA2_annotatedMat_A_C.zip\Abiotrophia_defectiva_ATCC_49176.mat")

# # 示例：打印所有变量名
# print("MAT 文件中的变量名:", data.keys())

# 示例：提取名为 "matrix_data" 的数组
# matrix_data = data["matrix_data"]
# print("矩阵数据形状:", matrix_data.shape)
# print("前 5 行 5 列数据:\n", matrix_data[:5, :5])