# Example file for finding the thermal loading of the components in a cryogenic stage
# Author: Henry Nachman
# Last Updated: 28 June 2024

import numpy as np
import sys, os, csv, json

from tc_tools import *
from tc_utils import *

from fit_types import *

abspath = os.path.abspath(__file__)
os.chdir(os.path.split(abspath)[0])

with open('BLASTO_TMv2.json', 'r') as stage_file:
    stage_data = json.load(stage_file)

highT = 240
lowT = 169

for component in stage_data.keys():  # Print the parsed data from the file
    mat = stage_data[component]["material"]
    tc = get_thermal_conductivity(highT, mat)
    print(f"{component} conductivity at {highT} = {tc} W/m/K")
    ConIntQuad = get_conductivity_integral(lowT, highT, mat)
    print(f"{component} conductivity integral = {ConIntQuad} W/m")
    OD = float(stage_data[component]["Dimensions"]["OD"])
    ID = float(stage_data[component]["Dimensions"]["ID"])
    area = np.pi*(0.5*(OD-ID))**2
    print(f"{component} cross sectional area = {area} m^2")
    ppu = area*ConIntQuad
    print(f"{component} power per unit = {ppu} W")
    numUnits = int(stage_data[component]["number"])
    power_total = ppu*numUnits
    print(f"{component} power total = {power_total} W")
    