import streamlit as st
from components.component import Component
from stages.stage import Stage
import random, os, sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as c
import json, pickle
import numpy as np
from stage_calc import *
import plotly.express as px
import logging
import matplotlib as mpl

from streamlit_extras.stylable_container import stylable_container
from plotting import *

# Define Paths

abspath = os.path.abspath(__file__)
file_path = os.path.dirname(abspath)
cmr_path = file_path.split("ThermalModelTools")[0]
path_to_mat_lib = os.path.join(cmr_path, "thermal_conductivity", "lib")
if cmr_path not in sys.path:
    sys.path.append(cmr_path)
if path_to_mat_lib not in sys.path:
    sys.path.append(path_to_mat_lib)

def default_page_load():
    st.set_page_config("Interactive Thermal Model GUI", page_icon=":thermometer:", layout="wide")
    HORIZONTAL_RED = f"{file_path}{os.sep}static{os.sep}blast-logo.png"
    ICON_RED = f"{file_path}{os.sep}static{os.sep}blast-logo.png"
    st.logo(HORIZONTAL_RED, icon_image=ICON_RED)
    
default_page_load()


if not os.path.exists(cmr_path):
    print(f"ERROR : path to cryogenics materials properties repository is not found {cmr_path}")
    exit()


mat_list = [folder for folder in os.listdir(path_to_mat_lib) if os.path.isdir(os.path.join(path_to_mat_lib, folder))]
mat_list.sort()

# # Function to generate a random color
def random_color(value = 200):
    cmap = plt.cm.get_cmap('Blues')  # You can choose any colormap you like
    return c.to_hex(cmap(370/value))

def get_color():
    if True: #st.context.theme.type == 'light':
        return "#f7f7ff" #"#fff5f5"
    else:
        return "#271d42" # "#4d3e2b"
def get_dark_color():
    return "#6d6bff" #"#ffa1a1"

# Initialize stages and components
if 'main_stage' not in st.session_state:
    st.session_state.main_stage = [] # Stage("Stage 1", high_temp=270.0, low_temp=60.0, color=get_color())

# st.write("Session State:", st.session_state)
# Initialize session state
if 'editing_stage_properties' not in st.session_state:
    st.session_state.editing_stage_properties = {}

if 'optimize_clicked' not in st.session_state:
    st.session_state.optimize_clicked = False

if 'optimized' not in st.session_state:
    st.session_state.optimized = False

if st.session_state.main_stage == []:
    st.session_state.stages_exist = False
else:
    st.session_state.stages_exist = True
# Include custom CSS
with open(f"{file_path}{os.sep}static{os.sep}styles.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Streamlit app
title_area, logo_area = st.columns(2)
title_area.title("Interactive Thermal Model GUI")
logo_area.image(f"{file_path}{os.sep}static{os.sep}blast-logo.png", width=200)  # Display the logo in the main body

tabs = st.tabs(["Component Modeling", "Result Tables", "Plots", "Quick Calc", "About"])


# Main Page Content
with tabs[0]:
    
    # Sidebar for input fields and buttons
    st.sidebar.header("Add Components and Stages")


   
    
    # Select the type of component you want to add
    
    def get_material_fit_names(mat_name):
        # Load the material class from the material pkl file
        with open(os.path.join(path_to_mat_lib, mat_name, f"material.pkl"), 'rb') as f:
            material_obj = pickle.load(f)
        fits_list = [fit.name for fit in material_obj.fits]
        all_fits_file = os.path.join(path_to_mat_lib, mat_name, f"{mat_name}_fits.csv")
        
        return fits_list
        
              
    def sidebar_inputs():
        if st.session_state.main_stage == []:
            st.sidebar.warning("Please add a stage to begin")
            selected_comp_type = "Stage"
                    # Input field for naming the component or stage
            name = st.sidebar.text_input("Name")

            ############################################################
            ############################################################

            # If adding a stage, add T2 temperature
            if selected_comp_type == "Stage":
                low_temp = st.sidebar.number_input("Low Temperature (°K)", key="LowTemp", value=25.0, format="%.1f")
                high_temp = st.sidebar.number_input("High Temperature (°K)", key="HighTemp", value=270.0, format="%.1f")

        else:
            # Select a stage to add the component to
            selected_stage_name = st.sidebar.selectbox("Select Stage to Add Component",
                                                    [st.session_state.main_stage.name] + [stage.name for stage in st.session_state.main_stage.stages])
            component_type_list = ["Stage", "Standard", "A/L", "Coax", "Power per Part"]
            selected_comp_type = st.sidebar.selectbox("Select Component Type", component_type_list)
        
            # Input field for naming the component or stage
            name = st.sidebar.text_input("Name")

            ############################################################
            ############################################################

            # If adding a stage, add T2 temperature
            if selected_comp_type == "Stage":
                low_temp = st.sidebar.number_input("Low Temperature (°K)", key="LowTemp", value=25.0, format="%.1f")
                high_temp = st.sidebar.number_input("High Temperature (°K)", key="HighTemp", value=270.0, format="%.1f")
            
            # Dictionary to hold component properties
            component_properties = {}

            if selected_comp_type == "Standard":
                # Add input fields for Standard component properties
                component_properties["Type"] = "Standard"
                component_properties["Material"] = st.sidebar.selectbox("Material", mat_list)
                has_interpolation, valid_range, interp_func = find_interpolation(component_properties["Material"]) # Searches for interpolation file, returns True if it exists
                if has_interpolation: # If interpolation file exists
                    component_properties["Interpolate"] = st.sidebar.checkbox(f"Use Interpolation in range :\n{valid_range[0]} K - {valid_range[1]} K", value=True) # Provide checkbox to use interpolation
                if not component_properties["Interpolate"]: # If interpolation is not selected, search for available fits
                    component_properties["Fit Choice"] = st.sidebar.selectbox("Fit Choice", get_material_fit_names(component_properties["Material"]))
                else:
                    component_properties["Fit Choice"] = None
                component_properties["OD (m)"] = st.sidebar.number_input("OD (m)", value=0.0, format="%.3f")
                component_properties["ID (m)"] = st.sidebar.number_input("ID (m)", value=0.0, format="%.3f")
                component_properties["Length (m)"] = st.sidebar.number_input("Length (m)", value=0.0, format="%.3f")
                component_properties["Number"] = st.sidebar.number_input("Number", value=1, format="%d")

            if selected_comp_type == "A/L":
                # Add input fields for A/L component properties
                component_properties["Type"] = "A/L"
                component_properties["Material"] = st.sidebar.selectbox("Material", mat_list)
                has_interpolation, valid_range , interp_func = find_interpolation(component_properties["Material"]) # Searches for interpolation file, returns True if it exists
                if has_interpolation: # If interpolation file exists
                    component_properties["Interpolate"] = st.sidebar.checkbox(f"Use Interpolation in range :\n{valid_range[0]} K - {valid_range[1]} K", value=True) # Provide checkbox to use interpolation
                if not component_properties["Interpolate"]: # If interpolation is not selected, search for available fits
                    component_properties["Fit Choice"] = st.sidebar.selectbox("Fit Choice", get_material_fit_names(component_properties["Material"]))
                else:
                    component_properties["Fit Choice"] = None
                component_properties["A/L (m)"] = st.sidebar.number_input("A/L (m)", value=0.0, format="%.3f")
                component_properties["Length (m)"] = st.sidebar.number_input("Length (m)", value=0.0, format="%.3f")
                component_properties["Number"] = st.sidebar.number_input("Number", value=1, format="%d")

            if selected_comp_type == "Coax":
                # Add input fields for Coax component properties
                component_properties["Type"] = "Coax"
                component_properties["Casing Material"] = st.sidebar.selectbox("Casing Material", mat_list)
                has_interpolation, valid_range , interp_func = find_interpolation(component_properties["Casing Material"]) # Searches for interpolation file, returns True if it exists
                if has_interpolation: # If interpolation file exists
                    component_properties["Casing Interpolate"] = st.sidebar.checkbox(f"Use Interpolation for Casing material in range :\n{valid_range[0]} K - {valid_range[1]} K", value=True) # Provide checkbox to use interpolation
                else:
                    component_properties["Casing Interpolate"] = False
                if not component_properties["Casing Interpolate"]: # If interpolation is not selected, search for available fits
                    component_properties["Casing Fit Choice"] = st.sidebar.selectbox("Fit Choice", get_material_fit_names(component_properties["Casing Material"]))
                else:
                    component_properties["Casing Fit Choice"] = None

                component_properties["Insulator Material"] = st.sidebar.selectbox("Insulator Material", mat_list)
                has_interpolation, valid_range , interp_func = find_interpolation(component_properties["Insulator Material"]) # Searches for interpolation file, returns True if it exists
                if has_interpolation: # If interpolation file exists
                    component_properties["Insulator Interpolate"] = st.sidebar.checkbox(f"Use Interpolation for Insulator material in range :\n{valid_range[0]} K - {valid_range[1]} K", value=True) # Provide checkbox to use interpolation
                else:
                    component_properties["Insulator Interpolate"] = False
                if not component_properties["Insulator Interpolate"]: # If interpolation is not selected, search for available fits
                    component_properties["Insulator Fit Choice"] = st.sidebar.selectbox("Fit Choice", get_material_fit_names(component_properties["Insulator Material"]))
                else:
                    component_properties["Insulator Fit Choice"] = None

                component_properties["Core Material"] = st.sidebar.selectbox("Core Material", mat_list)
                has_interpolation, valid_range, interp_func = find_interpolation(component_properties["Core Material"]) # Searches for interpolation file, returns True if it exists
                if has_interpolation: # If interpolation file exists
                    component_properties["Core Interpolate"] = st.sidebar.checkbox(f"Use Interpolation for Core material in range :\n{valid_range[0]} K - {valid_range[1]} K", value=True) # Provide checkbox to use interpolation
                else:
                    component_properties["Core Interpolate"] = False
                if not component_properties["Core Interpolate"]: # If interpolation is not selected, search for available fits
                    component_properties["Core Fit Choice"] = st.sidebar.selectbox("Fit Choice", get_material_fit_names(component_properties["Core Material"]))
                else:
                    component_properties["Core Fit Choice"] = None


                component_properties["Case OD (m)"] = st.sidebar.number_input("Case OD (m)", value=0.0, format="%.3f")
                component_properties["Insulator OD (m)"] = st.sidebar.number_input("Insulator OD (m)", value=0.0, format="%.3f")
                component_properties["Core OD (m)"] = st.sidebar.number_input("Core OD (m)", value=0.0, format="%.3f")
                component_properties["Length (m)"] = st.sidebar.number_input("Length (m)", value=0.0, format="%.3f")
                component_properties["Number"] = st.sidebar.number_input("Number", value=1, format="%d")

            if selected_comp_type == "Power per Part":
                # Add input fields for Power per Part component properties
                component_properties["Type"] = "Power per Part"
                component_properties["Power per Part (W)"] = st.sidebar.number_input("Power per Part (W)", value=0.0, format="%.3f")
                component_properties["Number"] = st.sidebar.number_input("Number", value=1, format="%d")

            if "Transient" in selected_stage_name:
                component_properties["Time On (h/d)"] = st.sidebar.number_input("Time On (h/d)", value=0.0, format="%.1f", max_value=24.0, step = 0.5)
                component_properties["Time Off (h/d)"] = st.sidebar.number_input("Time Off (h/d)", value=0.0, format="%.1f", max_value=24.0, step = 0.5)

            if "4K" in selected_stage_name:
                component_properties["Providing Vapor"] = st.sidebar.checkbox("Providing Vapor", value=True)
            else:
                component_properties["Providing Vapor"] = st.sidebar.checkbox("Providing Vapor", value=False)
        ############################################################
        ############################################################


        # Button to add a new component or stage
        if st.sidebar.button("Add") and name:
            if selected_comp_type == "Stage":
                # Add a new stage
                if st.session_state.stages_exist == False:
                    st.session_state.main_stage = Stage(name, high_temp=high_temp, low_temp=low_temp, color=get_color())
                    st.sidebar.success(f"First stage added!")
                    st.session_state.stages_exist = True               
                else:
                    new_stage = Stage(name, high_temp = high_temp, low_temp = low_temp, color=get_color())
                    st.session_state.main_stage.add_stage(new_stage)
                    st.sidebar.success(f"Stage '{name}' added!")
            else:
                # Add a new component to the selected stage
                selected_stage = next((stage for stage in [st.session_state.main_stage] + st.session_state.main_stage.stages if stage.name == selected_stage_name), None)
                if selected_stage:
                    if selected_comp_type == "Standard":
                        selected_stage_temps = {}
                        selected_stage_temps["lowT"] = selected_stage.low_temp
                        selected_stage_temps["highT"] = selected_stage.high_temp
                        component_properties["Power per Part (W)"] = calculate_power_function(component_properties, selected_stage_temps, A_L = False)
                    new_component = Component(name, properties=component_properties)
                    selected_stage.add_component(new_component)
                    st.sidebar.success(f"Component '{name}' added to '{selected_stage_name}'!")
            st.rerun() 
            return component_properties

    component_props = sidebar_inputs()

    try:
        substages = [sub_stage for sub_stage in st.session_state.main_stage.stages if sub_stage.name != st.session_state.main_stage.name]
        all_stages = [st.session_state.main_stage] + substages
    except AttributeError:
        st.warning("No stages available. Please add a stage to begin.")
        substages = []
        all_stages = []

    # Function to save stages and components to a JSON file
    def save_to_json(stages):
        comps_dict = {
            stage.name : {
                comp.name : comp.properties for comp in stage.components
            } for stage in stages
        }
        stages_dict = {
            stage_ind.name : {
                "lowT" : stage_ind.low_temp,
                "highT" : stage_ind.high_temp,
            } for stage_ind in stages
        }
        power_dict = {
            stage.name : stage.power for stage in stages
        }

        save_dict = {
            "components": comps_dict,
            "stage_details": stages_dict,
            "total_power": power_dict
        }
        return save_dict

    # Button to download JSON
    download_file = st.sidebar.download_button(
            label="Download JSON",
            data=json.dumps(save_to_json(all_stages), indent=4),
            file_name="stages_components.json",
            mime="application/json"
        )


    # Function to load stages and components from a JSON file
    def load_from_json(json_data):
        stages = []
        for stage_name, stage_details in json_data["stage_details"].items():
            stage = Stage(
                stage_name,
                high_temp=stage_details["highT"],
                low_temp=stage_details["lowT"],
                color=get_color()
            )
            if stage_name in json_data["components"]:
                for comp_name, comp_properties in json_data["components"][stage_name].items():
                    component = Component(comp_name, properties=comp_properties)
                    stage.add_component(component)
            stage.power = json_data["total_power"].get(stage_name, 0)
            stages.append(stage)
        return stages

    # Button to upload JSON
    # uploaded_file = st.sidebar.file_uploader("Upload JSON", type="json")
    # if uploaded_file:
    #     json_data = json.load(uploaded_file)
    #     loaded_stages = load_from_json(json_data)
    #     if loaded_stages:
    #         st.session_state.main_stage = loaded_stages[0]
    #         st.session_state.main_stage.stages = loaded_stages[1:]
    #         st.sidebar.success("JSON loaded successfully!")


    # Button to upload JSON
    uploaded_file = st.sidebar.file_uploader("Upload JSON", type="json")
    if uploaded_file and st.sidebar.button("Click to load JSON"):
        json_data = json.load(uploaded_file)
        loaded_stages = load_from_json(json_data)
        st.session_state.main_stage = loaded_stages[0]
        st.session_state.main_stage.stages = loaded_stages[1:]
        st.sidebar.success("JSON loaded successfully!")

    clear_button = st.sidebar.button("Clear All", type="primary")
    
    if clear_button:
        st.session_state.main_stage = Stage("Stage 1", color=get_color())
        st.sidebar.success("All components and stages cleared!")

    ############################################################
    ############################################################

    # Display Functions

    # Function to display a stage with components
    def display_stage(stage):
        with stylable_container(
            key=f"{stage.name}_container",
            css_styles="""
                {
                    background-color: %s;
                    border: 0px solid %s;
                    border-radius: 0.5rem;
                    padding: 1em 1em 2em 1em; /* Top, Right, Bottom, Left */
                }
                """ % (get_color(), get_dark_color()),
        ): 
            if stage.name not in st.session_state.editing_stage_properties:
                st.session_state.editing_stage_properties[stage.name] = False
            with st.expander(f"{stage.name}", expanded=False):
                # Display stage properties as editable fields
                stage_df = pd.DataFrame([
                                        ["High Temp", stage.high_temp],
                                        ["Low Temp", stage.low_temp], 
                                        ["Power", stage.power]], 
                                        columns=["Property", "Value"])
                # st.markdown(stage_df.to_html(index=False), unsafe_allow_html=True)
                st.dataframe(stage_df, use_container_width=True, hide_index=True, on_select="rerun")

                rows = max(np.ceil(len(stage.components)/3).astype(int), 1)
                j = 0
                # Defines number of rows
                for n in range(rows):
                    # For each row, create 3 columns
                    cols = st.columns(min(len(stage.components) + 1,3), border=True)
                    for i in range(len(cols)): #for component in stage.components:
                        with cols[i]:
                            if j > len(stage.components) - 1:
                                break
                            component = stage.components[j]
                            # st.html(f"<div class='banner' style='--stage-color: {stage.color}'>")
                            # st.markdown(f"<div class='component'>", unsafe_allow_html=True)
                            st.markdown(f"<div class='component-name'>{component.name}</div>", unsafe_allow_html=True)

                            # Display component properties as editable fields
                            if st.button(f"Edit {component.name}", key=f"edit_{stage.name}_{component.name}"):
                                st.session_state.editing_component = component
                                st.session_state.editing_stage = stage

                            if st.session_state.get("editing_component") == component:
                                for prop, value in component.properties.items():
                                    if isinstance(value, (float, int)):
                                        new_value = st.number_input(prop, value=float(value) if isinstance(value, float) else int(value))
                                    elif isinstance(value, bool):
                                        new_value = st.checkbox(prop, value=value)
                                    else:
                                        new_value = st.text_input(prop, value)
                                    component.properties[prop] = new_value
                                if st.button("Save Changes", key=f"save_{stage.name}_{component.name}"):
                                    st.session_state.editing_component = None
                                    st.session_state.editing_stage = None
                                    st.success(f"Changes saved for {component.name}!")

                            # Display component properties as a table within the component box
                            if component.properties:
                                df = pd.DataFrame(
                                    [
                                        {
                                            "Property": key,
                                            "Value": (
                                                f"{value:.3e}" if isinstance(value, (int, float)) and not isinstance(value, bool)
                                                else ("True" if value is True else "False") if isinstance(value, bool)
                                                else value
                                            )
                                        }
                                        for key, value in component.properties.items()
                                    ]
                                )
                                st.dataframe(df, use_container_width=True, hide_index=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)
                        j += 1
    # Define Stages

    def get_stage_details(all_stages):
            
        stage_details = {}
        for stage_ind in all_stages:
            stage_details[stage_ind.name] = {"lowT": float(stage_ind.low_temp), "highT": float(stage_ind.high_temp)}

        # Create a dictionary of dictionaries with stage names as keys and component dictionaries as values
        stage_components_dict = {
            stage.name: {
                component.name: component.properties for component in stage.components
            }
            for stage in all_stages
        }
        return stage_components_dict, stage_details
    
    stage_components_dict, stage_details = get_stage_details(all_stages)

    def calc_power_button_press(stage_components_dict, stage_details):
        components_dict = get_all_powers(stage_components_dict, stage_details)
        for stage_name, components in components_dict.items():
            total_power = 0
            for component_name, properties in components.items():
                # properties["Power per Part (W)"] = float(calculate_power_function(properties, stage_details[stage_name], A_L = False))
                if "Power per Part (W)" in properties and "Number" in properties:
                    properties["Power Total (W)"] = float(properties["Power per Part (W)"]) * int(properties["Number"])
                    total_power += properties["Power Total (W)"]
            for stage in all_stages:
                if stage.name == stage_name:
                    stage.power = total_power
                    break
        if any(stage.name == "4K - LHe" for stage in all_stages):
            sum_var, updated_cooling_data = get_sum_variance(save_to_json(all_stages))
            # updated_cooling_data = {"NAME" : [0,0]}
        else:
            updated_cooling_data = {"NAME" : [0,0]}
            st.warning("Sum variance can only be calculated with a complete system. Please add a 4K - LHe stage.")
        return all_stages, updated_cooling_data
    # Function buttons
    button_col1, button_col2 = st.columns(2)
    
    
    button_col1.button("Calculate Power", use_container_width=True, type="primary")
    if button_col1:
        all_stages, updated_cooling_data = calc_power_button_press(stage_components_dict, stage_details)

    optim_clicked = st.session_state.get("optimize_clicked", False)
    button_clicked = button_col2.button("Optimize", use_container_width=True, type="primary")
    optim_number = button_col2.slider("Optimize Points", min_value=5, max_value=100, value=10, step=5, key="optimize_slider")
    if button_clicked:
        st.session_state.optimize_clicked = True
    if button_col2 and st.session_state.optimize_clicked:
        if any(stage.name == "VCS 2" for stage in all_stages) and any(stage.name == "VCS 1" for stage in all_stages) and any(stage.name == "4K - LHe" for stage in all_stages):
            updated_details, optimize_output_data, heatmap = optimize_tm(stage_components_dict, stage_details, num_points = optim_number)
            # get_sum_variance(save_to_json(all_stages))
            # updated_stage_details = stage_details
            # updated_details = stage_components_dict
            # Update the stages and components with the optimized details
            for stage_name, components in updated_details.items():
                for stage in all_stages:
                    if stage.name == stage_name:
                        stage.power = 0  # Reset total power
                        for component_name, properties in components.items():
                            for component in stage.components:
                                if component.name == component_name:
                                    component.properties.update(properties)
                                    if "Power Total (W)" in properties:
                                        stage.power += properties["Power Total (W)"]

                # Update stage temperature details
            for stage_name, details in optimize_output_data["stage_details"].items():
                for stage in all_stages:
                    if stage.name == stage_name:
                        stage.low_temp = details["lowT"]
                        stage.high_temp = details["highT"]
            st.session_state.optimized = heatmap
        else:
            st.warning("Optimization can only run with a complete system. Please add a VCS 2 stage.")
        st.session_state.optimize_clicked = False

    # Display the main stage and nested stages
    st.header("Stages")
    # display_stage(st.session_state.main_stage)
    for sub_stage in all_stages:
        display_stage(sub_stage)

# Second Page Content

updated_temperature_data = [
        {"Stage": stages.name,
        # "High Temperature (K)": f"{stages.high_temp:.2f}", 
        "Stage Temperature (K)": f"{stages.low_temp:.2f}",
        "Total Power (W)": f"{stages.power:.2e}"
        }
        for stages in all_stages
    ]

temp_data_df = pd.DataFrame.from_records(updated_temperature_data) #, columns=["Property", "Value"])
cooling_data_df = pd.DataFrame.from_dict(updated_cooling_data, orient='index', columns=["Value", "Units"])
with tabs[1]:
    st.dataframe(temp_data_df, use_container_width=True, hide_index=True)
    st.dataframe(cooling_data_df, use_container_width=True)
with tabs[2]:
    st.header("Plots")

    if st.session_state.stages_exist:
        # Select a stage for plotting
        stage = st.pills("Select Stage for Plot", all_stages, default=all_stages[0], format_func=lambda stage: stage.name, key="selected_stage_plot")

        if stage.components:
            st.subheader(f"Power Distribution for {stage.name}")

            plot_pie_chart(stage)

            # Dropdown to select a component for detailed view
            selected_component = st.selectbox(
                "Select Component for Details",
                stage.components,
                format_func=lambda component: component.name,
                key="selected_component_dropdown"
            )

            # Display selected component details
            if selected_component:
                st.subheader(f"Details for {selected_component.name}")

                component_df = pd.DataFrame(
                    [
                        {
                            "Property": key,
                            "Value": (
                                f"{value:.3e}" if isinstance(value, (int, float)) and not isinstance(value, bool)
                                else ("True" if value is True else "False") if isinstance(value, bool)
                                else value
                            )
                        }
                        for key, value in selected_component.properties.items()
                    ]
                )
                st.dataframe(component_df, use_container_width=True, hide_index=True)

                try:
                    int_fig, int_ax = plot_integral(selected_component.properties, stage, name=selected_component.name)
                    left_col, mid_col, right_col = st.columns([0.2, 0.6, 0.2])
                    mid_col.pyplot(int_fig, use_container_width=True)
                except:
                    st.warning("Integral plot not available for this component type.")
        # Sum Var plot
        left_col, mid_col, right_col = st.columns([0.2, 0.6, 0.2])
        try:
            fig, ax = plt.subplots()

            cmap = plt.cm.jet  # define the colormap
            # extract all colors from the .jet map
            cmaplist = [cmap(i) for i in range(cmap.N)]
            # force the first color entry to be grey

            # create the new map
            cmap = mpl.colors.LinearSegmentedColormap.from_list(
                'Custom cmap', cmaplist, cmap.N)

            # define the bins and normalize
            bounds = np.linspace(-10, 1, 20)
            norm = mpl.colors.BoundaryNorm(bounds, cmap.N)


            [VCS2grid, VCS1grid, SumVarArr] = st.session_state.optimized
            hm = ax.imshow(np.log(SumVarArr), extent=(VCS1grid.min(), VCS1grid.max(), VCS2grid.min(), VCS2grid.max()), origin='lower', cmap="Blues_r", aspect='auto')

            fig.colorbar(hm, label='ln(Sum Variance)')#, cmap=cmap, norm=norm, spacing="proportional", ticks=bounds, boundaries=bounds)#, ticks=np.round(np.linspace(SumVarArr.min(), SumVarArr.max(), 5)), format='%.2f')
            ax.set_ylabel('VCS2 temperature')
            ax.set_xlabel('VCS1 temperature')
            ax.set_title('2D Heatmap of Stage Temperature Variance')
            plt.savefig(f"{file_path}{os.sep}Screenshots{os.sep}heatmap.png", dpi=600, bbox_inches='tight')
            mid_col.pyplot(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Error {e} Optimization must be run to display the heatmap. Please click the 'Optimize' button on the main page.")

with tabs[3]:
    st.header("Quick Calculation Tools")
    st.subheader("Thermal Conductivity Calculator")
    quick_pick = {}

    quick_pick["Material"] = st.selectbox("Material", mat_list, key="qp_material")
    qp_temp = st.number_input("Temperature (K)", value=100.0, format="%.1f", key="qp_temp")

    has_interpolation, valid_range, interp_func = find_interpolation(quick_pick["Material"]) # Searches for interpolation file, returns True if it exists
    qp_use_interp = has_interpolation
    if has_interpolation: # If interpolation file exists
        quick_pick["Interpolate"] = st.checkbox(f"Use Interpolation in range :\n{valid_range[0]} K - {valid_range[1]} K", value=True, key="qp_interpolate") # Provide checkbox to use interpolation
        qp_use_interp = quick_pick["Interpolate"]
    if not qp_use_interp: # If interpolation is not selected, search for available fits
        print(get_material_fit_names(quick_pick["Material"]))
        quick_pick["Fit Choice"] = st.selectbox("Fit Choice", get_material_fit_names(quick_pick["Material"]), key="qp_fit_choice")
    else:
        quick_pick["Fit Choice"] = None

    if qp_use_interp:
        interp_exists, valid_range, interp_func = find_interpolation(quick_pick["Material"]) # Check if interpolation file exists
        ConVal = interp_func(qp_temp*u.K)*u.W/u.m/u.K
    elif quick_pick["Fit Choice"] is not None:
        fit_obj = get_fit_by_name(quick_pick["Material"], quick_pick["Fit Choice"])
        ConVal = fit_obj.calc_tc(qp_temp*u.K)
        print(ConVal)
    st.markdown(f"Conductivity: {ConVal}")


    st.subheader("Integral Calculator")
    lowT = st.number_input("Low Temperature (K)", value=4.0, format="%.1f", key="qp_lowT")
    highT = st.number_input("High Temperature (K)", value=300.0, format="%.1f", key="qp_highT")
    qp_stage = Stage("QP", high_temp = highT, low_temp = lowT, color=get_color())
    
    if quick_pick["Fit Choice"] is not None:
        fit_obj = get_fit_by_name(quick_pick["Material"], quick_pick["Fit Choice"])
        ConIntQuad = fit_obj.tc_integral(lowT*u.K, highT*u.K)[0].value
        st.markdown(f"Conductivity Integral (Quad): {ConIntQuad}")


    try:
        int_fig, int_ax = plot_integral(quick_pick, qp_stage, name=quick_pick["Material"])
        left_col, mid_col, right_col = st.columns([0.2, 0.6, 0.2])
        mid_col.pyplot(int_fig, use_container_width=True)
    except:
        st.warning("Integral plot not available for this component type.")
    # quick_pick["OD (m)"] = st.number_input("OD (m)", value=0.0, format="%.3f", key="qp_od")
    # quick_pick["ID (m)"] = st.number_input("ID (m)", value=0.0, format="%.3f", key="qp_id")
    # quick_pick["Length (m)"] = st.number_input("Length (m)", value=0.0, format="%.3f", key="qp_length")
    # quick_pick["Number"] = st.number_input("Number", value=1, format="%d", key="qp_number")

with tabs[4]:
    st.header("About")
    st.markdown("""
        This is an interactive thermal model GUI for modeling the thermal properties of cryogenic systems.
        It allows users to add components, stages, and visualize the thermal properties of the system.
        The development of this tool was done in support of the Balloon-borne Large Aperture Sub-millimeter Telescopes (BLAST) collaboration.
        ### Features:
        - Add and edit components and stages.
        - Calculate total thermal power requirements.
        - Optimize liquid helium cryogenic stage temperatures.
        - Calculate liquid helium and balloon specific parameters.
        - Visualize power distribution and temperature variance.
        parametersparameters
        
        ### Help
        For more guidance, please refer to the [documentation](https://github.com/henry-e-n/python_thermal_model/wiki/0.-Thermal-Model-Wiki).
        
        ### Creators:
        This tool is a culmination of decades of various similar efforts by researchers across experimental cosmology, and other cryogenic experimental fields. 
                The development of this Python-based tool, package, and GUI was led by Henry Nachman at the University of Texas at Austin.

        If you have any questions, suggestions, or issues, please feel free to reach out:
        
        Henry Nachman (henry.nachman@utexas.edu)""")