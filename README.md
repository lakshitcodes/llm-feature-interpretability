1. Finalised Ames Housing Dataset to set the basline (ground truth)
2. Made a random sample picker script to map columns with their respective values to feed that to the LLMs
3. Model used gemma-3-12b-it



Iteration 1 : 
5 houses using gemma-3-12b-it
Perturb using :
def perturb_value(value):
    # ---------- NUMERIC FEATURES ----------
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
