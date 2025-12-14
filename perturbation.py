import os
import time
import json
import random
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import re
from datetime import datetime

# ================= CONFIGURATION =================
N_HOUSES = 50  # Number of houses to test (Set to 50 or 100 for real run)
INPUT_FILE = "random_sample.txt"
HISTORY_LOG = "processed_parcel_ids.txt"
RESULTS_FILE = "results.txt"
LOG_DIR = "logs"
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

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
    "Garage Type",
}


# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ================= 1. HELPER FUNCTIONS =================


def perturb_value(value):
    # ---------- NUMERIC FEATURES ----------
    if isinstance(value, (int, float)):
        if value == 0:
            return value

        perturbed = value * 0.01  # shrink to 1%

        if isinstance(value, int):
            perturbed = int(round(perturbed))

        return max(0, perturbed)

    # ---------- CATEGORICAL FEATURES ----------
    if isinstance(value, str):
        return "Not Available"

    return value


def parse_sample_file(filepath):
    """Reads the 'Key : Value' format from random_sample.txt into a Dictionary"""
    data_dict = {}
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Attempt to convert numbers to float/int
                    try:
                        if "." in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass  # Keep as string if not a number

                    data_dict[key] = value
        return data_dict
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Run RandomGenerator.py first.")
        return None


def serialize_row(row_dict):
    """Converts the dictionary back to a string prompt for the LLM"""
    prompt_text = ""
    for key, value in row_dict.items():
        if key != "Sale Price":  # Don't give the answer to the LLM!
            prompt_text += f"- {key}: {value}\n"
    return prompt_text


import time
import re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure API Key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemma-3-12b-it")


def call_gemini_api(serialized_data):
    """
    Sends the specific 'Ames Housing' prompt template to Gemini.
    """
    # 1. Define your specific Template
    # We inject the variable 'serialized_data' into the placeholder spot.
    full_prompt_text = f"""I will provide you with the technical specifications of a residential property in Ames, Iowa. Based on these features, predict the final Sale Price of the house.

Property Details:
{serialized_data}

Task: Analyze the features above and predict the sale price in USD.

Output Format: Return only the predicted price as a raw number. Do not include currency symbols, commas, or explanations in your final answer.
"""

    # Rate Limiting (Optional but good for free tier)
    # time.sleep(2)

    try:
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            temperature=0.0,  # Keep temp low for mathematical consistency
            max_output_tokens=100,  # We only expect a number, so we can lower this
        )

        # 2. Send the FULL structured prompt
        response = model.generate_content(
            full_prompt_text,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        if not response.parts:
            print(f"\n   Error: Empty response.")
            return 0.0

        # 3. Clean and Extract Number
        raw_text = response.text.strip()

        # Regex to find the last number in the text (handles 150000 and 150,000.00)
        matches = re.findall(r"[\d,]+\.?\d*", raw_text)

        if matches:
            # Remove commas (e.g., "150,000" -> "150000")
            best_match = matches[-1].replace(",", "")
            try:
                return float(best_match)
            except ValueError:
                return 0.0

        return 0.0

    except Exception as e:
        if "429" in str(e):
            print("\n   Hit Rate Limit (429). Retrying in 30s...")
            time.sleep(30)
            return call_gemini_api(serialized_data)  # Recursive retry

        print(f"\n   Gemini Error: {e}")
        return 0.0


def trigger_random_generator():
    """
    Simulates running your RandomGenerator.py.
    In a real scenario, you might use: os.system('python RandomGenerator.py')
    """
    print(" -> Generating new random sample...")
    os.system("python RandomGenerator.py")
    # For now, I assume random_sample.txt is already updated or static for this demo.


# ================= 2. MAIN EXPERIMENT LOOP =================


def run_experiment():
    print(f"Starting Perturbation Analysis for {N_HOUSES} houses...")

    # Open results file to write headers
    with open(RESULTS_FILE, "w") as res_file:
        res_file.write(f"Experiment Started: {datetime.now()}\n")
        res_file.write(
            "Parcel_ID, Feature_Perturbed, Original_Price, New_Price, Importance_Score\n"
        )

    for i in range(1, N_HOUSES + 1):
        print(f"\n=== Processing House {i}/{N_HOUSES} ===")

        # 1. Generate New Sample
        trigger_random_generator()

        # 2. Read the Data
        house_data = parse_sample_file(INPUT_FILE)
        if not house_data:
            break

        parcel_id = house_data.get("Parcel ID", "Unknown")

        # 3. Log Parcel ID to History (Tracking)
        with open(HISTORY_LOG, "a") as history:
            history.write(f"{datetime.now()} | Processed Parcel ID: {parcel_id}\n")

        # 4. Get BASELINE Prediction (Original Data)
        original_prompt = serialize_row(house_data)
        baseline_price = call_gemini_api(original_prompt)
        print(f"   Parcel {parcel_id}: Baseline Price = ${baseline_price}")

        # 5. PERTURBATION LOOP (Iterate through every feature)
        # We create a specific log file for this house
        house_log_path = os.path.join(
            LOG_DIR, f"log_{parcel_id}_{int(time.time())}.txt"
        )

        with open(house_log_path, "w") as house_log:
            house_log.write(f"Baseline Price: {baseline_price}\n")
            house_log.write("-" * 40 + "\n")

            for feature in house_data.keys():
                # Skip the ID and the Target
                if feature not in IMPORTANT_FEATURES:
                    continue

                # --- A. Create Perturbed Copy ---
                perturbed_data = house_data.copy()
                original_value = perturbed_data[feature]

                # --- B. Nullify Logic ---
                perturbed_data[feature] = perturb_value(original_value)

                # --- C. Get New Prediction ---
                new_prompt = serialize_row(perturbed_data)
                new_price = call_gemini_api(new_prompt)

                # --- D. Calculate Importance ---
                importance = abs(baseline_price - new_price)

                # --- E. Console & Log Output ---
                log_msg = f"Feature: {feature:25} | Changed '{original_value}' -> '{perturbed_data[feature]}' | New Price: {new_price} | Impact: {importance}\n"
                house_log.write(log_msg)

                # Save to aggregated results (CSV format for easy analysis later)
                with open(RESULTS_FILE, "a") as res_file:
                    res_file.write(
                        f"{parcel_id}, {feature}, {baseline_price}, {new_price}, {importance}\n"
                    )

        print(f"   -> Finished logs for Parcel {parcel_id}")

    print("\n\nExperiment Completed. Check 'results.txt' for final data.")


if __name__ == "__main__":
    run_experiment()
