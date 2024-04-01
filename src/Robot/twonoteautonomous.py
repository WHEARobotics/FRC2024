from dataclasses import dataclass

from Robot.intake import WristAngleCommands, IntakeCommands
from Robot.shooter import ShooterControlCommands, ShooterPivotCommands, ShooterKickerCommands
from autobaseclass import AutoBaseClass, AutonomousControls

@dataclass(frozen=True)
class AutoState_TwoNote:
    ShooterWheelOuttake = 1
    KickerShot = 2
    Rollback = 3
    RollbackComplete = 4
    Idle = 5
    IntakeNoteFromFloor = 6
    IntakeNoteInAir = 7
    Handoff = 8
    KickerIntakeIdle = 9
    End = 10

class TwoNoteAutonomous(AutoBaseClass):
    def intake_auto_action(self, intake_action: int) -> tuple[WristAngleCommands, IntakeCommands]:
        if intake_action == 1:
            intake_control_auto = IntakeCommands.intake_action
            wrist_control_auto = WristAngleCommands.wrist_intake_action
        elif intake_action == 2:
            intake_control_auto = IntakeCommands.intake_action
            wrist_control_auto = WristAngleCommands.wrist_stow_action
        else:
            intake_control_auto = IntakeCommands.idle
            wrist_control_auto = WristAngleCommands.wrist_stow_action
    
        self.debug_string_widget.getEntry().setString(
            f"iac({intake_action}) : {self.wrist_control_auto}, {self.intake_control_auto}")
        return (wrist_control_auto, intake_control_auto)
    
    
    def shooter_auto_action(self, shooter_action: bool) -> tuple[
        ShooterControlCommands, ShooterPivotCommands, WristAngleCommands]:
        if shooter_action:
            shooter_control_auto = ShooterControlCommands.shooter_wheel_outtake
            shooter_pivot_auto = ShooterPivotCommands.shooter_pivot_sub_action
            wrist_control_auto = WristAngleCommands.wrist_mid_action
        else:
            shooter_pivot_auto = ShooterPivotCommands.shooter_pivot_feeder_action
            shooter_control_auto = ShooterControlCommands.shooter_wheel_idle
            wrist_control_auto = self.wrist_control_auto
        return (shooter_control_auto, shooter_pivot_auto, wrist_control_auto)
    
    def kicker_auto_action(self, kicker_action: int = 0) -> tuple[
        ShooterKickerCommands, IntakeCommands]:  # use 1 for shooting, 2 for intaking, 0 for idle
        if kicker_action == 1:
            shooter_kicker_auto = ShooterKickerCommands.kicker_shot
        elif kicker_action == 2:
            shooter_kicker_auto = ShooterKickerCommands.kicker_intake_slower
            intake_control_auto = IntakeCommands.outtake_action
        else:
            shooter_kicker_auto = ShooterKickerCommands.kicker_idle
            intake_control_auto = IntakeCommands.idle
        return (shooter_kicker_auto, intake_control_auto)
     
    def periodic(self) -> AutonomousControls:
        if self.auto_state == AutoState_TwoNote.ShooterWheelOuttake:
            self.shooter_auto_action(True)
            if self.wiggleTimer.advanceIfElapsed(0.75):
                self.auto_state = AutoState_TwoNote.KickerShot
        # state 1 sets the shooter flywheels up and the shooter_pivot moves to sub angle
        elif self.auto_state == AutoState_TwoNote.KickerShot:
            self.kicker_auto_action(1)
            if self.wiggleTimer.advanceIfElapsed(0.5):
                self.auto_state = AutoState_TwoNote.Rollback
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
        # state 2 sets the kicker to outtake the note
        elif self.auto_state == AutoState_TwoNote.Rollback:
            self.kicker_auto_action(0)
            self.shooter_auto_action(False)
            self.x_speed = 0.18
            self.intake_auto_action(1)
            if self.wiggleTimer.advanceIfElapsed(1.6):
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
                if self.double_shot_finished:
                    self.auto_state = AutoState_TwoNote.End
                else:
                    self.auto_state = AutoState_TwoNote.RollbackComplete
        # state 3 stop kicker and start moving back and intake
        elif self.auto_state == AutoState_TwoNote.RollbackComplete:
            self.x_speed = 0.0
            self.auto_state = AutoState_TwoNote.Idle
            self.wiggleTimer.reset()
        # stop robot moving
        elif self.auto_state == AutoState_TwoNote.Idle:
            self.x_speed = 0.0
            if self.wiggleTimer.advanceIfElapsed(0.2):
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
                self.auto_state = AutoState_TwoNote.IntakeNoteFromFloor
        # idle state for 0.2 seconds
        elif self.auto_state == AutoState_TwoNote.IntakeNoteFromFloor:
            self.intake_auto_action(2)
            self.x_speed = -0.17
            if self.wiggleTimer.advanceIfElapsed(1.3):
                self.auto_state = AutoState_TwoNote.IntakeNoteInAir
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
        # intake stops and goes back in
        elif self.auto_state == AutoState_TwoNote.IntakeNoteInAir:
            self.intake_auto_action(3)
            self.intake_control_auto = IntakeCommands.intake_action
            if self.wiggleTimer.advanceIfElapsed(0.3):
                self.auto_state = AutoState_TwoNote.Handoff
        # intake again to make sure its in
        elif self.auto_state == AutoState_TwoNote.Handoff:
            self.x_speed = 0.0
            self.kicker_auto_action(2)
            if self.wiggleTimer.advanceIfElapsed(0.8):
                self.auto_state = AutoState_TwoNote.KickerIntakeIdle
        # kicker intake handoff
        elif self.auto_state == AutoState_TwoNote.KickerIntakeIdle:
            self.kicker_auto_action(0)
            self.double_shot_finished = True
            self.auto_state = AutoState_TwoNote.ShooterWheelOuttake
        elif self.auto_state == AutoState_TwoNote.End:
            # Final state. Just make it explicit.
            self.x_speed = 0.0
        else:
            self.x_speed = 0.0
            self.shooter_auto_action(False)
            self.intake_auto_action(0)
    
        # This isn't used yet, but notice that it contains all the values that will be passed to the drive, shooter, and intake
        return AutonomousControls(
            x_drive_pct=self.x_speed, y_drive_pct=0, rot_drive_pct=0,
            distance_to_speaker_m=0,
            shooter_pivot_command=self.shooter_pivot_auto, shooter_control_command=self.shooter_control_auto,
            kicker_command=self.shooter_kicker_auto,
            wrist_command=self.wrist_control_auto,
            intake_command=self.intake_control_auto)