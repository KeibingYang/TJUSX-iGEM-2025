import cobra
import pandas as pd
import os
import matplotlib.pyplot as plt
from cobra.flux_analysis import flux_variability_analysis


def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")


def run_fba(mat_file_path):
    save_path = "D:\\_AAA原桌面\\竞赛\\iGEM2\\fba_results"
    save_path = os.path.join(save_path, mat_file_path.split("\\")[-1].split(".")[0])
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    try:
        check_file_exists(mat_file_path)
        print("Loading model...")
        model = cobra.io.load_matlab_model(mat_file_path)

        print(f"\nModel ID: {model.id if model.id else 'Not specified'}")
        print(f"Reactions: {len(model.reactions)}, Metabolites: {len(model.metabolites)}, Genes: {len(model.genes)}")
        print(f"Objective: {model.objective.expression}")

        print("\nRunning FBA...")
        solution = model.optimize()
        if solution.status != 'optimal':
            print(f"Warning: Optimization did not converge. Status: {solution.status}")
            return

        print(f"\nObjective Value: {solution.objective_value:.6f}")

        # === FBA Top 10 fluxes ===
        flux_series = solution.fluxes.head(10)
        print("Top 10 Fluxes:")
        for rxn, flux in flux_series.items():
            print(f"{rxn}: {flux:.6f}")

        flux_series.to_csv("fba_top10_fluxes.csv", header=["flux"])
        flux_series.plot(kind='bar', title="Top 10 Reaction Fluxes", figsize=(10, 6))
        plt.ylabel("Flux")
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, "fba_top10_fluxes.png"))
        plt.show()

        # === Uptake & Secretion ===
        print("\nAnalyzing Uptake and Secretion Reactions...")
        exchange_rxns = [rxn for rxn in model.reactions if rxn.id.startswith("EX_")]
        exchange_fluxes = pd.Series({rxn.id: solution.fluxes[rxn.id] for rxn in exchange_rxns})
        exchange_fluxes.to_csv("exchange_fluxes.csv", header=["flux"])

        uptake_fluxes = exchange_fluxes[exchange_fluxes > 0].sort_values()
        secretion_fluxes = exchange_fluxes[exchange_fluxes < 0].sort_values()

        if not uptake_fluxes.empty:
            uptake_fluxes.plot(kind='barh', title="Uptake Fluxes", color='green', figsize=(8, 5))
            plt.xlabel("Flux")
            plt.tight_layout()
            plt.savefig(os.path.join(save_path, "uptake_fluxes.png"))
            plt.show()

        if not secretion_fluxes.empty:
            secretion_fluxes.plot(kind='barh', title="Secretion Fluxes", color='orange', figsize=(8, 5))
            plt.xlabel("Flux")
            plt.tight_layout()
            plt.savefig(os.path.join(save_path, "secretion_fluxes.png"))
            plt.show()

        # === FVA for first 10 reactions ===
        print("\nRunning FVA for first 10 reactions...")
        first_10_rxns = model.reactions[:10]
        fva_result = flux_variability_analysis(model, reaction_list=first_10_rxns)
        fva_result.to_csv("fva_first10.csv")

        print("\nFVA Result:")
        print(fva_result)

        # Plot FVA range safely
        fva_result["reaction"] = fva_result.index
        fva_result["range"] = (fva_result["maximum"] - fva_result["minimum"])

        # Calculate center and error bar safely
        fva_result["center"] = (fva_result["maximum"] + fva_result["minimum"]) / 2
        fva_result["error"] = fva_result["range"].abs() / 2

        # Drop any rows with NaNs or negative error
        fva_plot_data = fva_result.dropna(subset=["center", "error"])
        fva_plot_data = fva_plot_data[fva_plot_data["error"] >= 0]

        plt.figure(figsize=(10, 6))
        plt.errorbar(
            fva_plot_data["reaction"],
            fva_plot_data["center"],
            yerr=fva_plot_data["error"],
            fmt='o', ecolor='red', capsize=5
        )
        plt.title("FVA Ranges for First 10 Reactions")
        plt.ylabel("Flux Range")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, "fva_first10_plot.png"))
        plt.show()
        
        print("\nAll results saved as CSV and PNG.")

        # === Stacked bar chart of top 20 reactions ===
        print("\nGenerating stacked bar chart for top 20 fluxes...")
        top20_fluxes = solution.fluxes.abs().sort_values(ascending=False).head(20)
        flux_df = pd.DataFrame({
            "flux": solution.fluxes[top20_fluxes.index],
            "positive": solution.fluxes[top20_fluxes.index].clip(lower=0),
            "negative": solution.fluxes[top20_fluxes.index].clip(upper=0).abs()
        })

        flux_df[["positive", "negative"]].plot(
            kind='bar',
            stacked=True,
            figsize=(12, 6),
            title="Top 20 Reaction Fluxes (Stacked Positive/Negative)"
        )
        plt.ylabel("Flux")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, "flux_stacked_bar_top20.png"))
        plt.show()

        # === Heatmap of top 50 fluxes ===
        print("Generating heatmap of top 50 fluxes...")
        import seaborn as sns

        top50_fluxes = solution.fluxes.abs().sort_values(ascending=False).head(50)
        heatmap_data = pd.DataFrame({
            "flux": solution.fluxes[top50_fluxes.index]
        })

        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data.T, cmap="coolwarm", annot=False, cbar_kws={'label': 'Flux'})
        plt.title("Heatmap of Top 50 Fluxes")
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, "flux_heatmap_top50.png"))
        plt.show()



    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Replace this path with your own .mat file
    mat_file_path = "D:\_AAA原桌面\竞赛\iGEM2\dataset\AGORA2.0\AGORA2_annotatedMat_A_C.zip\Acinetobacter_baumannii_AB_TG2018.mat"
    run_fba(mat_file_path)
