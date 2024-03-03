## Author: Henry Nachman
## Description: This file searches the subfolder library of materials for thermal conductivity fits
## which it then compiles and outputs - creating easy to use, human-readable, files
## containing the thermal conductivity fits for the entire library.

import os, sys

os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}\\thermal_conductivity")

# import sys
# sys.path.append(os.getcwd())


from thermal_conductivity.fit_types import *
from thermal_conductivity.tc_utils import *

path_to_lib = f"{os.getcwd()}\\lib"
mat_directories = [folder for folder in os.listdir(path_to_lib) if not folder.endswith(".md")]

path_to_fits = dict()
for mat in mat_directories:
    raw_str = f"{path_to_lib}\\{mat}\\RAW"
    path_to_fits[mat] = raw_str


output_array = compile_csv(path_to_fits)
create_data_table(output_array, "..\\thermal_conductivity_compilation.txt")
create_tc_csv(output_array, "..\\thermal_conductivity_compilation.csv")