import h5py
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

os.chdir(sys.path[0])

all_files = os.listdir(f"{os.getcwd()}\\FITS")
print(all_files)
extension = ".lh5"
raw_files = [file for file in all_files if file.endswith(extension)]
raw_names = [os.path.splitext(name)[0] for name in raw_files]
print(f"Found {len(raw_names)}, lh5 material files: {raw_names}")

# def compile_measurements(material_name):
#     big_data = np.empty((2,3))
#     with h5py.File(f"{material_name}.lh5", "r") as f:
#         for key in f.keys():
#             big_data = np.vstack((big_data, np.array(f[f"{key}/raw_data"])))
#         big_data = big_data[2:,:]
#     return big_data

def compile_measurements(material_name, plots=False):
    with h5py.File(f"{material_name}.lh5", "r") as f:
            fig, axs = plt.subplots(2, 2, figsize=(8, 6))
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

for mat in raw_names:
    # Compile the data from all measurements into 1 data array
    big_data = compile_measurements(mat, plots=False) # Turn plots to True for plots

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


    # plt.plot(lowT, lowT_koT,'.')
    # plt.show()
    # plt.plot(log_hi_T, log_hi_k,'.')
    # plt.show()

    # Fit the low data
    low_fit = np.polyfit(lowT, lowT_koT, 2)
    fit_xs = np.linspace(np.min(lowT), np.max(lowT), 100)
    # plt.plot(fit_xs, np.polyval(low_fit, fit_xs))
    # plt.plot(lowT, lowT_koT, '.')
    # plt.show()

    low_poly1d = np.poly1d(low_fit)
    # print(low_poly1d)

    # Fit the high data
    hi_fit = np.polyfit(log_hi_T, log_hi_k, 3)
    fit_xs = np.linspace(np.min(log_hi_T), np.max(log_hi_T), 100)
    # plt.plot(fit_xs, np.polyval(hi_fit, fit_xs))
    # plt.plot(log_hi_T, log_hi_k, '.')
    # plt.ylabel("log10(k)")
    # plt.xlabel("log10(T)")
    # plt.show()

    hi_poly1d = np.poly1d(hi_fit)
    # print(hi_poly1d)

    # Some statistics ??
    # hi_fit_pred = hi_poly1d(log_hi_T)
    # residuals = log_hi_k - hi_fit_pred

    # # Calculate R-squared
    # total_variance = np.sum((log_hi_k - np.mean(log_hi_k))**2)
    # explained_variance = np.sum((hi_fit_pred - np.mean(log_hi_k))**2)
    # r_squared = explained_variance / total_variance

    # print(total_variance, explained_variance, r_squared)



    # plt.plot(lowT, lowT_k,'.')
    # lowTplotrange = np.arange(min(lowT), max(lowT))
    # plt.plot(lowTplotrange, lowTplotrange*low_poly1d(lowTplotrange))
    # plt.xlabel("T")
    # plt.ylabel("k")
    # plt.show()


    # plt.plot(hiT, hiT_k,'.')
    # hiTplotrange = np.arange(min(hiT), max(hiT))
    # print(hiTplotrange)
    # plt.plot(hiTplotrange, 10**hi_poly1d(np.log10(hiTplotrange)))
    # plt.xlabel("T")
    # plt.ylabel("k")
    # plt.show()


    # print(low_poly1d) # k/T = low_poly1d(T)
    # print(hi_poly1d) # log10(k) = hi_poly1d(log10(T))
    # print(thresh)


    comp_file = "ThermalConductivityFits.lh5"

    with h5py.File(comp_file, "w") as f:
        f.create_group(f"{mat}")
        f[f"{mat}"].create_group("low_fit")
        f[f"{mat}"].create_group("hi_fit")
        f[f"{mat}/low_fit"].create_dataset("fit_param", data=low_poly1d)
        f[f"{mat}/low_fit"].create_dataset("fit_range", data=[0,thresh])
        f[f"{mat}/hi_fit"].create_dataset("fit_param", data=hi_poly1d)
        f[f"{mat}/hi_fit"].create_dataset("fit_range", data=[thresh, max(hiT)])


    def get_fit(material, range):
        with h5py.File(comp_file, 'r') as f:
            return np.array(f[f"{material}/{range}_fit/fit_param"])

    def get_fit_thresh(material):
        with h5py.File(comp_file, 'r') as f:
            return f[f"{material}/low_fit/fit_range"][-1]

    def get_k(material, T):
        thresh = get_fit_thresh(material)
        if T >= thresh:
            range = "hi"
            
            fit_params = get_fit(material, range)
            val = 10**np.polyval(fit_params, np.log10(T))
        else:
            range = "low"
            fit_params = get_fit(material, range)
            val = T*np.polyval(fit_params, T)
        
        return val
        
    # get_k("SS304", 1200)