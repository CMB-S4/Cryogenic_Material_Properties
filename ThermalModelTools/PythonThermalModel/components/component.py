# components/component.py


class Component:
    def __init__(self, name, properties=None):
        self.name = name
        self.properties = properties if properties is not None else {}

        self.comp_type = properties.get("Type", "Unknown")
        self.material = properties.get("Material", "Unknown")
        self.interpolate = properties.get("Interpolate", False)
        self.fit_choice = properties.get("Fit Choice", "None")
        self.OD = properties.get("OD", 0.0)
        self.ID = properties.get("ID", 0.0)
        self.length = properties.get("Length", 0.0)
        self.number = properties.get("Number", 1)


    def update_property(self, key, value):
        self.properties[key] = value
    
    def __repr__(self):
        return f"Component(name={self.name}, properties={self.properties})"
