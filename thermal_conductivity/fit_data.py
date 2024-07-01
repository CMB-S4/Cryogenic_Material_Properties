## Thermal Conductivity Raw Data Fitting
## Author: Henry Nachman
## Last Edited: 21 June 2024

# Import Statements
import numpy as np
import matplotlib.pyplot as plt
import os, json, shutil
import argparse

# note : most functions needed for running this notebook can be found in tc_utils.
from tc_utils import *


def main():
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
        path_to_mat = f"{path_to_lib}\\{mat}"
        raw_str = f"{path_to_mat}\\RAW"
        config_str = f"{path_to_mat}\\config.yaml"
        parent_yaml_str = f"{path_to_mat}\\parent.yaml"
        other_str = f"{path_to_mat}\\OTHERFITS"
        nist_str = f"{path_to_mat}\\NIST"
        source = []
        if os.path.exists(raw_str): # Finds the raw data if it exists.
            path_to_RAW[mat] = raw_str
            source.append("RAW")
        if os.path.exists(other_str): # Finds other fits
            source.append("other")
        if os.path.exists(nist_str): # Finds NIST fit
            source.append("NIST")

        if not os.path.exists(config_str): # Check for existing JSON
            parent = "NA"
        else:
            with open(config_str, 'r') as file:
                mat_config = json.load(file)
            parent = mat_config[0]["parent"]

        yaml_dict = []
        for i in range(len(source)):
            yaml_dict.append({"name":f"{mat}", "parent":f"{parent}", "source":f"{source[i]}"}) # Define JSON dictionary
        yaml_dict = json.dumps(yaml_dict, indent=4)
        with open(config_str, 'w') as file:
            file.write(yaml_dict) # Write to new JSON


    # Load the JSON
    for mat in mat_directories:
        path_to_mat = f"{path_to_lib}\\{mat}"
        raw_str = f"{path_to_mat}\\RAW"
        config_str = f"{path_to_mat}\\config.yaml"

        if os.path.exists(raw_str):
            with open(config_str, 'r') as file:
                mat_config = json.load(file)
            parent = mat_config[0]["parent"]
            if parent != "NA":
                print(mat, "has parent:", parent)
                parent_dir = f"{path_to_lib}\\{parent}"
                if not os.path.exists(parent_dir):
                    os.mkdir(parent_dir)
                    os.mkdir(f"{parent_dir}\\RAW")
                raw_files = get_datafiles(raw_str)
                for file in raw_files:
                    shutil.copy(f"{raw_str}\\{file}", f"{parent_dir}\\RAW\\{file}")


    # Lets compile the different necessary paths for each material
    path_to_RAW = dict()
    path_to_fits = dict()
    path_to_plots = dict()

    for mat in mat_directories:
        path_to_mat = f"{path_to_lib}\\{mat}"
        raw_str = f"{path_to_mat}\\RAW"
        fits_str = f"{path_to_mat}\\fits"
        plots_str = f"{path_to_mat}\\plots"
        if os.path.exists(raw_str):
            path_to_RAW[mat] = raw_str
            if not os.path.exists(fits_str):
                os.mkdir(fits_str)
            path_to_fits[mat] = fits_str
            if not os.path.exists(plots_str):
                os.mkdir(plots_str)
            path_to_fits[mat] = fits_str
            path_to_plots[mat] = plots_str


    # Now we can loop through each material and run our fitting algorithm
    # You can also change the array that mat cycles through if you wish to only run the code for certain materials
    for mat in path_to_RAW.keys(): #  ["Kapton"]: # 
        perc_diff_avgs = np.array([])
        ## First, let's collect the raw data from their csv files
        big_data, data_dict = parse_raw(mat, path_to_RAW[mat], plots=True, weight_const=0.00)
        T, k, koT, weights = [big_data[:,0], big_data[:,1], big_data[:,2], big_data[:,3]]
        
        gaps = len(find_gaps(T, 0.8)) > 0
        # print(find_gaps(T, 100))
        maxT, minT = [max(T), min(T)]
        fit_orders = [3,3]
        fit_types = ["Nppoly", "polylog"]

        lenLow = len(T[T<=20])
        lenHi = len(T[T>=20])

        # lenHi = 10
        # lenLow = 0


        if lenHi==0:
            print(f"{mat} : Using a low fit")
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
                print(f"{mat} : Using a hi fit")
                hi_fit_xs, hi_fit = logk_function(np.log10(T), np.log10(k), fit_orders[1], weights)
                low_fit, erf_loc = [[0], -1]
                fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, fit_catch = "high")
                fit_args["combined_function_type"] = fit_types[1]
                perc_diff_hi, perc_diff_arr = get_percdiff(T[T>=min(hi_fit_xs)],k[T>=min(hi_fit_xs)], fit_args)
                fit_args["hi_perc_err"] = perc_diff_hi
                fit_args["low_perc_err"] =  0
                fit_args["combined_perc_err"] =  perc_diff_hi
                
        elif lenLow==0:
            print(f"{mat} : Using a hi fit")
            hi_fit_xs, hi_fit = logk_function(np.log10(T), np.log10(k), fit_orders[1], weights)
            low_fit, low_fit_xs, erf_loc = [[0], [0], -1]
            fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc)
            perc_diff_hi, perc_diff_arr = get_percdiff(T[T>=min(hi_fit_xs)],k[T>=min(hi_fit_xs)], fit_args)
            fit_args["hi_perc_err"] = perc_diff_hi
            fit_args["low_perc_err"] =  0
            fit_args["combined_perc_err"] =  perc_diff_hi
            fit_args["combined_function_type"] = fit_types[1]
        else:
            print(f"{mat} : Using a combined fit")# - data exists on both sides of 20K")
            erf_locList = np.linspace(np.sort(T)[0], np.sort(T)[-1], 15)
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

        if gaps:
            print(f"Gap found in data - splitting fit into low and high")
            low_array = format_splitfit(fit_args, "low")
            high_array = format_splitfit(fit_args, "hi")
            if (fit_args["low_fit_range"][0] == fit_args["low_fit_range"][1]):
                create_data_table(high_array, f"{path_to_fits[mat]}\\{mat}.txt")
                create_tc_csv(high_array, f"{path_to_fits[mat]}\\{mat}.csv")
            elif (fit_args["hi_fit_range"][0] == fit_args["hi_fit_range"][1]):
                create_data_table(low_array, f"{path_to_fits[mat]}\\{mat}.txt")
                create_tc_csv(low_array, f"{path_to_fits[mat]}\\{mat}.csv")
            else:
                create_data_table(low_array, f"{path_to_fits[mat]}\\{mat}_lo.txt")
                create_tc_csv(low_array, f"{path_to_fits[mat]}\\{mat}_lo.csv")
                create_data_table(high_array, f"{path_to_fits[mat]}\\{mat}_hi.txt")
                create_tc_csv(high_array, f"{path_to_fits[mat]}\\{mat}_hi.csv")
            make_fit_lh5(fit_args, path_to_fits[mat])

        else:
            # print(fit_args)
            output_array = format_combofit(fit_args)
            # Finally, we will output the fit parameters as a csv, and lh5 file - and plot the data.
            create_data_table(output_array, f"{path_to_fits[mat]}\\{mat}.txt")
            create_tc_csv(output_array, f"{path_to_fits[mat]}\\{mat}.csv")
            make_fit_lh5(fit_args, path_to_fits[mat])
            # PLOTTING CODE
        if plots:
            tk_plot(mat,path_to_RAW, data_dict, fit_args, fit_range = [100e-3, np.sort(T)[-1]], points=True, fits="combined", fill=True)

if __name__ == "__main__":
    main()