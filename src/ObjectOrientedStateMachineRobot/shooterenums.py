from dataclasses import dataclass


@dataclass(frozen=True)
class ShooterPivotCommandEnum:
    shooter_pivot_in_action = 1
    shooter_pivot_feeder_action = 2
    shooter_pivot_amp_action = 3
    shooter_pivot_sub_action = 4

    shooter_pivot_manual_up = 5
    shooter_pivot_manual_down = 6


@dataclass(frozen=True)
class ShooterKickerCommandEnum:
    kicker_intake = 1
    kicker_amp_shot = 2
    kicker_shot = 3
    kicker_adjustment = 4
    kicker_idle = 0


@dataclass(frozen=True)
class ShooterControlCommandsEnum:
    shooter_wheel_idle = 1
    shooter_wheel_intake = 2
    shooter_wheel_outtake = 3
