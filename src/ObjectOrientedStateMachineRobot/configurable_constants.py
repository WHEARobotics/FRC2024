from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigurableConstants:
    # Sets a factor for slowing down the overall speed. 1 is no modification. 2 is half-speed, etc.
    JOYSTICK_DRIVE_SLOWDOWN_FACTOR = 3
