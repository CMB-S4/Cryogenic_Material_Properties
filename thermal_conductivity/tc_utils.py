## Author: Henry Nachman
## Description: This file contains many of the functions needed to properly format data,
## produce data fits, and save the resulting fits. This file must be imported for 
## the other files and notebooks of this repository to run.


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import string, yaml, csv
import h5py
import sys,os
from datetime import datetime
import regex as re
import pickle as pkl
abspath = os.path.abspath(__file__)
sys.path.insert(0, os.path.dirname(abspath))


from fit_types import * # Imports the different fit types from the associated file
from tc_plots import plot_interpolation
from tc_tools import get_parameters
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
    # print(f"Found {len(raw_files)} measurements.")
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
    # with open(f"{raw_directory}{os.sep}references.bib", 'w') as bfile:
    with open(f"{raw_directory}{os.sep}references.txt", 'w') as file:
        i = 0
        for rawfile in raw_files:
            f_path = raw_directory + os.sep + rawfile
            try:
                file1 = np.loadtxt(f_path, dtype=str, delimiter=',')
            except ValueError:
                print(f"Error loading {rawfile} as csv from {f_path}")
            file.write(f"Reference : {i}\n")
            file.write(f"Filename  : {rawfile}\n")
            file.write(f"Title     : {file1[0][0]}\n")
            file.write(f"Author(s) : {file1[0][1].replace('--',',')}\n")
            year_match = re.search(r'\b(19[0-9]{2}|20[0-9]{2})\b', rawfile)
            year = year_match.group(0) if year_match else "????"
            file.write(f"Year      : {year}\n")
            file.write(f"Publisher : {file1[0][2]}\n")
            file.write(f"Search Key: {file1[0]}\n")
            file.write(f"\n-----------------------------------------------------\n")
            file.write("\n")
            # bfile.write(f"@article{{{year}_{i},\n")
            # bfile.write(f"  title = {{{file1[0][0]}}},\n")
            # bfile.write(f"  author = {{{file1[0][1].replace('--',',')}}},\n")
            # bfile.write(f"  year = {{{year}}},\n")
            # bfile.write(f"  publisher = {{{file1[0][2]}}},\n")
            # bfile.write(r"}")

            ref_name = rawfile[:-4]
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
            i+=1
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
    if n>=1:
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
    
    result = list(result)
    output_array = []
    keys = ["Fit Type", "Low Temp", "High Temp", "Perc Err"]
    if 'erfloc' in fit_args:
        keys.append("erf param")
    keys += result 

    for i in ["low", "hi", "combined"]:
        if len(fit_args[f"{i}_fit_param"]) == 0:
            # print(f"Skipping {i} fit as it has no parameters.")
            continue
        dict_vals = []
        dict_vals = np.append(dict_vals, np.array(fit_args[f"{i}_function_type"], dtype=str).flatten())
        dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', np.array(fit_args[f"{i}_fit_range"], dtype=float)).flatten())
        dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', float(fit_args[f"{i}_perc_err"])))
        dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', float(fit_args[f"erfloc"]))) ################################### 20250527
        param_str_arr  = np.char.mod('%0.' + str(5) + 'e', np.array(fit_args[f"{i}_fit_param"], dtype=float)).flatten()
        if i == "hi":
            param_str_arr = np.append(num_fit_param_lo*list(np.char.mod('%0.' + str(5) + 'e',[0])), param_str_arr)
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
    dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', float(0))) ################################### 20250527
    param_str_arr  = np.char.mod('%0.' + str(5) + 'e', np.array(fit_args[f"{fit}_fit_param"], dtype=float)).flatten()
    while len(param_str_arr) < len(result):
        param_str_arr = np.append(param_str_arr, np.char.mod('%0.' + str(5) + 'e',[0]))
    
    dict_vals = np.append(dict_vals, param_str_arr)

    mat_dict = dict(zip(keys, dict_vals))
    output_array.append(mat_dict)
    return output_array

def dict_combofit(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, perc_err=[0,0,0], fit_catch="NONE"):
    """
    Description : Makes a dictionary of the compound fit parameters and information with the appropriate formating and headings to be saved in other file formats.
    Arguments :
    - low_fit      - Array of the low fit parameters.
    - low_fit_xs   - Array of the low fit x values.
    - hi_fit       - Array of the high fit parameters.
    - hi_fit_xs    - Array of the high fit x values.
    - fit_orders   - Tuple of the fit orders for the low and high fits.
    - fit_types    - Tuple of the fit types for the low and high fits.
    - erf_loc      - Location of the error function.
    - perc_err     - Tuple of the percentage errors for the low, high, and combined fits.
    - fit_catch    - String indicating which fit to catch (low, high, or NONE).
    Returns :
    - arg_dict     - Dictionary of fit arguments - includes low fit, high fit, and combined fit arguments.
    """
    low_func = f"{fit_types[0]}"
    hi_func = f"{fit_types[1]}"

    low_param = np.array(low_fit)
    low_param = list(low_param[::-1]) ################################### 2024053

    hi_param = np.array(hi_fit)
    hi_param = list(hi_param[::-1]) ################################### 20240531

    if fit_catch == "low":
        all_params = low_param # np.append(erf_loc, [low_param]) ################################### 20240605
    elif fit_catch == "high":
        all_params = hi_param # np.append(erf_loc, [hi_param])################################### 20240612
    else:
        all_params = np.append(low_param, hi_param) # np.append(erf_loc, np.append(low_param, hi_param))################################### 20240612
    #########
    # print(low_fit, low_fit_xs, hi_fit, hi_fit_xs, fit_orders, fit_types, erf_loc, perc_err)
    arg_dict = {}

    if len(low_fit) != 0:
        arg_dict["low_fit_range"] = np.array([min(low_fit_xs), max(low_fit_xs)]).tolist()
    else:
        arg_dict["low_fit_range"] = []
    if len(hi_fit) != 0:
        arg_dict["hi_fit_range"] = np.array([10**min(hi_fit_xs), 10**max(hi_fit_xs)]).tolist()
    else:
        arg_dict["hi_fit_range"] = []

    arg_dict["low_function_type"] = low_func
    arg_dict["low_fit_param"] = low_param
    arg_dict["hi_function_type"] = hi_func
    arg_dict["hi_fit_param"] = hi_param
    arg_dict["combined_function_type"] = "comppoly"
    arg_dict["combined_fit_param"] = all_params
    if len(low_fit) != 0 and len(hi_fit) != 0:
        arg_dict["combined_fit_range"] = np.array([min(low_fit_xs), 10**max(hi_fit_xs)]).tolist()
    elif len(low_fit) != 0:
        arg_dict["combined_fit_range"] = np.array([min(low_fit_xs), max(low_fit_xs)]).tolist()
    elif len(hi_fit) != 0:
        arg_dict["combined_fit_range"] = np.array([10**min(hi_fit_xs), 10**max(hi_fit_xs)]).tolist()
    else:
        arg_dict["combined_fit_range"] = []    
    arg_dict["erfloc"] = erf_loc

    # arg_dict = {"low_function_type"  : low_func,
    #             "low_fit_param"      : low_param.tolist(),
    #             "low_fit_range"      : np.array([min(low_fit_xs), max(low_fit_xs)]).tolist(),
    #             "hi_function_type"   : hi_func,
    #             "hi_fit_param"       : hi_param.tolist(),
    #             "hi_fit_range"       : np.array([10**min(hi_fit_xs), 10**max(hi_fit_xs)]).tolist(),
    #             "combined_function_type" : "comppoly",
    #             "combined_fit_param" : all_params, #.tolist(),
    #             "combined_fit_range" : np.array([max(min(min(low_fit_xs), 10**min(hi_fit_xs)), float(0.001)), max(max(low_fit_xs), 10**max(hi_fit_xs))]).tolist(),
    #             "erfloc": erf_loc ################## 20240605
    #             }
    return arg_dict

# def dict_monofit(fit_param, fit_range, fit_type, perc_err="??"):
#     """
#     Description : Makes a dictionary of fit parameters for a single non-compound fit with the appropriate formating and headings to be saved in other file formats.
#     Arguments :
#     - fit_param   - Array of the fit parameters.
#     - fit_range   - Array of the fit range.
#     - fit_type    - String indicating the type of fit.
#     - perc_err    - Percentage error of the fit.
#     Returns :
#     - arg_dict    - Dictionary of fit arguments - includes low fit, high fit, and combined fit arguments.
#     """
#     fit_param = fit_param[::-1] ################################### 20240531
#     arg_dict = {"combined_function_type" : fit_type,
#                 "combined_fit_param" : fit_param.tolist(),
#                 "combined_fit_range" : np.array(fit_range).tolist(),
#                 "combined_perc_err": perc_err}
#     return arg_dict

# def format_monofit(fit_args):
#     """
#     Description : properly formats the fit arguments for a single non-compound fit with the appropriate formating and headings to be saved in other file formats.
#     """
#     num_fit_param_combined = len(fit_args["combined_fit_param"])

#     result = list(generate_alphabet_array(num_fit_param_combined, "l"))
    
#     output_array = []
#     keys = ["Fit Type", "Low Temp", "High Temp", "Perc Err"] + result

#     for i in ["combined"]:
#         dict_vals = []
#         dict_vals = np.append(dict_vals, np.array(fit_args[f"{i}_function_type"], dtype=str).flatten())
#         dict_vals = np.append(dict_vals, np.char.mod('%0.' + str(3) + 'f', np.array(fit_args[f"{i}_fit_range"], dtype=float)).flatten())
#         dict_vals = np.append(dict_vals, fit_args[f"{i}_perc_err"])

#         param_str_arr  = np.char.mod('%0.' + str(5) + 'e', np.array(fit_args[f"{i}_fit_param"], dtype=float)).flatten()

#         while len(param_str_arr) < len(result):
#             param_str_arr = np.append(param_str_arr, np.char.mod('%0.' + str(5) + 'e',[0]))
    
#         dict_vals = np.append(dict_vals, param_str_arr)
    
#         mat_dict = dict(zip(keys, dict_vals))
#         output_array.append(mat_dict)
    
#     return output_array

def find_closest(arr, val): 
    """
    Description : Finds the closest Temperature value in an array to a given value and returns the difference and index.
    Arguments :
    - arr - Array of values to search.
    - val - Value to find the closest match to.
    Returns :
    - stored_T - The closest value in the array to the given value.
    - stored_index - The index of the closest value in the array.
    """
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
    """
    Description : Splits the data into low and high temperature ranges based on the erf_loc value.
    Arguments :
    - big_data - Array of measurement data concatenated (should be of shape: [N, 4]).
    - erf_loc  - Temperature at which to split the data for fitting (and to place the error function).
    Returns :
    - lowT, lowT_k, lowT_koT, low_ws, hiT, hiT_k, hiT_koT, hi_ws - Arrays of the low and high temperature ranges and their corresponding k/T values and weights.
    """
    
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


def compile_csv(path_to_fits, mat_name = None):
    """
    Description : Compiles the fit data of every material and outputs to a single array.
    """
    output_array = []
    for mat in path_to_fits.keys():
        file = path_to_fits[mat]
        # if mat_name != None:
        #     if mat_name == "parent":
        #         file_path = f"{file}{os.sep}{os.path.split(os.path.split(file)[0])[1]}.csv"
        #     else:
        #         file_path = f"{file}{os.sep}{mat_name}.csv"
        # else:
        #     file_path = f"{file}{os.sep}{mat}.csv"
        # if not os.path.exists(file_path):
        #     for i in ["lo", "hi"]:
        #         if mat_name != None:
        #             if mat_name == "parent":
        #                 file_path = f"{file}{os.sep}{os.path.split(os.path.split(file)[0])[1]}_{i}.csv"
        #             else:
        #                 file_path = f"{file}{os.sep}{mat_name}_{i}.csv"
        #         else:
        #             file_path = f"{file}{os.sep}{mat}_{i}.csv"
        #         material_file = np.loadtxt(file_path, dtype=str, delimiter=',')
        #         headers = material_file[0]
        #         headers = np.append([f"Material Name"], headers)
        #         comb_fit = material_file[-1]
        #         comb_fit = np.append([f"{mat}_{i}"], comb_fit)
        #         mat_dict = dict(zip(headers, comb_fit))
        #         output_array.append(mat_dict)

        
        # else:
        
        for csv_file in os.listdir(file):
            if csv_file.endswith(".csv"):
                file_path = os.path.join(file, csv_file)
                material_file = np.loadtxt(file_path, dtype=str, delimiter=',')
                headers = material_file[0]
                headers = np.append(["Material Name"], headers)
                comb_fit = material_file[-1]
                comb_fit = np.append([f"{mat}"], comb_fit)
                mat_dict = dict(zip(headers, comb_fit))
                output_array.append(mat_dict)
            
            else:
                continue

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
            low_fit = []
            low_fit_xs = []

        # Fit the high data
        
        if fit_types[1] == "polylog" and (len(hiT)!=0):
            hi_fit_xs, hi_fit = logk_function(log_hi_T, log_hi_k, fit_orders[1], hi_ws)
        elif (len(hiT)==0):
            hi_fit = []
            hi_fit_xs = []

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




def get_all_fits(mat_direct, subset=None):
    """
    Gets all the paths to the fit files in the given directory.

    Arguments:
    - mat_direct: str, the path to the material folder.

    Returns:
    - path_to_fit_dict: dict, a dictionary containing the paths to the fit files.

    """
    path_to_fit_dict = dict()

    fit_str = f"{mat_direct}{os.sep}fits"
    other_str = f"{mat_direct}{os.sep}OTHERFITS"
    nist_str = f"{mat_direct}{os.sep}NIST"
    raw_str = f"{mat_direct}{os.sep}RAW"
    
    mat = os.path.split(mat_direct)[-1] # Get the material name from the directory path

    if os.path.exists(fit_str): # Prioritize RAW fits
        path_to_fit_dict["raw_fit"] = fit_str
    if os.path.exists(other_str): # Then other fits
        path_to_fit_dict["other_fit"] = other_str
    if os.path.exists(nist_str): # Lastly NIST Fits
        path_to_fit_dict["NIST_fit"] = nist_str
    
    return path_to_fit_dict


########################################################################################
########################################################################################
from scipy.interpolate import interp1d


def interpolate(folder_path, preferred_fit = None):

    # Let's search to see if the material has room temperature data so we can include that in our interpolation
    room_temperature_data = False
    config_path = f"{folder_path}{os.sep}room_temperature.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        room_temperature_data = True
        room_temp = float(config['room_temperature_conductivity'][0])
        room_k = float(config['room_temperature_conductivity'][1])

    # Loading all fit data for the material in question
    fits = np.loadtxt(f"{folder_path}{os.sep}all_fits.csv", dtype = str, delimiter = ',')
    num_fits = len(fits) - 1

    # This creates a list of each fit's low and high temperature bounds
    low_temps = fits[1:, 2]
    low_temps = [float(i) for i in low_temps]
    high_temps = fits[1:, 3]
    high_temps = [float(i) for i in high_temps]

    # We want to sort our fits to go in numerical order by low temperature range 
    # This will make it easy to choose when to switch fits during interpolation
    sorting_indices = np.argsort(low_temps)
    low_temps = np.array(low_temps)[sorting_indices]
    high_temps = np.array(high_temps)[sorting_indices]
    sorting_indices = np.append(0, sorting_indices + 1)
    sorted_fits = fits[sorting_indices, :]
    fit_names = sorted_fits[1:, 0]

    Ts = np.empty(0, float)
    ks = np.empty(0, float)

    # If we have a fit we prefer the interpolation to use, it will create the points here and block other fits from overriding them later
    if preferred_fit != None:
        preferred_fit = str(preferred_fit)
        parameters = get_parameters(sorted_fits, preferred_fit)
        func_type = get_func_type(parameters['fit_type'])
        preferred_fit_range = parameters['fit_range']
        T = np.logspace(np.log10(preferred_fit_range[0]), np.log10(preferred_fit_range[1]), 1000)
        k = func_type(T, parameters)
        Ts = np.append(Ts, T)
        ks = np.append(ks, k)

    # Here, we go through every fit for the chosen material and decide what parts of each fit to use
    for i in range(num_fits):
        # We don't want to use a fit whose temperature range is contained inside the last fit we used
        if i != 0 and high_temps[i] <= high_temps[i - 1]:
            continue
        # We want to reduce the list of fits just to the one in question because tc tools can get confused if two fits are both named "raw_fit" for example
        current_fit = sorted_fits[[0, i + 1], :]
        parameters = get_parameters(current_fit, fit_names[i])
        func_type = get_func_type(parameters['fit_type'])
        fit_range = parameters['fit_range']
        # If two fits intersect at the temperature ranges, we want it to switch from one to the other so it does not oscillate between the two
        if i != 0 and low_temps[i] < high_temps[i - 1]:
            fit_range[0] = high_temps[i - 1]
        T = np.logspace(np.log10(fit_range[0]), np.log10(fit_range[1]), 1000)
        # Here we remove any points that intersect with our preferred fit
        if preferred_fit != None:
            indices = np.where((T < preferred_fit_range[0]) | (T > preferred_fit_range[1]))
            T = T[indices]
        # Here we generate our conductivity points to feed to the interpolation
        # Some fits don't function the same as others and are not currently supported
        try:
            k = func_type(T, parameters)
        except:
            print(f"{func_type} not supported.")
            k = [0 for i in T]

        Ts = np.append(Ts, T)
        ks = np.append(ks, k)

    if room_temperature_data:
        Ts = np.append(Ts, room_temp)
        ks = np.append(ks, room_k)
        
    return interp1d(Ts, ks)

def update_interpolation(folder_path, preferred_fit = None):
    material = os.path.split(folder_path)[-1]
    # Creating the interpolation
    interpolation = interpolate(folder_path, preferred_fit)

    # Creating a pickle file with the interpolation function for the material in question
    with open(f'{folder_path}{os.sep}interpolation.pkl', 'wb') as file:
        pkl.dump(interpolation, file)

    # Creating plots for to view the interpolation curve
    plot_interpolation(folder_path, interpolation)
    plt.savefig(f"{folder_path}{os.sep}plots{os.sep}{material}_interpolation.png", dpi=300) 
    plt.savefig(f"{folder_path}{os.sep}plots{os.sep}{material}_interpolation.pdf", dpi=300) 