## Thermal Conductivity Raw Data Fitting
## Author: Henry Nachman
## Last Edited: 21 June 2024

# Import Statements
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TKAgg')
import os, json, shutil
import argparse

# note : most functions needed for running this notebook can be found in tc_utils.
from tc_utils import *
from tc_plots import get_percdiff, tk_plot

def fit_lowT_data(mat, T, k, koT, fit_orders, weights, fit_types):
    """
    Description: This function fits the low temperature data using a polynomial fit. It first checks if the low temperature data is available, and if not, it uses a high temperature fit. It also checks for gaps in the data and splits the data accordingly.
    
    Arguments :
    - mat (str) - The name of the material being fitted
    - T (np.array) - The temperature data
    - k (np.array) - The thermal conductivity data
    - koT (np.array) - thermal_conductivity / temperature data
    - fit_orders (list) - The orders of the polynomial fits for the low and high temperature data
    """
    print(f"{mat:>15} : Using a low fit")
    low_fit_xs, low_fit = koT_function(T, koT, fit_orders[0], weights)
    hi_fit, hi_fit_xs, erf_loc = [[0], [0], 0]
    fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, fit_catch = "low")
    fit_args["combined_function_type"] = fit_types[0]
    perc_diff_low, perc_diff_arr = get_percdiff(T[T<=max(low_fit_xs)],k[T<=max(low_fit_xs)], fit_args)
    # print(perc_diff_low, perc_diff_arr)
    fit_args["low_perc_err"] =  perc_diff_low
    fit_args["hi_perc_err"] =  0
    fit_args["combined_perc_err"] =  perc_diff_low
    fit_args["combined_function_type"] = fit_types[0]
    if perc_diff_low > 50:
        print(f"{mat:>15} : Using a hi fit")
        hi_fit_xs, hi_fit = logk_function(np.log10(T), np.log10(k), fit_orders[1], weights)
        low_fit, erf_loc = [[0], -1]
        fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, fit_catch = "high")
        fit_args["combined_function_type"] = fit_types[1]
        perc_diff_hi, perc_diff_arr = get_percdiff(T[T>=min(hi_fit_xs)],k[T>=min(hi_fit_xs)], fit_args)
        fit_args["hi_perc_err"] = perc_diff_hi
        fit_args["low_perc_err"] =  0
        fit_args["combined_perc_err"] =  perc_diff_hi
    return fit_args

def fit_highT_data(mat, T, k, koT, fit_orders, weights, fit_types):
    """
    Description: This function fits the high temperature data using a polynomial fit. It first checks if the high temperature data is available, and if not, it uses a low temperature fit. It also checks for gaps in the data and splits the data accordingly.
    Arguments :
    - mat (str) - The name of the material being fitted
    - T (np.array) - The temperature data
    - k (np.array) - The thermal conductivity data
    - koT (np.array) - thermal_conductivity / temperature data
    - fit_orders (list) - The orders of the polynomial fits for the low and high temperature data
    """
    print(f"{mat:>15} : Using a hi fit")
    hi_fit_xs, hi_fit = logk_function(np.log10(T), np.log10(k), fit_orders[1], weights)
    low_fit, low_fit_xs, erf_loc = [[0], [0], -1]
    fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc)
    perc_diff_hi, perc_diff_arr = get_percdiff(T[T>=min(hi_fit_xs)],k[T>=min(hi_fit_xs)], fit_args)
    fit_args["hi_perc_err"] = perc_diff_hi
    fit_args["low_perc_err"] =  0
    fit_args["combined_perc_err"] =  perc_diff_hi
    fit_args["combined_function_type"] = fit_types[1]
    return fit_args

def fit_combined_data(mat, T, k, koT, fit_orders, weights, fit_types, big_data, path_to_plots):
    """
    Description: This function fits the combined data using a polynomial fit. It first checks if the combined data is available, and if not, it uses a low temperature fit. It also checks for gaps in the data and splits the data accordingly.
    Arguments :
    - mat (str) - The name of the material being fitted
    - T (np.array) - The temperature data
    - k (np.array) - The thermal conductivity data
    - koT (np.array) - thermal_conductivity / temperature data
    - fit_orders (list) - The orders of the polynomial fits for the low and high temperature data
    - big_data (np.array) - The combined data
    - path_to_plots (str) - The path to the plots directory (for saving plots)
    """
    print(f"{mat:>15} : Using a combined fit")# - data exists on both sides of 20K")
    erf_locList = np.linspace(np.sort(T)[0], np.sort(T)[-1], 15)
    perc_diff_avgs = np.array([])
    for erf_loc in erf_locList:
        dsplit = split_data(big_data, erf_loc)
        lowT, lowT_k, lowT_koT, low_ws, hiT, hiT_k, hiT_koT, hi_ws = dsplit
        # Take a log10 of the high range
        log_hi_T = np.log10(hiT)
        log_hi_k = np.log10(hiT_k)
        
        if (len(lowT)==0):
            low_fit = [0]
            low_fit_xs = [0]
        else:
            low_fit_xs, low_fit = koT_function(lowT, lowT_koT, fit_orders[0], low_ws)
        if (len(hiT)==0):
            hi_fit = [0]
            hi_fit_xs = [0]
        else:
            hi_fit_xs, hi_fit = logk_function(log_hi_T, log_hi_k, fit_orders[1], hi_ws)
        fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc)
        ## With the fit complete, let's output a formatted dictionary with the fit parameters
        # output_array = format_combofit(fit_args)
        ## We want to figure out the best location for the split in data, so we will compute the residual of the combined fit
        # low_param, hi_param, erf_param = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["combined_fit_erfloc"]
        # kpred = loglog_func(T, low_param, hi_param, erf_param)
        # and append it to the array resVal
        # diff = kpred-k
        # perc_diff_arr = 100*abs(diff/kpred)
        perc_diff_avg, perc_diff_arr = get_percdiff(T, k, fit_args)
        perc_diff_avgs = np.append(perc_diff_avgs, perc_diff_avg)
    # Now that we have found the residuals of the fits for many different split locations, let's choose the best one.    
    erf_locdict = dict(zip(erf_locList, perc_diff_avgs))
    bestRes = min(erf_locdict.values())
    besterf_loc = [key for key in erf_locdict if erf_locdict[key] == bestRes]
    
    # We will repeat the above fit with this new 'optimized' split location
    fit_args = dual_tc_fit(big_data, path_to_plots[mat], erf_loc=min(besterf_loc), fit_orders=fit_orders, plots=False)
    perc_diff_avg, perc_diff_arr = get_percdiff(T, k, fit_args)
    print(f"Low-Hi split centered at : {min(besterf_loc)} ~~ with average percent difference value of: {perc_diff_avg:.2f}%")

    perc_diff_low, perc_diff_arr = get_percdiff(T[T<=max(low_fit_xs)],k[T<=max(low_fit_xs)], fit_args)
    perc_diff_hi, perc_diff_arr = get_percdiff(T[T>=min(hi_fit_xs)],k[T>=min(hi_fit_xs)], fit_args)
    perc_diff_combo, perc_diff_arr = get_percdiff(T,k, fit_args)
    fit_args["low_perc_err"] =  perc_diff_low
    fit_args["hi_perc_err"] =  perc_diff_hi
    fit_args["combined_perc_err"] =  perc_diff_combo
    return fit_args

def main():
    """
    Description: This is the main function that runs the thermal conductivity fitting program. 
    It first finds the raw data directories.
    Then it creates the config.yaml files for each material in the library, which contains the material name, parent material, source of data, and fit type.
    Finally it tries to fit the data for each material in the library.
    """
    # Define the Arg Parser
    parser = argparse.ArgumentParser(description="Run the thermal conductivity fitting program.")
    parser.add_argument('--matlist', help="List of materials to fit, add sequentially with space delimiters and no brackets (with quotes)", type=str, nargs="+", default=None)
    parser.add_argument('--plot', help="Boolean: make plots?", type=bool, default=True)

    args = parser.parse_args()

    plots = args.plot # Set to true to reproduce all plots, note this will likely lengthen the time to run the code

    # First we need to find where all our raw data is:

    abspath = os.path.abspath(__file__)
    path_to_lib = f"{os.path.split(abspath)[0]}{os.sep}lib"
    mat_directories = [folder for folder in os.listdir(path_to_lib) if not folder.endswith(".md")]

    path_to_RAW = dict()
    if args.matlist != None:
        print(f"Running only for materials: {args.matlist}")
        mat_directories = args.matlist
    else:
        pass

    for mat in mat_directories:
        path_to_mat = f"{path_to_lib}{os.sep}{mat}"
        raw_str = f"{path_to_mat}{os.sep}RAW"
        config_str = f"{path_to_mat}{os.sep}config.yaml"
        parent_yaml_str = f"{path_to_mat}{os.sep}parent.yaml"
        other_str = f"{path_to_mat}{os.sep}OTHERFITS"
        nist_str = f"{path_to_mat}{os.sep}NIST"
        source = []
        if os.path.exists(raw_str): # Finds the raw data if it exists.
            path_to_RAW[mat] = raw_str
            source.append("RAW")
        if os.path.exists(other_str): # Finds other fits
            source.append("other")
        if os.path.exists(nist_str): # Finds NIST fit
            source.append("NIST")
        
        # Check for existing config file
        # if it doesn't exist, set the parent to "NA" (undefined parent material)
        if not os.path.exists(config_str): 
            parent = "NA"
        else: # if it does exist, load the parent from the config file
            with open(config_str, 'r') as file:
                mat_config = json.load(file)
            parent = mat_config[0]["parent"]

        # Check for existing config file
        # if it doesn't exist, set the fit type None (undefined parent material)

        if not os.path.exists(config_str):
            conf_fit_type = None
        else: # if it does exist, load the parent from the config file
            with open(config_str, 'r') as file:
                mat_config = json.load(file)
            conf_fit_type = None # mat_config[0]["fit_type"]

        

        # Defines the dictionary for the config file
        yaml_dict = []
        for i in range(len(source)):
            yaml_dict.append({"name":f"{mat}", 
                              "parent":f"{parent}",
                              "source":f"{source[i]}",
                              "fit_type":f"{conf_fit_type}"}) # Define JSON dictionary
        yaml_dict = json.dumps(yaml_dict, indent=4)
        with open(config_str, 'w') as file:
            file.write(yaml_dict) # Write to new JSON


    # Loops over material list and checks if the parent material exists in the library
    for mat in mat_directories:
        path_to_mat = f"{path_to_lib}{os.sep}{mat}"
        raw_str = f"{path_to_mat}{os.sep}RAW"
        config_str = f"{path_to_mat}{os.sep}config.yaml"

        if os.path.exists(raw_str):
            with open(config_str, 'r') as file: # opens the config file
                mat_config = json.load(file)
            parent = mat_config[0]["parent"]
            if parent != "NA": # if the parent is not "NA", check if it exists in the library
                print(mat, "has parent:", parent)
                parent_dir = f"{path_to_lib}{os.sep}{parent}"
                if not os.path.exists(parent_dir): # if the parent directory does not exist, create it
                    os.mkdir(parent_dir)
                    os.mkdir(f"{parent_dir}{os.sep}RAW")
                raw_files = get_datafiles(raw_str)
                for file in raw_files:
                    shutil.copy(f"{raw_str}{os.sep}{file}", f"{parent_dir}{os.sep}RAW{os.sep}{file}")


    # Lets compile the different necessary paths for each material
    path_to_RAW = dict()
    path_to_fits = dict()
    path_to_plots = dict()

    # Now we can loop through each material and run our fitting algorithm
    # You can also change the array that mat cycles through if you wish to only run the code for certain materials
    for mat in mat_directories: #path_to_RAW.keys(): #  ["Kapton"]: #
        path_to_mat = f"{path_to_lib}{os.sep}{mat}"
        raw_str = f"{path_to_mat}{os.sep}RAW"
        fits_str = f"{path_to_mat}{os.sep}fits"
        plots_str = f"{path_to_mat}{os.sep}plots"

        config_str = f"{path_to_mat}{os.sep}config.yaml"
        if os.path.exists(raw_str):
            path_to_RAW[mat] = raw_str
            if not os.path.exists(fits_str):
                os.mkdir(fits_str)
            path_to_fits[mat] = fits_str
            if not os.path.exists(plots_str):
                os.mkdir(plots_str)
            path_to_fits[mat] = fits_str
            path_to_plots[mat] = plots_str
        else:
            print(f"Skipping {mat} as it does not have a RAW directory.")
            continue

        with open(config_str, 'r') as file: # opens the config file
            mat_config = json.load(file)
        fit_type = mat_config[0]["fit_type"] # pull the fit type from the config file


        
        ## First, let's collect the raw data from their csv files
        big_data, data_dict = parse_raw(mat, path_to_RAW[mat], plots=True, weight_const=0.00)
        T, k, koT, weights = [big_data[:,0], big_data[:,1], big_data[:,2], big_data[:,3]]
        
        gaps = len(find_gaps(T, 0.8)) > 0
        # print(find_gaps(T, 100))
        maxT, minT = [max(T), min(T)]
        fit_orders = [3,3]
        fit_types = ["Nppoly", "polylog"] # the fitting code can only fit these types

        lenLow = len(T[T<=20])
        lenHi = len(T[T>=20])

        if fit_type == "None":
            if lenLow == 0 and lenHi == 0:
                print(f"{mat} : No data to fit")
                continue
            elif lenLow == 0:
                # Using a hi fit
                fit_type = fit_types[1]
            elif lenHi == 0:
                # Using a low fit - no high data to fit
                fit_type = fit_types[0]
            else:
                fit_type = "combined"

        if fit_type == fit_types[0]: # If the fit type is a low fit, we will only fit the low data
            fit_args = fit_lowT_data(mat, T, k, koT, fit_orders, weights, fit_types)
        elif fit_type == fit_types[1]: # if the fit type is a high fit, we will only fit the high data
            fit_args = fit_highT_data(mat, T, k, koT, fit_orders, weights, fit_types)
        elif fit_type == "combined": # If the fit type is a combined fit, we will fit the low and high data
            fit_args = fit_combined_data(mat, T, k, koT, fit_orders, weights, fit_types, big_data, path_to_plots)
        elif fit_type == "OFHC":
            continue

        if gaps:
            print(f"Gap found in data - splitting fit into low and high")
            low_array = format_splitfit(fit_args, "low")
            high_array = format_splitfit(fit_args, "hi")
            if (fit_args["low_fit_range"][0] == fit_args["low_fit_range"][1]):
                create_data_table(high_array, f"{path_to_fits[mat]}{os.sep}{mat}.txt")
                create_tc_csv(high_array, f"{path_to_fits[mat]}{os.sep}{mat}.csv")
            elif (fit_args["hi_fit_range"][0] == fit_args["hi_fit_range"][1]):
                create_data_table(low_array, f"{path_to_fits[mat]}{os.sep}{mat}.txt")
                create_tc_csv(low_array, f"{path_to_fits[mat]}{os.sep}{mat}.csv")
            else:
                create_data_table(low_array, f"{path_to_fits[mat]}{os.sep}{mat}_lo.txt")
                create_tc_csv(low_array, f"{path_to_fits[mat]}{os.sep}{mat}_lo.csv")
                create_data_table(high_array, f"{path_to_fits[mat]}{os.sep}{mat}_hi.txt")
                create_tc_csv(high_array, f"{path_to_fits[mat]}{os.sep}{mat}_hi.csv")
            make_fit_lh5(fit_args, path_to_fits[mat])

        else:
            output_array = format_combofit(fit_args)
            create_data_table(output_array, f"{path_to_fits[mat]}{os.sep}{mat}.txt")
            create_tc_csv(output_array, f"{path_to_fits[mat]}{os.sep}{mat}.csv")
            make_fit_lh5(fit_args, path_to_fits[mat])
        if plots:
            tk_plot(mat,path_to_RAW, data_dict, fit_args, fit_range = [100e-3, np.sort(T)[-1]], points=True, fits="combined", fill=True)

if __name__ == "__main__":
    main()