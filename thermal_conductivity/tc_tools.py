## Functions for using the thermal conductivity repository
## Author: Henry Nachman
## Date Created: 21 June 2024
## Last Updated: 28 June 2024

import numpy as np
import os, sys

abspath = os.path.abspath(__file__)
sys.path.insert(0, os.path.dirname(abspath))


from itertools import dropwhile
from fit_types import get_func_type

path_to_tcFiles = f"{os.path.split(abspath)[0]}{os.sep}..{os.sep}"
all_files = os.listdir(path_to_tcFiles)
exist_files = [file for file in all_files if file.startswith("tc_fullrepo")]
tc_file_date = exist_files[0][-12:-4]

TCdata = np.loadtxt(f"{path_to_tcFiles}{os.sep}tc_fullrepo_{tc_file_date}.csv", dtype=str, delimiter=',') # imports compilation file csv


def get_parameters(TCdata, mat="", index=None):
    """
    Function: extracts the fit parameters for the specified material

    Arguments: 
    - TCdata: (array) the array of the imported compilation file
    - mat: (string) the material of interest

    Returns: Dictionary of specified material fit parameters.
    """
    headers = TCdata[0] # pulls the headers from the file
    
    if index is not None:
        mat_row = TCdata[index]
    else:
        mat_names = TCdata[:,0] # makes an array of material names
        mat_row = TCdata[int(np.argwhere(mat_names == mat)[0][0])] # searches material name array for mat specified above and return relevant row
      
    param_headers = headers[5:]
    fit_type = mat_row[1]
    num_hi = sum(1 for c in param_headers if c.isupper()) # searches for the number of low parameters (by lower case letter)
    num_low = sum(1 for c in param_headers if c.islower()) # searches for number of high parameters
    fit_params = mat_row 
    fit_params = np.char.replace(fit_params, "^", "0")
    # fit_range, low_param, hi_param, erf_param = np.array(mat_row[2:4], dtype=float), np.array(fit_params[:num_low], dtype=float), np.array(fit_params[num_low:-1], dtype=float), float(fit_params[-1])

    fit_range = np.array(mat_row[2:4], dtype=float) # pulls the fit range
    # loop through headers and if lower case add to low_param vice versa
    low_param = []
    hi_param = []
    erf_param = None
    for key in headers[5:]:
        if key.islower() and key != "erf param":
            low_param.append(float(fit_params[int(np.argwhere(headers == key)[0][0])]))
        elif key.isupper():
            hi_param.append(float(fit_params[int(np.argwhere(headers == key)[0][0])]))
        elif key == "erf param":
            erf_param = float(fit_params[int(np.argwhere(headers == key)[0][0])])

    # now we have a list of lower and upper parameters but, they might have trailing 0s if they have fewer parameters than other materials
    # so now we remove those trailing 0s
    def remove_trailing_zeros(arr):
        return list(dropwhile(lambda x: x == 0, arr[::-1]))
    low_param = remove_trailing_zeros(low_param)
    hi_param = remove_trailing_zeros(hi_param)
    if fit_type not in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    # print(low_param, hi_param, erf_param)
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": fit_range,
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    return param_dictionary

def get_thermal_conductivity(T, material, verbose=True):
    """
    Function: Finds the thermal conductivity of a given material at a particular temperature.

    Arguments:
    - T: float. Temperature in Kelvin 
    - material: str. Material name string.

    Returns: k_val, thermal conductivity in W/m/K
    """
    param_dictionary = get_parameters(TCdata, material)
    if verbose:
        if T<param_dictionary["fit_range"][0] or T>param_dictionary["fit_range"][1]:
            print(f"**Requested value out of range of {material} fit - estimation success not guaranteed")
    func = get_func_type(param_dictionary["fit_type"])
    k_val = func(T, param_dictionary)
    return k_val

def get_conductivity_integral(T_low, T_high, material, extra_parameters = [], verbose=True):
    """
    Function: Finds the integrated thermal conductivity of a given material over a temperature range.

    Arguments:
    - T_low: float. lower bound temperature in Kelvin
    - T_high: float. upper bound temperature in Kelvin
    - material: str. Material name string.

    Returns: ConInt, thermal conductivity in W/m
    """
    T_values = np.linspace(T_low, T_high, 1000) # defines the temperature array over which to calculate integral
    param_dictionary = get_parameters(TCdata, material) # gets the material fit parameters
    func = get_func_type(param_dictionary["fit_type"]) # finds the material fit type
    if verbose:
        if min(T_values)<param_dictionary["fit_range"][0] or max(T_values)>param_dictionary["fit_range"][1]:
            print(f"**Requested value out of range of {material} fit - estimation success not guaranteed")
    if len(extra_parameters) != 0:
        k_values = func(T_values, extra_parameters, param_dictionary)
    else:
        k_values = func(T_values, param_dictionary) # determines the thermal conductivity at each T point

    ConInt = np.trapz(k_values, T_values) # integrates over the function
    return ConInt


def make_a_table(TCdata, materials):
    T_one = np.roud(np.arange(0.01, .1, 0.005), 3)
    T_full = []
    for i in range(4):
        T_full.extend(T_one*10**(i+1))
    T_full = np.round(T_full, 2)

    tc_datatable = T_full
    for mat in materials:
        params = get_parameters(TCdata, mat)
        func_type = get_func_type(params["fit_type"])
        # print(mat, func_type)
        y_data = []
        for n in range(len(T_full)):
            if (T_full[n] < params["fit_range"][0]) or (T_full[n] > params["fit_range"][1]):
                y_data.append(0)
            else:
                y_append = func_type(T_full[n], params)
                if (y_append > 1e6) or (y_append < 0):
                    y_data.append(0)
                else:
                    y_data.append(y_append)
        tc_datatable = np.vstack((tc_datatable, np.round(y_data,3)))
    headers = np.insert(materials, 0, ["Temperature [K]"], axis=0)
    tc_datatable = np.insert(np.array(tc_datatable, dtype=object), 0, headers, axis = 1)

    with open("data_table.csv", 'w', newline='') as savefile:
        # convert array into dataframe         
        # save the dataframe as a csv file 
        np.savetxt(savefile, np.transpose(tc_datatable), delimiter=",", fmt="%s")

    return
"""
curated_TC = np.loadtxt(f"{path_to_tcFiles}{os.sep}tc_fullrepo_{tc_file_date}.csv", dtype=str, delimiter=',') # imports compilation file csv
curated_matnames = curated_TC[1:,0]

make_a_table(curated_TC, curated_matnames)
"""