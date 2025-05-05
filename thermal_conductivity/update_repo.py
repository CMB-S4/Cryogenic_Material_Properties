## Make plots for all materials
### Author: Henry Nachman
#### Last Updated: 2024-06-13


import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, os

from tc_tools  import *
from tc_utils import get_all_fits, compile_csv, create_tc_csv
from tc_plots import plot_all_fits, plot_OFHC_RRR

def main():
    # Define important paths
    home_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = home_dir+f'{os.sep}lib'
    
    
    for folder_name in os.listdir(lib_dir): # loop through each material folder in lib/
        
        folder_path = os.path.join(lib_dir, folder_name)
        if os.path.isdir(folder_path): # If it is a directory, we will process the fits in it
            # First lets make a compilation file of each fit available for a material
            paths = get_all_fits(folder_path) # paths to each fit file in the directory
            csv = compile_csv(paths, folder_name) # format the csv
            create_tc_csv(csv, f"{folder_path}{os.sep}all_fits.csv") # save the compilation file

            # Now import the data from that all_fits file
            TCdata = np.loadtxt(f"{folder_path}{os.sep}all_fits.csv", dtype=str, delimiter=',') #

            # This makes the plot with all the fits available - with a special case for OFHC RRR
            if folder_name == "OFHC_RRR":
                plot_OFHC_RRR(TCdata, folder_name, folder_path) # Special case for OFHC RRR to use a different plotting function
            else:
                plot_all_fits(TCdata, folder_name, folder_path)

        # now we need to check and update the parent files

    # big_data, data_dict = parse_raw(mat, path_to_RAW[mat], plots=True, weight_const=0.00)
    # tk_plot(mat,path_to_RAW, data_dict, fit_args, fit_range = [100e-3, np.sort(T)[-1]], points=True, fits="combined", fill=True)

if __name__ == "__main__":
    main()