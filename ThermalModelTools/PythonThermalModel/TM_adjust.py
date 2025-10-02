# Author : Henry Nachman
# Description:
# A python script to adjust the thermal model results based on the outputs of
# the filter transfer model.

import json, os, sys
from astropy import units as u
import pandas as pd
from configparser import ConfigParser

abspath = os.path.abspath(__file__)
root_path = os.path.dirname(abspath)
sys.path.append(os.path.join(root_path))
from stage_calc import get_all_powers, optimize_tm, get_sum_variance
import argparse

def main(exp_path):
        
    # Define the path to the thermal model json file
    file = os.path.join(exp_path, "input_configs", "thermal_model.json")  # Replace with the actual path to your thermal model JSON file

    # First, let's import the thermal model json we want to manipulate.

    json_load = components = json.load(open(file))
    components = json.load(open(file))["components"]
    stage_details = json_load["stage_details"]

    # Now we import the results from the thermalization
    stage_dict = {"Stage 0":{}, "Stage I":{}, "Stage II":{}, "Stage III":{}, "Stage IV":{}}
    path_to_output = f"{exp_path}{os.sep}Sim_Outputs{os.sep}blast_tng_filters_out.cfg"

    config = ConfigParser()
    config.read_file(open(path_to_output))

    for section in config.sections():
        stage_dict[section] = float((config[section]["Total"]).split("#")[0])*u.W
            
    # Convert the stage_dict to a pandas DataFrame
    # stage_df = pd.DataFrame(stage_dict)


    # Run the thermal model optimization
    updated_details, output_data, heatmap = optimize_tm(components, stage_details, num_points = 10)
    # print(output_data["total_power"])

    # Estimate Hold Time
    sum_variance_value, balloon_estimates = get_sum_variance(output_data)
    hold_time = balloon_estimates["Cryo Hold Time"]
    # print(f"\nInitial Cryo Hold Time: {hold_time}\n")

    # Update the components with the new power values from the stage_dict

    stage_translation = {
        "RT": "Stage 0",
        "VCS 2": "Stage I",
        "VCS 1": "Stage II",
        "4K - LHe": "Stage III",
        "1K": "Stage IV"
    }

    # updated_details, output_data, heatmap = optimize_tm(components, stage_details, num_points = 10)
    # print(output_data["total_power"])
    # sum_variance_value, balloon_estimates = get_sum_variance(output_data)
    # hold_time = balloon_estimates["Cryo Hold Time"]
    # print(hold_time)


    # Loop over the stages and components in the JSON file
    for stage, components_dict in components.items():
        # Check if the component is an optical load
        for component_name in components_dict.keys():
            if "optical load" == component_name.lower():
                # print(f"Stage: {stage}, Component: {component_name}, {components_dict[component_name]['Power per Part (W)']}")
                # if the stage has a corresponding stage in the optical filter output
                if stage in stage_translation:
                    # print("Updated Power: ", stage_dict[stage_translation[stage]][filter_stack].value)
                    components_dict[component_name]['Power per Part (W)'] = stage_dict[stage_translation[stage]].value

    updated_details, output_data, heatmap = optimize_tm(components, stage_details, num_points = 10)
    print(output_data["total_power"])
    sum_variance_value, balloon_estimates = get_sum_variance(output_data)
    hold_time_result = balloon_estimates["Cryo Hold Time"]

    print(f"\nUpdated Cryo Hold Time: {hold_time_result}\n")

    # Save output_data, balloon_estimates, updated_details, and hold_time_result to a txt file
    output_file = os.path.join(exp_path, "Sim_Outputs", "thermal_model_adjustment_results.json")
    results = {
        "output_data": output_data,
        "balloon_estimates": balloon_estimates,
        "updated_details": updated_details,
        "hold_time_result": str(hold_time_result)
    }
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adjust the thermal model based on filter transfer model outputs.")
    parser.add_argument("experiment_path", type=str, help="Path to the experiment directory.")
    args = parser.parse_args()
    experiment_path = args.experiment_path
    if not os.path.exists(experiment_path):
        raise FileNotFoundError(f"The specified experiment path does not exist: {experiment_path}")
    main(experiment_path)
