import wpilib
import wpilib.drive
import wpimath
from wpilib import SmartDashboard, Field2d, SendableChooser
from wpilib.shuffleboard import Shuffleboard, BuiltInWidgets
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d, Pose2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time
import math
from dataclasses import dataclass
import ntcore
import rev
from wpimath.units import meters

from vision import Vision #Vision file import
from CrescendoSwerveDrivetrain import CrescendoSwerveDrivetrain
from CrescendoSwerveModule import CrescendoSwerveModule
from intake import Intake, WristAngleCommands, IntakeCommands
from shooter import Shooter, ShooterControlCommands, ShooterKickerCommands, ShooterPivotCommands
from wpilib import DriverStation
from dataclasses import dataclass

@dataclass(frozen=True)
class FieldPositions:
    speaker_x_red = 8.31
    speaker_x_blue = -8.31
    speaker_y = 1.44

    desired_x_for_autonomous_driving_red = 5.5
    desired_x_for_autonomous_driving_blue = -5.5

@dataclass(frozen=True)
class AutoPlan:
    ONE_NOTE = 3
    ONE_NOTE_PORT = 2
    ONE_NOTE_STARBOARD = 1
    TWO_NOTE_CENTER = 0

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

@dataclass(frozen=True)
class AutoState_OneNote:
    ShooterWheelOuttake = 1
    KickerShot = 2
    RollbackAndPivot = 3
    RollbackOutOfZone = 5
    RollbackComplete = 6
    End = 7


class Myrobot(wpilib.TimedRobot):
    def robotInit(self):
        """ Robot initialization. Run once on startup. Do all one-time
        initialization here."""

        self.swerve = CrescendoSwerveDrivetrain()
        self.intake = Intake()
        self.shooter = Shooter()

        self.xbox = wpilib.XboxController(0)
        self.xbox_operator = wpilib.XboxController(1)

        # Sets a factor for slowing down the overall speed. 1 is no modification. 2 is half-speed, etc.
        self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR = 1.0

        self.JOYSTICK_QUICKER_MOVE = 0.5

        self.joystick_divider = self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR

        #Temporary:
        networktables_instance = ntcore.NetworkTableInstance.getDefault()
        smartdashboard_table = networktables_instance.getTable("SmartDashboard")
        botposeTopic = smartdashboard_table.getTopic("Field/Robot")
        self.botposeentry = botposeTopic.getGenericEntry()
        self.botposeentry.set(ntcore.Value.makeFloatArray([3.0, 5.0, 1.0]))

        
        ally = DriverStation.getAlliance()
        if ally is not None:
            if ally == DriverStation.Alliance.kRed:
                self.speaker_x = FieldPositions.speaker_x_red
                self.desired_x_for_autonomous_driving = FieldPositions.desired_x_for_autonomous_driving_red
                #set x value to the red side x
                pass
            elif ally == DriverStation.Alliance.kBlue:
                self.speaker_x = FieldPositions.speaker_x_blue
                self.desired_x_for_autonomous_driving = FieldPositions.desired_x_for_autonomous_driving_blue
                #set the x value to the blue side
        else:
            print("No alliance found, defaulting to red")
            self.speaker_x = FieldPositions.speaker_x_red
            self.desired_x_for_autonomous_driving = FieldPositions.desired_x_for_autonomous_driving_red
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

        wpilib.CameraServer.launch()

        self.shuffle_tab = Shuffleboard.getTab("status")
        self.gyro_widget = self.shuffle_tab.add("gyro", 0).withWidget(BuiltInWidgets.kGyro).withSize(2,2)
        self.joystick_rot_widget = self.shuffle_tab.add("joystick rot", 0).withWidget(BuiltInWidgets.kGyro).withSize(2,2)
        self.turn_motor_widgets = []
        self.turn_motor_widgets.append(self.shuffle_tab.add("turn motor 1", 0).withPosition(5, 1))
        self.turn_motor_widgets.append(self.shuffle_tab.add("turn motor 2", 0).withPosition(6,1))
        self.turn_motor_widgets.append(self.shuffle_tab.add("turn motor 3", 0).withPosition(7,1))
        self.turn_motor_widgets.append(self.shuffle_tab.add("turn motor 4", 0).withPosition(8,1))
        self.encoder_widgets = []
        self.encoder_widgets.append(self.shuffle_tab.add("bl encoder 1", 0).withPosition(5,2))
        self.encoder_widgets.append(self.shuffle_tab.add("fr encoder 2", 0).withPosition(6,2))
        self.encoder_widgets.append(self.shuffle_tab.add("br encoder 3", 0).withPosition(7,2))
        self.encoder_widgets.append(self.shuffle_tab.add("br encoder 4", 0).withPosition(8,2))
        self.current_wrist_position_widget = self.shuffle_tab.add("Current Wrist Pos", 0).withWidget(BuiltInWidgets.kGyro).withSize(2,2).withPosition(2,3)
        self.current_shooter_position_widget = self.shuffle_tab.add("Current Shooter Pos", 0).withWidget(BuiltInWidgets.kGyro).withSize(2,2).withPosition(7, 3)
        self.desired_wrist_position_widget = self.shuffle_tab.add("Desired Wrist Position", 0).withWidget(BuiltInWidgets.kGyro).withSize(2,2).withPosition(0, 3)
        self.desired_shooter_position_widget = self.shuffle_tab.add("Desired Shooter Position", 0).withWidget(BuiltInWidgets.kGyro).withSize(2,2).withPosition(5,3)
        self.optical_sensor_widget = self.shuffle_tab.add("Optical sensor", False).withWidget(BuiltInWidgets.kBooleanBox).withPosition(7,0)
        self.debug_string_widget = self.shuffle_tab.add("Debug", "").withPosition(6 , 6).withSize(7,1)
        self.auto_chooser_widget = SendableChooser()
        self.auto_chooser_widget.setDefaultOption("One-note STARBOARD", AutoPlan.ONE_NOTE_STARBOARD)
        self.auto_chooser_widget.addOption("One-note PORT", AutoPlan.ONE_NOTE_PORT)
        self.auto_chooser_widget.addOption("Two note middle", AutoPlan.TWO_NOTE_CENTER)
        self.auto_chooser_widget.addOption("One-note", AutoPlan.ONE_NOTE)
        self.shuffle_tab.add("Auto Selector", self.auto_chooser_widget).withSize(2, 1).withPosition(1, 2)
        self.auto_plan = self.auto_chooser_widget.getSelected()

        # Track state machines
        self.fsm_tab = Shuffleboard.getTab("State Machines")
        # self.autonomous_state_widget = self.fsm_tab.add("robot.autonomous_state", self.autonomous_state)
        # self.auto_state_widget = self.fsm_tab.add("robot.auto_state", self.auto_state)
    
    def readAbsoluteEncoders(self) :
        '''
        getting necessary values to be able to send the values to the smart dashboard to be able to be viewed.
        '''

        to_degrees = 360
        #constant set to set positions of encoders to degrees iff they measure 0-1

        self.absEnc1 = self.swerve.backLeft.correctedEncoderPosition()#* 360
        self.absEnc2 = self.swerve.frontRight.correctedEncoderPosition()# * 360
        self.absEnc3 = self.swerve.frontLeft.correctedEncoderPosition()# * 360
        self.absEnc4 = self.swerve.backRight.correctedEncoderPosition()# * 360
        self.absEnc2b = self.swerve.frontRight.correctedEncoderPosition() * 360
        
        self.turnmotor1 = self.swerve.backLeft.turnMotorEncoder.getPosition() / (150.0/7.0) * to_degrees
        self.turnmotor2 = self.swerve.frontRight.turnMotorEncoder.getPosition() / (150.0/7.0) * to_degrees
        self.turnmotor3 = self.swerve.frontLeft.turnMotorEncoder.getPosition() / (150.0/7.0) * to_degrees
        self.turnmotor4 = self.swerve.backRight.turnMotorEncoder.getPosition() / (150.0/7.0) * to_degrees

        self.pigeon_yaw = self.swerve.gyro.get_yaw()

        self.shooter_encoder = self.shooter.shooter_pivot_encoder.getPosition() * to_degrees
        self.shooter_absolute_encoder_pos = self.shooter.corrected_encoder_pos * to_degrees
        self.shooter_desired_pos = self.shooter.desired_angle
        self.shooter_flywheel_speed = self.shooter.shooter_wheel_encoder.getCountsPerRevolution()

        self.wrist_encoder_degrees = self.intake.wrist_encoder.getPosition() * to_degrees
        self.wrist_limit_switch = self.intake.wrist_limit_switch.get()
        self.wrist_desired_pos = self.intake.desired_angle

    def outputToSmartDashboard(self) :
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

        # if sd_button_1 == True:
        wpilib.SmartDashboard.putString('DB/String 0',"Enc Back Left {:4.3f}".format( self.absEnc1))
        wpilib.SmartDashboard.putString('DB/String 5',"Enc Back Right {:4.3f}".format( self.absEnc4))
        wpilib.SmartDashboard.putString('DB/String 4',"Enc Front Left {:4.3f}".format( self.absEnc3))
        wpilib.SmartDashboard.putString('DB/String 3',"Enc Front Right {:4.3f}".format( self.absEnc2))

        wpilib.SmartDashboard.putString('DB/String 7',"Optical sensor {:4.3f}".format(self.shooter.optical_sensor.get()))

        self.gyro_widget.getEntry().setDouble(self.swerve.gyro.get_yaw().value)
        joystick_x, joystick_y, joystick_rot = self.getJoystickDriveValues()
        joystick_deg = 180.0 * joystick_rot
        self.joystick_rot_widget.getEntry().setDouble(joystick_deg)
        self.turn_motor_widgets[0].getEntry().setDouble(self.turnmotor1)
        self.turn_motor_widgets[1].getEntry().setDouble(self.turnmotor2)
        self.turn_motor_widgets[2].getEntry().setDouble(self.turnmotor3)
        self.turn_motor_widgets[3].getEntry().setDouble(self.turnmotor4)
        self.encoder_widgets[0].getEntry().setDouble(self.absEnc1)
        self.encoder_widgets[1].getEntry().setDouble(self.absEnc2)
        self.encoder_widgets[2].getEntry().setDouble(self.absEnc3)
        self.encoder_widgets[3].getEntry().setDouble(self.absEnc4)
        self.current_wrist_position_widget.getEntry().setDouble(self.wrist_encoder_degrees)
        self.current_shooter_position_widget.getEntry().setDouble(self.shooter_encoder)
        self.desired_shooter_position_widget.getEntry().setDouble(self.wrist_desired_pos)
        self.desired_shooter_position_widget.getEntry().setDouble(self.shooter_desired_pos)
        self.optical_sensor_widget.getEntry().setBoolean(self.shooter.optical_sensor.get())

    def readAbsoluteEncodersAndOutputToSmartDashboard(self) :
        """
        This function basically combine the two function above

        It's vital that this function be called periodically, that is, 
        in both `disabledPeriodic` and `teleopPeriodic` and `autoPeriodic`
        """
        self.readAbsoluteEncoders()
        self.outputToSmartDashboard ()

       
    def calculateDegreesFromAbsoluteEncoderValue(self, absEncoderValue):
        """
        This returns the absolute encoder value as a 0 to 360, not from 0 to 1
        """
        return absEncoderValue * 360
            
    def disabledInit(self):
        pass

    def disabledPeriodic(self):
        self.readAbsoluteEncodersAndOutputToSmartDashboard()
        self.shooter.periodic(0, 0, 0, 0)

        self.intake.wrist_motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.frontLeft.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.frontRight.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.backLeft.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.backRight.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

        # we can set the motors to make sure they are on break when disabled

    def disabledExit(self):
        pass

    def autonomousInit(self):
        """ Initialize for autonomous here."""
        self.auto_plan = self.auto_chooser_widget.getSelected()

        self.autonomous_state = self.AUTONOMOUS_STATE_AIMING

        self.auto_state = 1
        self.shooter_pivot_auto = 0
        self.shooter_control_auto = 0
        self.shooter_kicker_auto = 0

        self.wrist_control_auto = 0
        self.intake_control_auto = 0

        self.shuffle_button_1 = True
        self.shuffle_button_2 = False
        self.shuffle_button_3 = False
        self.shuffle_button_4 = False
        
        self.wiggleTimer.reset()
        self.wiggleTimer.start()

        self.double_shot_finished = False

    def autonomous_periodic_aiming(self, botpose):
            x = botpose[0]
            y = botpose[1]
            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 

            desired_direction = self.calculate_desired_direction(desired_yaw, current_yaw)
            wpilib.SmartDashboard.putString("DB/String 0", str(x))    
            wpilib.SmartDashboard.putString("DB/String 1", str(y))

            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 
           

            direction_to_travel = self.calculate_desired_direction(desired_yaw, current_yaw)
            self.vision.get_rotation_autonomous_periodic_for_speaker_shot(self.botpose, current_yaw)

            if direction_to_travel < -1:
                self.intake.periodic(1, 1)
            elif direction_to_travel > 2:
                self.intake.periodic(3, 2)
            else:
               self.rot = 0.0
            # How can we tell that we have completed turning? When we do that
            # self.automous_state = self.AUTONOMOUS_STATE_SPEAKER_SHOOTING

    def autonomous_periodic_shooting(self, botpose):
        """
        this will get the angle needed for the shooter to be able to shoot from different positions by calculating through trig
        """
        print("NOT IMPLEMENTED")
        pass

    def is_botpose_valid(self, botpose):
        if botpose == None:
            return False
        if len(botpose) < 1:
            return False
        if botpose[0] == -1:
            return False
        if botpose[0] == 0 and botpose[1] == 0 and botpose[1] == 0:
            return False
        return True

    def autonomousPeriodic(self):
        self.botpose = self.vision.checkBotpose()

        def intake_auto_action(intake_action):
            if intake_action == 1:
                self.intake_control_auto = IntakeCommands.intake_action
                self.wrist_control_auto = WristAngleCommands.wrist_intake_action
            elif intake_auto_action == 2:
                self.wrist_control_auto = WristAngleCommands.wrist_stow_action
                self.intake_control_auto = IntakeCommands.intake_action
            else:
                self.intake_control_auto = IntakeCommands.idle
                self.wrist_control_auto = WristAngleCommands.wrist_stow_action

            self.debug_string_widget.getEntry().setString(f"iac({intake_action}) : {self.wrist_control_auto}, {self.intake_control_auto}")

        def shooter_auto_action(shooter_action : bool):
            if shooter_action:
                self.shooter_control_auto = ShooterControlCommands.shooter_wheel_outtake
                self.shooter_pivot_auto = ShooterPivotCommands.shooter_pivot_sub_action
                self.wrist_control_auto = WristAngleCommands.wrist_mid_action
            else:
                self.shooter_pivot_auto = ShooterPivotCommands.shooter_pivot_feeder_action
                self.shooter_control_auto = ShooterControlCommands.shooter_wheel_idle

        def kicker_auto_action(kicker_action = 0): # use 1 for shooting, 2 for intaking, 0 for idle
            if kicker_action == 1:
                self.shooter_kicker_auto = ShooterKickerCommands.kicker_shot
            elif kicker_action == 2:
                self.shooter_kicker_auto = ShooterKickerCommands.kicker_intake_slower
                self.intake_control_auto = IntakeCommands.outtake_action
            else:
                self.shooter_kicker_auto = ShooterKickerCommands.kicker_idle
                self.intake_control_auto = IntakeCommands.idle
            
        if self.auto_plan == AutoPlan.TWO_NOTE_CENTER:
            self.autonomous_state_machine_two_note_center(intake_auto_action, kicker_auto_action, shooter_auto_action)
        elif self.auto_plan == AutoPlan.ONE_NOTE_STARBOARD:
            self.autonomous_state_machine_one_note_starboard(intake_auto_action, kicker_auto_action, shooter_auto_action)
        elif self.auto_plan == AutoPlan.ONE_NOTE_PORT:
            self.autonomous_state_machine_one_note_port(intake_auto_action, kicker_auto_action, shooter_auto_action)
        elif self.auto_plan == AutoPlan.ONE_NOTE:
            self.autonomous_state_machine_one_note_port(intake_auto_action, kicker_auto_action, shooter_auto_action)
        else:
            raise ValueError("Unknown auto plan")

        self.swerve.drive(self.x_speed, self.y_speed, self.rot, True)
        print(f"Autoplan s {self.auto_plan} and Self.rot is {self.rot}")
        self.shooter.periodic(0, self.shooter_pivot_auto, self.shooter_control_auto, self.shooter_kicker_auto)
        self.intake.periodic(self.wrist_control_auto, self.intake_control_auto)

    def autonomous_state_machine_one_note_combined(self, intake_auto_action, kicker_auto_action, shooter_auto_action, is_starboard: bool):
        """
        This state machine is for autonomous shooting from the starboard side of the speaker.

        Face the speaker.
        If the robot is on the RIGHT side of the speaker, it is on the STARBOARD side. Otherwise, it's on the PORT side.
        """
        if self.auto_state == AutoState_OneNote.ShooterWheelOuttake:
            shooter_auto_action(1)
            if self.wiggleTimer.advanceIfElapsed(0.75):
                self.auto_state = AutoState_OneNote.KickerShot
        # state 1 sets the shooter flywheels up and the shooter_pivot moves to sub angle
        elif self.auto_state == AutoState_OneNote.KickerShot:
            kicker_auto_action(1)
            if self.wiggleTimer.advanceIfElapsed(0.5):
                if self.auto_plan != AutoPlan.ONE_NOTE:
                    self.auto_state = AutoState_OneNote.RollbackAndPivot
                else:
                    self.auto_state = AutoState_OneNote.End
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
        # state 2 sets the kicker to outtake the note
        elif self.auto_state == AutoState_OneNote.RollbackAndPivot:
            kicker_auto_action(0)
            shooter_auto_action(False)
            intake_auto_action(0)

            self.x_speed = 0.14
            self.y_speed = -0.15 if self.auto_plan == AutoPlan.ONE_NOTE_STARBOARD else + 0.15
            if self.wiggleTimer.advanceIfElapsed(1.9):
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
                self.auto_state = AutoState_OneNote.End
        # state 3 stop kicker and start moving back and intake
        elif self.auto_state == AutoState_OneNote.End:
            self.x_speed = 0.0
            self.y_speed = 0.0
            self.rot = 0.0
            self.wiggleTimer.reset()
            kicker_auto_action(0)
            shooter_auto_action(False)
            intake_auto_action(0)
        # stop robot moving

    def autonomous_state_machine_one_note_starboard(self, intake_auto_action, kicker_auto_action, shooter_auto_action):
        """
        This state machine is for autonomous shooting from the starboard side of the speaker.

        Face the speaker.
        If the robot is on the RIGHT side of the speaker, it is on the STARBOARD side. Otherwise, it's on the PORT side.
        """
        self.autonomous_state_machine_one_note_combined(intake_auto_action, kicker_auto_action, shooter_auto_action, is_starboard=True)

    def autonomous_state_machine_one_note_port(self, intake_auto_action, kicker_auto_action, shooter_auto_action):
        """
        This state machine is for autonomous shooting from the port side of the speaker.

        Face the speaker.
        If the robot is on the LEFT side of the speaker, it is on the PORT side. Otherwise, it's on the STARBOARD side.
        """
        self.autonomous_state_machine_one_note_combined(intake_auto_action, kicker_auto_action, shooter_auto_action, is_starboard=False)

    def autonomous_state_machine_two_note_center(self, intake_auto_action, kicker_auto_action, shooter_auto_action):
        if self.auto_state == AutoState_TwoNote.ShooterWheelOuttake:
            shooter_auto_action(1)
            if self.wiggleTimer.advanceIfElapsed(0.75):
                self.auto_state = AutoState_TwoNote.KickerShot
        # state 1 sets the shooter flywheels up and the shooter_pivot moves to sub angle
        elif self.auto_state == AutoState_TwoNote.KickerShot:
            kicker_auto_action(1)
            if self.wiggleTimer.advanceIfElapsed(0.5):
                self.auto_state = AutoState_TwoNote.Rollback
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
        # state 2 sets the kicker to outtake the note
        elif self.auto_state == AutoState_TwoNote.Rollback:
            kicker_auto_action(0)
            shooter_auto_action(False)
            self.x_speed = 0.18
            intake_auto_action(1)
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
            intake_auto_action(2)
            self.x_speed = -0.17
            if self.wiggleTimer.advanceIfElapsed(1.3):
                self.auto_state = AutoState_TwoNote.IntakeNoteInAir
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
        # intake stops and goes back in
        elif self.auto_state == AutoState_TwoNote.IntakeNoteInAir:
            intake_auto_action(3)
            self.intake_control_auto = IntakeCommands.intake_action
            if self.wiggleTimer.advanceIfElapsed(0.3):
                self.auto_state = AutoState_TwoNote.Handoff
        # intake again to make sure its in
        elif self.auto_state == AutoState_TwoNote.Handoff:
            self.x_speed = 0.0
            kicker_auto_action(2)
            if self.wiggleTimer.advanceIfElapsed(0.8):
                self.auto_state = AutoState_TwoNote.KickerIntakeIdle
        # kicker intake handoff
        elif self.auto_state == AutoState_TwoNote.KickerIntakeIdle:
            kicker_auto_action(0)
            self.double_shot_finished = True
            self.auto_state = AutoState_TwoNote.ShooterWheelOuttake
        elif self.auto_state == AutoState_TwoNote.End:
            # Final state. Just make it explicit.
            self.x_speed = 0.0
        else:
            self.x_speed = 0.0
            shooter_auto_action(False)
            intake_auto_action(0)

        # This isn't used yet, but notice that it contains all the values that will be passed to the drive, shooter, and intake
        return AutonomousControls(
            x_drive_pct=self.x_speed, y_drive_pct=0, rot_drive_pct=0,
            distance_to_speaker_m=0,
            shooter_pivot_command=self.shooter_pivot_auto, shooter_control_command=self.shooter_control_auto,
            kicker_command=self.shooter_kicker_auto,
            wrist_command=self.wrist_control_auto,
            intake_command=self.intake_control_auto)

    def autonomousExit(self):
        pass

    def teleopInit(self):
        self.halfSpeed = True

        self.intake.wrist_motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.frontLeft.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.frontRight.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.backLeft.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.backRight.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

        self.outtake_action = 2 # this action speeds up the intake motors to outtake
        self.wrist_intake_action = 2 # this action raises the wrist up
        self.wrist_in_action = 1 # this action puts the wrist down
        self.wrist_mid_action = 3 # action to move the intake to a position not in the way with the shooter and note

        self.shooter_pivot_start = 1 # this pivots the shooter into a 0 degree angle
        self.shooter_pivot_max = 2 # this pivots the shooter into a 90 degree angle
        self.shooter_pivot_amp = 3 # this pivots the shooter into a 180 degree angle
        self.shooter_pivot_sub = 4 # subwoofer angle to move the shooter to the sub angle
        self.shooter_pivot_manual_up = 5 # this manually pivots the shooter up
        self.shooter_pivot_manual_down = 6 # this manually pivots the shooter down

        self.shooter_action_intake = 2 # this action moves the shooter motors to intake
        self.shooter_action_shot = 3 # this action moves the shooter motors to outtake
        
        self.kicker_intake = 1 # this action moves the kicker motors and feed the note into the shooter
        self.kicker_amp_shot = 2 # this utilizes the kicker to shoot into the amp.
        self.kicker_shooter = 3 # this speeds up the kicker to be able to shoot with it at high speeds into the flywheels

        self.intake_idle = 0
        self.shooter_pivot_idle = 0
        self.shooter_flywheel_idle = 0
        self.wrist_idle = 0
        self.kicker_idle = 0

        self.wiggleTimer.reset()

        self.percent_output = 0.1

        self.kicker_state = 0


        # is used to go to else, stopping the motor

    def teleopPeriodic(self):

        self.driveWithJoystick()

        self.Abutton = self.xbox_operator.getAButton()
        self.Bbutton = self.xbox_operator.getBButton()
        self.Xbutton = self.xbox_operator.getXButton()
        self.Ybutton = self.xbox_operator.getYButton()
        self.RightBumper = self.xbox_operator.getRightBumper()
        self.LeftBumper = self.xbox_operator.getLeftBumper()
        self.leftStickButton = self.xbox_operator.getLeftStickButton()
        self.rightStickButton = self.xbox_operator.getRightStickButton()
        self.leftTrigger = self.xbox_operator.getLeftTriggerAxis()
        self.rightTrigger = self.xbox_operator.getRightTriggerAxis()
        self.startButton = self.xbox_operator.getStartButton()
        self.backButton = self.xbox_operator.getBackButton()

        self.readAbsoluteEncodersAndOutputToSmartDashboard()

        self.botpose = self.vision.checkBotpose()

        # we commented out this for now because we dont want any position control for our first robot tests
        if self.leftStickButton:
            self.shooter_pivot_control = ShooterPivotCommands.shooter_pivot_manual_up
        elif self.rightStickButton:
            self.shooter_pivot_control = ShooterPivotCommands.shooter_pivot_manual_down
        else:
            self.shooter_pivot_control = ShooterPivotCommands.shooter_pivot_idle

        if self.Abutton:
            self.wrist_position = WristAngleCommands.wrist_intake_action
            self.intake_control = IntakeCommands.intake_action
            self.shooter_pivot_control = ShooterPivotCommands.shooter_pivot_feeder_action
        elif self.Bbutton:
            self.wrist_position = WristAngleCommands.wrist_stow_action
            self.intake_control = IntakeCommands.outtake_action
            self.kicker_action = ShooterKickerCommands.kicker_intake
            self.shooter_pivot_control = 2
        # this is the button to transfer the note from the intake into the shooter kicker
        elif self.Xbutton:
            self.kicker_action = ShooterKickerCommands.kicker_amp_shot # amp shot to shoot into the amp
        elif self.rightTrigger:
            self.kicker_action = ShooterKickerCommands.kicker_shot
        elif self.LeftBumper:
            self.intake_control = IntakeCommands.outtake_shot_action
        elif self.RightBumper:
            self.intake_control = IntakeCommands.intake_action

        # this is used after holding y(the flywheel speeds) to allow the kicker move the note into the flywheels to shoot
        else:
            self.intake_control = IntakeCommands.idle
            self.wrist_position = WristAngleCommands.wrist_stow_action
            self.kicker_action = ShooterKickerCommands.kicker_idle
            # this stops the motor from moving

        if self.Ybutton:
            self.shooter_control = self.shooter_action_shot
        else:
            self.shooter_control = self.shooter_flywheel_idle
        # this button speeds up the shooter flywheels before shooting the note

        # we could use manual intake to do without changing the wrist to move the note farther in. i could be wrong and we might just want
        # to hold intake longer to push the note farther.

        if self.startButton:
            self.shooter_pivot_control = self.shooter_pivot_amp
        elif self.leftTrigger:
            self.shooter_pivot_control = self.shooter_pivot_sub
            self.wrist_position = WristAngleCommands.wrist_mid_action
        elif self.backButton:
            self.shooter_pivot_control = ShooterPivotCommands.shooter_under_chain_action

            
        # wrist positions for intake to move towards the requested location remove magic numbers!
        self.intake.periodic(self.wrist_position, self.intake_control)
        
        if self.is_botpose_valid(self.botpose):
            speaker_distance_m = self.vision.distance_to_speaker(self.botpose[0], self.botpose[1], self.speaker_x, 1.44)
        else:
            # No botpose!
            speaker_distance_m = 0
        self.shooter.periodic(speaker_distance_m, self.shooter_pivot_control, self.shooter_control, self.kicker_action)

        self.Abutton = self.xbox.getAButton()
        self.Bbutton = self.xbox.getBButton()

        if self.xbox.getRightBumper() and self.xbox.getLeftBumper():
            self.swerve.gyro.set_yaw(0)
        
        if self.xbox.getRightTriggerAxis() > 0.5:
            self.joystick_divider = self.JOYSTICK_QUICKER_MOVE
        else:
            self.joystick_divider = self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR

        if self.is_botpose_valid(self.botpose):
            x = self.botpose[0]
            y = self.botpose[1]
            wpilib.SmartDashboard.putString("DB/String 0", str(x))    
            wpilib.SmartDashboard.putString("DB/String 1", str(y))    
            
            current_yaw = self.botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 

            speaker_x = 6.5273#the x coordinate of the speaker marked in the field drawings in m.
            speaker_y = 1.98#height of the speaker in meters.

            bot_x = self.botpose[0]#the x coordinate from the botpose table
            bot_y = self.botpose[1]#the y pos from the botpose table

            desired_direction = self.calculate_desired_direction(desired_yaw, current_yaw)
            wpilib.SmartDashboard.putString("DB/String 2", f"{desired_direction:3.1f}")
            if abs(desired_direction) < 1.0:
                wpilib.SmartDashboard.putString("DB/String 3", "Shoot, you fools!")
            else:
                wpilib.SmartDashboard.putString("DB/String 3", "Hold!"  )
        else:
            # wpilib.SmartDashboard.putString("DB/String 0", "No botpose")
            pass

    def driveWithJoystick(self):
        # Step 1: Get the joystick values
        joystick_x, joystick_y, joystick_rot = self.getJoystickDriveValues()

        # Step 2: Calculate the speeds for the swerve
        x_speed, y_speed, rot = self.speeds_for_joystick_values(self.joystick_x, self.joystick_y, joystick_rot)

        #Unused : self.magnitude = math.sqrt(self.joystick_x*self.joystick_x + self.joystick_y*self.joystick_y)/3

        # Step 3: Drive the swerve with the desired speeds
        self.swerve.drive(x_speed, y_speed, rot, fieldRelative=True)
        '''
        this uses our joystick inputs and accesses a swerve drivetrain function to use field relative and the swerve module to drive the robot.
        '''

    def getJoystickDriveValues(self) -> tuple[float, float, float]:
        # allow joystick to be off from center without giving input

        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_x = applyDeadband(self.joystick_x, 0.05)
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_y = applyDeadband(self.joystick_y, 0.1)
        joystick_rot = -self.xbox.getRightX()
        joystick_rot = applyDeadband(joystick_rot, 0.1)

        return self.joystick_x, self.joystick_y, joystick_rot

    def speeds_for_joystick_values(self, joystick_x, joystick_y, joystick_rot):
        x_speed = self.joystickscaling(joystick_y) / self.joystick_divider
        y_speed = self.joystickscaling(joystick_x) / self.joystick_divider
        rot = joystick_rot # TODO: Could add a joystickscaling here
        return x_speed, y_speed, rot

    def calculate_desired_direction(self, desired_angle, current_angle):
        if current_angle >180:
            current_angle = current_angle - 360
        if desired_angle >180:
            desired_angle = desired_angle - 360
        desired_direction = desired_angle - current_angle
        return desired_direction

    def joystickscaling(self, input): #this function helps bring an exponential curve in the joystick value and near the zero value it uses less value and is more flat
        a = 1
        output = a * input * input * input + (1 - a) * input
        return output
         

    def teleopExit(self):
        pass
    


if __name__ == '__main__':
    wpilib.run(Myrobot)

	