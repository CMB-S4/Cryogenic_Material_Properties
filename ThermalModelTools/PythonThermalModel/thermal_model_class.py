# Creating classes for easy use of the thermal model

from stage_calc import calculate_power_function, get_all_powers, optimize_tm
from plotting import plot_integral, plot_pie_chart

from stages.stage import Stage
from astropy import units as u

class ThermalModel:
    def __init__(self, stages):
        self.components = stages["components"]
        self.stage_temps = stages["stage_details"]
        self.total_power = stages["total_power"]
        self.stages = list(self.components.keys())

    def get_stage(self, name):
        """ Returns a Stage object for the specified stage name.
        Args:
            name (str): The name of the stage to search for.
        Returns:
            Stage: An object containing the stage's properties and methods.
        """
        for stage_name in self.stages:
            if stage_name == name:
                return Stage(name=stage_name,
                             high_temp=self.stage_temps[stage_name]["highT"],
                             low_temp=self.stage_temps[stage_name]["lowT"],
                             power=self.total_power.get(stage_name, 0.0),
                             components=self.components.get(stage_name, []))       
        return None

    def get_component(self, name, stage=None):
        """ Returns a Component_Inspect object for the specified component name and stage.
        If stage is None, it searches all stages for the component and returns the first one found.
        Args:
            name (str): The name of the component to search for.
            stage (str, optional): The name of the stage to search in. Defaults to None.
        Returns:
            Component_Inspect: An object containing the component's properties and methods.
        """
        if stage is not None: # Indentifies the specified stage
            for component in self.components[stage]: # Searches for the component with specified name
                if component == name:
                    selected_comp = Component_Inspect(self, component, stage)
                    return selected_comp  # Returns component object
        else:
            for stage, stage_components in self.components.items():
                for component in stage_components:
                    if component == name:
                        return Component_Inspect(self, component, stage)
        return None
    
    def update_all_powers(self):
        """ Updates the power for all components in the thermal model.
        This method iterates through all components in each stage and calculates their power based on the current stage temperatures.
        """
        self.components = get_all_powers(self.components, self.stage_temps)
        self.total_power = sum(comp.calculate_power() for stage in self.components.values() for comp in stage)

    def optimize(self, optimization_points: int = 10):
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
        # Placeholder for optimization logic
        optimize_tm(self.components, self.stage_temps, optimization_points)

    def plot_stage(self, stage_name, streamlit=False):
        """
        Plot the thermal model for a specific stage.

        Args:
            stage_name (str): The name of the stage to plot.
            streamlit (bool, optional): Whether to use Streamlit for plotting. Defaults to False.

        Returns:
            Figure: The plotted figure.
        """
        stage = self.get_stage(stage_name)
        if stage is not None:
            fig = plot_pie_chart(stage, streamlit=streamlit)
            return fig

class Component_Inspect:
    def __init__(self, model, component, stage):
        self.model = model
        self.name = component
        self.properties = model.components[stage][component]
        self.type = self.properties.get("Type", "Unknown")
        if self.type == "Unknown":
            raise ValueError("Component type is not specified in properties.")
        elif self.type == "Power per Part":
            self.power_per_part = self.properties.get("Power per Part (W)", 0.0)
        elif self.type in ["Component", "Standard", "A/L", "Coax"]:
            self.length = self.properties.get("Length", 0.0)
            if self.type in ["Component", "Standard", "A/L"]:
                self.material = self.properties.get("Material", "Unknown")
                self.interpolate = self.properties.get("Interpolate", False)
                self.fit_choice = self.properties.get("Fit Choice", "None")
                if self.type in ["Component", "Standard"]:
                    self.OD = self.properties.get("OD", 0.0)
                    self.ID = self.properties.get("ID", 0.0)
                if self.type == "A/L":
                    self.AoL = self.properties.get("A/L", 0.0)
            elif self.type == "Coax":
                self.casing_mat = self.properties.get("Casing Material", "Unknown")
                self.casing_interpolate = self.properties.get("Casing Interpolate", False)
                self.casing_fit_choice = self.properties.get("Casing Fit Choice", "None")

                self.insulation_mat = self.properties.get("Insulation Material", "Unknown")
                self.insulation_interpolate = self.properties.get("Insulation Interpolate", False)
                self.insulation_fit_choice = self.properties.get("Insulation Fit Choice", "None")

                self.core_mat = self.properties.get("Core Material", "Unknown")
                self.core_interpolate = self.properties.get("Core Interpolate", False)
                self.core_fit_choice = self.properties.get("Core Fit Choice", "None")

                self.case_od = self.properties.get("Case OD (m)", 0.0)
                self.insulator_od = self.properties.get("Insulator OD (m)", 0.0)
                self.core_od = self.properties.get("Core OD (m)", 0.0)

        self.number = self.properties.get("Number", 1)
        self.stage = stage
        self.total_power = self.calculate_power()

    def calculate_power(self):
        """Calculate the power function for the given component.

        Args:
            self (Component_Inspect): The component object for which to calculate power.
        Returns:
            float: The calculated power per unit.
        """
        stage_temps = self.model.stage_temps[self.stage]
        if self.type == "Power per Part":
            return self.power_per_part * self.number
        elif self.type in ["Component", "Standard", "A/L", "Coax"]:
            return calculate_power_function(self.model.components[self.stage][self.name], stage_temps, A_L=(self.type == "A/L"))
        else:
            raise ValueError(f"Unknown component type: {self.type}")

    def plot(self):
        """Plot the thermal conductivity of the component.
        This method uses the component's properties to determine the appropriate plotting method.
        Returns:
            Figure: The plotted figure.
        """
        # Placeholder for plotting logic
        plot_integral(self, self.model.get_stage(self.stage))