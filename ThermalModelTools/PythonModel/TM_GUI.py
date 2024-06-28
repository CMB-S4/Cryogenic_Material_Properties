# A GUI to help build a Thermal Model json
# Author: Henry Nachman + Copilot
#

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import json
import numpy as np
import os

class EditComponentDialog(simpledialog.Dialog):
    def __init__(self, parent, title, component, material, OD, ID, length, number):
        self.component = component
        self.material = material
        self.OD = OD
        self.ID = ID
        self.length = length
        self.number = number
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Component:").grid(row=0)
        tk.Label(master, text="Material:").grid(row=1)
        tk.Label(master, text="OD:").grid(row=2)
        tk.Label(master, text="ID:").grid(row=3)
        tk.Label(master, text="Length:").grid(row=4)
        tk.Label(master, text="Number:").grid(row=5)

        self.component_entry = tk.Entry(master)
        self.material_entry = tk.Entry(master)
        self.OD_entry = tk.Entry(master)
        self.ID_entry = tk.Entry(master)
        self.length_entry = tk.Entry(master)
        self.number_entry = tk.Entry(master)

        self.component_entry.grid(row=0, column=1)
        self.material_entry.grid(row=1, column=1)
        self.OD_entry.grid(row=2, column=1)
        self.ID_entry.grid(row=3, column=1)
        self.length_entry.grid(row=4, column=1)
        self.number_entry.grid(row=5, column=1)

        self.component_entry.insert(0, self.component)
        self.material_entry.insert(0, self.material)
        self.OD_entry.insert(0, self.OD)
        self.ID_entry.insert(0, self.ID)
        self.length_entry.insert(0, self.length)
        self.number_entry.insert(0, self.number)

        return self.component_entry  # initial focus

    def apply(self):
        self.component = self.component_entry.get()
        self.material = self.material_entry.get()
        self.OD = self.OD_entry.get()
        self.ID = self.ID_entry.get()
        self.length = self.length_entry.get()
        self.number = self.number_entry.get()

class CryoStage:
    def __init__(self, root):
        self.root = root
        style = ttk.Style(self.root)
        style.theme_use("clam")

        self.root.title("Cryogenic Thermal Stage")

        abspath = os.path.abspath(__file__)
        path_to_tcFiles = f"{os.path.split(abspath)[0]}{os.sep}"
        all_files = os.listdir(path_to_tcFiles)
        exist_files = [file for file in all_files if file.startswith("tc_fullrepo")]
        print(exist_files)
        tc_file_date = exist_files[0][-12:-4]

        TCdata = np.loadtxt(f"{path_to_tcFiles}{os.sep}tc_fullrepo_{tc_file_date}.csv", dtype=str, delimiter=',') # imports compilation file csv

        self.mat_list = list(TCdata[1:,0])
        
        # Create widgets
        self.component_label = tk.Label(root, text="Component:", font=("Times New Roman", 12))
        self.component_entry = tk.Entry(root)
        self.material_label = tk.Label(root, text="Material:", font=("Times New Roman", 12)) 
        self.material_entry = ttk.Combobox(state="readonly", values=self.mat_list)
        self.OD_label = tk.Label(root, text="OD (m):", font=("Times New Roman", 12))
        self.OD_entry = tk.Entry(root)
        self.ID_label = tk.Label(root, text="ID (m):", font=("Times New Roman", 12))
        self.ID_entry = tk.Entry(root)
        self.length_label = tk.Label(root, text="Length (m):", font=("Times New Roman", 12))
        self.length_entry = tk.Entry(root)
        self.number_label = tk.Label(root, text="Number:", font=("Times New Roman", 12))
        self.number_entry = tk.Entry(root)

        self.add_button = tk.Button(root, text="Add Component", command=self.add_component, width=20, font=("Times New Roman", 12))
        self.save_button = tk.Button(root, text="Save to JSON", command=self.save_to_json, width=20, font=("Times New Roman", 12))
        self.load_button = tk.Button(root, text="Load from JSON", command=self.load_from_json, width=20, font=("Times New Roman", 12))

        # Create a Treeview widget
        self.tree = ttk.Treeview(root, columns=("Component Name", "Material", "OD", "ID", "Length", "Number"))
        self.tree.heading("#1", text="Component Name")
        self.tree.heading("#2", text="Material")
        self.tree.heading("#3", text="OD")
        self.tree.heading("#4", text="ID")
        self.tree.heading("#5", text="Length")
        self.tree.heading("#6", text="Number")

        # Add an "Edit" button
        self.edit_button = tk.Button(root, text="Edit", command=self.edit_selected_book)

        # Pack widgets
        self.component_label.pack()
        self.component_entry.pack()
        self.material_label.pack()
        self.material_entry.pack()
        self.OD_label.pack()
        self.OD_entry.pack()
        self.ID_label.pack()
        self.ID_entry.pack()
        self.length_label.pack()
        self.length_entry.pack()
        self.number_label.pack()
        self.number_entry.pack()

        self.add_button.pack()
        self.save_button.pack()
        self.load_button.pack()
        self.tree.pack()
        self.edit_button.pack()

        # Initialize components dictionary
        self.components = {}

    def add_component(self):
        component = self.component_entry.get()
        material_index = self.material_entry.current()
        material = self.mat_list[material_index]
        OD = self.OD_entry.get()
        ID = self.ID_entry.get()
        length = self.length_entry.get()
        number = self.number_entry.get()
        if component and material:
            self.components[component] = {
                "material": material,
                "Dimensions": {"OD": OD, "ID": ID, "length": length},
                "number": number
            }
            self.component_entry.delete(0, tk.END)
            self.material_entry.set('')  # Reset the Combobox
            self.OD_entry.delete(0, tk.END)
            self.ID_entry.delete(0, tk.END)
            self.length_entry.delete(0, tk.END)
            self.number_entry.delete(0, tk.END)
            self.update_treeview()

    def save_to_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, "w") as json_file:
                json.dump(self.components, json_file, indent=4)
                print(f"Saved {len(self.components)} components to {filename}")
                print(f"Components saved: {self.components}")  # Print the components saved to JSON

    def load_from_json(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, "r") as json_file:
                self.components = json.load(json_file)
                print(f"Loaded {len(self.components)} components from {filename}")
                self.update_treeview()

    def update_treeview(self):
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        for component, details in self.components.items():
            self.tree.insert("", "end", values=(component, details["material"], details["Dimensions"]["OD"], details["Dimensions"]["ID"], details["Dimensions"]["length"], details["number"]))
        print(f"Updated components: {self.components}")  # Print updated components

    def edit_selected_book(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])["values"]
            component, material, OD, ID, length, number = values

            dialog = EditComponentDialog(self.root, "Edit Component", component, material, OD, ID, length, number)
            if dialog.component and dialog.OD and dialog.ID and dialog.length and dialog.number:
                # Remove the old component key if the component name was changed
                if dialog.component != component:
                    del self.components[component]

                self.components[dialog.component] = {
                    "material": dialog.material,
                    "Dimensions": {
                        "OD": dialog.OD,
                        "ID": dialog.ID,
                        "length": dialog.length
                    },
                    "number": dialog.number
                }

                self.update_treeview()
                print(f"Edited component: {self.components[dialog.component]}")  # Print the edited component
                # Optionally, re-select the edited item
                for item in self.tree.get_children():
                    if self.tree.item(item)["values"] == (dialog.component, dialog.material, dialog.OD, dialog.ID, dialog.length, dialog.number):
                        self.tree.selection_set(item)
                        break

if __name__ == "__main__":
    root = tk.Tk()
    app = CryoStage(root)
    root.mainloop()
