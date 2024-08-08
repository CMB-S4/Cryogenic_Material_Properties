import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dependencies import ALL
import pandas as pd
import numpy as np
import json
import base64
import sys, os, csv, json


from stage_calc import calculate_power_function, get_all_powers, optimize_tm

abspath = os.path.abspath(__file__)
file_path = os.path.dirname(abspath)
sys.path.insert(0, f"{file_path}{os.sep}..{os.sep}..{os.sep}")

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


path_to_tcFiles = f"{file_path}{os.sep}..{os.sep}.."
all_files = os.listdir(path_to_tcFiles)
exist_files = [file for file in all_files if file.startswith("tc_fullrepo")]
# print(exist_files)
tc_file_date = exist_files[0][-12:-4]

TCdata = np.loadtxt(f"{path_to_tcFiles}{os.sep}tc_fullrepo_{tc_file_date}.csv", dtype=str, delimiter=',') # imports compilation file csv
# TCdata = list(TCdata[1:,0])

# Sample data for materials (replace this with actual data loading as needed)
# TCdata = np.array([
#     ["Material"],
#     ["Aluminum"],
#     ["Copper"],
#     ["Steel"],
# ])

mat_list = list(TCdata[1:, 0])

# Cryogenic stages
stages = ["VCS 1", "VCS 2", "4K - LHe", "1K", "300mK", "100mK"]
stage_temps = [260, 240, 169, 4.2, 2, 0.3, 0.1]

stage_details = {}
for i in range(len(stages)):
    stage_details[stages[i]] = {"lowT": stage_temps[i+1], "highT": stage_temps[i]}

# print(stage_details)
# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Cryogenic Thermal Stage"),
            dbc.Row([
                dbc.Col(dbc.Label("Cryogenic Stage:"), width=3),
                dbc.Col(dcc.Dropdown(id="cryogenic-stage", options=[{"label": stage, "value": stage} for stage in stages]), width=9)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(dbc.Label("Type:"), width=3),
                dbc.Col(dcc.Dropdown(id="type", options=[{"label": "Component", "value": "Component"}, {"label": "Other", "value": "Other"}]), width=9)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(dbc.Label("Component:"), width=3),
                dbc.Col(dbc.Input(id="component", type="text"), width=9)
            ], className="mb-3", id="component-row"),
            dbc.Row([
                dbc.Col(dbc.Label("Material:"), width=3),
                dbc.Col(dcc.Dropdown(id="material", options=[{"label": m, "value": m} for m in mat_list]), width=9)
            ], className="mb-3", id="material-row"),
            dbc.Row([
                dbc.Col(dbc.Label("OD (m):"), width=3),
                dbc.Col(dbc.Input(id="od", type="number"), width=9)
            ], className="mb-3", id="od-row"),
            dbc.Row([
                dbc.Col(dbc.Label("ID (m):"), width=3),
                dbc.Col(dbc.Input(id="id", type="number"), width=9)
            ], className="mb-3", id="id-row"),
            dbc.Row([
                dbc.Col(dbc.Label("Length (m):"), width=3),
                dbc.Col(dbc.Input(id="length", type="number"), width=9)
            ], className="mb-3", id="length-row"),
            dbc.Row([
                dbc.Col(dbc.Label("Power per Part (W):"), width=3),
                dbc.Col(dbc.Input(id="power", type="number"), width=9)
            ], className="mb-3", id="power-row"),
            dbc.Row([
                dbc.Col(dbc.Label("Number:"), width=3),
                dbc.Col(dbc.Input(id="number", type="number"), width=9)
            ], className="mb-3"),
        ]),
        dbc.Col([
            dcc.Upload(id="upload-json", children=html.Div(['Load from JSON']), 
                       style={'width': '140px', 'height': '40px', 'lineHeight': '35px', 
                              'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 
                              'textAlign': 'center', 'margin': '10px'}),
            dbc.Button("Add",             id="add",                 className="addbutton mr-2"),
            dbc.Button("Save to JSON",    id="save-json",           className="savebutton mr-2"),
            dbc.Button("Calculate Power", id="calculate-power",     className="calcbutton mr-2"),
            dbc.Button("Optimize",        id="new-process-button",  className="optimizebutton mr-2")
        ], width=4),
        dcc.Download(id="download-json"),
        ]),
    dbc.Row([
        html.H2("Components by Cryogenic Stage"),
        html.Div(id="table-container")
    ]),
    dbc.Row(
        dbc.Col(
            html.Div(
                "Henry Nachman - for BLAST.",
                className="footer-text",
                style={
                    "textAlign": "center",
                    "padding": "20px",
                    "backgroundColor": "#f8f9fa",
                    "marginTop": "20px"
                }
            )
        )
    )
])

# Initial empty components dictionary
components = {stage: {} for stage in stages}

# @app.callback(
#     Output("table-container", "children"),
#     [Input("add", "n_clicks"), Input("upload-json", "contents"), Input("calculate-power", "n_clicks"), Input({"type": "editable-table", "index": dash.ALL}, "data")],
#     [State("cryogenic-stage", "value"), State("type", "value"), State("component", "value"), State("material", "value"), State("od", "value"), State("id", "value"), State("length", "value"), State("power", "value"), State("number", "value"), State("table-container", "children")],
#     prevent_initial_call=True
# )
# def add_component(n_clicks, json_contents, calc_clicks, updated_data, stage, entry_type, component, material, od, id_val, length, power, number, current_table):
#     global components
#     ctx = dash.callback_context

#     if not ctx.triggered:
#         raise dash.exceptions.PreventUpdate

#     trigger = ctx.triggered[0]['prop_id'].split('.')[0]

#     if trigger == 'add':
#         if stage and number:
#             if stage not in components:
#                 components[stage] = {}
#             if entry_type == "Component" and component and material and od and id_val and length:
#                 components[stage][component] = {
#                     "material": material,
#                     "OD": od, "ID": id_val, "length": length,
#                     "number": number,
#                     "Power per Part (W)": 0,
#                     "Power Total (W)": 0,
#                 }
#             elif entry_type == "Other" and power:
#                 components[stage][component] = {
#                     "number": number,
#                     "Power per Part (W)": power,
#                     "Power Total (W)": 0,
#                 }
#     elif trigger == 'upload-json' and json_contents:
#         content_type, content_string = json_contents.split(',')
#         decoded = base64.b64decode(content_string).decode('utf-8')
#         components = json.loads(decoded)
#     elif trigger == 'calculate-power':
#         for stage, comps in components.items():
#             for comp, details in comps.items():
#                 num = float(details["number"])
#                 if "OD" in details:
#                     # od = float(details["OD"])
#                     # id_val = float(details["ID"])
#                     # length = float(details["length"])
#                     try:
#                         # power_per_part = od * id_val * length
#                         power_per_part = calculate_power_function(details, stage_details[stage])
#                         details["Power per Part (W)"] = power_per_part
#                     except ValueError:
#                         continue
#                 else:
#                     power_per_part = float(details["Power per Part (W)"])
#                 details["Power Total (W)"] = power_per_part*num
#     elif trigger == '{"type":"editable-table","index":ALL}':
#         for stage, comps in components.items():
#             updated_stage_data = next(item for item in updated_data if item['index'] == stage)
#             df = pd.DataFrame(updated_stage_data['data'])
#             df.set_index("Component", inplace=True)
#             components[stage] = df.to_dict(orient="index")
#     return generate_table()
@app.callback(
    Output("table-container", "children"),
    [Input("add", "n_clicks"), Input("upload-json", "contents"), Input("calculate-power", "n_clicks"), Input("new-process-button", "n_clicks"), Input({"type": "editable-table", "index": dash.ALL}, "data")],
    [State("cryogenic-stage", "value"), State("type", "value"), State("component", "value"), State("material", "value"), State("od", "value"), State("id", "value"), State("length", "value"), State("power", "value"), State("number", "value"), State("table-container", "children")],
    prevent_initial_call=True
)
def add_component(n_clicks, json_contents, calc_clicks, updated_data, new_process_clicks, stage, entry_type, component, material, od, id_val, length, power, number, current_table):
    global components, stage_details
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'add':
        if stage and number:
            if stage not in components:
                components[stage] = {}
            if entry_type == "Component": #  and component and material and od and id_val and length
                components[stage][component] = {
                    "material": material,
                    "OD": od, "ID": id_val, "length": length,
                    "number": number,
                    "Power per Part (W)": 0,
                    "Power Total (W)": 0,
                }
            elif entry_type == "Other" and power:
                components[stage][component] = {
                    "number": number,
                    "Power per Part (W)": power,
                    "Power Total (W)": 0,
                }
    elif trigger == 'upload-json' and json_contents:
        content_type, content_string = json_contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        json_data = json.loads(decoded)
        components = json_data.get("components", components)
        stage_details = json_data.get("stage_details", stage_details)
    elif trigger == 'calculate-power':
        details = get_all_powers(components, stage_details)
        output_data = {
        "components": components,
        "stage_details": stage_details,
        "total_power": {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in components.items()}
        }   
        print(output_data["total_power"])
    elif trigger == "new-process-button":
        details, stage_details = optimize_tm(components, stage_details)
        output_data = {
        "components": components,
        "stage_details": stage_details,
        "total_power": {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in components.items()}
        }   
        print(output_data["total_power"])
    elif trigger == '{"type":"editable-table","index":ALL}':
        for stage, comps in components.items():
            updated_stage_data = next(item for item in updated_data if item['index'] == stage)
            df = pd.DataFrame(updated_stage_data['data'])
            df.set_index("Component", inplace=True)
            components[stage] = df.to_dict(orient="index")
    return generate_table()


@app.callback(
    Output("download-json", "data"),
    Input("save-json", "n_clicks"),
    prevent_initial_call=True
)
# def save_to_json(n_clicks):
#     return dict(content=json.dumps(components, indent=4), filename="components.json")
def save_to_json(n_clicks):
    # Include stage details and total power in the JSON data
    output_data = {
        "components": components,
        "stage_details": stage_details,
        "total_power": {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in components.items()}
    }
    return dict(content=json.dumps(output_data, indent=4), filename="components.json")


@app.callback(
    [Output("component-row", "style"), Output("material-row", "style"), Output("od-row", "style"), Output("id-row", "style"), Output("length-row", "style"), Output("power-row", "style")],
    Input("type", "value")
)
def toggle_fields(entry_type):
    if entry_type == "Component":
        return {"display": "block"}, {"display": "block"}, {"display": "block"}, {"display": "block"}, {"display": "block"}, {"display": "none"}
    elif entry_type == "Other":
        return {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "block"}
    return {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}


@app.callback(
    Output("table-container", "children", allow_duplicate=True),
    Input({"type": "editable-table", "index": ALL}, "data"),
    prevent_initial_call=True
)

def update_table_data(data):
    global components
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    for item in ctx.inputs_list[0]:
        stage = item["id"]["index"]
        updated_data = pd.DataFrame(item["value"]).set_index("Component").to_dict(orient="index")
        for comp, details in updated_data.items():
            for key, value in details.items():
                if key in ["OD", "ID", "length", "number", "Power per Part (W)", "Power Total (W)"]:
                    try:
                        updated_data[comp][key] = float(value)
                    except ValueError:
                        updated_data[comp][key] = 0.0
        components[stage] = updated_data
    
    return generate_table()


def generate_table():
    tables = []
    for stage, comps in components.items():
        if comps:
            df = pd.DataFrame.from_dict(comps, orient="index").reset_index().rename(columns={'index': 'Component'})
            total_power = df["Power Total (W)"].sum()
            tables.append(html.H3(f"{stage} - High Temp: {stage_details[stage]['highT']:.2e} K, Low Temp: {stage_details[stage]['lowT']:.2e} K - (Total Power: {total_power:.2e} W)",
                        style={
                        "color": "#1e3799",  # Example color
                        "fontSize": "24px",  # Example font size
                        "marginTop": "20px",  # Example margin top
                        "fontWeight": "bold",  # Example font weight
                        "textAlign": "center",  # Example text alignment
                        "backgroundColor": "#AEC6CF",  # Example background color
                        "padding": "8px",  # Example padding
                        "borderRadius": "5px"  # Example border radius
                    }))
            tables.append(dash_table.DataTable(
                id={"type": "editable-table", "index": stage},
                columns=[{"name": col, "id": col, "editable": True} for col in df.columns],
                data=df.to_dict('records'),
                editable=True
            ))
    return tables


if __name__ == "__main__":
    app.run_server(debug=True)
