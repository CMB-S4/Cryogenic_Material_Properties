# Example file for finding the thermal loading of the components in a cryogenic stage
# Author: Henry Nachman
# Last Updated: 28 June 2024

import numpy as np
import sys, os, csv, json
import matplotlib.pyplot as plt
import pickle

this_path = os.path.abspath(__file__)
this_dir = os.path.dirname(this_path)
cmr_path = this_dir.split("ThermalModelTools")[0]
path_to_mat_lib = os.path.join(cmr_path, "thermal_conductivity", "lib")

from astropy import units as u

if cmr_path not in sys.path:
    sys.path.append(cmr_path)
if path_to_mat_lib not in sys.path:
    sys.path.append(path_to_mat_lib)

# from thermal_conductivity.tc_tools import *
from thermal_conductivity.tc_utils import *
from thermal_conductivity.fit_types import *

def calculate_power_function(details, stage_temps, A_L = False):
    """Calculate the power function for a given component.

    Args:
        details (dict): The details of the component.
        stage_temps (dict): The temperature details of the stage.
        A_L (bool, optional): Whether to use the A/L value. Defaults to False.

    Returns:
        ppu (float): The calculated power per unit.
    """

    # lowT, highT = stage_temps["lowT"], stage_temps["highT"]
    # mat = details["Material"]
    # print(mat)
    # if not A_L:
    #     OD, ID = float(details["OD (m)"]), float(details["ID (m)"])
    #     area = np.pi*(0.5*(OD))**2 - np.pi*(0.5*(ID))**2
    #     length = details["Length (m)"]

    lowT, highT = stage_temps["lowT"], stage_temps["highT"]
    mat = details["Material"]
    if not A_L:
        OD, ID = float(details["OD (m)"]), float(details["ID (m)"])
        area = np.pi*(0.5*(OD))**2 - np.pi*(0.5*(ID))**2
        length = details["Length (m)"]
        A_L_val = area/length
    else:
        A_L_val = details["A/L (m)"]

    if "Interpolate" in details and details["Interpolate"]:
        interp_exists, valid_range, interp_func = find_interpolation(mat) # Check if interpolation file exists
        if lowT < valid_range[0] or highT > valid_range[1]:
            print(f"ERROR: Interpolation range for {mat} is {valid_range}, but requested range is {lowT} to {highT}. Using default material fit instead.")
            fits_obj = get_material_fits(mat)
            first_fit = fits_obj[0]
            ConIntQuad = first_fit.tc_integral(lowT*u.K, highT*u.K)[0].value
        else:
            ConIntQuad = get_interpolation_integral(lowT, highT, mat)
    else:
        fit_obj = get_fit_by_name(mat, details["Fit Choice"])
        ConIntQuad = fit_obj.tc_integral(lowT*u.K, highT*u.K)[0].value
    print(ConIntQuad)
    
    ppu = A_L_val*ConIntQuad

    return float(ppu)

def get_all_powers(components, stage_details):
    """Calculate the total power for all components in each stage.

    Args:
        components (dict): The component details.
        stage_details (dict): The stage temperature details.

    Returns:
        components (dict): The updated component details with power calculations.
    """
    print("CH1")
    for stage, comps in components.items(): 
        for comp, details in comps.items():
            num = float(details["Number"])
            if details.get("Type") == "Coax":
                power_per_part = calculate_coax_power(details, stage_details[stage])
                details["Power per Part (W)"] = power_per_part
    for stage, comps in components.items(): 
        for comp, details in comps.items():
            num = float(details["Number"])
            if details.get("Type") == "Coax":
                power_per_part = calculate_coax_power(details, stage_details[stage])
                details["Power per Part (W)"] = power_per_part
            elif details.get("Type") == "A/L":
                power_per_part = calculate_power_function(details, stage_details[stage], A_L=True)
                details["Power per Part (W)"] = power_per_part
            elif details.get("Type") == "Component":
                power_per_part = calculate_power_function(details, stage_details[stage])
                details["Power per Part (W)"] = power_per_part
            else:
                power_per_part = float(details["Power per Part (W)"])
            details["Power Total (W)"] = float(power_per_part * num)
    
    return components


def calculate_coax_power(details, stage_temp):
    """Calculate the power for coaxial components.

    Args:
        details (dict): The details of the coaxial component.
        stage_temp (dict): The temperature details of the stage.

    Returns:
        power_per_part (float): The calculated power per part for the coaxial component.
    """
    # Implement the power calculation logic for Coax components here
    # Example placeholder logic:
    case_details = {"Material" : details["Casing Material"], "OD (m)" : details["Case OD (m)"], "ID (m)" : details["Insulator OD (m)"], "Length (m)" : details["Length (m)"], "Fit Choice": details["Casing Fit Choice"], "Interpolate": details["Casing Interpolate"]}
    case_ppp = calculate_power_function(case_details, stage_temp)

    insulator_details = {"Material" : details["Insulator Material"], "OD (m)" : details["Insulator OD (m)"], "ID (m)" : details["Core OD (m)"], "Length (m)" : details["Length (m)"], "Fit Choice": details["Insulator Fit Choice"], "Interpolate": details["Insulator Interpolate"]}
    insulator_ppp = calculate_power_function(insulator_details, stage_temp)
    # Implement the power calculation logic for Coax components here
    # Example placeholder logic:
    case_details = {"Material" : details["Casing Material"], "OD (m)" : details["Case OD (m)"], "ID (m)" : details["Insulator OD (m)"], "Length (m)" : details["Length (m)"], "Fit Choice": details["Casing Fit Choice"], "Interpolate": details["Casing Interpolate"]}
    case_ppp = calculate_power_function(case_details, stage_temp)

    insulator_details = {"Material" : details["Insulator Material"], "OD (m)" : details["Insulator OD (m)"], "ID (m)" : details["Core OD (m)"], "Length (m)" : details["Length (m)"], "Fit Choice": details["Insulator Fit Choice"], "Interpolate": details["Insulator Interpolate"]}
    insulator_ppp = calculate_power_function(insulator_details, stage_temp)

    core_details = {"Material" : details["Core Material"], "OD (m)" : details["Core OD (m)"], "ID (m)" : 0, "Length (m)" : details["Length (m)"], "Fit Choice": details["Core Fit Choice"], "Interpolate": details["Core Interpolate"]}
    core_ppp = calculate_power_function(core_details, stage_temp)

    power_per_part = case_ppp + insulator_ppp + core_ppp


    return power_per_part


def get_sum_variance(output_data):
    """Calculate the sum variance for the output data.

    Args:
        output_data (dict): The output data containing stage details and total power.

    Returns:
        SumVariance: The calculated sum variance for each stage.
        cooling_details_dict: A dictionary containing cooling details.
    """
    HeCap = 300 # L
    FridgeCap = 6 #J
    MaxFlightTime = 35*24*3600
    HeRho = 0.125 #kg/L
    HeLH = 21 #kJ/kg
    Cpgas = 5.5 # kJ/(kg*K)
    HeBP = 4.2 # K
    HeCap = 300 # L
    FridgeCap = 6 #J
    MaxFlightTime = 35*24*3600
    HeRho = 0.125 #kg/L
    HeLH = 21 #kJ/kg
    Cpgas = 5.5 # kJ/(kg*K)
    HeBP = 4.2 # K

    VCS1_Efficiency = 1
    VCS2_Efficiency = 1

    He3Load = output_data["total_power"]["4K - LHe"] + output_data["total_power"]["4K - Transient"]
    mk300Load = output_data["total_power"]["300mK"]
    VCS1_Temp = output_data["stage_details"]["VCS 1"]["lowT"]
    VCS2_Temp = output_data["stage_details"]["VCS 2"]["lowT"]
    # CoolingCap =HeRho*HeLH*HeCap
    # MaxConsumption = CoolingCap/MaxFlightTime
    # MaxLoad4K = CoolingCap/(MaxFlightTime*1000)

    # 3He Fridge Recycle
    heat = 30*60 #min * sec/min = sec
    RecyclePower = 35**2/500
    RecycleEnergy = heat*RecyclePower
    He3HoldTime = (FridgeCap/mk300Load)/3600

    total_average_load = He3Load + RecycleEnergy/(He3HoldTime*3600)
    # if "LNA" in output_data["components"]["4K - Transient"].keys() and "Motor Axles" in output_data["components"]["4K - Transient"].keys():
    #     loadProvidingVapor = output_data["total_power"]["4K - LHe"] + output_data["components"]["4K - Transient"]["LNA"]["Power Total (W)"] + output_data["components"]["4K - Transient"]["Motor Axles"]["Power Total (W)"]
    # else:
    #     loadProvidingVapor = output_data["total_power"]["4K - LHe"] + output_data["total_power"]["4K - Transient"]

    loadProvidingVapor = 0.0
    for comp_name, comp_details in output_data["components"]["4K - LHe"].items():
        if "Providing Vapor" in comp_details and comp_details["Providing Vapor"]:
            if comp_details.get("Providing Vapor", False):
                loadProvidingVapor += comp_details.get("Power Total (W)", 0.0)
    for comp_name, comp_details in output_data["components"]["4K - Transient"].items():
        if "Providing Vapor" in comp_details and comp_details["Providing Vapor"]:
            if comp_details.get("Providing Vapor", False):
                loadProvidingVapor += comp_details.get("Power Total (W)", 0.0)
    print(f"Load Providing Vapor: {loadProvidingVapor} W")
        
    
    LitersPCycle = (total_average_load*He3HoldTime*3.6)/(HeRho*HeLH)
    NumCycles = HeCap/LitersPCycle
    CryoHoldTime = NumCycles*He3HoldTime

    
    VCS1CoolingCap = cooling_power(VCS1_Temp, HeBP, loadProvidingVapor, VCS1_Efficiency)
    VCS2VaporTemp = VCS1CoolingCap/(loadProvidingVapor/(HeLH)*Cpgas)+HeBP
    VCS2CoolingCap = cooling_power(VCS2_Temp, VCS2VaporTemp, loadProvidingVapor, VCS2_Efficiency)
    # SumVariance = ((VCS1CoolingCap+VCS2CoolingCap)-(output_data["total_power"]["VCS 1"]+output_data["total_power"]["VCS 2"]))**2
    SumVariance = ((VCS1CoolingCap-output_data["total_power"]["VCS 1"])**2 + (VCS2CoolingCap-output_data["total_power"]["VCS 2"])**2)**(1/2)
    cooling_details_dict = {
        "He3Cap"                : [HeCap, "L"],
        "Total Average Load"    : [total_average_load, "W"],
        "Load Providing Vapor"  : [loadProvidingVapor, "W"],
        "VCS1 Cooling Capacity" : [VCS1CoolingCap, "W"],
        "VCS2 Vapor Temp"       : [VCS2VaporTemp, "K"],
        "VCS2 Cooling Capacity" : [VCS2CoolingCap, "W"],
        "Fridge Hold Time"      : [He3HoldTime, "hrs"],
        "Cryo Hold Time"        : [CryoHoldTime/24, "days"],
    }

    # units_dict = {
    #     "He3Cap" : "L",
    #     "Total Average Load" : "W",
    #     "Load Providing Vapor" : "W",
    #     "VCS1 Cooling Capacity" : "W",
    #     "VCS2 Vapor Temp" : "K",
    #     "VCS2 Cooling Capacity" : "W",
    #     "He3 Hold Time" : "hrs",        
    #     "Cryo Hold Time" : "days",
    # }

    return SumVariance, cooling_details_dict

def cooling_power(TempOut, TempIn, Power4k, Efficiency):
    """Calculate the cooling power based on the temperatures and efficiency.
    Args:
        TempOut (float): The output temperature.
        TempIn (float): The input temperature.
        Power4k (float): The power at 4K.
        Efficiency (float): The efficiency of the cooling system.
    Returns:
        CoolingPower  (float): The calculated cooling power.
    """
    cp = 5.205453 * TempOut - 18.689101
    ci = 5.205453 * TempIn - 18.689101
    CoolingPower = (cp - ci) * Efficiency * Power4k / 21
    return CoolingPower

def optimize_tm(components_input, stage_details_input, num_points=10):
    """
    Optimizes a VCS cooled thermal model
    Takes in components dictionary and stage details dictionary
    Args:
        components_input (dict): The input component details.
        stage_details_input (dict): The input stage details.
        num_points (int): The number of points to sample for VCS temperatures.
    Returns:
        details (dict): The updated component details with power calculations.
        output_data (dict): The output data containing stage details and total power.
        grids (list): A list containing the VCS2 grid, VCS1 grid, and SumVarArr.

    """
    # Step one - import data
    # Step two - calculate power
    # Step three - change temps
    # Step four - go back to step 2
    VCS2_temps = np.linspace(100, 260, num_points)
    VCS1_temps = np.linspace(5, 100, num_points)
    VCS2_grid, VCS1_grid = np.meshgrid(VCS2_temps, VCS1_temps) 
    SumVarArr = np.zeros_like(VCS2_grid)
    best_sum_var = 1e6
    # sum_var_dict = {}
    # hold_time_arr = []
    stage_details = stage_details_input.copy()
    components = components_input.copy()
    i = 0
    for vcs2temp in VCS2_temps:
        j = 0
        stage_details["VCS 2"]["lowT"] = vcs2temp        
        stage_details["VCS 1"]["highT"] = vcs2temp
        for vcs1temp in VCS1_temps:
            stage_details["VCS 1"]["lowT"] = vcs1temp
            stage_details["4K - LHe"]["highT"] = vcs1temp # Update the 4K LHe stage high temp to match VCS2 low temp
            details = get_all_powers(components, stage_details)
            stage_total_power = {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in details.items()}
            output_data = {
            "components": components,
            "stage_details": stage_details,
            "total_power": stage_total_power
            }
            sum_var, cooling_dict = get_sum_variance(output_data)
            SumVarArr[i, j] = sum_var
            # hold_time_arr = np.append(hold_time_arr, cooling_dict["Cryo Hold Time"])
            if sum_var < best_sum_var:
                best_sum_var = sum_var
                optimal_vcs = {"VCS 2":vcs2temp, "VCS 1":vcs1temp}
            j += 1
        i += 1
    stage_details["VCS 2"]["lowT"] = optimal_vcs["VCS 2"]        
    stage_details["VCS 1"]["highT"] = optimal_vcs["VCS 2"]
    stage_details["VCS 1"]["lowT"] = optimal_vcs["VCS 1"]
    stage_details["4K - LHe"]["highT"] = optimal_vcs["VCS 1"] # Update the 4K LHe stage high temp to match VCS2 low temp
    details = get_all_powers(components, stage_details)

    stage_total_power = {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in details.items()}
    output_data = {
        "components": components,
        "stage_details": stage_details,
        "total_power": stage_total_power
        }

    return details, output_data, [VCS2_grid, VCS1_grid, SumVarArr]


def save_to_json_manual(components, stage_details):
    """Save the components and stage details to a JSON file.
    Args:
        components (dict): The component details.
        stage_details (dict): The stage temperature details.
    Returns:
        output_data (dict): A dictionary containing the components, stage details, and total power.
    """
    # Include stage details and total power in the JSON data
    output_data = {
        "components": components,
        "stage_details": stage_details,
        "total_power": {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in components.items()}
    }
    return output_data # dict(content=json.dumps(output_data, indent=4), filename="components.json")


def find_interpolation(material):
    """Check if an interpolation file exists for the given material.

    Args:
        material (str): The name of the material to check.  

    Returns:
        bool: True if the interpolation file exists, False otherwise.
    """
    # Load the material object from the specified path
    mat_file = os.path.join(path_to_mat_lib, material, "material.pkl")
    with open(mat_file, 'rb') as f:
        mat = pickle.load(f)
    if hasattr(mat, 'interpolate_function'):
        interp_func = mat.interpolate_function
        if interp_func is None:
            return False, None, None
        # interp_func = get_interpolation(os.path.join(path_to_mat_lib, material))
        valid_range = [round(float(interp_func.x[0]), 2), round(float(interp_func.x[-1]), 2)]
        return True, valid_range, interp_func
    else:
        return False, None, None
    
def load_thermal_model(json_path):
    with open(json_path, 'r') as f:
        thermal_model = json.load(f)
    return thermal_model