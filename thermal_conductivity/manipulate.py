from material_class import Material, Fit, DataSet
import matplotlib.pyplot as plt
import numpy as np
import pickle, os

from scipy.special import erf

from fit_types import Nppoly, polylog, loglog_func, linear_fit
from tc_utils import *

lib_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
mat_list = [d for d in os.listdir(lib_folder) if os.path.isdir(os.path.join(lib_folder, d))]
for material in mat_list:
    
    material_of_interest = material

    material_folder = os.path.join("lib", material_of_interest)
    pickle_file = os.path.join(material_folder, "material.pkl")
    if os.path.exists(pickle_file):
        print(f"Loading {material_of_interest} from pickle")
    # Load the material of interest from the saved pickle file
    testmat = pickle.load(open(pickle_file, "rb"))

    testmat.data_classes = testmat.get_data()[1]
    # print([data.reference for data in testmat.data_classes.values()])
    for fit in testmat.fits:
        if hasattr(fit, 'reference'):
            print(fit.reference)
        else:
            # see if the fit has NIST in its name
            if "NIST" in fit.name:
                fit.add_reference("NIST Cryogenic Material Database")
            if "data" in fit.name:
                fit.add_reference("Data Fit (see references for included data)")
            
    print([fit.reference if hasattr(fit, 'reference') else None for fit in testmat.fits])

    testmat.print_refs()

    with open(pickle_file, "wb") as f:
        pickle.dump(testmat, f)