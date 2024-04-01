import abc
from dataclasses import dataclass

from wpimath.units import meters
from intake import WristAngleCommands, IntakeCommands
from shooter import ShooterControlCommands, ShooterKickerCommands, ShooterPivotCommands

@dataclass(frozen=True)
class AutonomousControls:
    x_drive_pct: float # -1 to 1
    y_drive_pct: float # -1 to 1
    rot_drive_pct: float # -1 to 1

    distance_to_speaker_m: meters
    shooter_pivot_command: ShooterPivotCommands
    shooter_control_command: ShooterControlCommands
    kicker_command: ShooterKickerCommands

    wrist_command: WristAngleCommands
    intake_command: IntakeCommands


class AutoBaseClass(abc.ABC):
    @abc.abstractmethod
    def periodic(self) -> AutonomousControls:
        pass