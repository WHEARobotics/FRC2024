import wpilib
import wpilib.drive
import logging

from makoboard import Makoboard
from vision import VisionState
from robotstateteleop import RobotStateTeleop
from controllers import Controllers
from crescendofield import CrescendoField
from robotstateautonomous import RobotStateAutonomous
from robotstatedisabled import RobotStateDisabled
from robotstatemachine import RobotStateMachine
from vision import Vision  # Vision file import
from crescendodrivetrain import CrescendoSwerveDrivetrain, CrescendoSwerveDrivetrainState
from intake import Intake, IntakeState
from shooter import Shooter, ShooterState
from wpilib import DriverStation


def initialize_simulated_components(desired_auto_x, speaker_x):
    # TODO: Replace these with mock objects
    return CrescendoSwerveDrivetrain(), Intake(), Shooter(), Controllers(), Vision(desired_auto_x, speaker_x)


def initialize_real_components(desired_auto_x, speaker_x):
    return CrescendoSwerveDrivetrain(), Intake(), Shooter(), Controllers(), Vision(desired_auto_x, speaker_x)


def output_to_smart_dashboard(swerve_state: CrescendoSwerveDrivetrainState, shooter_state: ShooterState,
                              intake_state: IntakeState):
    """
    This puts the raw values of the encoder
    on the SmartDashboard as DB/String[0-8].
    """
    # down below is code setting up the DB buttons. they are found in the smart dashboard basic tab and we can push
    # them through the
    # dashboard to do a few actions, in this case changing between different string values.
    sd_button_1 = wpilib.SmartDashboard.getBoolean("New Name 0", False)
    sd_button_2 = wpilib.SmartDashboard.getBoolean("DB/Button 1", False)
    sd_button_3 = wpilib.SmartDashboard.getBoolean("DB/Button 2", False)
    sd_button_4 = wpilib.SmartDashboard.getBoolean("DB/Button 3", False)

    if sd_button_1:
        wpilib.SmartDashboard.putString('DB/String 0', "Enc Back Left {:4.3f}".format(
            swerve_state.back_left.corrected_motor_position))
        wpilib.SmartDashboard.putString('DB/String 1', "Enc Back Right {:4.3f}".format(
            swerve_state.back_right.corrected_motor_position))
        wpilib.SmartDashboard.putString('DB/String 2', "Enc Front Left {:4.3f}".format(
            swerve_state.front_left.corrected_motor_position))
        wpilib.SmartDashboard.putString('DB/String 3', "Enc Front Right {:4.3f}".format(
            swerve_state.front_right.corrected_motor_position))

        wpilib.SmartDashboard.putString('DB/String 5',
                                        f"Turn motor pos BL  {swerve_state.back_left.turn_motor_position:4.1f}")
        wpilib.SmartDashboard.putString('DB/String 6',
                                        f"Turn motor pos BR  {swerve_state.back_right.turn_motor_position:4.1f}")
        wpilib.SmartDashboard.putString('DB/String 7',
                                        f"Turn motor pos FL  {swerve_state.front_left.turn_motor_position:4.1f}")
        wpilib.SmartDashboard.putString('DB/String 8',
                                        f"Turn motor pos FR  {swerve_state.front_right.turn_motor_position:4.1f}")

        wpilib.SmartDashboard.putString('DB/String 9', f"Gyro Angle  {swerve_state.yaw:4.1f}")
        # swerve drive preset with absolute and motor encoder poses with gyro

    elif sd_button_2:
        # wpilib.SmartDashboard.putString('DB/String 0',
        #                                 f"shooter_pos_deg {shooter_state.encoder_degrees:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 1', f"wrist_pos_deg {intake_state.wrist_encoder_pos:1.3f}")

        wpilib.SmartDashboard.putString('DB/String 2',
                                        f"shooter_abs_deg {shooter_state.absolute_encoder_pos:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 3', f"limit_switch {intake_state.wrist_limit_switch_pos:1.3f}")

        # wpilib.SmartDashboard.putString('DB/String 5', f"des_shooter_pos{shooter_state.shooter_desired_pos:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 6', f"des_wrist_pos{intake_state.wrist_desired_pos:1.3f}")

        # wpilib.SmartDashboard.putString('DB/String 7',
        #                                 f"shooter_speed_rpm{shooter_state.shooter_flywheel_speed:4.1f}")

        wpilib.SmartDashboard.putString('DB/String 8',
                                        "wrist_position {:4.0f}".format(intake_state.wrist_encoder_pos))
        # wpilib.SmartDashboard.putString('DB/String 9',
        #                                 "shooter_pivot_action {:4.0f}".format(shooter_state.shooter_pivot_control))
    # shooter and intake preset with the intake and shooter motor poses + limit switch value and abs shooter encoder pos

    elif sd_button_3:
        pass
    # vision preset with botpose: x, y, yaw(the other values are not important to us), disred angle to speaker,
    # distance to speaker, desired pitch needed to get to the speaker, and more later.
    elif sd_button_4:

        wpilib.SmartDashboard.putString('DB/String 0', f"gyro_pos{swerve_state.yaw:4.1f}")

        # wpilib.SmartDashboard.putString('DB/String 1',
        #                                 f"shooter_pos_deg {shooter_state.shooter_encoder_degrees:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 2', f"wrist_pos_deg {intake_state.wrist_encoder_pos:1.3f}")

        wpilib.SmartDashboard.putString('DB/String 3', f"limit_switch {intake_state.wrist_limit_switch_pos:1.3f}")
        # wpilib.SmartDashboard.putString('DB/String 4',
        #                                 f"shooter_speed_rpm{shooter_state.shooter_flywheel_speed:4.1ff}")

        # wpilib.SmartDashboard.putString('DB/String 5',f"gyro+bot_yaw_diff{self.:4.1f}")
        # set this up to see the difference between the pigeon and botpose yaw we cant add because vision is not
        # fully complete

        # also figure out how to get the meters per second speed o swerve modules.

    # competition preset to have values needed duting competition like the intake + shooter angle, gyro angle,
    # desired pitch, angle to speaker, the limit switch value, and anything else
    else:
        pass
    # this will be used for just testing and to print anything we want when a smart dashboard button is not pushed


class ObjectOrientedRobot(wpilib.TimedRobot):
    field: CrescendoField

    # Components
    swerve: CrescendoSwerveDrivetrain
    intake: Intake
    shooter: Shooter
    controllers: Controllers
    vision: Vision

    # Visualization
    shuffleboard: Makoboard

    # State machine
    robot_state_machine: RobotStateMachine

    def robotInit(self):
        """ Robot initialization. Run once on startup. Do all one-time
        initialization here."""

        logging.basicConfig(level=logging.DEBUG)
        self.field = CrescendoField(DriverStation.getAlliance())
        desired_auto_x = self.field.desired_x_for_autonomous_driving
        speaker_x = self.field.speaker_x

        logging.info(f"Robot is in simulation: {wpilib.RobotBase.isSimulation()}")
        self.swerve, self.intake, self.shooter, self.controllers, self.vision = \
            initialize_simulated_components(desired_auto_x, speaker_x) if wpilib.RobotBase.isSimulation() \
            else initialize_real_components(desired_auto_x, speaker_x)

        self.shuffleboard = Makoboard(self.swerve)
        self.shuffleboard.set_bot_position(3, 3, 45)

        self.robot_state_machine = RobotStateMachine(RobotStateDisabled(self))

    def read_component_states(self) -> (CrescendoSwerveDrivetrainState, ShooterState, IntakeState, VisionState):
        """
        Read the states of all the components and return them as a tuple.
        """

        swerve_encoder_state = self.swerve.get_state()
        shooter_state = self.shooter.get_state()
        intake_state = self.intake.get_state()
        vision_state = self.vision.get_state()
        return swerve_encoder_state, shooter_state, intake_state, vision_state

    def read_absolute_encoders_and_output_to_smart_dashboard(self):
        """
        This function basically combine the two function above

        It's vital that this function be called periodically, that is, 
        in both `disabledPeriodic` and `teleopPeriodic` and `autoPeriodic`
        """
        swerve_state, shooter_state, intake_state, vision_state = self.read_component_states()
        output_to_smart_dashboard(swerve_state, shooter_state, intake_state)
        self.shuffleboard.swerve.show(swerve_state)
        self.shuffleboard.shooter.show(shooter_state)
        self.shuffleboard.intake.show(intake_state)
        self.shuffleboard.vision.show(vision_state)
        self.shuffleboard.main.show(swerve_state, vision_state)

    def disabledInit(self):
        self.robot_state_machine.set_state(RobotStateDisabled(self))

    def disabledPeriodic(self):
        self.robot_state_machine.set_state(self.robot_state_machine.periodic(self))

    def disabledExit(self):
        pass

    def autonomousInit(self):
        self.robot_state_machine.set_state(RobotStateAutonomous(self))

    def autonomousPeriodic(self):
        next_state = self.robot_state_machine.periodic(self)
        # Note that `next_state` can be the same as (and often is!) the same as the current state
        self.robot_state_machine.set_state(next_state)

    def autonomousExit(self):
        pass

    def teleopInit(self):
        self.robot_state_machine.set_state(RobotStateTeleop(self))

    def teleopPeriodic(self):
        self.robot_state_machine.set_state(self.robot_state_machine.periodic(self))

    def teleopExit(self):
        pass


if __name__ == '__main__':
    wpilib.run(ObjectOrientedRobot)
