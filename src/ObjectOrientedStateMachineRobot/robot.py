import wpilib
import wpilib.drive
from wpimath import applyDeadband

from configurable_constants import ConfigurableConstants
from controllers import Controllers
from crescendofield import CrescendoField
from robotstateautonomous import RobotStateAutonomous
from robotstatedisabled import RobotStateDisabled
from robotstatemachine import RobotStateMachine
from vision import Vision #Vision file import
from crescendordrivetrain import CrescendoSwerveDrivetrain, CrescendoSwerveDrivetrainState
from intake import Intake, WristAngleCommands, IntakeCommands, IntakeState
from shooter import Shooter, ShooterState
from wpilib import DriverStation
import logging


def initialize_simulated_components():
    # TODO: Replace these with mock objects
    return CrescendoSwerveDrivetrain(), Intake(), Shooter(), Controllers

def initialize_real_components():
    return CrescendoSwerveDrivetrain(), Intake(), Shooter(), Controllers

def outputToSmartDashboard(swerve_state: CrescendoSwerveDrivetrainState, shooter_state: ShooterState,
                           intake_state: IntakeState):
    """
    This puts the raw values of the encoder
    on the SmartDashboard as DB/String[0-8].
    """
    # down below is code setting up the DB buttons. they are found in the smart dashboard basic tab and we can push them through the
    # dashboard to do a few actions, in this case changing between different string values.
    sd_button_1 = wpilib.SmartDashboard.getBoolean("New Name 0", False)
    sd_button_2 = wpilib.SmartDashboard.getBoolean("DB/Button 1", False)
    sd_button_3 = wpilib.SmartDashboard.getBoolean("DB/Button 2", False)
    sd_button_4 = wpilib.SmartDashboard.getBoolean("DB/Button 3", False)

    if sd_button_1 == True:
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

    elif sd_button_2 == True:
        wpilib.SmartDashboard.putString('DB/String 0',
                                        f"shooter_pos_deg {shooter_state.shooter_encoder_degrees:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 1', f"wrist_pos_deg {intake_state.wrist_encoder_pos:1.3f}")

        wpilib.SmartDashboard.putString('DB/String 2',
                                        f"shooter_abs_deg {shooter_state.shooter_absolute_encoder_pos:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 3', f"limit_switch {intake_state.wrist_limit_switch_pos:1.3f}")

        wpilib.SmartDashboard.putString('DB/String 5', f"des_shooter_pos{shooter_state.shooter_desired_pos:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 6', f"des_wrist_pos{intake_state.wrist_desired_pos:1.3f}")

        wpilib.SmartDashboard.putString('DB/String 7',
                                        f"shooter_speed_rpm{shooter_state.shooter_flywheel_speed:4.1f}")

        wpilib.SmartDashboard.putString('DB/String 8',
                                        "wrist_position {:4.0f}".format(intake_state.wrist_encoder_pos))
        wpilib.SmartDashboard.putString('DB/String 9',
                                        "shooter_pivot_action {:4.0f}".format(self.shooter_pivot_control))
    # shooter and intake preset with the intake and shooter motor poses + limit switch value and abs shooter encoder pos

    elif sd_button_3 == True:
        pass
    # vision preset with botpose: x, y, yaw(the other values are not important to us), disred angle to speaker, distance to speaker,
    # desired pitch needed to get to the speaker, and more later.
    elif sd_button_4 == True:

        wpilib.SmartDashboard.putString('DB/String 0', f"gyro_pos{swerve_state.yaw:4.1f}")

        wpilib.SmartDashboard.putString('DB/String 1',
                                        f"shooter_pos_deg {shooter_state.shooter_encoder_degrees:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 2', f"wrist_pos_deg {intake_state.wrist_encoder_pos:1.3f}")

        wpilib.SmartDashboard.putString('DB/String 3', f"limit_switch {intake_state.wrist_limit_switch_pos:1.3f}")
        wpilib.SmartDashboard.putString('DB/String 4',
                                        f"shooter_speed_rpm{shooter_state.shooter_flywheel_speed:4.1ff}")

        # wpilib.SmartDashboard.putString('DB/String 5',f"gyro+bot_yaw_diff{self.:4.1f}")
        # set this up to see the difference between the pigeon and botpose yaw we cant add because vision is not fully complete

        # also figure out how to get the meters per second speed o swerve modules.

    # competition preset to have values needed duting competition like the intake + shooter angle, gyro angle, desired pitch,
    # angle to speaker, the limit switch value, and anything else
    else:
        pass
    # this will be used for just testing and to print anything we want when a smart dashboard button is not pushed


class Myrobot(wpilib.TimedRobot):

    def robotInit(self):
        """ Robot initialization. Run once on startup. Do all one-time
        initialization here."""

        logging.basicConfig(level=logging.DEBUG)

        logging.info(f"Robot is in simulation: {wpilib.RobotBase.isSimulation()}")
        self.swerve, self.intake, self.shooter, self.controllers = \
            initialize_simulated_components() if wpilib.RobotBase.isSimulation() \
            else initialize_real_components()

        self.robot_state_machine = RobotStateMachine(RobotStateDisabled(self))
        self.field = CrescendoField(DriverStation.getAlliance())

        # this checks wether we have set ourselves through the smartdashbard our alliance side and color. for vision we want to check to change
        # the x value to use the same april tags but use them as if we were on either side of the field.
        self.vision = Vision(self.desired_x_for_autonomous_driving, self.speaker_x)
        # gets the vision class and sets the arguments in init to be used in the file

        # Autonomous state machine
        self.AUTONOMOUS_STATE_AIMING = 1
        self.AUTONOMOUS_STATE_SPEAKER_SHOOTING = 2
        self.autonomous_state = self.AUTONOMOUS_STATE_AIMING

        # Initialize commands sent to the mechanisms.
        self.wrist_position = WristAngleCommands.wrist_stow_action
        self.intake_control = IntakeCommands.idle

        self.shooter_control = 0

        self.shooter_pivot_control = 0

        self.kicker_action = 0

        self.kicker_outtake = 1

        self.x_speed = 0.0
        self.y_speed = 0.0
        self.rot = 0.0
        # speed values for the swerve to be changed throughout the different states to drive
        # it would be a good idea to set them in every state and make sure they are 0.0 when we dont want to move

        self.wiggleTimer = wpilib.Timer()
        

    def read_component_states(self) -> (CrescendoSwerveDrivetrainState, ShooterState, IntakeState):
        '''
        getting necessary values to be able to send the values to the smart dashboard to be able to be viewed.
        '''

        swerve_encoder_state = self.swerve.read_state()()
        shooter_state = self.shooter.read_state()
        intake_state = self.intake.read_state()
        return swerve_encoder_state, shooter_state, intake_state
    

    def readAbsoluteEncodersAndOutputToSmartDashboard(self) :
        """
        This function basically combine the two function above

        It's vital that this function be called periodically, that is, 
        in both `disabledPeriodic` and `teleopPeriodic` and `autoPeriodic`
        """
        swerve_state, shooter_state, intake_state = self.read_component_states()
        outputToSmartDashboard (swerve_state, shooter_state, intake_state)

       
    # def calculateDegreesFromAbsoluteEncoderValue(self, absEncoderValue):
    #     """
    #     This returns the absolute encoder value as a 0 to 360, not from 0 to 1
    #     """
    #     return absEncoderValue * 360
            
    def disabledInit(self):
        self.robot_state_machine.set_state(RobotStateDisabled(self))

    def disabledPeriodic(self):
        self.robot_state_machine.periodic()
    def disabledExit(self):
        self.robot_state_machine.finalize()

    def autonomousInit(self):
        self.robot_state_machine.set_state(RobotStateAutonomous(self))

    def autonomousPeriodic(self):
        self.robot_state_machine.periodic()

    def autonomousExit(self):
        self.robot_state_machine.finalize()

    def teleopInit(self):
        self.robot_state_machine.set_state(RobotStateTeleop(self))


    def teleopPeriodic(self):
        self.robot_state_machine.periodic()


    # def calculate_desired_direction(self, desired_angle, current_angle):
    #     if current_angle >180:
    #         current_angle = current_angle - 360
    #     if desired_angle >180:
    #         desired_angle = desired_angle - 360
    #     desired_direction = desired_angle - current_angle
    #     return desired_direction
    
    # def robot_april_tag_orientation(self, rotation, desired_angle, current_angle):
    #     desired_state = (0.0, Rotation2d(0.0))
    #     if not current_angle > 0 and not current_angle < 1:
    #         self.frontLeft.setDesiredState(desired_state, True)
    #         self.frontRight.setDesiredState(desired_state, True)
    #         self.backLeft.setDesiredState(desired_state, True)
    #         self.backRight.setDesiredState(desired_state, True)
    #     elif current_angle > 0:
    #         desired_state = 
    # random stuff will be worked on later



    def teleopExit(self):
        self.robot_state_machine.finalize()
    


if __name__ == '__main__':
    wpilib.run(Myrobot)
    # sys.argv[0] = 'robotpy sim --main D:\src\lobrien\FRC2024\src\ObjectOrientedStateMachineRobot\robot.py'
    # main()
	#