import wpilib
import wpilib.drive
import wpimath
from wpilib import SmartDashboard, Field2d
from wpilib.shuffleboard import Shuffleboard, BuiltInWidgets
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d, Pose2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time
import math
import ntcore
import rev

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

        self.JOYSTICK_QUICKER_MOVE = 0.7

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

        self.wrist_encoder = self.intake.wrist_encoder.getPosition() * to_degrees
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
        self.current_wrist_position_widget.getEntry().setDouble(self.wrist_encoder)
        self.current_shooter_position_widget.getEntry().setDouble(self.shooter_encoder)
        self.desired_shooter_position_widget.getEntry().setDouble(self.wrist_desired_pos)
        self.desired_shooter_position_widget.getEntry().setDouble(self.shooter_desired_pos)
        

        #TEMPORARY!
        

        #     wpilib.SmartDashboard.putString('DB/String 5',f"Turn motor pos BL  {self.turnmotor1:4.1f}")
        #     wpilib.SmartDashboard.putString('DB/String 6',f"Turn motor pos BR  {self.turnmotor4:4.1f}")
        #     wpilib.SmartDashboard.putString('DB/String 7',f"Turn motor pos FL  {self.turnmotor3:4.1f}")
        #     wpilib.SmartDashboard.putString('DB/String 8',f"Turn motor pos FR  {self.turnmotor2:4.1f}")

        # wpilib.SmartDashboard.putString('DB/String 7',f"Gyro Angle  {self.pigeon_yaw:4.1f}") 
        # # swerve drive preset with absolute and motor encoder poses with gyro
            
        # elif sd_button_2 == True:
        #     wpilib.SmartDashboard.putString('DB/String 0',f"shooter_pos_deg {self.shooter_encoder:1.3f}")
        #     wpilib.SmartDashboard.putString('DB/String 1',f"wrist_pos_deg {self.wrist_encoder:1.3f}")

        #     wpilib.SmartDashboard.putString('DB/String 2',f"shooter_abs_deg {self.shooter_absolute_encoder_pos:1.3f}")
        #     wpilib.SmartDashboard.putString('DB/String 3',f"limit_switch {self.wrist_limit_switch:1.3f}")

        #     wpilib.SmartDashboard.putString('DB/String 5',f"des_shooter_pos{self.shooter_desired_pos:1.3f}")
        #     wpilib.SmartDashboard.putString('DB/String 6',f"des_wrist_pos{self.wrist_desired_pos:1.3f}")

        #     wpilib.SmartDashboard.putString('DB/String 7',f"shooter_speed_rpm{self.shooter_flywheel_speed:4.1f}")

        # wpilib.SmartDashboard.putString('DB/String 4',"wrist_action {:4.0f}".format( self.wrist_position))
        # wpilib.SmartDashboard.putString('DB/String 5',"shooter_pivot_action {:4.0f}".format( self.shooter_pivot_control))
        # # shooter and intake preset with the intake and shooter motor poses + limit switch value and abs shooter encoder pos
            
        # elif sd_button_3 == True:
        #     pass
        # # vision preset with botpose: x, y, yaw(the other values are not important to us), disred angle to speaker, distance to speaker,
        # # desired pitch needed to get to the speaker, and more later.
        # elif sd_button_4 == True:
            
        #     wpilib.SmartDashboard.putString('DB/String 0',f"gyro_pos{self.pigeon:4.1f}")

        #     wpilib.SmartDashboard.putString('DB/String 1',f"shooter_pos_deg {self.shooter_encoder:1.3f}")
        #     wpilib.SmartDashboard.putString('DB/String 2',f"wrist_pos_deg {self.wrist_encoder:1.3f}")

        #     wpilib.SmartDashboard.putString('DB/String 3',f"limit_switch {self.wrist_limit_switch:1.3f}")
        #     wpilib.SmartDashboard.putString('DB/String 4',f"shooter_speed_rpm{self.shooter_flywheel_speed:4.1f}")

            # wpilib.SmartDashboard.putString('DB/String 5',f"gyro+bot_yaw_diff{self.:4.1f}")
            # set this up to see the difference between the pigeon and botpose yaw we cant add because vision is not fully complete

            # also figure out how to get the meters per second speed o swerve modules.

        # competition preset to have values needed duting competition like the intake + shooter angle, gyro angle, desired pitch,
        # angle to speaker, the limit switch value, and anything else
        # else:
        #     pass
        # this will be used for just testing and to print anything we want when a smart dashboard button is not pushed

       
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

        # print (f"the limit switch says it is{self.intake.wrist_limit_switch.get()}")

        # we can set the motors to make sure they are on break when disabled

    def disabledExit(self):
        pass

    def autonomousInit(self):
        """ Initialize for autonomous here."""
        self.autonomous_state = self.AUTONOMOUS_STATE_AIMING

        self.auto_state = 1
        self.shooter_pivot_auto = 0
        self.shooter_control_auto = 0
        self.shooter_kicker_auto = 0
        
        self.wiggleTimer.reset()
        self.wiggleTimer.start()

    def autonomous_periodic_aiming(self, botpose):
            
            x = botpose[0]
            y = botpose[1]
            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 

            desired_direction = self.calculate_desired_direction(desired_yaw, current_yaw)
            wpilib.SmartDashboard.putString("DB/String 0", str(x))    
            wpilib.SmartDashboard.putString("DB/String 1", str(y))
            #wpilib.SmartDashboard.putString("DB/String 2", f"{desired_direction:3.1f}")    
            
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

        if self.auto_state == 1:
            self.shooter_control_auto = ShooterControlCommands.shooter_wheel_outtake
            self.shooter_pivot_auto = ShooterPivotCommands.shooter_pivot_sub_action
            if self.wiggleTimer.advanceIfElapsed(2):
                self.auto_state = 2
        if self.auto_state == 2:
            self.shooter_kicker_auto = ShooterKickerCommands.kicker_shot
            self.shooter_control_auto = ShooterControlCommands.shooter_wheel_outtake
            if self.wiggleTimer.advanceIfElapsed(1.5):
                self.auto_state = 4
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
        # elif self.auto_state == 3:
        #     self.shooter_kicker_auto = ShooterKickerCommands.kicker_idle
        #     self.shooter_control_auto = ShooterControlCommands.shooter_wheel_idle
        #     self.x_speed = 0.15
            # if self.wiggleTimer.advanceIfElapsed(3):
            #     self.auto_state = 4
        elif self.auto_state == 4:
            self.shooter_kicker_auto = ShooterKickerCommands.kicker_idle
            self.shooter_control_auto = ShooterControlCommands.shooter_wheel_idle
            self.x_speed = 0.0
            self.wiggleTimer.reset()
        
        self.swerve.drive(self.x_speed, 0, 0, True)
        self.shooter.periodic(0, self.shooter_pivot_auto, self.shooter_control_auto, self.shooter_kicker_auto)
        # self.shooter_control = 2 # this sets the shooter to always spin at shooting speed
        # during the whole autonomous gamemode.
            
        if self.is_botpose_valid(self.botpose):
            if self.autonomous_state == self.AUTONOMOUS_STATE_AIMING:
                self.autonomous_periodic_aiming(self.botpose)
            elif self.autonomous_state == self.AUTONOMOUS_STATE_SPEAKER_SHOOTING:
                self.autonomous_periodic_shooting(self.botpose)
        else:
           wpilib.SmartDashboard.putString("DB/String 0", str("noBotpose")) 

        self.swerve.drive(self.x_speed, self.y_speed, self.rot, True)   
        # wrist positions for intake to move towards the requested location remove magic numbers!
        self.intake.periodic(self.wrist_position, self.intake_control)
        if self.is_botpose_valid(self.botpose):
            speaker_distance_m = self.distance_to_speaker(self.botpose[0], self.botpose[1], self.speaker_x, FieldPositions.speaker_y)
        else:
            # No botpose!
            speaker_distance_m = 0
        self.shooter.periodic(speaker_distance_m, self.shooter_pivot_control, self.shooter_control, self.kicker_action)

    def autonomousExit(self):
        pass

    def teleopInit(self):
        self.halfSpeed = True

        self.intake.wrist_motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.frontLeft.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.frontRight.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.backLeft.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.backRight.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

        self.intake_action = 1 # this action speeds up the intake motors to intake
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
        
        # if self.LeftBumper:
        #     self.intake_control = IntakeCommands.intake_action
        # elif self.RightBumper:
        #     self.intake_control = IntakeCommands.outtake_action
        # # else:
        #     self.intake_control = IntakeCommands.idle
        
        # we could use manual intake to do without changing the wrist to move the note farther in. i could be wrong and we might just want
        # to hold intake longer to push the note farther.
        

      

        if self.startButton:
            self.shooter_pivot_control = self.shooter_pivot_amp
        elif self.leftTrigger:
            self.shooter_pivot_control = self.shooter_pivot_sub
            self.wrist_position = WristAngleCommands.wrist_mid_action
        # changes the shooter pitch angle to pitch into the amp or subwoofer speaker angle
            
        # this state machine is used to check if we have the note in our kicker and we have let go of the intake to the kicker button
        # once we let go we want the state machine to set the state to 3 to kick it back for a bit away from the flywheels so they 
        # could speed up
                

        # the goal of this state machine is when the state has memory of intaking with the wrist and then after when the kicker intakes to
        # the shooter we check to see if the state has memory of both happening and we let go of the kicker intake button, the state completes
        # and the kicker adjusts the note back away from the flywheels. 
             
        # if self.kicker_state == 0: 
        # # we start by checking if we intook with the wristy
        #     if self.intake_control == IntakeCommands.intake_action:
        #        self.kicker_state = 1 
        # elif self.kicker_state == 1:
        # # we check to see if we have the wrist tucked back
        #     if self.intake.motor_pos_degrees < 5:
        #         self.kicker_state = 2
        # elif self.kicker_state == 2:
        # # we check to see if we started doing the kicker intake action
        #     if self.kicker_action == ShooterKickerCommands.kicker_intake:
        #         self.kicker_state = 3
        #     elif self.intake_control == IntakeCommands.intake_action:
        #         self.kicker_state = 0
        # elif self.kicker_state == 3:
        # # check to see if we finished intaking with the kicker and stopped
        #     if self.kicker_action != ShooterKickerCommands.kicker_intake:
        #         self.wiggleTimer.reset()
        #         self.wiggleTimer.start()
        #         self.kicker_state = 4
        # elif self.kicker_state == 4:
        # # adjusts the kicker to move the note back until the timer passes the 0.3 seconds
        #     if self.wiggleTimer.advanceIfElapsed(0.3): #0.3 seconds are change-able
        #         self.kicker_action = ShooterKickerCommands.kicker_idle
        #         self.kicker_state = 0
        #     else:
        #         self.kicker_action = ShooterKickerCommands.kicker_adjustment # 4

            
        # wrist positions for intake to move towards the requested location remove magic numbers!
        self.intake.periodic(self.wrist_position, self.intake_control)
        
        if self.is_botpose_valid(self.botpose):
            speaker_distance_m = self.distance_to_speaker(self.botpose[0], self.botpose[1], self.speaker_x, self.speaker_y)
        else:
            # No botpose!
            speaker_distance_m = 0
        self.shooter.periodic(speaker_distance_m, self.shooter_pivot_control, self.shooter_control, self.kicker_action)


         # self.botpose = self.vision.checkBotpose()


         # self.current_yaw = self.botpose[5]#getting the yaw from the self.botpose table
         # self.desired_yaw = 0 #where we want our yaw to go 

        self.Abutton = self.xbox.getAButton()
        self.Bbutton = self.xbox.getBButton()

        if self.xbox.getRightBumper() and self.xbox.getLeftBumper():
            self.swerve.gyro.set_yaw(0)
        
        if self.xbox.getRightTriggerAxis() > 0.85:
            self.joystick_divider = self.JOYSTICK_QUICKER_MOVE

        else:
            self.joystick_divider = self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR



        

        # wpilib.SmartDashboard.putString('DB/String 1',f"Desired angle: {self.desired_angle:.1f}")
        # wpilib.SmartDashboard.putString('DB/String 2', f"Current angle: {self.current_angle:.1f}")
        # wpilib.SmartDashboard.putString('DB/String 3', f"Desired Turn Count: {self.desired_turn_count:.1f}")

        # wpilib.SmartDashboard.putString('DB/String 4', f"abs_encoder_pos {self.correctedEncoderPosition():.3f}")
        

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

            # self.speaker_distance = self.distance_to_speaker(bot_x, bot_y, speaker_x, speaker_y)
            # #fills the distance to speaker function with its required values for the calculate pitch function

            # self.calculate_pitch = self.calculate_desired_pitch(self.speaker_distance, speaker_y)
            # #fills the calculate pitch function with necessary values to be properly called
            # pitch_in_degrees = self.radians_to_degrees(self.calculate_pitch)
            # #converts the pitch shooter angle to degrees from radians

            # wpilib.SmartDashboard.putString("DB/String 4", str(pitch_in_degrees))
          
           

            
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
        self.joystick_x = applyDeadband(self.joystick_x, 0.1)
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_y = applyDeadband(self.joystick_y, 0.1)
        joystick_rot = -self.xbox.getRightX()
        joystick_rot = applyDeadband(joystick_rot, 0.1)
        #joystick_rot = 180 * joystick_rot

        return self.joystick_x, self.joystick_y, joystick_rot
    def speeds_for_joystick_values(self, joystick_x, joystick_y, joystick_rot):
        x_speed = self.joystickscaling(joystick_y) / self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR
        y_speed = self.joystickscaling(joystick_x) / self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR
        rot = joystick_rot # TODO: Could add a joystickscaling here
        return x_speed, y_speed, rot

    def calculate_desired_direction(self, desired_angle, current_angle):
        if current_angle >180:
            current_angle = current_angle - 360
        if desired_angle >180:
            desired_angle = desired_angle - 360
        desired_direction = desired_angle - current_angle
        return desired_direction
    
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

    
    def joystickscaling(self, input): #this function helps bring an exponential curve in the joystick value and near the zero value it uses less value and is more flat
        a = 1
        output = a * input * input * input + (1 - a) * input
        return output
         

    def teleopExit(self):
        pass
    


if __name__ == '__main__':
    wpilib.run(Myrobot)

	