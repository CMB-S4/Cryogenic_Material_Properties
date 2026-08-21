import sys
import string
import pickle
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

PACKAGE_DIR = Path(__file__).resolve().parent
path_to_mat_lib = PACKAGE_DIR / "lib"


def _import_sibling(module_name: str):
    """Import a module that lives next to this file via importlib, keyed off this
    file's own location on disk rather than the working directory or sys.path.
    Keeps this package importable the same way on any OS and independent of how
    (or from where) it is loaded.
    """
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(
        module_name, PACKAGE_DIR / f"{module_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


material_class = _import_sibling("material_class")
Material = material_class.Material
Fit = material_class.Fit

fit_types = _import_sibling("fit_types")
get_func_name = fit_types.get_func_name

def get_materials_list() -> list:
    """
    Description : Retrieves a list of all materials available in the materials library.
    Returns:
        materials (list): List of material names.
    """
    materials = [folder.name for folder in path_to_mat_lib.iterdir() if folder.is_dir()]
    return materials

def get_material(mat: str) -> Material:
    """
    Description : Retrieves the material object from the materials library.

    Args:
        mat (str): Material name.

    Returns:
        material (Material): Material object if found, else None.
    """
    material_path = path_to_mat_lib / mat
    if material_path.exists():
        with open(material_path / "material.pkl", "rb") as f:
            material = pickle.load(f)
            return material
    else:
        return None


def get_material_fits(mat_name: str) -> list:
    """
    Description : Retrieves the fit object for a specific material.
    Args:
        mat_name (str): Material name.
    Returns:
        material.fits (list): List of Fit objects for the material.
    """
    material = get_material(mat_name)
    if material:
        return material.fits
    return None


def get_fit_by_name(mat_name: str, fit_name: str) -> Fit:
    """
    Description : Retrieves the fit object for a specific material and fit name.
    Args:
        mat_name (str): Material name.
        fit_name (str): Fit name.
    
    Returns:
        fit (Fit): Fit object if found, else None.
    """
    material = get_material(mat_name)
    if material:
        for fit in material.fits:
            if fit.name == fit_name:
                return fit
    return None


def get_interpolation_integral(lowT: float, highT: float, mat: str) -> float:
    """Get the integral of the interpolation function for a material.

    Args:
        lowT (float): Lower temperature bound in Kelvin.
        highT (float): Upper temperature bound in Kelvin.
        mat (str): Material name.
    Returns:
        integral (float) : Integral of the interpolation function between lowT and highT.
    """
    material = get_material(mat)
    if hasattr(material, "interpolate_function"):
        interp_func = material.interpolate_function

        T_values = np.linspace(lowT, highT, 1000)
        k_values = interp_func(T_values)
        integral = np.trapezoid(k_values, T_values)
        return integral
    else:
        raise ValueError(f"No interpolation function found for material {mat}.")
        return None


###############################################


def generate_alphabet_array(n: int) -> list:
    """
    Description : Generates a list of n letters from the alphabet (used for making the human readable txt files).
    Args:
        n (int): Number of letters to generate.
    Returns:
        alphabet (list) : List of letters.
    """
    alphabet = list(string.ascii_lowercase)
    if n >= 1:
        return alphabet[:n]
    else:
        return []


def fits_to_df(fit_list: list) -> pd.DataFrame:
    """
    Converts a list of Fit objects to a dataframe
    Args:
        fit_list (list): List of Fit objects.
    Returns:
        df (pd.DataFrame): Dataframe containing the fit information.
    """
    if not fit_list or len(fit_list) == 0:
        return None
    # list of Fit attributes to include in the dataframe
    fit_attrs = ["source", "fit_type", "range", "parameters"]
    # List of keys to serve as column headers
    list_of_alphabet = generate_alphabet_array(26)
    max_params = max(len(fit.parameters) for fit in fit_list)
    keys = ["Fit_Name", "fit_type", "Tlow", "Thigh"] + [
        list_of_alphabet[i] for i in range(max_params)
    ]

    # Create a list of dictionaries, each representing a row in the dataframe
    data = []
    for fit in fit_list:
        row = {}  # Initialize all keys with None
        for attr in fit_attrs:
            if attr == "source":
                row["Fit_Name"] = fit.name
            if attr == "fit_type":
                fit_name = str(fit.fit_type)
                row["fit_type"] = fit_name
            if attr == "range":
                row["Tlow"], row["Thigh"] = fit.range
            if attr == "parameters":
                for i, param in enumerate(fit.parameters):
                    row[list_of_alphabet[i]] = param
            # else:
            #     row[attr] = getattr(fit, attr)
        data.append(row)

    df = pd.DataFrame(data, columns=keys)
    return df


def mat_to_csv(material: Material) -> None:
    """
    Description: Converts a dataframe to a csv file
    Args:
        material (Material): Material object.
    Returns:
        None
    """
    df = fits_to_df(material.fits)
    csv_file = material.folder / f"{material.name}_fits.csv"
    df.to_csv(csv_file, index=False)
    return
