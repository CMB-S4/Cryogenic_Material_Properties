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

everything_bagel = dict()
simple_bagel = dict()
path_to_otherfits = dict()
path_to_rawData = dict()

def make_pathtofit(mat_direct, subset=None, fits_to_parse="ALL"):
    path_to_fit_dict = dict()
    if subset!=None:
        subset_array = []
        for mat in mat_direct:
            if mat in subset:
                subset_array = np.append(subset_array, mat)
        mat_direct = subset_array
    for mat in mat_direct:
        mat_str = f"{path_to_lib}\\{mat}"
        fit_str = f"{mat_str}\\fits"
        other_str = f"{mat_str}\\OTHERFITS"
        nist_str = f"{mat_str}\\NIST"
        raw_str = f"{mat_str}\\RAW"
        
        if fits_to_parse=="ALL":
            if os.path.exists(fit_str): # Prioritize RAW fits
                path_to_fit_dict[mat] = fit_str
                path_to_rawData[mat] = fit_str
            elif os.path.exists(other_str): # Then other fits
                path_to_fit_dict[mat] = other_str
            elif os.path.exists(nist_str): # Lastly NIST Fits
                path_to_fit_dict[mat] = nist_str

        if fits_to_parse=="OTHER":
            if os.path.exists(other_str): # Then other fits
                path_to_fit_dict[mat] = other_str
            elif os.path.exists(nist_str): # Lastly NIST Fits
                path_to_fit_dict[mat] = nist_str

        if fits_to_parse=="RAW":
            if os.path.exists(raw_str): # Prioritize RAW fits
                path_to_fit_dict[mat] = fit_str
    
    return path_to_fit_dict

current_date = datetime.now().date()

# Want to create 4 output files
# 1. Plain Bagel : Simple file that has only 1 fit per material and ignores weird materials
simple_mat_direct = ["Aluminum_1100", "Beryllium_Copper","Brass","CFRP","Constantan","Cu_OFHC_RRR50",
                     "G10_FR4","Glass_FabricPolyester_He_warp","Graphite","Inconel_718","Invar_Fe36Ni",
                     "Iron","Kapton","Ketron","Kevlar49_Composite_Aramid","Lead","Macor","Manganin",
                     "Molybdenum","MylarPET","NbTi","Nichrome","Nickel_Steel_Fe_2.25_Ni","Nylon",
                     "Phosbronze","Platinum","Polystyrene_2.0_lbft3","Polyurethane_2.0_lbft3_CO2",
                     "PVC_1.25_lbft3_air","Stainless_Steel","Teflon","Ti6Al4V","Titanium_15333",
                     "Torlon","Tungsten","VESPEL"]
simple_bagel = make_pathtofit(mat_directories, subset=simple_mat_direct)
output_array = compile_csv(simple_bagel)
create_data_table(output_array, f"..\\tc_generic_{current_date}.txt")
create_tc_csv(output_array, f"..\\tc_generic_{current_date}.csv")


# 2. Everything Bagel : File that contains every single material and alloy
everything_bagel = make_pathtofit(mat_directories, fits_to_parse="ALL")
output_array = compile_csv(everything_bagel)
create_data_table(output_array, f"..\\tc_fullrepo_{current_date}.txt")
create_tc_csv(output_array, f"..\\tc_fullrepo_{current_date}.csv")

# 3. Other fits + NIST
other_fits = make_pathtofit(mat_directories, fits_to_parse="OTHER")
output_array = compile_csv(other_fits)
create_data_table(output_array, f"..\\tc_other_fits_{current_date}.txt")
create_tc_csv(output_array, f"..\\tc_other_fits_{current_date}.csv")

# 4. RAW / from data fits
raw_fits = make_pathtofit(mat_directories, fits_to_parse="RAW")
output_array = compile_csv(raw_fits)
create_data_table(output_array, f"..\\tc_rawdata_fits_{current_date}.txt")
create_tc_csv(output_array, f"..\\tc_rawdata_fits_{current_date}.csv")
