import sys
import pickle
import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erf

TC_PACKAGE_DIR = Path(__file__).resolve().parent.parent / "thermal_conductivity"


def _import_sibling(module_name: str):
    """Import a module from the thermal_conductivity package via importlib, keyed
    off that package's location on disk rather than the working directory or
    sys.path. Keeps this dev tool working the same way on any OS.
    """
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(
        module_name, TC_PACKAGE_DIR / f"{module_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


material_class = _import_sibling("material_class")
Material, Fit, DataSet = material_class.Material, material_class.Fit, material_class.DataSet

fit_types = _import_sibling("fit_types")
Nppoly, polylog, loglog_func, linear_fit = (
    fit_types.Nppoly,
    fit_types.polylog,
    fit_types.loglog_func,
    fit_types.linear_fit,
)

tc_utils = _import_sibling("tc_utils")

lib_folder = TC_PACKAGE_DIR / "lib"
mat_list = [d.name for d in lib_folder.iterdir() if d.is_dir()]
# for material in mat_list:
    
#     material_of_interest = material

#     material_folder = os.path.join("lib", material_of_interest)
#     pickle_file = os.path.join(material_folder, "material.pkl")
#     if os.path.exists(pickle_file):
#         print(f"Loading {material_of_interest} from pickle")
#     # Load the material of interest from the saved pickle file
#     testmat = pickle.load(open(pickle_file, "rb"))

#     testmat.data_classes = testmat.get_data()[1]
#     # print([data.reference for data in testmat.data_classes.values()])
#     for fit in testmat.fits:
#         if hasattr(fit, 'reference'):
#             print(fit.reference)
#         else:
#             # see if the fit has NIST in its name
#             if "NIST" in fit.name:
#                 fit.add_reference("NIST Cryogenic Material Database")
#             if "data" in fit.name:
#                 fit.add_reference("Data Fit (see references for included data)")
            
#     print([fit.reference if hasattr(fit, 'reference') else None for fit in testmat.fits])

#     testmat.print_refs()

#     with open(pickle_file, "wb") as f:
#         pickle.dump(testmat, f)

for material in mat_list:
    print(material)
    # open the pickle file
    material_folder = lib_folder / material
    pickle_path = material_folder / "material.pkl"
    if material == "Cu_OFHC":
        continue
    if pickle_path.exists():
        mat = pickle.load(open(pickle_path, "rb"))
        # for fit in mat.fits:
        if mat.fit_type == "polylog" or mat.fit_type == "Nppoly":
            # print(f"{material} has polylog fit: {mat.name}")
            # mat.plot_data_fit()
            # plt.show()
            mat = mat.update_fit("polylog", 5)
            # mat.plot_data_fit()
            # plt.show()
        if mat.fit_type == 'loglog':
            print(f"{material} has loglog fit: {mat.name}")
            # mat.plot_data_fit()
            # plt.show()
            try:
                mat = mat.update_fit("loglog", None)
            except:
                print(f"Fit update failed for {material}.")
        
        with open(pickle_path, "wb") as f:
            pickle.dump(mat, f)

            # mat.plot_data_fit()
            # plt.show()