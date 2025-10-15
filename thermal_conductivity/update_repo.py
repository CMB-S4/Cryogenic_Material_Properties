"""
Author : Henry Nachman
This file cycles through every folder in the lib directory and updates the material pickle files.
If a material has a parent, it also copies any raw data files to the parent folder.
Then updates the parent accordingly.

This script fits data if it hasn't been fit yet, or if force_update=True is passed to the Material class.
This is useful if new data has been added to a material or if the fit function has changed.

This script also creates a plethora of plots, and compilation files for each material.
"""
import os
import shutil
import pickle
from material_class import Material
import numpy as np
import matplotlib.pyplot as plt
import argparse
from datetime import datetime as dt

from tc_utils import mat_to_csv, fits_to_df
from fit_types import Nppoly
from tqdm import tqdm

this_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_dir)

def main(mat_list = None, force_update=False):
    lib_folder = os.path.join(this_dir, "lib")
    # If no material list is provided, update all materials in the lib folder
    if mat_list is None:
        mat_list = [d for d in os.listdir(lib_folder) if os.path.isdir(os.path.join(lib_folder, d))]
    
    parent_list = []
    # First pass: update all materials and copy raw data to parents
    for material in tqdm(mat_list, 
                         unit="mat", 
                         unit_scale=True, 
                         desc="Updating materials", 
                         leave=True, 
                         colour='blue',
                         ascii=" >"):
        try:
            # print(f"\nUpdating material: {material}")
            mat = Material(material, force_update=force_update)
            if mat.parent is not None and mat.parent not in parent_list:
                parent_list.append(mat.parent)
                mat_list.append(mat.parent)  # Ensure parent materials are also updated

            if len(mat.fits) != 0:
                # Plot the data
                mat.plot_data()
                plt.savefig(os.path.join(mat.plot_folder, f"{mat.name}_data.png"))
                plt.close()

                # Plot the fits
                mat.plot_data_fit()
                # x_plot = np.logspace(np.log10(mat.temp_range[0]), np.log10(mat.temp_range[1]), 100)
                # y_plot_low = Nppoly(x_plot, *mat.fits[0].parameters[:(np.size(mat.fits[0].parameters)-1)//2])
                # plt.plot(x_plot, y_plot_low, label="Low T Fit", color="orange")
                plt.savefig(os.path.join(mat.plot_folder, f"{mat.name}_fits.png"))
                plt.close()

                # Plot the interpolation
                mat.plot_interpolation()
                plt.savefig(os.path.join(mat.plot_folder, f"{mat.name}_interpolation.png"))
                plt.close()

                # Plot all fits
                mat.plot_all_fits()
                plt.savefig(os.path.join(mat.plot_folder, f"{mat.name}_all_fits.png"))
                plt.close()

                # Create the csv file of fits
                mat_to_csv(mat)
        except Exception as e:
            print(f"Error updating material {material}: {e}")
            continue                
        with open(os.path.join(mat.folder, "material.pkl"), "wb") as f:
            pickle.dump(mat, f)

    mat_list = [d for d in os.listdir(lib_folder) if os.path.isdir(os.path.join(lib_folder, d))]
    # Lastly, we want to make the overall compilation files
    curated_mat_list = ["Aluminum_1100", "Beryllium_Copper","CFRP","Cu_OFHC_RRR50",
                "G10_FR4","Glass_FabricPolyester_He_warp","Graphite","Inconel_718","Invar_Fe36Ni",
                "Iron","Kapton","Ketron","Kevlar49_Composite_Aramid","Lead","Macor","Manganin",
                "Molybdenum","MylarPET","NbTi","Nichrome","Nickel_Steel_Fe_2.25_Ni","Nylon",
                "Phosbronze","Platinum","Polystyrene_2.0_lbft3","Polyurethane_2.0_lbft3_CO2",
                "PVC_1.25_lbft3_air","Stainless_Steel","Teflon","Ti6Al4V","Titanium_15333",
                "Torlon","Tungsten","VESPEL"]
    # The chosen fit for a given material will be the fit with the largest temperature range
    compilation_fits = []
    curated_comp_fits = []
    for material in mat_list:
        # Load the material from the pickle file
        with open(os.path.join(lib_folder, material, "material.pkl"), "rb") as f:
            mat = pickle.load(f)
        if len(mat.fits) == 0:
            print(f"Material {material} has no fits, skipping compilation file creation.")
            continue
        # Find the fit with the largest temperature range
        best_fit = max(mat.fits, key=lambda fit: fit.range[1] - fit.range[0])
        compilation_fits.append(best_fit)
        if material in curated_mat_list:
            curated_comp_fits.append(best_fit)
    # Save the compilation fits to a csv
    # remove old compilation files
    all_files = os.listdir(os.path.dirname(this_dir))
    exist_files = [file for file in all_files if file.startswith("tc_compilation")]
    for file in exist_files:
        os.remove(os.path.join(os.path.dirname(this_dir), file))
    general_comp_file = os.path.join(os.path.dirname(this_dir), f"tc_compilation_allfits_{dt.now().strftime('%Y%m%d')}.csv") 
    fits_to_df(compilation_fits).to_csv(general_comp_file, index=False)

    # Let's also make a more curated compilation file
    curated_comp_file = os.path.join(os.path.dirname(this_dir), f"tc_compilation_curated_{dt.now().strftime('%Y%m%d')}.csv")
    fits_to_df(curated_comp_fits).to_csv(curated_comp_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update material library.")
    parser.add_argument("--matlist", nargs='*', help="List of materials to update. If not provided, all materials will be updated.")
    parser.add_argument("--force_update", action='store_true', help="Force update of all materials, even if pickle files exist.")
    args = parser.parse_args()
    main(mat_list=args.matlist, force_update=args.force_update)