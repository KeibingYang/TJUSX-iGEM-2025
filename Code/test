import scipy.io
from cobra.io import load_matlab_model
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
from scipy.signal import savgol_filter

# ---------------------- 字体设置（解决中文显示问题） ----------------------
plt.rcParams["font.family"] = "SimHei"  # 优先使用黑体，若缺失则自动回退
plt.rcParams["axes.unicode_minus"] = False


def mat_to_cobra_model(file_path, model_var_name="model"):

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        mat_data = scipy.io.loadmat(file_path, simplify_cells=True)
        print(f"MAT文件中的变量: {list(mat_data.keys())}")

        if model_var_name not in mat_data:
            raise ValueError(f"未找到变量 '{model_var_name}'")

        model_data = mat_data[model_var_name]
        print(
            f"模型数据类型: {type(model_data)}, 键: {list(model_data.keys()) if isinstance(model_data, dict) else 'N/A'}")

        if model_data is None:
            raise ValueError("模型数据为空")

        model = load_matlab_model(file_path)
        return model

    except Exception as e:
        print(f"解析失败: {e}")
        return None


def find_substrate_exchange_reaction(model, preferred_id="EX_glc__D_e"):

    if preferred_id in model.reactions:
        return preferred_id

    # 按关键词搜索葡萄糖相关反应
    glucose_keywords = ["glc", "glucose", "葡萄糖"]
    candidates = [rxn.id for rxn in model.reactions
                  if any(kw in rxn.id.lower() or kw in rxn.name.lower() for kw in glucose_keywords)]

    if candidates:
        print(f"未找到 {preferred_id}，使用候选反应: {candidates[0]}")
        return candidates[0]

    # 最后尝试第一个交换反应
    exchange_reactions = [rxn.id for rxn in model.reactions if rxn.id.startswith("EX_")]
    return exchange_reactions[0] if exchange_reactions else None


def calculate_growth_rates(models, substrate_range, default_substrate_id="EX_glc__D_e"):
    """计算生长速率（处理反应不存在的情况）"""
    growth_rates = []
    for model in models:
        if model is None:
            growth_rates.append(None)
            continue

        substrate_id = find_substrate_exchange_reaction(model, default_substrate_id)
        if not substrate_id:
            print("警告: 未找到任何交换反应，跳过此模型")
            growth_rates.append(None)
            continue

        print(f"使用反应: {substrate_id}")
        rates = []
        for conc in substrate_range:
            try:
                rxn = model.reactions.get_by_id(substrate_id)
                original_lb, original_ub = rxn.bounds
                rxn.bounds = (-conc, 1000)

                solution = model.optimize()
                rates.append(solution.objective_value if solution.status == 'optimal' else np.nan)

                rxn.bounds = (original_lb, original_ub)
            except Exception as e:
                print(f"计算错误: {e}，当前浓度: {conc}")
                rates.append(np.nan)

        growth_rates.append(rates)
    return growth_rates


def plot_growth_comparison(substrate_range, growth_rates, strain_names, output_file="growth_comparison.pdf"):
    """绘制生长曲线（处理NaN值）"""
    with PdfPages(output_file) as pdf:
        plt.figure(figsize=(10, 6))
        for i, (rates, name) in enumerate(zip(growth_rates, strain_names)):
            if rates is None:
                continue

            valid_mask = ~np.isnan(rates)
            valid_sub = substrate_range[valid_mask]
            valid_rates = rates[valid_mask]

            if len(valid_rates) >= 3:
                smooth_rates = savgol_filter(valid_rates, window_length=min(5, len(valid_rates)), polyorder=2)
                plt.plot(valid_sub, smooth_rates, 'o-', label=name, linewidth=2)
            else:
                plt.plot(valid_sub, valid_rates, 'o-', label=name, linewidth=2)

        plt.xlabel('葡萄糖浓度 (mmol/L)', fontsize=14)
        plt.ylabel('生长速率 (1/h)', fontsize=14)
        plt.title('不同葡萄糖浓度下的生长速率比较', fontsize=16)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(fontsize=12)
        plt.tight_layout()
        pdf.savefig()
        plt.close()


def analyze_essential_genes(models, strain_names):
    """分析必需基因（处理基因列表长度不一致问题）"""
    essential_genes = {}
    for i, model in enumerate(models):
        if model is None:
            continue

        strain = strain_names[i]
        genes = []
        for gene in model.genes:
            with model:
                gene.knock_out()
                solution = model.optimize()
                if solution.status != 'optimal' or solution.objective_value < 0.01:
                    genes.append(gene.id)

        essential_genes[strain] = genes

    # 统一基因列表长度（用空值填充）
    max_len = max(len(genes) for genes in essential_genes.values()) if essential_genes else 0
    for strain in essential_genes:
        essential_genes[strain] += [np.nan] * (max_len - len(essential_genes[strain]))

    return essential_genes


def main():
    # 模型文件路径（需确认路径正确）
    model_paths = [
        "1-80/23-Bacillus_amyloliquefaciens_Y2.mat",
        "1-80/77-Bifidobacterium_breve_MCC_1128.mat"
    ]
    strain_names = ["解淀粉芽孢杆菌Y2", "解淀粉芽孢杆菌Y4"]

    # 加载模型
    models = [mat_to_cobra_model(path) for path in model_paths]

    # 计算生长速率
    substrate_range = np.linspace(0.1, 10, 20)
    growth_rates = calculate_growth_rates(models, substrate_range)

    # 绘图（仅绘制有效数据）
    valid_indices = [i for i, rates in enumerate(growth_rates) if rates is not None]
    if valid_indices:
        plot_growth_comparison(substrate_range,
                               [growth_rates[i] for i in valid_indices],
                               [strain_names[i] for i in valid_indices])

    # 分析必需基因
    essential_data = analyze_essential_genes(models, strain_names)

    # 保存为CSV（处理NaN值）
    if essential_data:
        df = pd.DataFrame(essential_data).fillna("")  # 用空字符串替代NaN
        df.to_csv("essential_genes.csv", index=False)
        print("必需基因分析结果已保存至 essential_genes.csv")

    print("分析完成！")


if __name__ == "__main__":
    main()
