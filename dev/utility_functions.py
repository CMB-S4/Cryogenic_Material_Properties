import h5py
import matplotlib.pyplot as plt
import numpy as np


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