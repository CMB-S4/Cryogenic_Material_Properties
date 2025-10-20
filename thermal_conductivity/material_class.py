import numpy as np
import os, sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import json, shutil, pickle, yaml
from scipy.interpolate import interp1d
from scipy.integrate import quad
from astropy import units as u
from astropy import constants as const
from inspect import signature

this_dir = os.path.dirname(os.path.abspath(__file__))
# Add this directory to the system path to allow imports
if this_dir not in sys.path:
    sys.path.append(this_dir)


from fit_types import get_func_type, linear_fit, loglog_func, Nppoly, polylog
class Material:
    """
    A class to represent a material with thermal conductivity data and fits.

    Attributes:
        name (str): Name of the material.
        folder (str): Path to the material's folder.
        data_folder (str): Path to the folder containing raw data files.
        plot_folder (str): Path to the folder for saving plots.
        parent (str): Name of the parent material, if any.
        fit_type (function): The function type used for fitting the data.
        fits (list): List of Fit objects representing different fits applied to the data.
        data_classes (dict): Dictionary of DataSet objects for each data file.
        temp_range (tuple): Temperature range covered by the data.
        raw_fit_params (np.ndarray): Parameters from the initial fit to all included data.
        raw_fit_cov (np.ndarray): Covariance matrix from the initial fit to all included data.
        room_temp_tuple (tuple): Tuple containing room temperature and corresponding conductivity, if available.
        interpolate_function (function): Interpolation function for thermal conductivity based on fits.
    """
    def __init__(self, name, parent: str=None, fit_type = "loglog", force_update: bool =False):
        """Initialize the Material class.

        Args:
            name (str): Name of the material.
            parent (str, optional): Name of the parent material. Defaults to None.
            fit_type (function, optional): The fitting function to use. Defaults to loglog_func.
            force_update (bool, optional): Whether to force update the material. Defaults to False.

        """
        self.name = name
        self.folder = "lib"+os.sep+name #
        folder_path = os.path.join(this_dir,"lib", name)

        # If the folder exists and contains a pickle file with the class already stored then load it
        pickle_file = os.path.join(self.folder, "material.pkl")
        if os.path.exists(pickle_file) and not force_update:
            with open(pickle_file, "rb") as f:
                material = pickle.load(f)
                self.__dict__.update(material.__dict__)
            # print(f"Loaded existing material: {self.name}")
            self.folder = "lib"+os.sep+name # os.path.join(this_dir, "lib", name)
            self.data_folder = os.path.join(self.folder, "RAW")
            self.plot_folder = os.path.join(self.folder, "PLOTS")
            if not os.path.exists(self.plot_folder):
                os.mkdir(self.plot_folder)
        # If the material pickle doesn't exist, then create the material from scratch
        else:
            self.data_folder = os.path.join(self.folder, "RAW")
            self.plot_folder = os.path.join(self.folder, "PLOTS")
            if not os.path.exists(self.plot_folder):
                os.mkdir(self.plot_folder)
            self.parent = parent
            self.fit_type = fit_type
            self.fits = []
            if os.path.exists(self.data_folder) and os.listdir(self.data_folder) != []:
                self.data_classes = self.get_data()[1]
                included_data = [ds.data for ds in self.data_classes.values() if ds.include]
                all_data = np.vstack(included_data)
                self.temp_range = (min(all_data[:,0]), max(all_data[:,0]))

                try:
                    fit_param, fit_cov = self.fit_data()
                    self.raw_fit_params = fit_param
                    self.raw_fit_cov = fit_cov
                except Exception as e:
                    print(f"Could not fit data for {self.name}: {e}")
                    self.raw_fit_params = None
                    self.raw_fit_cov = None
            else:
                self.data_classes = None
                self.temp_range = None
                self.raw_fit_params = None
                self.raw_fit_cov = None

            room_temp_file = os.path.join(self.folder, "room_temperature.yaml")
            if os.path.exists(room_temp_file):
                with open(room_temp_file, 'r') as file:
                    import yaml
                    config = yaml.safe_load(file)
                self.room_temp_tuple = config['room_temperature_conductivity']
            else:
                self.room_temp_tuple = None
        if len(self.fits) > 0:
            self.interpolate_function = self.interpolate(preferred_fit=None)
        
        # If it has a parent
        # We want to copy any raw data files to the parent folder
        # And also copy any fits we have to the parent material
        if self.parent is not None:
            parent_folder = os.path.join(this_dir, "lib", self.parent)
            if not os.path.exists(parent_folder):
                os.mkdir(parent_folder)

            # If the parent material doesn't have a RAW folder, create it
            if os.path.exists(self.data_folder) and self.data_classes is not None:
                if os.listdir(self.data_folder) != []:
                    parent_raw_folder = os.path.join(parent_folder, "RAW")
                    if not os.path.exists(parent_raw_folder):
                        os.mkdir(parent_raw_folder)
                    # if this material has csv files in the data folder, copy them to the parent data folder
                    for file in os.listdir(self.data_folder):
                        if file.endswith(".csv"):
                            src = os.path.join(self.data_folder, file)
                            dst = os.path.join(parent_raw_folder, file)
                            if not os.path.exists(dst):
                                shutil.copy(src, dst)
                            # This code block may be needed to avoid overwriting files in the parent folder
                            # i = 1
                            # if os.path.exists(dst):
                            #     print(f"File {file} already exists in parent folder. Renaming to avoid overwrite.")
                            #     while os.path.exists(dst):
                            #         dst = os.path.join(parent_raw_folder, f"{file.split('.')[0]}_{i}.csv")
                            #         i += 1
                            # print(f"Copying {src} to {dst}")
                            # shutil.copy(src, dst)
            # Now we want to see if the parent already has a class pickle file
            parent_pickle = os.path.join(parent_folder, "material.pkl")
            if os.path.exists(parent_pickle):
                parent_class = pickle.load(open(parent_pickle, "rb"))
                # load the existing fits
                existing_fits = [fit.name for fit in parent_class.get_fits()]
                # If it does, we want to add our fits to the parent class fits
                for fit in self.fits:
                    if fit.name not in existing_fits:
                        # print(f"Adding fits from {self.name} to parent material {self.parent}.")
                        parent_class.add_fits(self.name, fit.source, fit.range, fit.parameters, fit.parameter_covariance, fit.fit_type, fit.fit_error)
            # If the parent class doesn't yet exist, we want to create it
            else:
                parent_class = Material(self.parent, force_update=True)
                for fit in self.fits:
                    parent_class.add_fits(self.name, fit.source, fit.range, fit.parameters, fit.parameter_covariance, fit.fit_type, fit.fit_error)
            # Finally, we save the updated parent class
            with open(parent_pickle, "wb") as f:
                pickle.dump(parent_class, f)
            # print(f"Updating data to parent material: {self.parent}")

    def get_data(self):
        """Get the data for the material.

        Returns:
            dict: A dictionary containing the data for the material.
            dict: A dictionary containing DataSet objects for each data file.
        """
        data_dict = {}
        data_class_dict = {}
        if not os.path.exists(self.data_folder):
            return None, None
        for file in os.listdir(self.data_folder):
            if file.endswith(".csv"):
                reference_row = np.loadtxt(os.path.join(self.data_folder, file), delimiter=",", max_rows=1, dtype=str)
                ref_string = [i for i in reference_row if i != '']
                data = np.loadtxt(os.path.join(self.data_folder, file), delimiter=",", skiprows=2)
                # If the data is only one row (one dimensional), we need to reshape it to be two dimensional
                if len(data.shape) == 1:
                    data = data.reshape((1, -1))
                data_dict[file] = data
                data_class_dict[file] = DataSet(file, data, ref_string=ref_string)
        return data_dict, data_class_dict
    
    def update_data(self):
        """Update the data for the material.

        Returns:
            dict: A dictionary containing the updated data for the material.
            dict: A dictionary containing updated DataSet objects for each data file.
        """
        self.data_classes = self.get_data()[1]
        return
        
    def fit_data(self, n_param = None, p0=None, bounds=None):
        """Fit the data for the material.

        Args:
            n_param (int, optional): The number of parameters for the fit. Defaults to 8.
            p0 (array-like, optional): Initial guess for the fit parameters. Defaults to None.
            bounds (tuple, optional): Bounds for the fit parameters. Defaults to None.

        Returns:
            popt (np.ndarray): Optimal values for the fit parameters.
            pcov (np.ndarray): Covariance matrix of the fit parameters.
        """
        if self.data_classes == None:
            print("No data to fit.")
            return None, None
        # Only fit the dataset classes that have a fit tag (aren't excluded)
        included_data = [ds.data for ds in self.data_classes.values() if ds.include]

        # concatenate the data from all files
        all_data = np.vstack(included_data)
        x = all_data[:, 0]
        y = all_data[:, 1]

        # fit to a log scale version of the function to equally value low temps
        def log_func(x, *args):
            y = get_func_type(self.fit_type)(x, *args)
            return np.log(y)

        if self.fit_type == "loglog":
            n_param = 9
            p0 =  [1.13377143e-07, -2.98684987e-05,  1.90655344e-03,  8.47382032e-02,
                    9.98573679e-03,  2.45862017e-02,  1.00316703e-01,  6.12147734e-01,
                    np.mean([min(x),max(x)])] # This is just an example starting point for the fit
            bounds = ((-np.inf, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf, min(x)), 
                    (np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, max(x)))
            popt, pcov = curve_fit(log_func, x, np.log(y), maxfev=10000, p0=np.ones(n_param) if p0 is None else p0, bounds=(0, np.inf) if bounds is None else bounds)
        elif n_param is None:
            # Assume the function has a defined number of parameters, like power law or something.
            sig = signature(get_func_type(self.fit_type))
            n_param = len(sig.parameters)
            
        # use the fit_type function to fit the data
        popt, pcov = curve_fit(log_func, x, np.log(y), maxfev=10000, p0=np.ones(n_param) if p0 is None else p0)
        new_fit = Fit(self.name, "data", (min(x), max(x)), popt, pcov, self.fit_type)
        new_fit.add_reference("Data Fit (see references for included data)")
        self.fits.append(new_fit)
        return popt, pcov
    
    def update_fit(self, new_fit_type, n_param=None):
        """
        Use this function to change the default fit type for the material and refit the data.
        Args:
            new_fit_type (str): The new fit type to use.
        """
        for i, fit in enumerate(self.fits):
            if fit.source == "data":
                # delete the existing fit
                del self.fits[i]
        self.fit_type = new_fit_type
        try:
            popt, pcov = self.fit_data(n_param=n_param)
        except ValueError:

            print(f"Failed to fit. Please ensure you have specified the appropriate number of fit parameters (if the fit type does not have a specified number).")
            raise ValueError
            return
        self.raw_fit_params = popt
        self.raw_fit_cov = pcov
        # Now update the material.fits list, replace the fit with source "data"
        # for i, fit in enumerate(self.fits):
        #     print(fit.source, fit.fit_type)
        #     if fit.source == "data":
        #         self.fits[i] = Fit(self.name, "data", (min(self.temp_range), max(self.temp_range)), popt, pcov, self.fit_type)
        # print(self.fits)
        self.interpolate_function = self.interpolate(preferred_fit=None)
        return self

    def interpolate(self, preferred_fit: None):
        """
        Interpolate the thermal conductivity data for the material.
        Args:
            preferred_fit (Fit, optional): A Fit object that should be preferred in the interpolation. Defaults to None.
        Returns:
            interp_func (function): An interpolation function for the thermal conductivity data.
        """
        # Author : Ani Pagni
        # Let's search to see if the material has room temperature data so we can include that in our interpolation
        self.room_temp = self.room_temp_tuple[0] if self.room_temp_tuple is not None else None
        self.room_temp_conductivity = self.room_temp_tuple[1] if self.room_temp_tuple is not None else None
        
        # Collect the different fits
        fits = self.fits
        if len(fits) == 0:
            print("No fits to interpolate.")
            return None
        x_ranges = [fit.range for fit in fits]
        low_temps = [r[0] for r in x_ranges]
        high_temps = [r[1] for r in x_ranges]
        x_min = min(low_temps)
        x_max = max(high_temps)

        # We want to sort our fits to go in numerical order by low temperature range
        # This will make it easy to choose when to switch fits during interpolation
        sorting_indices = np.argsort(low_temps)
        # if self.roo
        # sorting_indices = np.append(0, sorting_indices+1)  # Add an index at the start for room temperature if it exists
        sorted_fits = [fits[i] for i in sorting_indices]
        Ts = np.empty(0, float)
        ks = np.empty(0, float)

        # If we have a fit we prefer the interpolation to use it will create the points here and block other fits from overriding them later
        if preferred_fit != None:
            T = np.logspace(np.log10(preferred_fit.range[0]), np.log10(preferred_fit.range[1]), 100)
            k = get_func_type(preferred_fit.fit_type)(T, *preferred_fit.parameters)
            Ts = np.append(Ts, T)
            ks = np.append(ks, k)
        
        # Here, we go through every fit for the chosen material and decide what parts of each fit to use
        for i, fit in enumerate(sorted_fits):
            # If we have a room temperature data point, we want to include it in the interpolation
            if self.room_temp is not None and i == 0:
                T = np.array([self.room_temp])
                k = np.array([self.room_temp_conductivity])
                Ts = np.append(Ts, T)
                ks = np.append(ks, k)
            
            # If we have a preferred fit, we want to skip any fits that overlap with it
            if preferred_fit != None:
                if (fit.range[0] >= preferred_fit.range[0]) and (fit.range[1] <= preferred_fit.range[1]):
                    continue
            
            # If this fit overlaps with the previous fit, we want to only use the part of the fit that doesn't overlap
            add_fit_range = fit.range
            if i > 0:
                prev_fit = sorted_fits[i-1]
                if fit.range[0] < max(Ts): # if the new fit starts before the previous fit ends
                    add_fit_range = (max(Ts), fit.range[1]) # set the range of this fit to the end of the last to the end of the new
            # Now we can create the points for this fit
            if add_fit_range[0] < add_fit_range[1]:
                T = np.logspace(np.log10(add_fit_range[0]), np.log10(add_fit_range[1]), 1000)
                # if T[-1] > add_fit_range[1]:
                #     T[-1] = add_fit_range[1]
                k = get_func_type(fit.fit_type)(T, *fit.parameters)
                Ts = np.append(Ts, T)
                ks = np.append(ks, k)
            
        # Finally, we sort the points and save them to a file
        sorted_indices = np.argsort(Ts)
        Ts = Ts[sorted_indices]
        ks = ks[sorted_indices]

        # create an interpolation function
        interp_func = interp1d(Ts, ks, bounds_error=False)
        interp_pkl = os.path.join(this_dir, "lib", self.name, "interpolation.pkl")
        with open(interp_pkl, "wb") as f:
            pickle.dump(interp_func, f)
        return interp_func

    def plot_data(self, loglog=True):
        """
        Plot the experimental data for the material.
        """
        if self.data_classes == None:
            # print("No data to fit.")
            return
        included_data = [ds.data for ds in self.data_classes.values() if ds.include]
        # concatenate the data from all files
        for dataclass in self.data_classes.values():
            if dataclass.include:
                data = dataclass.data
                plt.scatter(data[:,0], data[:,1], label=dataclass.name)

        # all_data = np.vstack(included_data)
        # x = all_data[:, 0]
        # y = all_data[:, 1]
        # plt.scatter(x, y, label="Data")
        plt.xlabel("T [K]", fontsize=15)
        plt.ylabel(r"Thermal Conductivity : $\kappa$ [W/m/K]", fontsize=15)
        if loglog:
            plt.xscale("log")
            plt.yscale("log")
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.title(f"Data for {self.name}", fontsize=15)
        plt.legend(fontsize=15)
        return

    def plot_data_fit(self):
        """
        Plot the experimental data and the fit to the data for the material.
        """
        if self.data_classes == None or self.raw_fit_params is None:
            # print("No data to fit.")
            return
        if self.fits == []:
            print("No fits to plot.")
            return
        included_data = [ds.data for ds in self.data_classes.values() if ds.include]
        # concatenate the data from all files
        all_data = np.vstack(included_data)
        x = all_data[:, 0]
        x_range_plot = np.logspace(np.log10(min(x)), np.log10(max(x)), 100)
        y_fit = get_func_type(self.fit_type)(x_range_plot, *self.raw_fit_params)
        plt.xlabel("T [K]", fontsize=15)
        plt.ylabel(r"Thermal Conductivity : $\kappa$ [W/m/K]", fontsize=15)
        plt.plot(x_range_plot, y_fit, color="red", label="Fit")
        self.plot_data()
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend()
        return
    
    def plot_interpolation(self, loglog=True):
        """
        Plot the interpolation fit for the material.
        """
        if hasattr(self, 'interpolate_function') and self.interpolate_function is not None:
            x_range_plot = np.logspace(np.log10(self.interpolate_function.x[0]), np.log10(self.interpolate_function.x[-1]), 100)
            y_fit = self.interpolate_function(x_range_plot)
            plt.plot(x_range_plot, y_fit, color="green", label="Interpolation")
            plt.xticks(fontsize=15)
            plt.yticks(fontsize=15)
            plt.xlabel("T [K]", fontsize=15)
            plt.ylabel(r"Thermal Conductivity : $\kappa$ [W/m/K]", fontsize=15)
            if self.data_classes is not None:
                self.plot_data()
            plt.legend()
            return
        else:
            return

    def plot_all_fits(self, loglog=True):
        """
        Plot all the available fits for the material.
        """
        if len(self.fits) == 0:
            print("No fits to plot.")
            return
        for fit in self.fits:
            x_range_plot = np.logspace(np.log10(fit.range[0]), np.log10(fit.range[1]), 100)
            # print(fit.range)
            # if x_range_plot[-1] > fit.range[1]:
            #     x_range_plot[-1] = fit.range[1]
            y_fit = fit.function()(x_range_plot, *fit.parameters)
            plt.plot(x_range_plot, y_fit, label=f"{fit.name}")
        if self.interpolate_function is not None:
            x_range_plot = np.logspace(np.log10(self.interpolate_function.x[0]), np.log10(self.interpolate_function.x[-1]), 100)
            y_fit = self.interpolate_function(x_range_plot)
            plt.plot(x_range_plot, y_fit, color="gray", linestyle=':', label="Interpolation")
        if loglog:
            plt.xscale("log")
            plt.yscale("log")
        
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.xlabel("T [K]", fontsize=15)
        plt.ylabel(r"Thermal Conductivity : $\kappa$ [W/m/K]", fontsize=15)
        plt.legend()
        return
    
    def save_fits(self):
        """
        Converts the self.fits to a dictionary and saves as a json file
        """
        fits_dict = {}
        for fit in self.fits:
            fit_dict = fit.__dict__.copy()
            # Convert numpy arrays to lists for JSON serialization
            if isinstance(fit_dict["parameters"], np.ndarray):
                fit_dict["parameters"] = fit_dict["parameters"].tolist()
            if isinstance(fit_dict["parameter_covariance"], np.ndarray):
                fit_dict["parameter_covariance"] = fit_dict["parameter_covariance"].tolist()
            fits_dict[fit.source] = fit_dict
        with open(os.path.join(self.folder, "fits.json"), "w") as f:
            json.dump(fits_dict, f, indent=4)
        return
    
    def get_fits(self):
        """
        Returns the list of Fit objects for the material.
        """
        return self.fits
    
    def add_fits(self, fit_name: str, source: str, fit_range: tuple, parameters: np.ndarray, parameter_covariance: np.ndarray, fit_type: str, fit_error: float = None):
        """
        Adds a new fit to the material.
        Args:
            fit_name (str): Name of the fit (usually material + source).
            source (str): Source of the fit (e.g., "data", "literature").
            fit_range (tuple): Temperature range over which the fit is valid.
            parameters (np.ndarray): Parameters of the fit function.
            parameter_covariance (np.ndarray): Covariance matrix of the fit parameters.
            fit_type (str): Type of fit function used.
            fit_error (float, optional): Optional error metric for the fit. Defaults to None.
        
        Alternatively, a Fit object can be created externally and added to the material by appending to self.fits.
        """
        new_fit = Fit(fit_name, source, fit_range, parameters, parameter_covariance, fit_type, fit_error)
        self.fits.append(new_fit)
        return
    
    def save(self):
        """
        Save the material class as a pickle file.
        """
        # Save the material class as a pickle file
        with open(os.path.join(self.folder, "material.pkl"), "wb") as f:
            pickle.dump(self, f)
        return
    
    def fit_by_name(self, fit_name):
        """
        Retrieves the fit object for a specified fit name.
        """
        for fit in self.fits:
            if fit.name == fit_name:
                return fit
        return None
    
    def print_refs(self):
        with open(os.path.join(self.folder, "references.txt"), "w") as f:
            fit_counter = 1
            if len(self.fits) != 0:
                f.write("Fits:\n")
                for fit in self.fits:
                    if hasattr(fit, 'reference'):
                        f.write(f"{fit_counter}. {fit.name}: {fit.reference}\n")
                    else:
                        f.write(f"{fit_counter}. {fit.name}: No reference available.\n")
                    fit_counter += 1
                f.write("\n--------------------------------\n")
            dataset_counter = 1
            if self.data_classes is not None:
                f.write("\nData Sets:\n")
                for dataset in self.data_classes:
                    dataset_obj = self.data_classes[dataset]
                    if hasattr(dataset_obj, 'reference'):
                        f.write(f"{dataset_counter}. {dataset_obj.name}:\n")
                        f.write(f"   Title        : {dataset_obj.reference[0]}\n")
                        if len(dataset_obj.reference) > 1:
                            f.write(f"   Author(s)    : {dataset_obj.reference[1]}\n")
                        if len(dataset_obj.reference) > 2:
                            f.write(f"   Journal/Year : {', '.join(dataset_obj.reference[2:])}\n")
                        f.write("\n")
                    else:
                        f.write(f"{dataset_counter}. {dataset_obj.name}: No reference available.\n")
                    dataset_counter += 1
        return
        
class Fit:
    """
    A class to represent a fit applied to the data.

    Attributes:
        material (str): Name of the material.
        source (str): Source of the fit (e.g., "data", "literature").
        name (str): Name of the fit (usually material + source).
        range (tuple): Temperature range over which the fit is valid.
        parameters (np.ndarray): Parameters of the fit function.
        parameter_covariance (np.ndarray): Covariance matrix of the fit parameters.
        fit_type (str): Type of fit function used.
        fit_error (float): Optional error metric for the fit.
        reference (str): Reference for the fit.
    """
    def __init__(self, material: str, source: str, range: tuple, parameters: np.ndarray, parameter_covariance: np.ndarray, fit_type=None, fit_error: float = None):
        self.material = material
        self.source = source
        self.name = f"{material}_{source}"
        self.range = range
        self.parameters = parameters
        self.parameter_covariance = parameter_covariance
        self.fit_type = fit_type
        self.fit_error = fit_error
    
    def function(self):
        """
        Returns the function type used for the fit as a callable.
        E.g. Fit.function()(x, *params) will evaluate the fit function at x.
        """
        return get_func_type(self.fit_type)
    
    @u.quantity_input
    def calc_tc(self, T: u.K):
        """
        Calculate the thermal conductivity at a specific temperature.
        Args:
            T (u.K): Temperature at which to calculate thermal conductivity.
        Returns:
            k (u.W/m/K): Thermal conductivity at temperature T.
        
        Uses astropy units to ensure correct unit handling.
        """
        # Convert temperature to Kelvin if it is not already
        T = T.to(u.K).value
        if self.fit_type is not None:
            return get_func_type(self.fit_type)(T, *self.parameters)*u.W/u.m/u.K
        else:
            print("No fit type defined.")
            return None
    
    @u.quantity_input
    def tc_integral(self, T1: u.K, T2: u.K):
        """
        Calculate the integral of the thermal conductivity over a temperature range.
        Args:
            T1 (u.K): Lower temperature limit.
            T2 (u.K): Upper temperature limit.
        Returns:
            integral (u.W/m): The integral of thermal conductivity from T1 to T2.
            error (float): Estimated error of the integral.
        
        Uses astropy units to ensure correct unit handling.
        """
        # Convert temperatures to Kelvin if they are not already
        T1 = T1.to(u.K).value
        T2 = T2.to(u.K).value
        if self.fit_type is not None:
            integral, error = quad(get_func_type(self.fit_type), T1, T2, args=tuple(self.parameters))*u.W/u.m
            return integral, error
        else:
            print("No fit type defined.")
            return None, None
    def plot(self, **plotkwargs):
        x = np.linspace(self.range[0], self.range[1], 100)
        y = get_func_type(self.fit_type)(x, *self.parameters)
        if 'label' in plotkwargs:
            plt.plot(x, y, **plotkwargs)
        else:
            plt.plot(x, y, label=f"{self.material} {self.source} fit", **plotkwargs)
        plt.xlabel("T [K]", fontsize=15)
        plt.ylabel(r"Thermal Conductivity : $\kappa$ [W/m/K]", fontsize=15)
        plt.xscale("log")
        plt.yscale("log")
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.title(f"Fit for {self.name}", fontsize=15)

    def add_reference(self, reference: str):
        """Adds a reference string to the fit.

        Args:
            reference (str): The reference string to add in the format 'Title, Author, Journal/Year'.
        """
        self.reference = reference
        return

class DataSet():
    """
    A class to represent a dataset from a CSV file.
    Attributes:
        name (str): Name of the dataset (usually the filename).
        data (np.ndarray): The data array with temperature and property values.
        include (bool): Whether to include this dataset in fits.
    """
    def __init__(self, name: str, data: np.ndarray, ref_string: str):
        self.name = name
        self.data = data
        self.include = self.inclusion_state()
        self.reference = ref_string

    def inclusion_state(self, state=True):
        """
        Set or get the inclusion state of the dataset (whether to include in the data fit of the material).
        Args:
            state (bool, optional): If provided, sets the inclusion state. Defaults to True.
        Returns:
            bool: The current inclusion state.
        """
        self.include = state
        return state
    