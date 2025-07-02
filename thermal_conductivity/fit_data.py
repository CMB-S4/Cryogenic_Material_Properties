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
from tqdm import tqdm

# note : most functions needed for running this notebook can be found in tc_utils.
from tc_utils import *
from tc_plots import get_percdiff, tk_plot

verbose = False  # Set this to True to enable print statements

def fit_lowT_data(mat, T, k, koT, fit_orders, weights, fit_types):
    if verbose:
        print(f"{mat:>15} : Using a low fit")
    low_fit_xs, low_fit = koT_function(T, koT, fit_orders[0], weights)
    hi_fit, hi_fit_xs, erf_loc = [[], [], 0]
    fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, fit_catch = "low")
    fit_args["combined_function_type"] = fit_types[0]
    perc_diff_low, perc_diff_arr = get_percdiff(T[T<=max(low_fit_xs)],k[T<=max(low_fit_xs)], fit_args)
    fit_args["low_perc_err"] =  perc_diff_low
    fit_args["hi_perc_err"] =  0
    fit_args["combined_perc_err"] =  perc_diff_low
    fit_args["combined_function_type"] = fit_types[0]
    if perc_diff_low > 50:
        if verbose:
            print(f"{mat:>15} : Using a hi fit")
        hi_fit_xs, hi_fit = logk_function(np.log10(T), np.log10(k), fit_orders[1], weights)
        low_fit, erf_loc = [[], -1]
        fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, fit_catch = "high")
        fit_args["combined_function_type"] = fit_types[1]
        perc_diff_hi, perc_diff_arr = get_percdiff(T[T>=min(hi_fit_xs)],k[T>=min(hi_fit_xs)], fit_args)
        fit_args["hi_perc_err"] = perc_diff_hi
        fit_args["low_perc_err"] =  0
        fit_args["combined_perc_err"] =  perc_diff_hi
    return fit_args

def fit_highT_data(mat, T, k, koT, fit_orders, weights, fit_types):
    if verbose:
        print(f"{mat:>15} : Using a hi fit")
    hi_fit_xs, hi_fit = logk_function(np.log10(T), np.log10(k), fit_orders[1], weights)
    low_fit, low_fit_xs, erf_loc = [[], [], -1]
    fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, fit_catch= "high")
    perc_diff_hi, perc_diff_arr = get_percdiff(T[T>=min(hi_fit_xs)],k[T>=min(hi_fit_xs)], fit_args)
    fit_args["hi_perc_err"] = perc_diff_hi
    fit_args["low_perc_err"] =  0
    fit_args["combined_perc_err"] =  perc_diff_hi
    fit_args["combined_function_type"] = fit_types[1]
    return fit_args

def fit_combined_data(mat, T, k, koT, fit_orders, weights, fit_types, big_data, path_to_plots):
    if verbose:
        print(f"{mat:>15} : Using a combined fit")
    erf_locList = np.linspace(np.sort(T)[0], np.sort(T)[-1], 15)
    perc_diff_avgs = np.array([])
    for erf_loc in erf_locList:
        dsplit = split_data(big_data, erf_loc)
        lowT, lowT_k, lowT_koT, low_ws, hiT, hiT_k, hiT_koT, hi_ws = dsplit
        log_hi_T = np.log10(hiT)
        log_hi_k = np.log10(hiT_k)
        if (len(lowT)==0):
            low_fit = []
            low_fit_xs = []
        else:
            low_fit_xs, low_fit = koT_function(lowT, lowT_koT, fit_orders[0], low_ws)
        if (len(hiT)==0):
            hi_fit = []
            hi_fit_xs = []
        else:
            hi_fit_xs, hi_fit = logk_function(log_hi_T, log_hi_k, fit_orders[1], hi_ws)
        fit_args = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc)
        perc_diff_avg, perc_diff_arr = get_percdiff(T, k, fit_args)
        perc_diff_avgs = np.append(perc_diff_avgs, perc_diff_avg)
    erf_locdict = dict(zip(erf_locList, perc_diff_avgs))
    bestRes = min(erf_locdict.values())
    besterf_loc = [key for key in erf_locdict if erf_locdict[key] == bestRes]
    fit_args = dual_tc_fit(big_data, path_to_plots[mat], erf_loc=min(besterf_loc), fit_orders=fit_orders, plots=False)
    perc_diff_avg, perc_diff_arr = get_percdiff(T, k, fit_args)
    if verbose:
        print(f"Low-Hi split centered at : {min(besterf_loc)} ~~ with average percent difference value of: {perc_diff_avg:.2f}%")
    if len(fit_args["low_fit_range"]) == 0:
        fit_args["low_perc_err"] = []
    else:
        perc_diff_low, perc_diff_arr = get_percdiff(T[T<=max(fit_args["low_fit_range"])],k[T<=max(fit_args["low_fit_range"])], fit_args)
        fit_args["low_perc_err"] =  perc_diff_low
    if len(fit_args["hi_fit_range"]) == 0:
        fit_args["hi_perc_err"] = []
    else:
        perc_diff_hi, perc_diff_arr = get_percdiff(T[T>=min(fit_args["hi_fit_range"])],k[T>=min(fit_args["hi_fit_range"])], fit_args)
        fit_args["hi_perc_err"] =  perc_diff_hi
    if len(fit_args["combined_fit_range"]) == 0:
        fit_args["combined_perc_err"] = []
    else:
        perc_diff_combo, perc_diff_arr = get_percdiff(T[T>=min(fit_args["combined_fit_range"])],k[T>=min(fit_args["combined_fit_range"])], fit_args)
        fit_args["combined_perc_err"] =  perc_diff_combo
    return fit_args

def main():
    global verbose
    parser = argparse.ArgumentParser(description="Run the thermal conductivity fitting program.")
    parser.add_argument('--matlist', help="List of materials to fit, add sequentially with space delimiters and no brackets (with quotes)", type=str, nargs="+", default=None)
    parser.add_argument('--plot', help="Boolean: make plots?", type=bool, default=True)
    parser.add_argument('--verbose', help="Boolean: print verbose output?", action='store_true')
    args = parser.parse_args()
    plots = args.plot
    verbose = args.verbose

    abspath = os.path.abspath(__file__)
    path_to_lib = f"{os.path.split(abspath)[0]}{os.sep}lib"
    mat_directories = [folder for folder in os.listdir(path_to_lib) if not folder.endswith(".md")]

    path_to_RAW = dict()
    if args.matlist != None:
        if verbose:
            print(f"Running only for materials: {args.matlist}")
        mat_directories = args.matlist

    for mat in mat_directories:
        path_to_mat = f"{path_to_lib}{os.sep}{mat}"
        raw_str = f"{path_to_mat}{os.sep}RAW"
        config_str = f"{path_to_mat}{os.sep}config.yaml"
        parent_yaml_str = f"{path_to_mat}{os.sep}parent.yaml"
        other_str = f"{path_to_mat}{os.sep}OTHERFITS"
        nist_str = f"{path_to_mat}{os.sep}NIST"
        source = []
        if os.path.exists(raw_str):
            path_to_RAW[mat] = raw_str
            source.append("RAW")
        if os.path.exists(other_str):
            source.append("other")
        if os.path.exists(nist_str):
            source.append("NIST")
        if not os.path.exists(config_str): 
            parent = "NA"
            conf_fit_type = None
        else:
            with open(config_str, 'r') as file:
                mat_config = json.load(file)
            parent = mat_config[0]["parent"]
            conf_fit_type = None
        yaml_dict = []
        if len(source) == 0:
            source = ["NA"]
        for i in range(len(source)):
            yaml_dict.append({"name":f"{mat}", 
                              "parent":f"{parent}",
                              "source":f"{source[i]}",
                              "fit_type":f"{conf_fit_type}"})
        yaml_dict = json.dumps(yaml_dict, indent=4)
        with open(config_str, 'w') as file:
            file.write(yaml_dict)

    for mat in mat_directories:
        path_to_mat = f"{path_to_lib}{os.sep}{mat}"
        raw_str = f"{path_to_mat}{os.sep}RAW"
        config_str = f"{path_to_mat}{os.sep}config.yaml"
        if os.path.exists(raw_str):
            with open(config_str, 'r') as file:
                mat_config = json.load(file)
            parent = mat_config[0]["parent"]
            if parent != "NA":
                if verbose:
                    print(mat, "has parent:", parent)
                parent_dir = f"{path_to_lib}{os.sep}{parent}"
                if not os.path.exists(parent_dir):
                    os.mkdir(parent_dir)
                    os.mkdir(f"{parent_dir}{os.sep}RAW")
                raw_files = get_datafiles(raw_str)
                for file in raw_files:
                    shutil.copy(f"{raw_str}{os.sep}{file}", f"{parent_dir}{os.sep}RAW{os.sep}{file}")

    path_to_RAW = dict()
    path_to_fits = dict()
    path_to_plots = dict()

    for mat_num in tqdm(range(len(mat_directories))):
        mat = mat_directories[mat_num]
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
            if verbose:
                print(f"Skipping {mat} as it does not have a RAW directory.")
            continue

        with open(config_str, 'r') as file:
            mat_config = json.load(file)
        fit_type = mat_config[0]["fit_type"]

        big_data, data_dict = parse_raw(mat, path_to_RAW[mat], plots=True, weight_const=0.00)
        T, k, koT, weights = [big_data[:,0], big_data[:,1], big_data[:,2], big_data[:,3]]
        gaps = len(find_gaps(T, 0.8)) > 0
        maxT, minT = [max(T), min(T)]
        fit_orders = [3,3]
        fit_types = ["Nppoly", "polylog"]
        lenLow = len(T[T<=20])
        lenHi = len(T[T>=20])

        if fit_type == "None":
            if lenLow == 0 and lenHi == 0:
                if verbose:
                    print(f"{mat} : No data to fit")
                continue
            elif lenLow == 0:
                fit_type = fit_types[1]
            elif lenHi == 0:
                fit_type = fit_types[0]
            else:
                fit_type = "combined"

        if fit_type == fit_types[0]:
            fit_args = fit_lowT_data(mat, T, k, koT, fit_orders, weights, fit_types)
        elif fit_type == fit_types[1]:
            fit_args = fit_highT_data(mat, T, k, koT, fit_orders, weights, fit_types)
        elif fit_type == "combined":
            fit_args = fit_combined_data(mat, T, k, koT, fit_orders, weights, fit_types, big_data, path_to_plots)
        elif fit_type == "OFHC":
            continue

        if gaps:
            if verbose:
                print(f"Gap found in data - splitting fit into low and high")
            if len(fit_args["low_fit_range"]) == 0 and len(fit_args["hi_fit_range"]) == 0:
                if verbose:
                    print(f"{mat} : No data to fit")
                continue
            elif len(fit_args["low_fit_range"]) == 0:
                high_array = format_splitfit(fit_args, "hi")
                create_data_table(high_array, f"{path_to_fits[mat]}{os.sep}{mat}_hi.txt")
                create_tc_csv(high_array, f"{path_to_fits[mat]}{os.sep}{mat}_hi.csv")
            elif len(fit_args["hi_fit_range"]) == 0:
                low_array = format_splitfit(fit_args, "low")
                create_data_table(low_array, f"{path_to_fits[mat]}{os.sep}{mat}_lo.txt")
                create_tc_csv(low_array, f"{path_to_fits[mat]}{os.sep}{mat}_lo.csv")
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
