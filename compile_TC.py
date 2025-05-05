## Author: Henry Nachman
## Description: This file searches the subfolder library of materials for thermal conductivity fits
## which it then compiles and outputs - creating easy to use, human-readable, files
## containing the thermal conductivity fits for the entire library.

import os, sys
from datetime import datetime

abspath = os.path.abspath(__file__)
file_path = os.path.dirname(abspath)
sys.path.insert(0, f"{file_path}")

from thermal_conductivity.fit_types import *
from thermal_conductivity.tc_utils import *

def main():

    path_to_lib = f"{file_path}{os.sep}thermal_conductivity{os.sep}lib"
    mat_directories = [folder for folder in os.listdir(path_to_lib) if not folder.endswith(".md")]

    everything_bagel = dict()
    simple_bagel = dict()
    path_to_otherfits = dict()
    path_to_rawData = dict()

    # # This code block deletes the old files
    try:
        all_files = os.listdir(f"{file_path}")
        exist_files = [file for file in all_files if file.startswith("tc_fullrepo")]
        old_date = exist_files[0][-12:-4]
        old_csvs = [file for file in all_files if file.endswith(f"{old_date}.csv")]
        old_txts = [file for file in all_files if file.endswith(f"{old_date}.txt")]

        old_files = np.hstack((old_csvs, old_txts))
        # print(old_files)
        for file in old_files:
            os.remove(f"{file_path}{os.sep}{file}")
        print(f"Removing files from date: {old_date}")
        os.chdir(f"{os.getcwd()}{os.sep}thermal_conductivity")
    except IndexError:
        pass

    # This code block finds all the files with data.

    current_date = datetime.now().date()
    print(f"Replacing with files from date: {current_date}")
    current_date = current_date.strftime('%Y%m%d')

    # Want to create 4 output files
    # 1. Plain Bagel : Simple file that has only 1 fit per material and ignores weird materials
    simple_mat_direct = ["Aluminum_1100", "Beryllium_Copper","CFRP","Cu_OFHC_RRR50",
                        "G10_FR4","Glass_FabricPolyester_He_warp","Graphite","Inconel_718","Invar_Fe36Ni",
                        "Iron","Kapton","Ketron","Kevlar49_Composite_Aramid","Lead","Macor","Manganin",
                        "Molybdenum","MylarPET","NbTi","Nichrome","Nickel_Steel_Fe_2.25_Ni","Nylon",
                        "Phosbronze","Platinum","Polystyrene_2.0_lbft3","Polyurethane_2.0_lbft3_CO2",
                        "PVC_1.25_lbft3_air","Stainless_Steel","Teflon","Ti6Al4V","Titanium_15333",
                        "Torlon","Tungsten","VESPEL"]
    simple_bagel = make_pathtofit(mat_directories, subset=simple_mat_direct)
    output_array = compile_csv(simple_bagel)
    bad_fit_mats = ["Brass", "Constantan","Cu_OFHC","Stainless_Steel_310","Stainless_Steel_316"]
    bad_simple_bagel = make_pathtofit(mat_directories, subset=bad_fit_mats)
    bad_fit_output_array = compile_csv(bad_simple_bagel)

    # Add a flag for bad materials
    filler_arr = {}
    filler_arr2 = {}
    for key in output_array[-2]:
        filler_arr[key] = "--"
        filler_arr2[key] = "--"
    filler_arr2["Material Name"] = "Flagged Materials Below :"
    output_array = np.append(output_array, [filler_arr])
    output_array = np.append(output_array, [filler_arr2])
    output_array = np.append(output_array, [filler_arr])
    output_array = np.append(output_array, bad_fit_output_array)
    
    #
    # create_data_table(output_array, f"{file_path}{os.sep}tc_generic_{current_date}.txt")
    create_tc_csv(output_array, f"{file_path}{os.sep}tc_simplified_{current_date}.csv")


    # 2. Everything Bagel : File that contains every single material and alloy
    everything_bagel = make_pathtofit(mat_directories, fits_to_parse="ALL")
    output_array = compile_csv(everything_bagel)
    # create_data_table(output_array, f"{file_path}{os.sep}tc_fullrepo_{current_date}.txt")
    create_tc_csv(output_array, f"{file_path}{os.sep}tc_fullrepo_{current_date}.csv")

    """
    # 3. Other fits + NIST
    other_fits = make_pathtofit(mat_directories, fits_to_parse="OTHER")
    output_array = compile_csv(other_fits)
    create_data_table(output_array, f"{file_path}{os.sep}tc_other_fits_{current_date}.txt")
    create_tc_csv(output_array, f"{file_path}{os.sep}tc_other_fits_{current_date}.csv")

    # 4. RAW / from data fits
    raw_fits = make_pathtofit(mat_directories, fits_to_parse="RAW")
    output_array = compile_csv(raw_fits)
    create_data_table(output_array, f"{file_path}{os.sep}tc_rawdata_fits_{current_date}.txt")
    create_tc_csv(output_array, f"{file_path}{os.sep}tc_rawdata_fits_{current_date}.csv")
    """

if __name__ == "__main__":
    main()