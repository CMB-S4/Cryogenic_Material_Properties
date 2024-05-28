## Author: Henry Nachman
## Description: This file searches the subfolder library of materials for thermal conductivity fits
## which it then compiles and outputs - creating easy to use, human-readable, files
## containing the thermal conductivity fits for the entire library.

import os, sys
from datetime import datetime
os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}\\thermal_conductivity")

from thermal_conductivity.fit_types import *
from thermal_conductivity.tc_utils import *

path_to_lib = f"{os.getcwd()}\\lib"
mat_directories = [folder for folder in os.listdir(path_to_lib) if not folder.endswith(".md")]

path_to_fits = dict()
path_to_nistfits = dict()
path_to_otherfits = dict()
path_to_rawData = dict()

for mat in mat_directories:
    mat_str = f"{path_to_lib}\\{mat}"
    fit_str = f"{mat_str}\\fits"
    other_str = f"{mat_str}\\OTHERFITS"
    nist_str = f"{mat_str}\\NIST"
    raw_str = f"{mat_str}\\RAW"
    if os.path.exists(fit_str):
        path_to_fits[mat] = fit_str
        path_to_rawData[mat] = fit_str
    elif os.path.exists(other_str):
        path_to_fits[mat] = other_str
    elif os.path.exists(nist_str):
        path_to_fits[mat] = nist_str

    if os.path.exists(nist_str):
        path_to_nistfits[mat] = nist_str
    if os.path.exists(other_str):
        path_to_otherfits[mat] = other_str

output_array = compile_csv(path_to_fits)

current_date = datetime.now().date()

create_data_table(output_array, f"..\\thermal_conductivity_compilation_{current_date}.txt")
create_tc_csv(output_array, f"..\\thermal_conductivity_compilation_{current_date}.csv")

output_array = compile_csv(path_to_nistfits)
create_data_table(output_array, f"..\\thermal_conductivity_compilation_NIST_{current_date}.txt")
create_tc_csv(output_array, f"..\\thermal_conductivity_compilation_NIST_{current_date}.csv")

output_array = compile_csv(path_to_otherfits)
create_data_table(output_array, f"..\\other_fits_{current_date}.txt")
create_tc_csv(output_array, f"..\\other_fits_{current_date}.csv")

output_array = compile_csv(path_to_rawData)
create_data_table(output_array, f"..\\rawData_Fits_{current_date}.txt")
create_tc_csv(output_array, f"..\\rawData_Fits_{current_date}.csv")
