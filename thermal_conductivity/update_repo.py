## Make plots for all materials
### Author: Henry Nachman
#### Last Updated: 2024-06-13


import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, os, json
from tqdm import tqdm

from tc_tools  import *
from tc_utils import get_all_fits, compile_csv, create_tc_csv
from tc_plots import plot_all_fits, plot_OFHC_RRR
import yaml

def main():
    # Define important paths
    home_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = home_dir+f'{os.sep}lib'
    
    parent_dictionary = {}
    num_dir = len(os.listdir(lib_dir)) # number of directories in lib/
    for i in tqdm(range(num_dir)):
        folder_name = os.listdir(lib_dir)[i] # loop through each material folder in lib/
        folder_path = os.path.join(lib_dir, folder_name)
        print(f"\n Processing {folder_name} ({i+1}/{num_dir})\n")
        if os.path.isdir(folder_path): # If it is a directory, we will process the fits in it
            # First lets make a compilation file of each fit available for a material
            paths = get_all_fits(folder_path) # paths to each fit file in the directory
            csv = compile_csv(paths, folder_name) # format the csv
            create_tc_csv(csv, f"{folder_path}{os.sep}all_fits.csv") # save the compilation file

            # Now import the data from that all_fits file
            TCdata = np.loadtxt(f"{folder_path}{os.sep}all_fits.csv", dtype=str, delimiter=',') #

            # This makes the plot with all the fits available - with a special case for OFHC RRR
            if folder_name == "Cu_OFHC":
                plot_OFHC_RRR(TCdata, folder_name, folder_path) # Special case for OFHC RRR to use a different plotting function
            else:
                plot_all_fits(TCdata, folder_name, folder_path)
        
        # now we need to check and update the parent files
        # Open the material config file
        config_path = os.path.join(folder_path, "config.yaml")
        if os.path.exists(config_path): # opens the config.yaml file if it exists
            with open(config_path, 'r') as config_file:
                config_data = yaml.safe_load(config_file)
                parent = config_data[0]['parent'] # get the parent name from the config.yaml file
                if parent != "NA": # If the parent is not NA, we will check if it exists in the lib directory
                    parent_path = os.path.join(lib_dir, parent)
                    if os.path.exists(parent_path): # check if the parent directory exists
                        if parent not in parent_dictionary.keys():
                            parent_dictionary[parent] = []
                        parent_dictionary[parent].append(folder_path) # and append it to the list of parent directories
                    else: # if it does not exist, we will create it
                        print(f"Creating parent folder : {folder_path}")
                        os.makedirs(parent_path) # make the directory
                        # create the config.yaml file
                        yaml_dict = []
                        yaml_dict.append({"name":f"{parent}", 
                                        "parent":f"NA",
                                        "source":f"NA",
                                        "fit_type":f"NA"}) # Define JSON dictionary
                        yaml_dict = json.dumps(yaml_dict, indent=4)
                        with open(f"{parent_path}{os.sep}config.yaml", 'w') as file:
                            file.write(yaml_dict)
                        if parent not in parent_dictionary.keys():
                            parent_dictionary[parent] = []
                        parent_dictionary[parent].append(folder_path)
        else:
            print(f"No config.yaml found in {folder_path}")

    # Now that every individual material has been processed, we will update the parent files with all of the fits of their children
    for parent in parent_dictionary.keys():
        parent_path = os.path.join(lib_dir, parent)
        print(f"PARENT: {parent}\n")
        full_paths = {}
        for child in parent_dictionary[parent]:
            paths = get_all_fits(child) # paths to each fit file in the directory
            for path in paths.keys():
                full_paths[os.path.basename(child) + "_" + os.path.basename(path)] = paths[path]
        csv = compile_csv(full_paths, "parent") # format the csv
        create_tc_csv(csv, f"{parent_path}{os.sep}all_fits.csv") # save the compilation file

        # Now import the data from that all_fits file
        TCdata = np.loadtxt(f"{parent_path}{os.sep}all_fits.csv", dtype=str, delimiter=',') #
        plot_all_fits(TCdata, parent, parent_path)

if __name__ == "__main__":
    main()