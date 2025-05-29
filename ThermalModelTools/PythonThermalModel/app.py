import streamlit as st
from components.component import Component
from stages.stage import Stage
import random, os, sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as c
import matplotlib.cm as cm
import json
import numpy as np
from stage_calc import *
import plotly.express as px
import logging
import matplotlib as mpl

from streamlit_extras.stylable_container import stylable_container

# # print("CHECKPOINT 1")
abspath = os.path.abspath(__file__)
file_path = os.path.dirname(abspath)
def default_page_load():
    st.set_page_config("Interactive Thermal Model GUI", page_icon=":thermometer:", layout="wide")
    HORIZONTAL_RED = f"{file_path}{os.sep}static{os.sep}blast-logo.png"
    ICON_RED = f"{file_path}{os.sep}static{os.sep}blast-logo.png"
    st.logo(HORIZONTAL_RED, icon_image=ICON_RED)
    
default_page_load()

# Define Paths

abspath = os.path.abspath(__file__)
file_path = os.path.dirname(abspath)
sys.path.insert(0, f"{file_path}{os.sep}..{os.sep}..{os.sep}")


git_repo_path = os.path.dirname(os.path.dirname(file_path))

path_to_tcFiles = git_repo_path
all_files = os.listdir(path_to_tcFiles)
exist_files = [file for file in all_files if file.startswith("tc_fullrepo")]
tc_file_date = exist_files[0][-12:-4]

TCdata = np.loadtxt(f"{path_to_tcFiles}{os.sep}tc_fullrepo_{tc_file_date}.csv", dtype=str, delimiter=',') # imports compilation file csv


mat_list = list(TCdata[1:, 0])


# # Function to generate a random color
def random_color(value = 200):
    cmap = plt.cm.get_cmap('Blues')  # You can choose any colormap you like
    return c.to_hex(cmap(370/value))

def get_color():
    return "#f7f7ff" #"#fff5f5"
def get_dark_color():
    return "#6d6bff" #"#ffa1a1"

# Initialize stages and components
if 'main_stage' not in st.session_state:
    st.session_state.main_stage = Stage("VCS 2", high_temp=270.0, low_temp=60.0, color=get_color())

# st.write("Session State:", st.session_state)
# Initialize session state
if 'editing_stage_properties' not in st.session_state:
    st.session_state.editing_stage_properties = {}

if 'optimize_clicked' not in st.session_state:
    st.session_state.optimize_clicked = False

if 'optimized' not in st.session_state:
    st.session_state.optimized = False

# Include custom CSS
with open(f"{file_path}{os.sep}static{os.sep}styles.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Streamlit app
title_area, logo_area = st.columns(2)
title_area.title("Interactive Thermal Model GUI")
logo_area.image(f"{file_path}{os.sep}static{os.sep}blast-logo.png", width=200)  # Display the logo in the main body

tabs = st.tabs(["Component Modeling", "Result Tables", "Plots"])


# print("CHECKPOINT 2")
# Main Page Content
with tabs[0]:
    
    # Sidebar for input fields and buttons
    st.sidebar.header("Add Components and Stages")


    # Select a stage to add the component to
    selected_stage_name = st.sidebar.selectbox("Select Stage to Add Component",
                                            [st.session_state.main_stage.name] + [stage.name for stage in st.session_state.main_stage.stages])

    # Select the type of component you want to add
    component_type_list = ["Stage", "Standard", "A/L", "Coax", "Power per Part"]
    selected_comp_type = st.sidebar.selectbox("Select Component Type", component_type_list)
    
    def sidebar_inputs():
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
            component_properties["OD (m)"] = st.sidebar.number_input("OD (m)", value=0.0, format="%.3f")
            component_properties["ID (m)"] = st.sidebar.number_input("ID (m)", value=0.0, format="%.3f")
            component_properties["Length (m)"] = st.sidebar.number_input("Length (m)", value=0.0, format="%.3f")
            component_properties["Number"] = st.sidebar.number_input("Number", value=1, format="%d")

        if selected_comp_type == "A/L":
            # Add input fields for A/L component properties
            component_properties["Type"] = "A/L"
            component_properties["Material"] = st.sidebar.selectbox("Material", mat_list)
            component_properties["A/L (m)"] = st.sidebar.number_input("A/L (m)", value=0.0, format="%.3f")
            component_properties["Length (m)"] = st.sidebar.number_input("Length (m)", value=0.0, format="%.3f")
            component_properties["Number"] = st.sidebar.number_input("Number", value=1, format="%d")

        if selected_comp_type == "Coax":
            # Add input fields for Coax component properties
            component_properties["Type"] = "Coax"
            component_properties["Casing Material"] = st.sidebar.selectbox("Casing Material", mat_list)
            component_properties["Insulator Material"] = st.sidebar.selectbox("Insulator Material", mat_list)
            component_properties["Core Material"] = st.sidebar.selectbox("Core Material", mat_list)
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

        ############################################################
        ############################################################

        # Button to add a new component or stage
        if st.sidebar.button("Add") and name:
            if selected_comp_type == "Stage":
                # Add a new stage
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

    
    # print("CHECKPOINT 3")
    sidebar_inputs()
    # print("CHECKPOINT 4")

    substages = [sub_stage for sub_stage in st.session_state.main_stage.stages if sub_stage.name != st.session_state.main_stage.name]
    all_stages = [st.session_state.main_stage] + substages
    
    # print("CHECKPOINT 5 - Main STAGE", all_stages[0].name, all_stages[0].low_temp, all_stages[0].high_temp)

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
        print("Loading JSON", st.session_state)
        st.sidebar.success("JSON loaded successfully!")

    # print("CHECKPOINT 6")
    # Button to clear everything
    # with stylable_container(
    #     "green",
    #     css_styles="""
    #     sidebar.button {
    #         background-color: #00FF00;
    #         color: black;
    #     }""",
    # ):
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
                    border: 1px solid %s;
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px)
                }
                """ % (get_color(), get_dark_color()),
        ):
                
            # st.write(st.session_state.editing_stage_properties)
            if stage.name not in st.session_state.editing_stage_properties:
                st.session_state.editing_stage_properties[stage.name] = False
            with st.expander(f"{stage.name}", expanded=False):
                # Display stage properties as editable fields
                # ##############################################################################################
                # EDIT FUNCTION THAT IS NOT CURRENTLY WORKING
                # ##############################################################################################
                # if st.button(f"Edit {stage.name}", key=f"edit_{stage.name}"):
                #     st.session_state.editing_stage_properties[stage.name] = True
                #     # st.experimental_rerun()  # Trigger re-render
                # if st.session_state.get("editing_stage_properties")[stage.name]:
                #     new_high_temp = st.number_input("High Temperature (°K)", value=float(stage.high_temp), format="%.1f", key=f"high_temp_{stage.name}")
                #     new_low_temp = st.number_input("Low Temperature (°K)", value=float(stage.low_temp), format="%.1f", key=f"low_temp_{stage.name}")
                #     # new_power = st.number_input("Power (W)", value=float(stage.power), format="%.1f", key=f"power_{stage.name}")
                #     # st.write("PRE", stage.low_temp, stage.high_temp, stage.power)
                #     if st.button("Save Changes", key=f"save_{stage.name}"):                  
                #         stage.low_temp = new_low_temp
                #         stage.high_temp = new_high_temp
                #         # stage.power = new_power
                        
                #         # st.write("MID", stage.low_temp, stage.high_temp, stage.power)
                #         st.success(f"Changes saved for {stage.name}!")
                #         st.session_state.editing_stage_properties[stage.name] = False
                #         # st.experimental_rerun()  # Trigger re-render
                # ##############################################################################################
                # EDIT FUNCTION THAT IS NOT CURRENTLY WORKING
                # ##############################################################################################

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
                                        {"Property": key, "Value": f"{value:.3e}" if isinstance(value, (int, float)) else value}
                                        for key, value in component.properties.items()
                                    ]
                                )
                                # st.markdown(df.to_html(index=False), unsafe_allow_html=True)
                                st.dataframe(df, use_container_width=True, hide_index=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        j += 1
    # Define Stages

    # print("CHECKPOINT 7")
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

    # print("CHECKPOINT 8")
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

    # print("CHECKPOINT 9")
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

    # print("CHECKPOINT 10")
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
# print("CHECKPOINT 11")
with tabs[1]:
    st.dataframe(temp_data_df, use_container_width=True, hide_index=True)
    st.dataframe(cooling_data_df, use_container_width=True)
# print("CHECKPOINT 12")
with tabs[2]:
    st.header("Plots")

    # Select a stage for plotting
    stage = st.pills("Select Stage for Plot", all_stages, default=all_stages[0], format_func=lambda stage: stage.name, key="selected_stage_plot")

    if stage.components:
        st.subheader(f"Power Distribution for {stage.name}")

        # Prepare data for the pie chart
        data = {
            "Component": [component.name for component in stage.components],
            "Power (W)": [
                float(component.properties.get("Power Total (W)", 0)) for component in stage.components
            ],
        }
        df = pd.DataFrame(data)

        # Plot the pie chart using Plotly with hover showing power in scientific notation
        fig = px.pie(
            df, 
            names="Component", 
            values="Power (W)", 
            title=f"Power Distribution for {stage.name}", 
            color_discrete_sequence=px.colors.sequential.RdBu,
            hover_data={"Power (W)": ":e"},  # Format hover data in scientific notation
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        fig2, ax = plt.subplots()
        # Use Plotly's RdBu color sequence for the matplotlib pie chart
        # Use the sequential RdBu colormap from matplotlib for the pie chart
        colors = [
                "#67001f",
                "#b2182b",
                "#d6604d",
                "#f4a582",
                "#fddbc7",
                # "#f7f7f7",
                # "#d1e5f0",
                "#92c5de",
                "#4393c3",
                "#2166ac",
                "#053061"
            ]
        
        def display_percentage(pct):
            return f'{pct:.1f}%' if pct > 3.5 else ''
        def display_labels(df):
            labels = []
            for i in range(len(df)):
                print("LABELS", df["Power (W)"][i])
                if df["Power (W)"][i] < (0.005*4.66):
                    labels.append(f'')
                else:
                    labels.append(f'{df["Component"][i]}')
            return labels
        wedges, texts, autotexts = ax.pie(
            df["Power (W)"], 
            labels=display_labels(df), 
            autopct=display_percentage, 
            startangle=5, 
            colors=colors, 
            textprops={'size': 'small'}
        )

        # Add arrows to labels
        for i, text in enumerate(texts):
            if text.get_text():  # Only add arrow if label is not empty
                ang = (wedges[i].theta2 + wedges[i].theta1) / 2.
                x = np.cos(np.deg2rad(ang))
                y = np.sin(np.deg2rad(ang))
                # Offset for the arrow
                arrow_x = 1.0 * x
                arrow_y = 1.0 * y
                # Offset for the label
                label_x = 1.2 * x
                label_y = 1.2 * y
                text.set_position((label_x, label_y))
                ax.annotate(
                    '', 
                    xy=(arrow_x, arrow_y), 
                    xytext=(label_x, label_y),
                    arrowprops=dict(arrowstyle="-", color='black', lw=.5),
                    va='center', ha='center'
                )
        ax.set_title(f"Power Distribution for {stage.name}")
        plt.savefig(f"{file_path}{os.sep}Screenshots{os.sep}pie_chart.png", dpi=600, bbox_inches='tight')
        st.plotly_chart(fig)

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
                list(selected_component.properties.items()),
                columns=["Property", "Value"]
            )
            st.dataframe(component_df, use_container_width=True, hide_index=True)

            try:
                int_fig, int_ax = plot_integral(selected_component, stage)
                plt.savefig(f"{file_path}{os.sep}Screenshots{os.sep}integral.png", dpi=600, bbox_inches='tight')

                left_col, mid_col, right_col = st.columns([0.2, 0.6, 0.2])
                mid_col.pyplot(int_fig, use_container_width=True)
            except:
                st.warning("Integral plot not available for this component type.")

    # Sum Var plot
    left_col, mid_col, right_col = st.columns([0.2, 0.6, 0.2])
    try:
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
        except NameError:
            st.warning("Optimization must be run to display the heatmap. Please click the 'Optimize' button on the main page.")
    except TypeError:
        st.warning("Optimization must be run to display the heatmap. Please click the 'Optimize' button on the main page.")