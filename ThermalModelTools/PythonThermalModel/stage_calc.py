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

from thermal_conductivity.tc_tools import *
from thermal_conductivity.tc_utils import *
from thermal_conductivity.fit_types import *

# file_name = "ExampleCryogenicStage1"

# with open(f'{file_path}{os.sep}{file_name}.json', 'r') as stage_file:
#     stage_data = json.load(stage_file)

# highT = 240
# lowT = 169

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
    tc = get_thermal_conductivity(highT, mat)
    # print(f"{component} conductivity at {highT} = {tc} W/m/K")
    ConIntQuad = get_conductivity_integral(lowT, highT, mat)

    ppu = A_L_val*ConIntQuad

    return ppu

# def get_all_powers(components, stage_details):
#     for stage, comps in components.items(): # For every stage
#         for comp, details in comps.items(): # For every component in that stage
#             # print(comp, details)
#             num = float(details["number"])
#             if "OD" in details: # If there is an "OD" tag
#                 if np.isnan(details["OD"]): # If the OD tag is NAN (i.e. it is not a standard component)
#                     power_per_part = float(details["Power per Part (W)"]) # Just take the power per part
#                 else: # If there is an OD
#                     power_per_part = calculate_power_function(details, stage_details[stage]) # calculate using the function
#                     details["Power per Part (W)"] = power_per_part
#             else: # If there are no standard components in that stage then use this
#                 power_per_part = float(details["Power per Part (W)"])
#             details["Power Total (W)"] = power_per_part*num
#     return details


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


def get_sum_variance(output_data):
    HeCap = 300 # L
    MaxFlightTime = 35*24*3600
    HeRho = 0.125 #kg/L
    HeLH = 21 #kJ/kg
    Cpgas = 5.5 # kJ/(kg*K)
    HeBP = 4.2 # K

    VCS1_Efficiency = 1
    VCS2_Efficiency = 1


    He3Load = output_data["total_power"]["4K - LHe"]
    mk300Load = output_data["total_power"]["300mK"]
    VCS1_Temp = output_data["stage_details"]["VCS 1"]["lowT"]
    VCS2_Temp = output_data["stage_details"]["VCS 2"]["lowT"]

    # print(VCS1_Temp)

    CoolingCap =HeRho*HeLH*HeCap

    MaxConsumption = CoolingCap/MaxFlightTime

    MaxLoad4K = CoolingCap/(MaxFlightTime*1000)

    # print(MaxLoad4K)

    # 3He Fridge Recycle
    heat = 30 #min
    RecyclePower = 35**2/500
    RecycleEnergy = heat*RecyclePower*60
    He3HoldTime = HeCap/mk300Load/3600


    total_average_load = He3Load + RecycleEnergy/(He3HoldTime*3600)

    loadProvidingVapor = 0.3 #Dont hardcode

    VCS1CoolingCap = cooling_power(VCS1_Temp, HeBP, loadProvidingVapor, VCS1_Efficiency)

    VCS2VaporTemp = VCS1CoolingCap/(loadProvidingVapor/(HeLH)*Cpgas)+HeBP

    VCS2CoolingCap = cooling_power(VCS2_Temp, VCS2VaporTemp, loadProvidingVapor, VCS2_Efficiency)

    SumVariance = ((VCS1CoolingCap+VCS2CoolingCap)-(output_data["total_power"]["VCS 1"]+output_data["total_power"]["VCS 2"]))**2

    return SumVariance

def cooling_power(TempOut, TempIn, Power4k, Efficiency):
    cp = 5.205453 * TempOut - 18.689101
    ci = 5.205453 * TempIn - 18.689101
    CoolingPower = (cp - ci) * Efficiency * Power4k / 21
    return CoolingPower

def optimize_tm(components, stage_details):
    # Step one - import data
    # Step two - calculate power
    # Step three - change temps
    # Step four - go back to step 2
    VCS1_temps = np.linspace(230, 260, 10)
    VCS2_temps = np.linspace(100, 200, 10)

    best_sum_var = 1e6
    sum_var_dict = {}
    for vcs1temp in VCS1_temps:
        stage_details["VCS 1"]["lowT"] = vcs1temp        
        stage_details["VCS 2"]["highT"] = vcs1temp
        for vcs2temp in VCS2_temps:
            print(f"Testing -- VCS1 :{vcs1temp}, VCS2 : {vcs2temp}")
            stage_details["VCS 2"]["lowT"] = vcs2temp
            details = get_all_powers(components, stage_details)
            output_data = {
            "components": components,
            "stage_details": stage_details,
            "total_power": {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in components.items()}
            }   
            sum_var = get_sum_variance(output_data)
            if sum_var < best_sum_var:
                best_sum_var = sum_var
                optimal_vcs = {"VCS 1":vcs1temp, "VCS 2":vcs2temp}
    stage_details["VCS 1"]["lowT"] = optimal_vcs["VCS 1"]        
    stage_details["VCS 2"]["highT"] = optimal_vcs["VCS 1"]
    stage_details["VCS 2"]["lowT"] = optimal_vcs["VCS 2"]
    details = get_all_powers(components, stage_details)
    return details, stage_details
# stage_array = []
# for component in stage_data.keys():  # Print the parsed data from the file
#     mat = stage_data[component]["material"]
#     tc = get_thermal_conductivity(highT, mat)
#     # print(f"{component} conductivity at {highT} = {tc} W/m/K")
#     ConIntQuad = get_conductivity_integral(lowT, highT, mat)
#     OD = float(stage_data[component]["Dimensions"]["OD"])
#     ID = float(stage_data[component]["Dimensions"]["ID"])
#     area = np.pi*(0.5*(OD-ID))**2
#     ppu = area*ConIntQuad    
#     numUnits = int(stage_data[component]["number"])
#     power_total = ppu*numUnits

#     component_dict = {
#         component : {
#             "conductivity integral" : ConIntQuad,
#             "area"                  : area,
#             "power per unit"        : ppu,
#             "power total"           : power_total
#         }
#     }

#     stage_array.append(component_dict)

#     # print(f"{component} \nconductivity integral = {ConIntQuad} W/m\ncross sectional area = {area} m^2\npower per unit = {ppu} W\npower total = {power_total} W")
# filename = f"{file_path}{os.sep}{file_name}_power.json"
# with open(filename, "w") as json_file:
#     json.dump(stage_array, json_file, indent=4)
#     print(f"Saved {len(stage_array)} components to {filename}")