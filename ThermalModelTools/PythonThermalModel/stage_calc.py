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

file_name = "ExampleCryogenicStage1"

with open(f'{file_path}{os.sep}{file_name}.json', 'r') as stage_file:
    stage_data = json.load(stage_file)

highT = 240
lowT = 169

stage_array = []
for component in stage_data.keys():  # Print the parsed data from the file
    mat = stage_data[component]["material"]
    tc = get_thermal_conductivity(highT, mat)
    # print(f"{component} conductivity at {highT} = {tc} W/m/K")
    ConIntQuad = get_conductivity_integral(lowT, highT, mat)
    OD = float(stage_data[component]["Dimensions"]["OD"])
    ID = float(stage_data[component]["Dimensions"]["ID"])
    area = np.pi*(0.5*(OD-ID))**2
    ppu = area*ConIntQuad    
    numUnits = int(stage_data[component]["number"])
    power_total = ppu*numUnits

    component_dict = {
        component : {
            "conductivity integral" : ConIntQuad,
            "area"                  : area,
            "power per unit"        : ppu,
            "power total"           : power_total
        }
    }

    stage_array.append(component_dict)

    # print(f"{component} \nconductivity integral = {ConIntQuad} W/m\ncross sectional area = {area} m^2\npower per unit = {ppu} W\npower total = {power_total} W")
filename = f"{file_path}{os.sep}{file_name}_power.json"
with open(filename, "w") as json_file:
    json.dump(stage_array, json_file, indent=4)
    print(f"Saved {len(stage_array)} components to {filename}")