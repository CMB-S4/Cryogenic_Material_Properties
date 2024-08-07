## Author: Henry Nachman
## Description: This file contains many of the functions needed to properly format data,
## produce data fits, and save the resulting fits. This file must be imported for 
## the other files and notebooks of this repository to run.


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import string, yaml, csv, h5py
import sys,os
from datetime import datetime

abspath = os.path.abspath(__file__)
sys.path.insert(0, os.path.dirname(abspath))


from fit_types import * # Imports the different fit types from the associated file

cmap = cm.get_cmap('Dark2')

markers = ['o', 's', 'd', 'P','3', '*']

###############################################################
###############################################################
##################### DATA EXTRACTION  ########################
###############################################################
###############################################################

def get_datafiles(raw_path):
    """
    Arguments :
    - raw_path - path to the folder containing the raw data csv files.
    
    Returns :
    - raw_files - array of csv file names containing the raw measurement data.
    """
    all_files = os.listdir(raw_path)
    extension = ".csv"
    raw_files = [file for file in all_files if file.endswith(extension)]
    print(f"Found {len(raw_files)} measurements.")
    return raw_files

def parse_raw(material_name, raw_directory, plots=False, weight_const=0):
    """
    Arguments : 
    - material_name - a pointer for the material name, this much match the folder name.
    - path_dict     - a dictionary object linking the material name to the path address of the raw files.

    Returns : 
    - big_data  - Array of all measurements concatenated (no reference information).
    - data_dict - A dictionary of data with references as the keys.
    """
    all_files = os.listdir(raw_directory)
    extension = ".csv"
    raw_files = [file for file in all_files if file.endswith(extension)]
    
    big_data = np.empty((0,4), float)
    data_dict = dict()
    with open(f"{raw_directory}{os.sep}references.txt", 'w') as file:
        for f in raw_files:
            f_path = raw_directory + os.sep + f
            try:
                file1 = np.loadtxt(f_path, dtype=str, delimiter=',')
            except ValueError:
                print(f_path)
            file.write(f)
            file.write("\n")
            file.write(str(file1[0]))
            file.write("\n \n")
            ref_name = f[:-4]
            raw_data = np.array(file1[2:,:], dtype=float)           
            
            if weight_const != 0:
                # year weights
                year = ref_name[-4:]
                weights = np.ones((len(raw_data),1))*(1-(weight_const*(2024-int(year))))
                weights[weights<0]=0 # replaces all negative weights with 0
            else:
                weights = np.ones((len(raw_data),1))
            raw_data = np.append(raw_data, weights, axis = 1)

            big_data = np.append(big_data, raw_data, axis=0)

            data_dict[ref_name] = raw_data
            T, k, koT, weights = raw_data.T
            
            if plots:
                plt.plot(T, k, '.', label=ref_name)
    if plots:
        plt.legend()
        plt.xlabel("Temperature")
        plt.ylabel("k")
        plt.semilogx()
        plt.semilogy()
        plt.savefig(f"{os.path.split(raw_directory)[0]}{os.sep}plots{os.sep}{material_name}_RAWDATA.pdf", dpi=300, format="pdf", bbox_inches='tight')
        # plt.show()
        plt.close()

    if len(big_data[:,3][big_data[:,3]!=0]) == 0:
                print(f"Weight set to loss of {weight_const*100}% per year - No remaining data to fit")

    return big_data, data_dict

###############################################################
###############################################################
################## PARAMETER FORMATTING #######################
###############################################################
###############################################################

def generate_alphabet_array(n, case = "l"):
    """
    Description : Generates a list of n letters from the alphabet (used for making the human readable txt files). 
    """
    if case == "l":
        alphabet = list(string.ascii_lowercase)
    else:
        alphabet = list(string.ascii_uppercase)
    if n>1:
        return alphabet[:n]
    else:
        return [] ####################################### 20240612
    
def format_combofit(fit_args):
    """
    Description : Makes a dictionary of strings with the appropriate formating and headings to be saved in other file formats.
    """
    
    max_fit_param = 0
    num_fit_param_hi = len(fit_args["hi_fit_param"])
    num_fit_param_lo = len(fit_args["low_fit_param"])
    num_fit_param_combined = len(fit_args["combined_fit_param"])

    n = num_fit_param_combined
    result_lo = generate_alphabet_array(num_fit_param_lo, "l")
    result_hi = generate_alphabet_array(num_fit_param_hi, "h")
    result = np.append(result_lo, result_hi)
    # result = np.append(result, "erf param") ################################### 20240605
    result = list(result)

    output_array = []
    keys = ["Fit Type", "Low Temp", "High Temp", "Perc Err", "erf param"] + result ################################### 20240605

    for i in ["low", "hi", "combined"]:
        dict_vals = []
        dict_vals = np.append(dict_vals, np.array(fit_args[f"{i}_function_type"], dtype=str).flatten())
        dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', np.array(fit_args[f"{i}_fit_range"], dtype=float)).flatten())
        dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', float(fit_args[f"{i}_perc_err"])))
        param_str_arr  = np.char.mod('%0.' + str(5) + 'e', np.array(fit_args[f"{i}_fit_param"], dtype=float)).flatten()
        while len(param_str_arr) < len(result):
            param_str_arr = np.append(param_str_arr, np.char.mod('%0.' + str(5) + 'e',[0]))
        dict_vals = np.append(dict_vals, param_str_arr)
    
        mat_dict = dict(zip(keys, dict_vals))
        output_array.append(mat_dict)
    return output_array

def format_splitfit(fit_args, fit = "low"):
    """
    Description : Makes a dictionary of strings with the appropriate formating and headings to be saved in other file formats.
    """
    
    max_fit_param = 0
    
    num_fit_param_hi = len(fit_args["hi_fit_param"])
    num_fit_param_lo = len(fit_args["low_fit_param"])
    if fit=="low":
        num_fit_param_hi = -1
    elif fit=="hi":
        num_fit_param_lo = -1
    num_fit_param_combined = len(fit_args["combined_fit_param"])

    n = num_fit_param_combined
    result_lo = generate_alphabet_array(num_fit_param_lo, "l")
    result_hi = generate_alphabet_array(num_fit_param_hi, "h")
    result = np.append(result_lo, result_hi)
    # result = np.append(result, "erf param") ################################### 20240605
    result = list(result)
    output_array = []
    keys = ["Fit Type", "Low Temp", "High Temp", "Perc Err", "erf param"] + result ################################### 20240605

    dict_vals = []
    dict_vals = np.append(dict_vals, np.array(fit_args[f"{fit}_function_type"], dtype=str).flatten())
    dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', np.array(fit_args[f"{fit}_fit_range"], dtype=float)).flatten())
    dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', float(fit_args[f"{fit}_perc_err"])))
    param_str_arr  = np.char.mod('%0.' + str(5) + 'e', np.array(fit_args[f"{fit}_fit_param"], dtype=float)).flatten()
    while len(param_str_arr) < len(result):
        param_str_arr = np.append(param_str_arr, np.char.mod('%0.' + str(5) + 'e',[0]))
    
    dict_vals = np.append(dict_vals, param_str_arr)

    mat_dict = dict(zip(keys, dict_vals))
    output_array.append(mat_dict)
    return output_array

def dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, perc_err=[0,0,0], fit_catch="NONE"):#, kdata):
    # low_func = f"{fit_orders[0]} order {fit_types[0]}"
    # hi_func = f"{fit_orders[1]} order {fit_types[1]}"
    
    low_func = f"{fit_types[0]}"
    hi_func = f"{fit_types[1]}"

    low_param = np.array(low_fit)
    low_param = low_param[::-1] ################################### 2024053

    hi_param = np.array(hi_fit)
    hi_param = hi_param[::-1] ################################### 20240531

    if fit_catch == "low":
        all_params = np.append(erf_loc, [low_param]) ################################### 20240605
    elif fit_catch == "high":
        all_params = np.append(erf_loc, [hi_param])################################### 20240612
    else:
        all_params = np.append(erf_loc, np.append(low_param, hi_param))################################### 20240612


    #########
    arg_dict = {"low_function_type"  : low_func,
                "low_fit_param"      : low_param.tolist(),
                "low_fit_range"      : np.array([min(low_fit_xs), max(low_fit_xs)]).tolist(),
                "hi_function_type"   : hi_func,
                "hi_fit_param"       : hi_param.tolist(),
                "hi_fit_range"       : np.array([10**min(hi_fit_xs), 10**max(hi_fit_xs)]).tolist(),
                "combined_function_type" : "comppoly",
                "combined_fit_param" : all_params.tolist(),
                "combined_fit_range" : np.array([min(min(low_fit_xs), 10**min(hi_fit_xs)), max(max(low_fit_xs), 10**max(hi_fit_xs))]).tolist(),
                "combined_fit_erfloc": erf_loc ################## 20240605
                }
    return arg_dict

def dict_monofit(fit_param, fit_range, fit_type, perc_err="??"):  
    fit_param = fit_param[::-1] ################################### 20240531
    arg_dict = {"combined_function_type" : fit_type,
                "combined_fit_param" : fit_param.tolist(),
                "combined_fit_range" : np.array(fit_range).tolist(),
                "combined_perc_err": perc_err}
    return arg_dict

def format_monofit(fit_args):
    """
    Description : Makes a dictionary of strings with the appropriate formating and headings to be saved in other file formats.
    """
    num_fit_param_combined = len(fit_args["combined_fit_param"])

    result = list(generate_alphabet_array(num_fit_param_combined, "l"))
    
    output_array = []
    keys = ["Fit Type", "Low Temp", "High Temp", "Perc Err"] + result

    for i in ["combined"]:
        dict_vals = []
        dict_vals = np.append(dict_vals, np.array(fit_args[f"{i}_function_type"], dtype=str).flatten())
        dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', np.array(fit_args[f"{i}_fit_range"], dtype=float)).flatten())
        dict_vals = np.append(dict_vals, fit_args[f"{i}_perc_err"])

        param_str_arr  = np.char.mod('%0.' + str(5) + 'e', np.array(fit_args[f"{i}_fit_param"], dtype=float)).flatten()

        while len(param_str_arr) < len(result):
            param_str_arr = np.append(param_str_arr, np.char.mod('%0.' + str(5) + 'e',[0]))
    
        dict_vals = np.append(dict_vals, param_str_arr)
    
        mat_dict = dict(zip(keys, dict_vals))
        output_array.append(mat_dict)
    
    return output_array

def find_closest(arr, val): 
    diff_arr = arr-val
    stored_T = max(diff_arr)
    stored_index = 0
    for i in range(len(arr)):
        if (diff_arr[i] > 0) and (diff_arr[i] < stored_T):
            stored_T = diff_arr[i]
            stored_index = i
        else:
            pass
    return stored_T, stored_index

def split_data(big_data, erf_loc):
    # divide the data array into three columns
    T, k, koT, weights = [big_data[:,0], big_data[:,1], big_data[:,2], big_data[:,3]]

    # # Version 2 of Code
    # # Find the low range
    # arg_low = np.argwhere(T<erf_loc)
    # try:
    #     next_T, next_index = find_closest(T, max(T[arg_low]))
    #     arg_low = np.append(arg_low,[next_index])
    # except ValueError:
    #     pass
    # print(erf_loc, arg_low)
    # lowT, lowT_k, lowT_koT = [T[arg_low], k[arg_low], koT[arg_low]]
    
    # # Find the high range
    # # print(np.arange(0,len(T)), arg_low)
    # arg_high = [i not in arg_low for i in np.arange(0,len(T))]
    # try:
    #     arg_high = np.append(arg_high, np.argmax(T[T<erf_loc]))
    # except ValueError:
    #     pass
    # # if len(arg_high)==len(T):
    # #     arg_high[-1] = False
    # hiT, hiT_k, hiT_koT = [T[arg_high], k[arg_high], koT[arg_high]]
    # low_ws, hi_ws = [weights[arg_low], weights[arg_high]]

    # Version 1 of Code
    lowT, lowT_k, lowT_koT = [T[T<erf_loc], k[T<erf_loc], koT[T<erf_loc]]
    hiT, hiT_k, hiT_koT = [T[T>erf_loc], k[T>erf_loc], koT[T>erf_loc]]
    low_ws, hi_ws = [weights[T<erf_loc], weights[T>erf_loc]]

    return [lowT, lowT_k, lowT_koT, low_ws, hiT, hiT_k, hiT_koT, hi_ws]

###############################################################
###############################################################
################## PARAMETER OUTPUT ###########################
###############################################################
###############################################################

def make_fit_yaml(fit_args, save_path):
    """
    Description : Takes fit arguments and exports a yaml text file with the included information.
    """
    with open(f"{save_path}{os.sep}{os.path.split(save_path)[1]}.yaml", 'w') as file:
        for key in fit_args.keys():
            yaml.dump(key, file)
            yaml.dump(np.array(fit_args[key]).tolist(), file)
    return

def make_fit_lh5(fit_args, save_path):
    """
    Description : Takes fit arguments and exports a lh5 file with the included information.
    """
    comp_file = f"{save_path}{os.sep}{os.path.split(save_path)[1]}.lh5"
    with h5py.File(comp_file, "w") as f:
        for key in fit_args:
            f.create_dataset(f"{key}", data=fit_args[key])
    return comp_file

def compile_csv(path_to_fits):
    """
    Description : Compiles the fit data of every material and outputs to a single array.
    """
    output_array = []
    for mat in path_to_fits.keys():
        file = path_to_fits[mat]
        if not os.path.exists(f"{file}{os.sep}{mat}.csv"):
            for i in ["lo", "hi"]:
                material_file = np.loadtxt(f"{file}{os.sep}{mat}_{i}.csv", dtype=str, delimiter=',')
                headers = material_file[0]
                headers = np.append([f"Material Name"], headers)
                comb_fit = material_file[-1]
                comb_fit = np.append([f"{mat}_{i}"], comb_fit)
                mat_dict = dict(zip(headers, comb_fit))
                output_array.append(mat_dict)
        else:
            material_file = np.loadtxt(f"{file}{os.sep}{mat}.csv", dtype=str, delimiter=',')
            headers = material_file[0]
            headers = np.append(["Material Name"], headers)
            comb_fit = material_file[-1]
            comb_fit = np.append([f"{mat}"], comb_fit)
            mat_dict = dict(zip(headers, comb_fit))
            output_array.append(mat_dict)

    return output_array


def create_data_table(data, output_file):
    """
    Description : Formats a dictionary in string style for saving to text file formats and saves to txt file.
    """
    # Extract column names from the first dictionary
    longest = 0
    longest_arg = 0
    columns = []
    for i in range(len(data)):
        for key in data[i].keys():
            if not key in columns:
                columns.append(key)
        # print(columns)
        # if len(data[i].keys())>longest:
        #     longest = len(data[i].keys())
        #     longest_arg = i
    
    # columns = list(data[longest_arg].keys())
                
    # Find the maximum width for each column
    column_widths = {column: (len(str(column))+18) for column in columns}
    # Open the output file in write mode
    with open(output_file, 'w') as file:
        # Write the header row
        file.write('| ' + ' | '.join(column.ljust(column_widths[column]) for column in columns) + ' |\n')
        # Write the separator row
        file.write('| ' + '---'.join(['-' * column_widths[column] for column in columns]) + ' |\n')

        for row in data:
            file.write("| ")
            write_row = []
            for param in columns:
                if np.isin(param, list(row.keys())):
                    add = str(row[param])
                    add = add.replace( "^", "0.00e+00")
                    add = add.replace( "0.00000e+00", "0.00e+00")
                    write_row.append(add)
                else:
                    write_row.append("0.00e+00")
            for i in range(len(write_row)):
                file.write(''.join(write_row[i]).ljust(column_widths[list(column_widths.keys())[i]])+" | ")
            file.write('\n')
    return

def create_tc_csv(data, output_file):
    """
    Description : Formats a dictionary and saves to csv file.
    """
    # Extract column names from the first dictionary
    # longest = 0
    # longest_arg = 0
    # for i in range(len(data)):
    #     if len(data[i].keys())>longest:
    #         longest = len(data[i].keys())
    #         longest_arg = i
    # # Extract column names from the first dictionary
    # columns = list(data[longest_arg].keys())

    columns = []
    for i in range(len(data)):
        for key in data[i].keys():
            if not key in columns:
                columns.append(key)
        # Open the output file in write mode with newline='' to ensure consistent line endings
    with open(output_file, 'w', newline='') as csvfile:
        # Create a CSV writer object
        csv_writer = csv.writer(csvfile)

        # Write the header row
        csv_writer.writerow(columns)

        # Write each data row
        for row in data:
            write_row = []
            for param in columns:
                if np.isin(param, list(row.keys())):
                    add = str(row[param])
                    add = add.replace( "^", "0.00e+00")
                    add = add.replace( "0.00000e+00", "0.00e+00")
                    write_row.append(add)
                else:
                    write_row.append("0.00e+00")
            csv_writer.writerow(write_row)
    return


###############################################################
###############################################################
######################## PLOTTING #############################
###############################################################
###############################################################

def plot_datapoints(data_dict):
    i = 0
    m = 1
    for ref_name in data_dict.keys():
        T, k, koT, ws = data_dict[ref_name].T
        plt.plot(T, k, marker=markers[i], ms=7, mfc='none', ls='none', label=ref_name, c=cmap((i%6)/6), alpha=np.mean(ws))
        # Adjustments for CFRP
        # print(ref_name) #, contains_word = bool(re.search(r'\b{}\b'.format(re.escape(word_to_check)), phrase)))
        # if m == 1:
        #     label="Clearwater"
        #     marker = markers[1]
        #     c=cmap((m%6)/6)
        #     plt.plot(T, k, marker=marker, ms=12, mfc='none', ls='none', label=label, c=c, alpha=1)
        # elif m==6:
        #     label = "DPP"
        #     marker = markers[2]
        #     c=cmap((m%6)/6)
        #     plt.plot(T, k, marker=marker, ms=12, mfc='none', ls='none', label=label, c=c, alpha=1)
        # elif m==8:
        #     label = "Graphlite"
        #     marker = markers[3]
        #     c=cmap((m%6)/6)
        #     plt.plot(T, k, marker=marker, ms=12, mfc='none', ls='none', label=label, c=c, alpha=1)
        # elif m==9:
        #     label = "Runyan/Jones \nGraphlite"
        #     marker = markers[5]
        #     c=cmap((m%6)/6)
        #     plt.plot(T, k, marker=marker, ms=12, mfc='none', ls='none', label=label, c=c, alpha=1)
        # else:
        #     label="none"
        # plt.plot(T, k, marker=marker, ms=12, mfc='none', ls='none', c=c, alpha=np.mean(ws))
        # Adjustments for SS304 simplified
        # plt.plot(T, k, marker=markers[i], ms=15, mfc='none', ls='none', label=f"Ref {m}", c=cmap((i%6)/6), alpha=np.mean(ws))

        i+=1
        m+=1
        if i == len(markers):
            i = 0
    return

def get_plotting_data(material_name, path_dict, data_dict, fit_args, fit_range):
    # Defines the directory for saving
    raw_directory = path_dict[material_name]

    # Extracts the fit parameters from the fit args object
    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["combined_fit_erfloc"], fit_args["combined_function_type"] ################################### 20240605
    
    # Defines a range over which to model the fit
    if fit_args["low_fit_range"][1] == 0:
        upper_bound = fit_range[1]
    else:
        upper_bound = fit_args["low_fit_range"][1]
    if fit_args["hi_fit_range"][0] == 0:
        lower_bound = fit_range[0]
    else:
        lower_bound = fit_args["hi_fit_range"][0]
    
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [lower_bound, upper_bound],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    
    low_t_range = np.linspace(fit_range[0],upper_bound,100)
    low_fit_k = loglog_func(low_t_range, param_dictionary)
    low_fit_koT = low_fit_k/low_t_range
    hi_t_range = np.linspace(lower_bound,fit_range[1],100)
    hi_fit_k = loglog_func(hi_t_range, param_dictionary)
    
    # extracts all the temp and tc data
    Tdata = np.concatenate([(data_dict[ref_name].T[0]) for ref_name in data_dict])
    kdata = np.concatenate([(data_dict[ref_name].T[1]) for ref_name in data_dict])

    # redefines the plot range based on data
    fit_range = [100e-4, 1.1*max(Tdata)]
    full_T_range = np.logspace(np.log10(fit_range[0]),np.log10(fit_range[1]),100)
    return Tdata, kdata, low_t_range, hi_t_range, low_fit_k, hi_fit_k, full_T_range, raw_directory


def plot_full(material_name: str, path_dict, data_dict, fit_args, fit_range=[100e-4,25e2], points=True, fits="combined", fill=False):
    Tdata, kdata, low_t_range, hi_t_range, low_fit_k, hi_fit_k, full_T_range, raw_directory = get_plotting_data(material_name, path_dict, data_dict, fit_args, fit_range)
    # Plots the data points
    plt.figure(figsize=(13, 11))
    if points:
        plot_datapoints(data_dict)

    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["combined_fit_erfloc"], fit_args["combined_function_type"] ################################### 20240605
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [min(Tdata), max(Tdata)],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531

    k_fit_combined = loglog_func(full_T_range, param_dictionary)
    if fits=="combined":
        plt.plot(full_T_range, k_fit_combined, linewidth=3, label='fit', c="c")
        if fill:
            avg_perc_diff, perc_diff_arr = get_percdiff(Tdata, kdata, fit_args)
            low_avg_perc_diff, hi_avg_perc_diff = [0,0]
            if len(Tdata[Tdata<30])>0:
                low_avg_perc_diff, low_perc_diff_arr = get_percdiff(Tdata[Tdata<30], kdata[Tdata<30], fit_args)
            if len(Tdata[Tdata>30])>0:
                hi_avg_perc_diff, hi_perc_diff_arr = get_percdiff(Tdata[Tdata>30], kdata[Tdata>30], fit_args)
            plt.fill_between(full_T_range, k_fit_combined*(1+avg_perc_diff/100), (k_fit_combined*(1-avg_perc_diff/100)),
                             alpha=0.25, color="c",
                             label=f"{np.char.mod('%0.' + str(2) + 'f', avg_perc_diff)}%")
                            #  label=f"{np.char.mod('%0.' + str(2) + 'f', avg_perc_diff)}, low: {np.char.mod('%0.' + str(2) + 'f', low_avg_perc_diff)}, hi: {np.char.mod('%0.' + str(2) + 'f', hi_avg_perc_diff)}%")
    # Plots the fits as they are seperately (rather then the combined fit)
    if fits=="split":
        plt.plot(low_t_range, low_fit_k, c='b')
        plt.plot(hi_t_range, hi_fit_k, c='b')        
    # plt.legend(loc='center right', bbox_to_anchor=(1.5, 0.5), fontsize=20)
    fs = 26
    plt.legend(loc='center right', bbox_to_anchor=(1.7, 0.5), fontsize=fs)    
    plt.xlabel("Temperature [K]", fontsize=fs)
    plt.xticks(fontsize=fs)
    plt.yticks(fontsize=fs)
    plt.ylabel("k [W/m/K]", fontsize=fs)
    plt.title(f"{material_name}", fontsize=32)
    plt.semilogx()
    plt.semilogy()
    plt.savefig(f"{os.path.split(raw_directory)[0]}{os.sep}plots{os.sep}{material_name}_fullPlot.pdf", dpi=300, format="pdf", bbox_inches='tight')
    plt.grid(True, which="both", ls="-", color='0.65', alpha=0.35)
    # plt.show()
    plt.close()
    
    return

def get_percdiff(Tdata, kdata, fit_args):
    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["combined_fit_erfloc"], fit_args["combined_function_type"] ################################### 20240605
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [min(Tdata), max(Tdata)],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    
    # Calculates the predicted k value for the measured T values (rather than a continuous range)
    func = get_func_type(param_dictionary["fit_type"])
    kpred_discrete = func(Tdata, param_dictionary)

    diff = kpred_discrete-kdata                 # the difference between the predicted and measured k values
    perc_diff_arr = 100*diff/kpred_discrete     # Calculates a percent difference 
    avg_perc_diff = np.mean(abs(perc_diff_arr)) # finds the average of that percent difference
    return avg_perc_diff, perc_diff_arr

def plot_splitfits(material_name: str, path_dict, data_dict, fit_args, fit_range=[100e-4,25e2], fill=True):
    Tdata, kdata, low_t_range, hi_t_range, low_fit_k, hi_fit_k, full_T_range, raw_directory = get_plotting_data(material_name, path_dict, data_dict, fit_args, fit_range)

    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["combined_fit_erfloc"], fit_args["combined_function_type"] ################################### 20240605
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [min(Tdata), max(Tdata)],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    
    # Now let's get to plotting
    fig, axs = plt.subplots(2, figsize=(8, 6))
    i = 0
    for ref_name in data_dict.keys():
        T, k, koT, ws = data_dict[ref_name].T
        axs[0].plot(T, koT, marker=markers[i], ms=7, mfc='none', ls='none',label=ref_name, c=cmap((i%6)/6), alpha=np.mean(ws))
        axs[1].plot(T, k, marker=markers[i], ms=7, mfc='none', ls='none',label=ref_name, c=cmap((i%6)/6), alpha=np.mean(ws))
        i+=1
        if i == len(markers):
            i = 0
    
    # AXS 0
    koT_fit = (1/full_T_range)*loglog_func(full_T_range, param_dictionary) # 20240605
    axs[0].set_xlabel("T")
    axs[0].set_ylabel("k/T")
    axs[0].title.set_text(f"{material_name}\nLow Temperature Fit")
    axs[0].set_xlim(0.9*min(low_t_range), 1.1*max(low_t_range))
    axs[0].set_ylim(0.8*min(low_fit_k/low_t_range), 1.2*max(kdata[Tdata<1.1*max(low_t_range)]/Tdata[Tdata<1.1*max(low_t_range)]))
    axs[0].plot(full_T_range, koT_fit, label='combined fit', c="c")
    axs[0].grid(True, which="both", ls="-", color='0.65')
    if fill:
        avg_perc_diff, perc_diff_arr = get_percdiff(Tdata, kdata, fit_args)
        low_avg_perc_diff, hi_avg_perc_diff = [0,0]
        if len(Tdata[Tdata<30])>0:
            low_avg_perc_diff, low_perc_diff_arr = get_percdiff(Tdata[Tdata<30], kdata[Tdata<30], fit_args)
        if len(Tdata[Tdata>30])>0:
            hi_avg_perc_diff, hi_perc_diff_arr = get_percdiff(Tdata[Tdata>30], kdata[Tdata>30], fit_args)
        axs[0].fill_between(full_T_range, koT_fit*(1+avg_perc_diff/100), (koT_fit*(1-avg_perc_diff/100)), alpha=0.25, color="c",
                            label=f"{np.char.mod('%0.' + str(2) + 'f', avg_perc_diff)}, low: {np.char.mod('%0.' + str(2) + 'f', low_avg_perc_diff)}, hi: {np.char.mod('%0.' + str(2) + 'f', hi_avg_perc_diff)}%")
    # AXS 1
    # axs[1].loglog(hi_xs, hi_fit_val)
    axs[1].plot(hi_t_range, hi_fit_k, c="c")
    axs[1].semilogx()
    axs[1].grid(True, which="both", ls="-", color='0.65')
    axs[1].set_ylabel("k")
    axs[1].set_xlabel("T")
    axs[1].set_xlim(0.9*min(hi_t_range), 1.1*max(hi_t_range))
    axs[1].set_ylim(0.9*min(hi_fit_k), 1.1*max(hi_fit_k))
    axs[1].title.set_text("High Temperature Fit")
    if fill:
        axs[1].fill_between(hi_t_range, hi_fit_k*(1+avg_perc_diff/100), (hi_fit_k*(1-avg_perc_diff/100)), alpha=0.25, color="c",
                            label=f"{np.char.mod('%0.' + str(2) + 'f', avg_perc_diff)}, low: {np.char.mod('%0.' + str(2) + 'f', low_avg_perc_diff)}, hi: {np.char.mod('%0.' + str(2) + 'f', hi_avg_perc_diff)}%")
    plt.legend(loc='center right', bbox_to_anchor=(1.5, 1.2))
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    plt.savefig(f"{os.path.split(raw_directory)[0]}{os.sep}plots{os.sep}{material_name}_subplots.pdf", dpi=300, format="pdf", bbox_inches='tight')
    # if show:
    # plt.show()
    plt.close()

    return

def plot_residuals(material_name: str, path_dict, data_dict, fit_args, fit_range=[100e-4,25e2]):
    Tdata, kdata, low_t_range, hi_t_range, low_fit_k, hi_fit_k, full_T_range, raw_directory = get_plotting_data(material_name, path_dict, data_dict, fit_args, fit_range)
    avg_perc_diff, perc_diff_arr = get_percdiff(Tdata, kdata, fit_args)

    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["combined_fit_erfloc"], fit_args["combined_function_type"] ################################### 20240605
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [min(Tdata), max(Tdata)],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    

    # Residual Plots
    koT_pred = (1/Tdata)*loglog_func(Tdata, param_dictionary)
    koT_data = (1/Tdata)*kdata
    fig, axs = plt.subplots(2, figsize=(8, 6))
    # axs[0].plot(Tdata, koT_data-koT_pred, '.')
    axs[0].plot(Tdata, perc_diff_arr, '.', c=cmap(np.pi/10))
    # axs[0].plot(Tdata, 100*(koT_data-koT_pred)/koT_data, '.')
    axs[0].hlines(0, 0.9*min(low_t_range), 1.1*max(low_t_range))
    axs[0].set_xlabel("Temperature (K)")
    # axs[0].set_ylabel("residuals in % of k/T")
    axs[0].set_ylabel("residuals in % of k")
    axs[0].set_xlim(0.9*min(low_t_range), 1.1*max(low_t_range))
    axs[0].set_ylim(0.9*min(perc_diff_arr), 1.1*max(perc_diff_arr))
    axs[0].semilogx()
    axs[0].title.set_text(f"{material_name}")
    # AXS 1
    # axs[1].plot(Tdata, kdata-kpred, '.')
    axs[1].plot(Tdata, perc_diff_arr, '.', c=cmap(np.pi/10))
    axs[1].hlines(0, 0.9*min(hi_t_range), 1.1*max(hi_t_range))
    axs[1].set_xlabel("Temperature (K)")
    axs[1].set_ylabel("residuals in % of k")
    axs[1].set_xlim(0.9*min(hi_t_range), 1.1*max(hi_t_range))
    axs[1].set_ylim(0.9*min(perc_diff_arr), 1.1*max(perc_diff_arr))
    axs[1].semilogx()
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    plt.savefig(f"{os.path.split(raw_directory)[0]}{os.sep}plots{os.sep}{material_name}_ResidualPlots.pdf", dpi=300, format="pdf", bbox_inches='tight')
    # plt.show()
    plt.close()

    return

def tk_plot(material_name: str, path_dict, data_dict, fit_args, fit_range=[100e-4,25e2], points=True, fits="combined", fill=False):
    """
    Description : Produces a beautiful plot of the raw data with the fit.

    Arguments :
    - material_name - material name
    - path_dict     - dictionary type of paths to data
    - data_dict     - dictionary of raw data with reference information as keys
    - fit_args      - combined fit arguments
    - fit_range     - default=[100e-4,25e2] -
    - points        - default=True          - Boolean argument, if true, data points are added to the plot.
    - fits          - options: 'combined', 'low', 'hi', other - defines which fits to plot.
    - fill          - default=False         - Boolean argument, if true, 15% confidence interval is shaded around plot.
    - show          - default=True          - Boolean argument, if true, plot is shown in notebook.

    Returns : 
    - null
    """    
    plot_full(material_name, path_dict, data_dict, fit_args, fit_range, points, fits, fill)

    plot_splitfits(material_name, path_dict, data_dict, fit_args, fit_range, fill)

    plot_residuals(material_name, path_dict, data_dict, fit_args, fit_range)

    return


###############################################################
###############################################################
######################### FITTING #############################
###############################################################
###############################################################
def dual_tc_fit(big_data, save_path, erf_loc = 20, fit_orders = (3,3), fit_types=("Nppoly", "polylog"), plots=False):
    """
    Arguments :
    - big_data   - Array of measurement data concatenated (should be of shape: [N, 3])
    - save_path  - File path to publish output files and plots.
    - erf_loc     - default=20    - Temperature at which to split the data for fitting (and to place the error function).
    - fit_orders - default=(3,3) - Polynomial fit order (low, high).
    - fit_types  - default=("k/T", "loglog") - defines the type of fit for each regime (low, high).
    - plots      - default=False - Boolean argument, if true, plots are made and saved to save_path.

    Returns :
    - arg_dict - Dictionary of fit arguments - includes low fit, high fit, and combined fit arguments.
    """
    
    dsplit = split_data(big_data, erf_loc)
    lowT, lowT_k, lowT_koT, low_ws, hiT, hiT_k, hiT_koT, hi_ws = dsplit

    # Take a log10 of the high range
    log_hi_T = np.log10(hiT)
    log_hi_k = np.log10(hiT_k)
    # Fit the low data
    try:
        if (fit_types[0] == "Nppoly") and (len(lowT)!=0):
            low_fit_xs, low_fit = koT_function(lowT, lowT_koT, fit_orders[0], low_ws)
        elif (len(lowT)==0):
            low_fit = [0]
            low_fit_xs = [0]

        # Fit the high data
        
        if fit_types[1] == "polylog" and (len(hiT)!=0):
            hi_fit_xs, hi_fit = logk_function(log_hi_T, log_hi_k, fit_orders[1], hi_ws)
        elif (len(hiT)==0):
            hi_fit = [0]
            hi_fit_xs = [0]

    except np.linalg.LinAlgError:
        print("LinAlgError - likely not enough points after weight to fit the data.")
        raise np.linalg.LinAlgError()
        
    # # Combine the fits
    # xrange_total = np.linspace(min(lowT), max(hiT), 100)
    # logk = loglog(xrange_total, low_poly1d, hi_poly1d, erf_place)
    # #

    if plots:
        fig, axs = plt.subplots(2, figsize=(8, 6))
        axs[0].plot(lowT, lowT_koT,'.')
        axs[0].plot(low_fit_xs, np.polyval(low_fit, low_fit_xs))
        axs[0].set_xlabel("T")
        axs[0].set_ylabel("k/T")
        axs[0].title.set_text("Low Temperature Fit")
        axs[1].loglog(10**hi_fit_xs, 10**np.polyval(hi_fit, hi_fit_xs))
        axs[1].loglog(hiT, hiT_k, '.')
        axs[1].grid(True, which="both", ls="-", color='0.65')
        axs[1].set_ylabel("k")
        axs[1].set_xlabel("T")
        axs[1].title.set_text("High Temperature Fit")
        plt.subplots_adjust(wspace=0.4, hspace=0.4)
        plt.savefig(f"{save_path}{os.sep}plots{os.sep}fits_subplots.pdf", dpi = 300, format="pdf")
        # plt.show()
        plt.close()


    arg_dict = dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc)#, k)
    return arg_dict


def find_gaps(data_array, threshold=0.5):
    """
    threshold - in log space
    """
    # Sort the array and keep track of the original indices
    sorted_indices = np.argsort(data_array)
    sorted_data = data_array[sorted_indices]
    
    # Calculate differences between consecutive elements
    diffs = np.diff(np.log10(sorted_data))
    
    # Find indices where differences exceed threshold
    major_gap_indices_sorted = np.where(diffs > threshold)[0]
    
    # Map these indices back to the original unsorted array
    major_gap_indices_original = sorted_indices[major_gap_indices_sorted]
    
    # Return indices of major gaps in the original array
    return major_gap_indices_original
