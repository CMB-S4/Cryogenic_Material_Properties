import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os, sys
import yaml

abspath = os.path.abspath(__file__)
sys.path.insert(0, os.path.dirname(abspath))


from fit_types import loglog_func, get_func_type
from tc_tools import get_parameters
cmap = cm.get_cmap('Dark2')

markers = ['o', 's', 'd', 'P','3', '*']
linestyle_tuple = ["-","--", "-.", ":"]
linewidths = [2, 3, 4, 5, 6, 7]

###############################################################
###############################################################
######################## PLOTTING #############################
###############################################################
###############################################################

def plot_datapoints(data_dict):
    """
    Plots the data points from the data_dict.
    Arguments:
    - data_dict: dictionary of data with reference information as keys
    Returns:
    - null
    """
    i = 0
    m = 1
    for ref_name in data_dict.keys():
        T, k, koT, ws = data_dict[ref_name].T
        split_name = ref_name.split("_")
        label = split_name[0] + " " + split_name[1]
        label = label.replace("EtAl", " et al.")
        plt.plot(T, k, marker=markers[i], ms=12, mfc='none', ls='none', label=label, c=cmap((i%6)/6), alpha=np.mean(ws), markeredgewidth=2)
        i+=1
        m+=1
        if i == len(markers):
            i = 0
    return

def get_plotting_data(material_name, path_dict, data_dict, fit_args, fit_range):
    """
    Description : Extracts the data needed for plotting the thermal conductivity data and fits.
    Arguments :
    - material_name - name of the material
    - path_dict     - dictionary type of paths to data
    - data_dict     - dictionary of raw data with reference information as keys
    - fit_args      - combined fit arguments
    - fit_range     - default=[100e-4,25e2] - range over which to model the fit
    Returns :
    - Tdata         - array of temperature data
    - kdata         - array of thermal conductivity data
    - low_t_range   - range of temperatures for the low fit
    - hi_t_range    - range of temperatures for the high fit
    - low_fit_k     - array of thermal conductivity data for the low fit
    - hi_fit_k      - array of thermal conductivity data for the high fit
    - full_T_range  - range of temperatures for the full fit
    - raw_directory - directory containing the raw data for the material
    """

    # Defines the directory for saving
    raw_directory = path_dict[material_name]

    # Extracts the fit parameters from the fit args object
    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["erfloc"], fit_args["combined_function_type"] ################################### 20240605
    
    # Defines a range over which to model the fit
    if len(fit_args["low_fit_range"]) == 0:
        upper_bound = fit_range[1]
    else:
        upper_bound = fit_args["low_fit_range"][1]
    if len(fit_args["hi_fit_range"]) == 0:
        lower_bound = fit_range[0]
    else:
        lower_bound = fit_args["hi_fit_range"][0]
    
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [lower_bound, upper_bound],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    
    low_t_range = np.linspace(fit_range[0],upper_bound,100)
    low_fit_k = loglog_func(low_t_range, param_dictionary)
    low_fit_koT = low_fit_k/low_t_range
    hi_t_range = np.linspace(lower_bound,fit_range[1],100)
    hi_fit_k = loglog_func(hi_t_range, param_dictionary)
    
    # extracts all the temp and tc data
    Tdata = np.concatenate([(data_dict[ref_name].T[0]) for ref_name in data_dict])
    kdata = np.concatenate([(data_dict[ref_name].T[1]) for ref_name in data_dict])

    # redefines the plot range based on data
    fit_range = [100e-4, 1.1*max(Tdata)]
    full_T_range = np.logspace(np.log10(fit_range[0]),np.log10(fit_range[1]),100)
    return Tdata, kdata, low_t_range, hi_t_range, low_fit_k, hi_fit_k, full_T_range, raw_directory


def plot_full(material_name: str, path_dict, data_dict, fit_args, fit_range=[100e-4,25e2], points=True, fits="combined", fill=False):
    """
    Description : Plots the thermal conductivity data and fits for a given material.
    Arguments :
    - material_name - name of the material
    - path_dict     - dictionary type of paths to data
    - data_dict     - dictionary of raw data with reference information as keys
    - fit_args      - combined fit arguments
    - fit_range     - default=[100e-4,25e2] - range over which to model the fit
    - points        - default=True          - Boolean argument, if true, data points are added to the plot.
    - fits          - options: 'combined', 'low', 'hi', other - defines which fits to plot.
    - fill          - default=False         - Boolean argument, if true, 15% confidence interval is shaded around plot.
    Returns :
    - null
    """

    Tdata, kdata, low_t_range, hi_t_range, low_fit_k, hi_fit_k, full_T_range, raw_directory = get_plotting_data(material_name, path_dict, data_dict, fit_args, fit_range)
    # Plots the data points
    plt.figure(figsize=(20, 17))
    if points:
        plot_datapoints(data_dict)

    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["erfloc"], fit_args["combined_function_type"] ################################### 20240605
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [min(Tdata), max(Tdata)],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531

    k_fit_combined = loglog_func(full_T_range, param_dictionary)
    if fits=="combined":
        plt.plot(full_T_range, k_fit_combined, linewidth=4, label='fit', c="black")
        if fill:
            avg_perc_diff, perc_diff_arr, *_ = get_percdiff(Tdata, kdata, fit_args)
            low_avg_perc_diff, hi_avg_perc_diff = [0,0]
            if len(Tdata[Tdata<30])>0:
                low_avg_perc_diff, low_perc_diff_arr, low_fit_sigma = get_percdiff(Tdata[Tdata<30], kdata[Tdata<30], fit_args)
            if len(Tdata[Tdata>30])>0:
                hi_avg_perc_diff, hi_perc_diff_arr, hi_fit_sigma = get_percdiff(Tdata[Tdata>30], kdata[Tdata>30], fit_args)
            plt.fill_between(full_T_range, k_fit_combined*(1+avg_perc_diff/100), (k_fit_combined*(1-avg_perc_diff/100)),
                             alpha=0.25, color="gray",
                             label=f"Perc Err : {np.char.mod('%0.' + str(2) + 'f', avg_perc_diff)}%")
                            #  label=f"{np.char.mod('%0.' + str(2) + 'f', avg_perc_diff)}, low: {np.char.mod('%0.' + str(2) + 'f', low_avg_perc_diff)}, hi: {np.char.mod('%0.' + str(2) + 'f', hi_avg_perc_diff)}%")
    # Plots the fits as they are seperately (rather then the combined fit)
    if fits=="split":
        plt.plot(low_t_range, low_fit_k, c='b')
        plt.plot(hi_t_range, hi_fit_k, c='b')        
    # plt.legend(loc='center right', bbox_to_anchor=(1.5, 0.5), fontsize=20)
    fs = 26
    plt.legend(loc='center right', bbox_to_anchor=(1.45, 0.5), fontsize=fs)    
    plt.xlabel(r"$\bar T$" + "[K]", fontsize=fs)
    plt.xticks(fontsize=fs)
    plt.yticks(fontsize=fs)
    plt.ylabel("Thermal Conductivity : k [W/m/K]", fontsize=fs)
    plt.title(f"{material_name.replace('_', ' ')}", fontsize=32)
    plt.semilogx()
    plt.semilogy()
    plt.grid('minor')
    plt.savefig(f"{os.path.split(raw_directory)[0]}{os.sep}plots{os.sep}{material_name}_fitToData_Plot.pdf", dpi=300, format="pdf", bbox_inches='tight')
    plt.grid(True, which="both", ls="-", color='0.65', alpha=0.35)
    # plt.show()
    plt.close()
    
    return

def get_percdiff(Tdata, kdata, fit_args):
    """
    Description : Calculates the percent difference between the predicted and measured thermal conductivity values.
    Arguments :
    - Tdata         - array of temperature data
    - kdata         - array of thermal conductivity data
    - fit_args      - combined fit arguments
    Returns :
    - avg_perc_diff - average percent difference between predicted and measured thermal conductivity values
    - perc_diff_arr - array of percent differences between predicted and measured thermal conductivity values
    """

    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["erfloc"], fit_args["combined_function_type"] ################################### 20240605
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [min(Tdata), max(Tdata)],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    
    # Calculates the predicted k value for the measured T values (rather than a continuous range)
    func = get_func_type(param_dictionary["fit_type"])
    try:
        kpred_discrete = func(Tdata, param_dictionary)
    except Exception as e:
        print(f"Error occurred while predicting k values: {e}")
        return None, None

    diff = kpred_discrete-kdata                 # the difference between the predicted and measured k values
    fit_std = np.sqrt(np.sum(diff*diff)/len(diff))

    perc_diff_arr = 100*diff/kpred_discrete     # Calculates a percent difference 
    avg_perc_diff = np.mean(abs(perc_diff_arr)) # finds the average of that percent difference
    return avg_perc_diff, perc_diff_arr, fit_std

def plot_splitfits(material_name: str, path_dict, data_dict, fit_args, fit_range=[100e-4,25e2], fill=True):
    """
    Description : Plots the thermal conductivity data and fits for a given material, split into low and high temperature fits.
    Arguments :
    - material_name - name of the material
    - path_dict     - dictionary type of paths to data
    - data_dict     - dictionary of raw data with reference information as keys
    - fit_args      - combined fit arguments
    - fit_range     - default=[100e-4,25e2] - range over which to model the fit
    - fill          - default=False         - Boolean argument, if true, 15% confidence interval is shaded around plot.
    Returns :
    - null
    """

    Tdata, kdata, low_t_range, hi_t_range, low_fit_k, hi_fit_k, full_T_range, raw_directory = get_plotting_data(material_name, path_dict, data_dict, fit_args, fit_range)

    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["erfloc"], fit_args["combined_function_type"] ################################### 20240605
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [min(Tdata), max(Tdata)],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    
    # Now let's get to plotting
    fig, axs = plt.subplots(2, figsize=(8, 6))
    i = 0
    for ref_name in data_dict.keys():
        T, k, koT, ws = data_dict[ref_name].T
        split_name = ref_name.split("_")
        label = split_name[0] + " " + split_name[1]
        label = label.replace("EtAl", " et al.")
        axs[0].plot(T, koT, marker=markers[i], ms=7, mfc='none', ls='none', c=cmap((i%6)/6), alpha=np.mean(ws))#,label=label)
        axs[1].plot(T, k, marker=markers[i], ms=7, mfc='none', ls='none', c=cmap((i%6)/6), alpha=np.mean(ws))#,label=label)
        i+=1
        if i == len(markers):
            i = 0
    # AXS 0
    koT_fit = (1/full_T_range)*loglog_func(full_T_range, param_dictionary) # 20240605
    axs[0].set_xlabel(r"$\bar T$ [K]")
    axs[0].set_ylabel(r"$k/\bar T$")
    axs[0].title.set_text(f"{material_name.replace('_', ' ')}\nLow Temperature Fit")
    axs[0].set_xlim(0.9*min(low_t_range), 1.1*max(low_t_range))
    axs[0].set_ylim(0.8*min(low_fit_k/low_t_range), 1.2*max(kdata[Tdata<1.1*max(low_t_range)]/Tdata[Tdata<1.1*max(low_t_range)]))
    axs[0].plot(full_T_range, koT_fit, label='combined fit', c="black")
    axs[0].grid(True, which="both", ls="-", color='0.65')
    if fill:
        avg_perc_diff, perc_diff_arr, *_ = get_percdiff(Tdata, kdata, fit_args)
        low_avg_perc_diff, hi_avg_perc_diff = [0,0]
        if len(Tdata[Tdata<30])>0:
            low_avg_perc_diff, low_perc_diff_arr, low_fit_sigma = get_percdiff(Tdata[Tdata<30], kdata[Tdata<30], fit_args)
        if len(Tdata[Tdata>30])>0:
            hi_avg_perc_diff, hi_perc_diff_arr, hi_fit_sigma = get_percdiff(Tdata[Tdata>30], kdata[Tdata>30], fit_args)
        axs[0].fill_between(full_T_range, koT_fit*(1+avg_perc_diff/100), (koT_fit*(1-avg_perc_diff/100)), alpha=0.25, color="gray",
                            label=f"Perc Err: {np.char.mod('%0.' + str(2) + 'f', low_avg_perc_diff)}%")
    axs[0].legend()
    # AXS 1
    # axs[1].loglog(hi_xs, hi_fit_val)
    axs[1].plot(hi_t_range, hi_fit_k, label='combined fit', c="black")
    axs[1].semilogx()
    axs[1].grid(True, which="both", ls="-", color='0.65')
    axs[1].set_ylabel(r"$k$ [W/mK]")
    axs[1].set_xlabel(r"$\bar T$ [K]")
    axs[1].set_xlim(0.9*min(hi_t_range), 1.1*max(hi_t_range))
    axs[1].set_ylim(0.9*min(hi_fit_k), 1.1*max(hi_fit_k))
    axs[1].title.set_text("High Temperature Fit")
    if fill:
        axs[1].fill_between(hi_t_range, hi_fit_k*(1+avg_perc_diff/100), (hi_fit_k*(1-avg_perc_diff/100)), alpha=0.25, color="gray",
                            label=f"Perc Err: {np.char.mod('%0.' + str(2) + 'f', hi_avg_perc_diff)}%")
    axs[1].legend()
    # plt.legend(loc='center right', bbox_to_anchor=(1.5, 1.2))
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    plt.savefig(f"{os.path.split(raw_directory)[0]}{os.sep}plots{os.sep}{material_name}_subplots.pdf", dpi=300, format="pdf", bbox_inches='tight')
    # if show:
    # plt.show()
    plt.close()

    return

def plot_residuals(material_name: str, path_dict, data_dict, fit_args, fit_range=[100e-4,25e2]):
    """
    Description : Plots the residuals of the thermal conductivity data and fits for a given material.
    Arguments :
    - material_name - name of the material
    - path_dict     - dictionary type of paths to data
    - data_dict     - dictionary of raw data with reference information as keys
    - fit_args      - combined fit arguments
    - fit_range     - default=[100e-4,25e2] - range over which to model the fit
    Returns :
    - null
    """

    Tdata, kdata, low_t_range, hi_t_range, low_fit_k, hi_fit_k, full_T_range, raw_directory = get_plotting_data(material_name, path_dict, data_dict, fit_args, fit_range)
    avg_perc_diff, perc_diff_arr, *_ = get_percdiff(Tdata, kdata, fit_args)

    low_param, hi_param, erf_param, fit_type = fit_args["low_fit_param"], fit_args["hi_fit_param"], fit_args["erfloc"], fit_args["combined_function_type"] ################################### 20240605
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    if fit_type in ["Nppoly", "polylog", "comppoly"]:
        low_param = low_param[::-1]
        hi_param = hi_param[::-1]
    param_dictionary = {"fit_type":  fit_type,
                        "fit_range": [min(Tdata), max(Tdata)],
                        "low_param": low_param,
                        "hi_param":  hi_param,
                        "erf_param": erf_param}
    # low_param = low_param[::-1] ################################### 20240531
    # hi_param = hi_param[::-1] ################################### 20240531
    

    # Residual Plots
    koT_pred = (1/Tdata)*loglog_func(Tdata, param_dictionary)
    koT_data = (1/Tdata)*kdata
    fig, axs = plt.subplots(2, figsize=(8, 6))
    # axs[0].plot(Tdata, koT_data-koT_pred, '.')
    axs[0].plot(Tdata, perc_diff_arr, '.', c=cmap(np.pi/10))
    # axs[0].plot(Tdata, 100*(koT_data-koT_pred)/koT_data, '.')
    axs[0].hlines(0, 0.9*min(low_t_range), 1.1*max(low_t_range))
    axs[0].set_xlabel("Temperature (K)")
    # axs[0].set_ylabel("residuals in % of k/T")
    axs[0].set_ylabel("residuals in % of k")
    axs[0].set_xlim(0.9*min(low_t_range), 1.1*max(low_t_range))
    axs[0].set_ylim(0.9*min(perc_diff_arr), 1.1*max(perc_diff_arr))
    axs[0].semilogx()
    axs[0].title.set_text(f"{material_name}")
    # AXS 1
    # axs[1].plot(Tdata, kdata-kpred, '.')
    axs[1].plot(Tdata, perc_diff_arr, '.', c=cmap(np.pi/10))
    axs[1].hlines(0, 0.9*min(hi_t_range), 1.1*max(hi_t_range))
    axs[1].set_xlabel("Temperature (K)")
    axs[1].set_ylabel("residuals in % of k")
    axs[1].set_xlim(0.9*min(hi_t_range), 1.1*max(hi_t_range))
    axs[1].set_ylim(0.9*min(perc_diff_arr), 1.1*max(perc_diff_arr))
    axs[1].semilogx()
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    plt.savefig(f"{os.path.split(raw_directory)[0]}{os.sep}plots{os.sep}{material_name}_ResidualPlots.pdf", dpi=300, format="pdf", bbox_inches='tight')
    # plt.show()
    plt.close()

    return

def tk_plot(material_name: str, path_dict, data_dict, fit_args, fit_range=[100e-4,25e2], points=True, fits="combined", fill=False):
    """
    Description : Produces a beautiful plot of the raw data with the fit.

    Arguments :
    - material_name - material name
    - path_dict     - dictionary type of paths to data
    - data_dict     - dictionary of raw data with reference information as keys
    - fit_args      - combined fit arguments
    - fit_range     - default=[100e-4,25e2] -
    - points        - default=True          - Boolean argument, if true, data points are added to the plot.
    - fits          - options: 'combined', 'low', 'hi', other - defines which fits to plot.
    - fill          - default=False         - Boolean argument, if true, 15% confidence interval is shaded around plot.
    - show          - default=True          - Boolean argument, if true, plot is shown in notebook.

    Returns : 
    - null
    
    """    
    plot_full(material_name, path_dict, data_dict, fit_args, fit_range, points, fits, fill)
    plot_splitfits(material_name, path_dict, data_dict, fit_args, fit_range, fill)
    plot_residuals(material_name, path_dict, data_dict, fit_args, fit_range)

    try:
        plot_full(material_name, path_dict, data_dict, fit_args, fit_range, points, fits, fill)
    except:
        print(f"Failed to plot full plot for {material_name}. This may be due to an insufficient number of data points or a poor fit.")
    try:
        plot_splitfits(material_name, path_dict, data_dict, fit_args, fit_range, fill)
    except:
        print(f"Failed to plot split fits for {material_name}. This may be due to an insufficient number of data points or a poor fit.")
    try:
        plot_residuals(material_name, path_dict, data_dict, fit_args, fit_range)
    except:
        print(f"Failed to plot residuals for {material_name}. This may be due to an insufficient number of data points or a poor fit.")
    return

def plot_all_fits(TCdata, folder_name, folder_path, save=True, show=False):
    """
    Description : Plots all the fits available in the TCdata array.
    Arguments :
    - TCdata       - array of thermal conductivity data
    - folder_name  - name of the folder containing the data
    - folder_path  - path to the folder containing the data
    - save         - default=True          - Boolean argument, if true, plot is saved to the folder.
    - show         - default=False         - Boolean argument, if true, plot is shown in notebook.
    Returns :
    - null
    """

    limits = [1, 1.1, 1e-4, 0] # [min_x, max_x, min_y, max_y]
    for i in range(1, len(TCdata)): # Loop over the different fits available
        mat_parameters = get_parameters(TCdata, index = i) # get the parameters for the fit in row i
        try:
            func_type = get_func_type(mat_parameters["fit_type"])
            fit_range = mat_parameters["fit_range"]
            # Let's make our plotting range the listed fit range
            T_range = np.linspace(fit_range[0], fit_range[1], 1000)
            # New T_range is over the entire range of the data regardless of individual fit range
            # T_range = np.logspace(np.log10(float(min(TCdata[1:, 2]))),np.log10(float(max(TCdata[1:, 3]))),1000) # 

            # Now let's use the fit to get the thermal conductivity values over the range
            # Luckily, every function type is defined in such a way to readily accept the parameter dictionary as it was defined above

            y_vals = func_type(T_range, mat_parameters)
            if "raw_fit" in str(TCdata[i][0]):
                linestyle = "--"
                linewidth = 3
                alpha=1
            else:
                linestyle = "-"
                linewidth = 4
                alpha = 0.5
            # Plotting
            plot_label = f"{TCdata[i][0]}"
            plt.plot(T_range, y_vals, label=plot_label, alpha=alpha, linestyle=linestyle, linewidth=linewidth)#, linestyle=np.random.choice(linestyle_tuple), linewidth=np.random.choice(linewidths)) # Plot the fit line for the material
            plt.semilogy()
            plt.semilogx()
            plt.title(f"Plot of {folder_name} Fits", fontsize=15)
            plt.xlabel("T [K]", fontsize=15)
            plt.ylabel("Thermal Conductivity : k [W/m/K]", fontsize=15)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            plt.grid()
            # Set xlim and ylim ignoring NaNs and inf
            finite_x = T_range[np.isfinite(T_range)]
            finite_y = y_vals[np.isfinite(y_vals)]
            if len(finite_x) > 0 and len(finite_y) > 0:
                # print(folder_name, limits[0], fit_range[0])
                limits[0] = float(min(limits[0], fit_range[0]))
                limits[1] = float(max(limits[1], fit_range[1]))
                limits[2] = float(max(min(limits[2], np.min(finite_y)), 1e-4))
                limits[3] = float(min(max(limits[3], np.max(finite_y)), 1e4))
        except:
            print(f"Error encountered when evaluating {func_type.__name__}, function type not yet supported. Skipping this fit.")
            pass
    plt.legend(loc='center', bbox_to_anchor=(1.25,0.5)) # Add legend to the plot for the material name or folder name if not specified in the dictionary
    plt.xlim(limits[0], limits[1])
    plt.ylim(limits[2], limits[3])
    # plt.xlim(1, 4)
    # plt.ylim(0.05, 0.5)
    # # plt.xlim(40, 200)
    # # plt.ylim(4, 16)
    
    plots_dir = f"{folder_path}{os.sep}plots{os.sep}"
    if not os.path.exists(plots_dir):
        print(f"making path {plots_dir}")
        os.mkdir(plots_dir)
    plt.tight_layout()
    if save:
        plt.savefig(f"{plots_dir}{folder_name}_all_fits.png", dpi=300) # Save the figure to the folder of the material
        plt.savefig(f"{plots_dir}{folder_name}_all_fits.pdf", dpi=300) # Save the figure to the folder of the material
        plt.clf()
    if show:
        plt.show()
        plt.clf()

    return

def plot_OFHC_RRR(TCdata, folder_name, folder_path, RRR_vals = np.array([10, 100, 200, 500, 1000])):
    """
    Description : Plots the thermal conductivity fits for OFHC copper with different RRR values.
    Arguments :
    - TCdata       - array of thermal conductivity data
    - folder_name  - name of the folder containing the data
    - folder_path  - path to the folder containing the data
    - RRR_vals     - array of RRR values to plot, default=[10, 100, 200, 500, 1000]
    Returns :
    - null
    """

    for i in range(len(RRR_vals)):
        # print(i)
        mat_parameters = get_parameters(TCdata, index = 1) # get the parameters for the first material in the array (assumes all materials have same fit type)
        # print(parameters)
        func_type = get_func_type(mat_parameters["fit_type"])
        fit_range = mat_parameters["fit_range"]
        # Let's make our plotting range the listed fit range
        T_range = np.linspace(fit_range[0], fit_range[1], 1000)

        # Now let's use the fit to get the thermal conductivity values over the range
        # Luckily, every function type is defined in such a way to readily accept the parameter dictionary as it was defined above
        
        y_vals = func_type(T_range, [RRR_vals[i]], mat_parameters)
        # Plotting
        plt.plot(T_range, y_vals, label=RRR_vals[i]) # Plot the fit line for the material
        plt.semilogy()
        plt.semilogx()
        plt.title(f"Plot of {folder_name} Fits")
        plt.xlabel("T [K]")
        plt.ylabel("Thermal Conductivity : k [W/m/K]")
        plt.grid()
        plt.legend(loc='best') # Add legend to the plot for the material name or folder name if not specified in the dictionary
        
    plt.savefig(f"{folder_path}{os.sep}plots{os.sep}{folder_name}_all_fits.pdf", dpi=300) # Save the figure to the folder of the material


#####################

#####################

def plot_interpolation(folder_path, interpolation_function, show = False):
    material = os.path.basename(folder_path)
    # Let's search to see if the material has room temperature data so we can include that in our interpolation
    room_temperature_data = False
    config_path = f"{folder_path}{os.sep}room_temperature.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        room_temperature_data = True
        room_temp = float(config['room_temperature_conductivity'][0])
        room_k = float(config['room_temperature_conductivity'][1])

    # Generating plot assets and loading all fit data for the material in question
    fig, ax = plt.subplots()
    fits = np.loadtxt(f"{folder_path}{os.sep}all_fits.csv", dtype = str, delimiter = ',')

    # This creates a list of each fit's low and high temperature bounds
    low_temps = fits[1:, 2]
    low_temps = [float(i) for i in low_temps]
    high_temps = fits[1:, 3]
    high_temps = [float(i) for i in high_temps]

    # Finding the range of the interpolation function
    T_range = [min(low_temps), max(high_temps)]

    if room_temperature_data:
        T_range = [min(low_temps), max(*high_temps, room_temp)]
        plt.plot(room_temp, room_k, '.', label = f"{room_temp} Kelvin conductivity")
    T = np.logspace(np.log10(T_range[0]), np.log10(T_range[1]), 1000)
    # Due to floating point error, we may want to redefine the final temperature point
    # I was recieving an error that 300.00000001 was out of the interpolation's range
    if room_temperature_data and T_range[1] == room_temp:
        T[-1] = room_temp
    # Here, we are generating the interpolation's conductivity points to plot 
    k = interpolation_function(T)

    # Finally, let's plot all the curves
    plt.plot(T, k, label = "interpolation")
    plot_all_fits(fits, material, folder_path, save = False, show = False)
    # If our room temperature data is out of bounds of the fits, we may want to shift the plot limits
    if room_temperature_data:
        plt.xlim(T_range[0], T_range[1])
        k_range = ax.get_ylim()
        plt.ylim(k_range[0], max(k_range[1], room_k))
    if show:
        plt.show()
        plt.clf()