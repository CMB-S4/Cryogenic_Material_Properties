# Example file for finding the thermal loading of the components in a cryogenic stage
# Author: Henry Nachman
# Last Updated: 28 June 2024

import numpy as np
import sys, os, csv, json

abspath = os.path.abspath(__file__)
file_path = os.path.split(abspath)[0]
sys.path.insert(0, f"{file_path}{os.sep}..{os.sep}..{os.sep}")

# sys.path.append(f"{os.path.split(abspath)[0]}{os.sep}..{os.sep}..")
# sys.path.append(f"{os.path.split(abspath)[0]}{os.sep}..{os.sep}..{os.sep}thermal_conductivity")

git_repo_path = f"{file_path}{os.sep}..{os.sep}..{os.sep}"
from thermal_conductivity.tc_tools import *
from thermal_conductivity.tc_utils import *
from thermal_conductivity.fit_types import *

def calculate_power_function(details, stage_temps, A_L = False):
    lowT, highT = stage_temps["lowT"], stage_temps["highT"]
    mat = details["material"]
    if not A_L:
        OD, ID = float(details["OD"]), float(details["ID"])
        area = np.pi*(0.5*(OD))**2 - np.pi*(0.5*(ID))**2
        length = details["length"]
        A_L_val = area/length
    else:
        A_L_val = details["A/L"]
    ConIntQuad = get_conductivity_integral(lowT, highT, mat, verbose=False)
    
    ppu = A_L_val*ConIntQuad

    return ppu

def get_all_powers(components, stage_details):
    for stage, comps in components.items(): 
        for comp, details in comps.items():
            num = float(details["number"])
            if details.get("Type") == "Coax":
                power_per_part = calculate_coax_power(details, stage_details[stage])
                details["Power per Part (W)"] = power_per_part
            elif details.get("Type") == "A/L":
                power_per_part = calculate_power_function(details, stage_details[stage], A_L=True)
                details["Power per Part (W)"] = power_per_part
            elif "OD" in details:
                power_per_part = calculate_power_function(details, stage_details[stage])
                details["Power per Part (W)"] = power_per_part
            else:
                power_per_part = float(details["Power per Part (W)"])
            details["Power Total (W)"] = power_per_part * num
    
    return components


def calculate_coax_power(details, stage_temp):
    # Implement the power calculation logic for Coax components here
    # Example placeholder logic:
    case_details = {"material" : details["mat_C"], "OD" : details["OD"], "ID" : details["OD_I"], "length" : details["length"]}
    case_ppp = calculate_power_function(case_details, stage_temp)
    
    insulator_details = {"material" : details["mat_I"], "OD" : details["OD_I"], "ID" : details["OD_c"], "length" : details["length"]}
    insulator_ppp = calculate_power_function(insulator_details, stage_temp)
    
    core_details = {"material" : details["material"], "OD" : details["OD_c"], "ID" : 0, "length" : details["length"]}
    core_ppp = calculate_power_function(core_details, stage_temp)

    power_per_part = case_ppp + insulator_ppp + core_ppp


    return power_per_part
