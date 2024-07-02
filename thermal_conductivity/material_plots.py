## Make plots for all materials
### Author: Henry Nachman
#### Last Updated: 2024-06-13


import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import erf
from scipy.integrate import quad
import sys, os
from fit_types import *
from tc_tools  import *

def main():
    # Get the absolute path of the current script
    abspath = os.path.abspath(__file__)
    print(os.path.split(abspath))
    path_to_tcFiles = f"{os.path.split(abspath)[0]}{os.sep}.."




    all_files = os.listdir(path_to_tcFiles)
    exist_files = [file for file in all_files if file.startswith("tc_fullrepo")]
    print(exist_files)
    tc_file_date = exist_files[0][-12:-4]

    TCdata = np.loadtxt(f"{path_to_tcFiles}{os.sep}tc_fullrepo_{tc_file_date}.csv", dtype=str, delimiter=',') # imports compilation file csv
    mat_names = TCdata[:,0]


    for mat in mat_names[1:]: # ["Graphite"]: # 
        param_dictionary = get_parameters(TCdata, mat)
        T = np.logspace(np.log10(param_dictionary["fit_range"][0]),np.log10(param_dictionary["fit_range"][1]),100)
        print(f"Plotting {mat} using fit type: {param_dictionary['fit_type']}")

        func = get_func_type(param_dictionary["fit_type"])
        y_pred = func(T, param_dictionary)

        plt.plot(T, y_pred, label=f'{mat} fit')
        plt.semilogx()
        plt.semilogy()
        plt.ylabel("k [W/m/K]")
        plt.xlabel("T [K]")
        plt.legend()
        plt.grid(True)
        plt.title(f"{mat} Thermal Conductivity Fit\nFit Type: {param_dictionary['fit_type']}")
        plots_dir = f"{os.path.split(abspath)[0]}{os.sep}lib{os.sep}{mat}{os.sep}plots{os.sep}"
        try:
            if not os.path.exists(plots_dir):
                print(f"making path {plots_dir}")
                os.mkdir(plots_dir)
            plt.savefig(f"{plots_dir}{mat}_fitPlot.pdf", dpi=300)
        except FileNotFoundError:
            pass
        plt.clf()
if __name__ == "__main__":
    main()