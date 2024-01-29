from dataclasses import dataclass


@dataclass
class GameControllerState:
    a: bool
    b: bool
    x: bool
    y: bool
    dpad_down: bool
    dpad_up: bool
    dpad_left: bool
    dpad_right: bool
    bumper_l: bool
    bumper_r: bool
    stop: bool
    restart: bool
    right_y: float
    right_x: float
    left_y: float
    left_x: float
    trigger_l: float
    trigger_r: float

    def to_xrc_control_strings(self) -> str:
        
        control_string = "// Written by SimBridge\n"
        control_string += f"a= {1 if self.a else 0}\n"
        control_string += f"b= {1 if self.b else 0}\n"
        control_string += f"x= {1 if self.x else 0}\n"
        control_string += f"y= {1 if self.y else 0}\n"
        control_string += f"dpad_down= {1 if self.dpad_down else 0}\n"
        control_string += f"dpad_up= {1 if self.dpad_up else 0}\n"
        control_string += f"dpad_left= {1 if self.dpad_left else 0}\n"
        control_string += f"dpad_right= {1 if self.dpad_right else 0}\n"
        control_string += f"bumper_l= {1 if self.bumper_l else 0}\n"
        control_string += f"bumper_r= {1 if self.bumper_r else 0}\n"
        control_string += f"stop= {1 if self.stop else 0}\n"
        control_string += f"restart= {1 if self.restart else 0}\n"

        control_string += f"right_y= {self.right_y:.3f}\n"
        control_string += f"right_x= {self.right_x:.3f}\n"
        control_string += f"left_y= {self.left_y:.3f}\n"
        control_string += f"left_x= {self.left_x:.3f}\n"
        control_string += f"trigger_l= {self.trigger_l:.3f}\n"
        control_string += f"trigger_r= {self.trigger_r:.3f}\n"

        return control_string
