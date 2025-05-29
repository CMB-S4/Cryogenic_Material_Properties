# components/component.py
class Component:
    def __init__(self, name, properties=None):
        self.name = name
        self.properties = properties if properties is not None else {}

    def update_property(self, key, value):
        self.properties[key] = value

    def __repr__(self):
        return f"Component(name={self.name}, properties={self.properties})"
