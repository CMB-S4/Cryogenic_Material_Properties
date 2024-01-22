import h5py
import matplotlib.pyplot as plt
import numpy as np
import os

def get_datafiles(material_name):
    all_files = os.listdir(material_name)
    extension = ".csv"
    raw_files = [file for file in all_files if file.endswith(extension)]
    print(f"For material {material_name}, found {len(raw_files)} measurements.")
    return raw_files

def extract_RAW(material_name, raw_files):
    file_name = f"{material_name}.lh5"
    with h5py.File(file_name, "w") as material_file:
            counter = 0
            for raw_file in raw_files:
                # print(raw_file)
                file1 = np.loadtxt(f"{material_name}/{raw_file}", dtype=str, delimiter=',')
                ref = file1[0,:]
                ref_encode = [s.encode('utf-8') for s in ref]
                headers = file1[1,:]
                data_RAW = np.asarray(file1[2:,:], dtype=float)
                group = material_file.create_group(f"ref{counter}")
                ref_set = material_file[f"ref{counter}"].create_dataset("ref_info", (3,), data=ref_encode)
                raw_set = material_file[f"ref{counter}"].create_dataset("raw_data", data=data_RAW)
                counter += 1
            print(f"Material lh5 file has been saved with filename {file_name}")

def get_fit(comp_file, material, range):
    with h5py.File(comp_file, 'r') as f:
        return np.array(f[f"{material}/{range}_fit/fit_param"])

def get_fit_thresh(comp_file, material):
    with h5py.File(comp_file, 'r') as f:
        return f[f"{material}/low_fit/fit_range"][-1]

def get_k(comp_file, material, T):
    thresh = get_fit_thresh(comp_file, material)
    if T >= thresh:
        range = "hi"
        
        fit_params = get_fit(comp_file, material, range)
        val = 10**np.polyval(fit_params, np.log10(T))
    else:
        range = "low"
        fit_params = get_fit(comp_file, material, range)
        val = T*np.polyval(fit_params, T)
    
    return val


def compile_measurements(material_name, plots=False):
    with h5py.File(f"{material_name}.lh5", "r") as f:
            if plots:
                 fig, axs = plt.subplots(2, 2, figsize=(8, 6))
            big_data = np.empty((3,))
            for key in f.keys():
                big_data = np.vstack((big_data, np.array(f[f"{key}/raw_data"])))
                T   = np.array(f[f"{key}/raw_data"])[:,0]
                k   = np.array(f[f"{key}/raw_data"])[:,1]
                koT = np.array(f[f"{key}/raw_data"])[:,2]
                if plots:
                    axs[0, 0].plot(T, k, '.', label=key)
                    axs[0, 1].plot(T, koT, '.', label=key)
                    axs[1, 0].plot(np.log10(T), np.log10(k),'.')
                    axs[1, 1].plot(np.log10(T), np.log10(koT),'.')
            
            if plots:
                axs[0,0].set_xlabel("T")
                axs[0,0].set_ylabel("k")
                axs[0,1].set_xlabel("T")
                axs[0,1].set_ylabel("k/T")
                axs[1,0].set_xlabel("log10(T)")
                axs[1,0].set_ylabel("log10(k)")
                axs[1,1].set_xlabel("log10(T)")
                axs[1,1].set_ylabel("log10(k/T)")

                plt.subplots_adjust(wspace=0.4, hspace=0.4)
                axs[0,1].legend(loc='center right', bbox_to_anchor=(1.5, 0.5))
                plt.show()
            big_data = big_data[2:,:]
    return big_data

def fit_thermal_conductivity(big_data, thresh = 20, fit_orders = (2,3)):
    # thresh     : 20    : The temperature threshold to split low and high data   
    # fit_orders : (2,3) : The polynomial order for the low and high fits respectively

    # divide the data array into three columns
    T = big_data[:,0]
    k = big_data[:,1]
    koT = big_data[:,2]

    # Set a temperature threshold for split between hi and low fits
    thresh = 20 # in K

    # Find the low range
    lowT = T[T<thresh]
    lowT_k = k[T<thresh]
    lowT_koT = koT[T<thresh]

    # Find the high range
    hiT = T[T>thresh]
    hiT_k = k[T>thresh]
    # Take a log10 of the high range
    log_hi_T = np.log10(hiT)
    log_hi_k = np.log10(hiT_k)

    # Fit the low data
    low_fit = np.polyfit(lowT, lowT_koT, fit_orders[0])
    fit_xs = np.linspace(np.min(lowT), np.max(lowT), 100)
    low_poly1d = np.poly1d(low_fit)


    # Fit the high data
    hi_fit = np.polyfit(log_hi_T, log_hi_k, fit_orders[1])
    fit_xs = np.linspace(np.min(log_hi_T), np.max(log_hi_T), 100)
    hi_poly1d = np.poly1d(hi_fit)

    return [low_poly1d, hi_poly1d, thresh, max(hiT)]





def save_tc_lh5file(material_args):
    os.chdir(os.path.split(os.getcwd())[0])
    comp_file = "ThermalConductivityFits.lh5"
    with h5py.File(comp_file, "w") as f:
        for i in range(len(material_args)):
            [low_fits, hi_fits, thresholds, hiTs, material_names] = material_args[i]
            f.create_group(f"{material_names}")
            f[f"{material_names}"].create_group("low_fit")
            f[f"{material_names}"].create_group("hi_fit")
            f[f"{material_names}/low_fit"].create_dataset("fit_param", data=low_fits)
            f[f"{material_names}/low_fit"].create_dataset("fit_range", data=[0,thresholds])
            f[f"{material_names}/hi_fit"].create_dataset("fit_param", data=hi_fits)
            f[f"{material_names}/hi_fit"].create_dataset("fit_range", data=[thresholds, hiTs])
    os.chdir(f"{os.getcwd()}\\FITS")


def save_tc_txtfile(material_args):
    os.chdir(os.path.split(os.getcwd())[0])
    comp_file = "ThermalConductivityFits.txt"
    f = open(comp_file, "w")
    for i in range(len(material_args)):
        [low_fits, hi_fits, thresholds, hiTs, material_names] = material_args[i]
        f.write(f"{material_names}\n")
        f.write("low_fit\n")
        f.write(f"fit_param {low_fits}\n")
        f.write(f"fit_range: {[0,thresholds]}\n")
        f.write("hi_fit\n")
        f.write(f"fit_param {hi_fits}\n")
        f.write(f"fit_range: {[thresholds, hiTs]}\n")
        f.write("\n")
    os.chdir(f"{os.getcwd()}\\FITS")