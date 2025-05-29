# stages/stage.py
class Stage:
    def __init__(self, name, high_temp=270.0, low_temp=70.0, power=None, color=None, components=None, stages=None):
        self.name = name
        self.high_temp = high_temp if high_temp is not None else 300.0  # Default to 25.0 if no temperature is provided
        self.low_temp = low_temp if low_temp is not None else 300.0  # Default to 25.0 if no temperature is provided
        self.power = power if power is not None else 0.0  # Default to 0.0 if no power is provided"
        self.color = color if color is not None else "#FFFFFF"  # Default to white if no color is provided
        self.components = components if components is not None else []
        self.stages = stages if stages is not None else []

    def add_component(self, component):
        self.components.append(component)

    def add_stage(self, stage):
        self.stages.append(stage)

    def __repr__(self):
        return f"Stage(name={self.name}, highT={self.high_temp}, lowT={self.low_temp}, power={self.power}, color={self.color}, components={self.components}, stages={self.stages})"
