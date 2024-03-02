from thermal_conductivity.tc_utils import *
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
path_to_lib = f"{os.getcwd()}\\thermal_conductivity\\lib"
mat_directories = [folder for folder in os.listdir(path_to_lib) if not folder.endswith(".md")]

path_to_RAW = dict()
for mat in mat_directories:
    raw_str = f"{path_to_lib}\\{mat}\\RAW"
    path_to_RAW[mat] = raw_str


print(path_to_RAW)

output_array = compile_csv(path_to_RAW)
create_data_table(output_array, "thermal_conductivity_compilation.txt")
create_tc_csv(output_array, "thermal_conductivity_compilation.csv")