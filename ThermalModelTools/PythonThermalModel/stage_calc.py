# Example file for finding the thermal loading of the components in a cryogenic stage
# Author: Henry Nachman
# Last Updated: 28 June 2024

import numpy as np
import sys, os, csv, json
import matplotlib.pyplot as plt

abspath = os.path.abspath(__file__)
file_path = os.path.split(abspath)[0]
sys.path.insert(0, f"{file_path}{os.sep}..{os.sep}..{os.sep}")

# sys.path.append(f"{os.path.split(abspath)[0]}{os.sep}..{os.sep}..")
# sys.path.append(f"{os.path.split(abspath)[0]}{os.sep}..{os.sep}..{os.sep}thermal_conductivity")
path_to_Onedrive = abspath.split("OneDrive")[0]
git_repo_path = f"{path_to_Onedrive}{os.sep}OneDrive - The University of Texas at Austin{os.sep}01_RESEARCH{os.sep}05_CMBS4{os.sep}Cryogenic_Material_Properties"
sys.path.insert(0, git_repo_path)
from thermal_conductivity.tc_tools import *
from thermal_conductivity.tc_utils import *
from thermal_conductivity.fit_types import *

def calculate_power_function(details, stage_temps, A_L = False):

    lowT, highT = stage_temps["lowT"], stage_temps["highT"]
    # print("Calculate Power Function for details:", details, "with stage temps:", stage_temps, "lowT:", lowT, "highT:", highT)
    mat = details["Material"]
    if not A_L:
        OD, ID = float(details["OD (m)"]), float(details["ID (m)"])
        area = np.pi*(0.5*(OD))**2 - np.pi*(0.5*(ID))**2
        length = details["Length (m)"]
        A_L_val = area/length
    else:
        A_L_val = details["A/L (m)"]
    ConIntQuad = get_conductivity_integral(lowT, highT, mat, verbose=False)
    
    ppu = A_L_val*ConIntQuad

    return float(ppu)

def get_all_powers(components, stage_details):
    # print("\nGet All Powers Stage Details", stage_details)
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
            # print(f"\nComponent Power Calc, {comp} in {stage} with stage temps {stage_details[stage]} -- Power per Part: {power_per_part} W, Number: {num}")
            details["Power Total (W)"] = float(power_per_part * num)
    
    return components


def calculate_coax_power(details, stage_temp):
    # Implement the power calculation logic for Coax components here
    # Example placeholder logic:
    case_details = {"Material" : details["Casing Material"], "OD (m)" : details["Case OD (m)"], "ID (m)" : details["Insulator OD (m)"], "Length (m)" : details["Length (m)"]}
    case_ppp = calculate_power_function(case_details, stage_temp)
    
    insulator_details = {"Material" : details["Insulator Material"], "OD (m)" : details["Insulator OD (m)"], "ID (m)" : details["Core OD (m)"], "Length (m)" : details["Length (m)"]}
    insulator_ppp = calculate_power_function(insulator_details, stage_temp)
    
    core_details = {"Material" : details["Core Material"], "OD (m)" : details["Core OD (m)"], "ID (m)" : 0, "Length (m)" : details["Length (m)"]}
    core_ppp = calculate_power_function(core_details, stage_temp)

    power_per_part = case_ppp + insulator_ppp + core_ppp


    return power_per_part


def get_sum_variance(output_data):
    # print(f"\nSUM VARIANCE OUTPUT DATA : {output_data['stage_details']}")#, output_data["total_power"])
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
    if "LNA" in output_data["components"]["4K - Transient"].keys() and "Motor Axles" in output_data["components"]["4K - Transient"].keys():
        loadProvidingVapor = output_data["total_power"]["4K - LHe"] + output_data["components"]["4K - Transient"]["LNA"]["Power Total (W)"] + output_data["components"]["4K - Transient"]["Motor Axles"]["Power Total (W)"]
    else:
        loadProvidingVapor = output_data["total_power"]["4K - LHe"] + output_data["total_power"]["4K - Transient"]
        
    
    LitersPCycle = (total_average_load*He3HoldTime*3.6)/(HeRho*HeLH)
    NumCycles = HeCap/LitersPCycle
    CryoHoldTime = NumCycles*He3HoldTime

    
    VCS1CoolingCap = cooling_power(VCS1_Temp, HeBP, loadProvidingVapor, VCS1_Efficiency)
    VCS2VaporTemp = VCS1CoolingCap/(loadProvidingVapor/(HeLH)*Cpgas)+HeBP
    VCS2CoolingCap = cooling_power(VCS2_Temp, VCS2VaporTemp, loadProvidingVapor, VCS2_Efficiency)
    SumVariance = ((VCS1CoolingCap+VCS2CoolingCap)-(output_data["total_power"]["VCS 1"]+output_data["total_power"]["VCS 2"]))**2

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
    cp = 5.205453 * TempOut - 18.689101
    ci = 5.205453 * TempIn - 18.689101
    CoolingPower = (cp - ci) * Efficiency * Power4k / 21
    return CoolingPower

def optimize_tm(components_input, stage_details_input, num_points=10):
    """
    Optimizes a VCS cooled thermal model
    Takes in components dictionary and stage details dictionary
    """
    # Step one - import data
    # Step two - calculate power
    # Step three - change temps
    # Step four - go back to step 2
    VCS2_temps = np.linspace(200, 260, num_points)
    VCS1_temps = np.linspace(25, 200, num_points)
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
        # print(f"\nOld Stage Details {stage_details}")
        # print("\nInitial powers", {stage: {comp: details["Power Total (W)"] for comp, details in comps.items()} for stage, comps in components.items()})
        stage_details["VCS 2"]["lowT"] = vcs2temp        
        stage_details["VCS 1"]["highT"] = vcs2temp
        for vcs1temp in VCS1_temps:
            stage_details["VCS 1"]["lowT"] = vcs1temp
            stage_details["4K - LHe"]["highT"] = vcs1temp # Update the 4K LHe stage high temp to match VCS2 low temp
            # print(f"\nOld powers", {stage: {comp: details["Power Total (W)"] for comp, details in comps.items()} for stage, comps in components.items()})
            # print("\nNew Stage Details", stage_details)
            details = get_all_powers(components, stage_details)
            # print("\nNew powers", {stage: {comp: det["Power Total (W)"] for comp, det in comps.items()} for stage, comps in details.items()})
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
                # print(f"SUM VARIANCE : {sum_var}, BEST : {best_sum_var}")
                optimal_vcs = {"VCS 2":vcs2temp, "VCS 1":vcs1temp}
            # print(f"Testing -- VCS1 :{vcs1temp}, VCS2 : {vcs2temp}, \nSum Variance : {sum_var}\nHoldTime : {cooling_dict['Cryo Hold Time']}")
            # print(f"Sum Variance : {sum_var}")
            j += 1
        i += 1
    stage_details["VCS 2"]["lowT"] = optimal_vcs["VCS 2"]        
    stage_details["VCS 1"]["highT"] = optimal_vcs["VCS 2"]
    stage_details["VCS 1"]["lowT"] = optimal_vcs["VCS 1"]
    stage_details["4K - LHe"]["highT"] = optimal_vcs["VCS 1"] # Update the 4K LHe stage high temp to match VCS2 low temp
    print("RESULTS OF OPTIMIZATION", optimal_vcs)
    details = get_all_powers(components, stage_details)

    stage_total_power = {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in details.items()}
    output_data = {
        "components": components,
        "stage_details": stage_details,
        "total_power": stage_total_power
        }

    return details, output_data, [VCS2_grid, VCS1_grid, SumVarArr]


def save_to_json_manual(components, stage_details):
    # Include stage details and total power in the JSON data
    output_data = {
        "components": components,
        "stage_details": stage_details,
        "total_power": {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in components.items()}
    }
    return output_data # dict(content=json.dumps(output_data, indent=4), filename="components.json")


def plot_integral(selected_component, stage):
    """
    Description:
    This function plots the thermal conductivity of a selected component over the temperature range defined by the stage.

    Arguments:
    selected_component : The component whose thermal conductivity is to be plotted.
    stage              : The stage object containing temperature information.

    Returns:
    fig, ax : The figure and axis objects for the plot.
    """
    all_files       = os.listdir(git_repo_path)
    exist_files     = [file for file in all_files if file.startswith("tc_fullrepo")]
    tc_file_date    = exist_files[0][-12:-4]

    TCdata = np.loadtxt(f"{git_repo_path}{os.sep}tc_fullrepo_{tc_file_date}.csv", dtype=str, delimiter=',') # imports compilation file csv
    material_of_interest = selected_component.properties["Material"]
    mat_parameters = get_parameters(TCdata, material_of_interest)
    func_type = get_func_type(mat_parameters["fit_type"])
    print(func_type)
    fit_range = mat_parameters["fit_range"]

    # Let's make our plotting range the listed fit range
    T_range = np.linspace(fit_range[0], fit_range[1], 1000)

    # Now let's use the fit to get the thermal conductivity values over the range
    # Luckily, every function type is defined in such a way to readily accept the parameter dictionary as it was defined above
    y_vals = func_type(T_range, mat_parameters)
    T_low, T_high = [stage.low_temp, stage.high_temp]

    # Plotting
    fill_between_range = np.arange(T_low, T_high)
    fig, ax = plt.subplots()
    ax.plot(T_range, y_vals, color="b")
    ax.fill_between(fill_between_range, np.zeros(len(fill_between_range)), func_type(fill_between_range, mat_parameters),
                    hatch="////", alpha = 0.5, edgecolor = 'b', facecolor="w",
                    label="Integration Area")
    ax.semilogy()
    ax.semilogx()
    ax.legend()
    ax.set_title(f"Plot of  {selected_component.name}")
    ax.set_xlabel("T [K]")
    ax.set_ylabel("Thermal Conductivity : k [W/m/K]")
    return fig, ax