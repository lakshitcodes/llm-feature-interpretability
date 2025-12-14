1. Finalised Ames Housing Dataset to set the basline (ground truth)
2. Made a random sample picker script to map columns with their respective values to feed that to the LLMs
3. Model used gemma-3-12b-it

Iteration 1 :
5 houses using gemma-3-12b-it
Perturb using :
def perturb_value(value): # ---------- NUMERIC FEATURES ----------
if isinstance(value, (int, float)):
if value == 0:
return value

        # Pick an aggressive perturbation mode
        mode = random.choice(["scale_up", "scale_down", "random_reset"])

        if mode == "scale_up":
            factor = random.uniform(2.0, 4.0)  # +100% to +300%
            perturbed = value * factor

        elif mode == "scale_down":
            factor = random.uniform(0.1, 0.2)  # -80% to -90%
            perturbed = value * factor

        else:  # random_reset
            perturbed = random.uniform(0.1 * value, 4.0 * value)

        # Preserve integer semantics
        if isinstance(value, int):
            perturbed = int(round(perturbed))

        return max(0, perturbed)

    # ---------- CATEGORICAL FEATURES ----------
    if isinstance(value, str):
        return random.choice(["Other", "Unknown", "Rare", "Low", "High"])

    return value

Iteration 2 :
IMPORTANT_FEATURES = {
"Neighborhood",
"Lot Area",
"Lot Frontage",
"Overall Quality",
"Overall Condition",
"Year Built",
"Year Remodeled/Added",
"Above Ground Living Area (sqft)",
"First Floor Area (sqft)",
"Total Basement Area (sqft)",
"Basement Finished Area 1 (sqft)",
"Basement Full Bathrooms",
"Full Bathrooms",
"Bedrooms Above Ground",
"Kitchen Quality",
"Heating Quality",
"Central Air Conditioning",
"Exterior Quality",
"Exterior Condition",
"Basement Height Quality",
"Basement Condition",
"Garage Capacity (Cars)",
"Garage Area (sqft)",
"Garage Type"
}

For Shapley : # Cell 7: Merge & Visualize All Results
import glob
import shap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Load All CSVs (Inputs)

csv*files = glob.glob("shap_results/features*\*.csv")
if not csv_files:
raise ValueError("No result files found! Did you run Cell 6?")

all_features = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

# 2. Load All SHAP Arrays (Outputs)

# We must ensure they load in the exact same order as the CSVs

npy*files = [f.replace("features*", "shap*values*").replace(".csv", ".npy") for f in csv_files]
all_shap_values = np.concatenate([np.load(f) for f in npy_files], axis=0)

print(f"✅ Successfully Merged Data for {len(all_features)} Houses.")

# 3. Generate the "Bee Swarm" Plot (Global Explainability)

plt.figure()
shap.summary_plot(all_shap_values, all_features, show=False)

# 4. Save High-Res Image for your B.Tech Report

plt.title(f"LLM Pricing Logic: Analysis of {len(all_features)} Houses")
plt.savefig("Final_SHAP_Analysis_Graph.png", bbox_inches='tight', dpi=300)
plt.show()

this is the combiner
