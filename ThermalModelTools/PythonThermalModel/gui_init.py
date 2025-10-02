import os

### Not Needed in this environment
def define_CMR_path():
    # Save the path_to_cmr to a file
    path_to_cmr = input("Enter the path to CMR: ")
    config_file = os.path.join(os.path.dirname(__file__), 'cmr_path.txt')

    try:
        with open(config_file, 'w') as f:
            f.write(path_to_cmr)
        
    except PermissionError:
        print("Permission denied, please specify a valid path to save cmr_path.txt.")
        save_path = input("Enter a valid path to save cmr_path.txt: ")
        with open(os.path.join(save_path, 'cmr_path.txt'), 'w') as f:
            f.write(path_to_cmr)
        return os.path.join(save_path, 'cmr_path.txt')
    return config_file

def init_gui():
    """
    Initializes the GUI for the thermal model.
    This function sets up the environment and runs the Streamlit app.
    """
    # Ensure the necessary directories exist
    gui_path = os.path.join(os.path.dirname(__file__), 'thermal_model_gui.py')
    print(gui_path)
    if not os.path.exists(gui_path):
        raise FileNotFoundError(f"GUI file {gui_path} does not exist.")
    # Run the Streamlit app
    print("Starting the Streamlit GUI...")
    os.system(f"streamlit run {gui_path}")