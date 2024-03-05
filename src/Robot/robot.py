import wpilib
import wpilib.drive
import wpimath
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time
import math
import rev

from vision import Vision #Vision file import
from CrescendoSwerveDrivetrain import CrescendoSwerveDrivetrain
from CrescendoSwerveModule import CrescendoSwerveModule
from intake import Intake
from shooter import Shooter
from wpilib import DriverStation


class Myrobot(wpilib.TimedRobot):

 

    def robotInit(self):
        """ Robot initialization. Run once on startup. Do all one-time
        initialization here."""

        self.vision = Vision()
        self.swerve = CrescendoSwerveDrivetrain()
        self.intake = Intake()
        self.shooter = Shooter()

        self.xbox = wpilib.XboxController(0)
        self.xbox_operator = wpilib.XboxController(1)

        # Sets a factor for slowing down the overall speed. 1 is no modification. 2 is half-speed, etc.
        self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR = 3

        self.speaker_y = 1.44 #m (either side)
        ally = DriverStation.getAlliance()
        if ally is not None:
            if ally == DriverStation.Alliance.kRed:
                self.speaker_x = 8.31
                self.desired_x_for_autonomous_driving = 5.5
                #set x value to the red side x
                pass
            elif ally == DriverStation.Alliance.kBlue:
                self.speaker_x = -8.31
                self.desired_x_for_autonomous_driving = -5.5
                #set the x value to the blue side
        else:
            self.speaker_x = 8.31
            self.desired_x_for_autonomous_driving = 5.5

        # Autonomous state machine
        self.AUTONOMOUS_STATE_AIMING = 1
        self.AUTONOMOUS_STATE_SPEAKER_SHOOTING = 2
        self.autonomous_state = self.AUTONOMOUS_STATE_AIMING

        self.wrist_position = 0 # position values for the wrist, intake and shooter

        self.intake_control = 0

        self.shooter_control = 0

        self.shooter_pivot_control = 0

        self.kicker_action = 0

        self.kicker_outtake = 1

        self.x_speed = 0.0
        self.y_speed = 0.0
        self.rot = 0.0

        
        
    
    def readAbsoluteEncoders(self) :
        """
        This reads the four absolute encoders position
        """
        self.absEnc1 = self.swerve.backLeft.correctedEncoderPosition()#* 360
        self.absEnc2 = self.swerve.frontRight.correctedEncoderPosition()# * 360
        self.absEnc3 = self.swerve.frontLeft.correctedEncoderPosition()# * 360
        self.absEnc4 = self.swerve.backRight.correctedEncoderPosition()# * 360
        self.absEnc2b = self.swerve.frontRight.correctedEncoderPosition() * 360
        
        self.turnmotor1 = self.swerve.backLeft.turnMotorEncoder.getPosition() / (150.0/7.0) * 360
        self.turnmotor2 = self.swerve.frontRight.turnMotorEncoder.getPosition() / (150.0/7.0) * 360
        self.turnmotor3 = self.swerve.frontLeft.turnMotorEncoder.getPosition() / (150.0/7.0) * 360
        self.turnmotor4 = self.swerve.backRight.turnMotorEncoder.getPosition() / (150.0/7.0) * 360

        self.pigeon = self.swerve.gyro.get_yaw()

        self.shooter_absolute_encoder_pos = self.shooter.absolute_encoder_pos

        self.wrist_encoder = self.intake.wrist_encoder.getPosition()
    
        #It get the values of the internal encoder

    def outputToSmartDashboard(self) :
        """
        This puts the raw values of the encoder
        on the SmartDashboard as DB/String[0-8].
        """
        # self.trunNurmal = self.turnmotor4 % 360.0

        # wpilib.SmartDashboard.putString('DB/String 0',"Enc Back Left {:4.3f}".format( self.absEnc1))
        # wpilib.SmartDashboard.putString('DB/String 3',"Enc Front Right {:4.3f}".format( self.absEnc2))
        # wpilib.SmartDashboard.putString('DB/String 2',"Enc Front Left {:4.3f}".format( self.absEnc3))
        # wpilib.SmartDashboard.putString('DB/String 1',"Enc Back Right {:4.3f}".format( self.absEnc4))
        # wpilib.SmartDashboard.putString('DB/String 0',"Enc FR angel {:4.3f}".format( self.absEnc2b))

        wpilib.SmartDashboard.putString('DB/String 0',"Wrist Enc {:4.3f}".format(self.wrist_encoder))


        # wpilib.SmartDashboard.putString('DB/String 5',f"Turn motor pos BL  {self.turnmotor1:4.1f}")
        # wpilib.SmartDashboard.putString('DB/String 8',f"Turn motor pos FR  {self.turnmotor2:4.1f}")
        # wpilib.SmartDashboard.putString('DB/String 7',f"Turn motor pos FL  {self.turnmotor3:4.1f}")
        # wpilib.SmartDashboard.putString('DB/String 6',f"Turn motor pos BR  {self.turnmotor4:4.1f}")
        # wpilib.SmartDashboard.putString('DB/String 9',f"Back right Nurmal  {self.trunNurmal:4.1f}")
        # wpilib.SmartDashboard.putString('DB/String 9',f"Gyro Angle  {self.pigeon:4.1f}")
        # wpilib.SmartDashboard.putString('DB/String 8',f"Botpose thinks angle is {self.botpose[5]:4.1f}")
        # wpilib.SmartDashboar.putString('DB/String 7', f"Gyro<->Botpose disagreement {self.pigeon-self.botpose[5]:4.1f}")

      

        # wpilib.SmartDashboard.putString('DB/String 7',f"Turn motor pos FL  {self.shooter.shooter_pivot_encoder.getPosition():4.1f}")
        

        
        # This is the internal turning motor encoder position.
        

        # wpilib.SmartDashboard.putString('DB/String 5', f"Back left deg: {self.calculateDegreesFromAbsoluteEncoderValue(self.absEnc1):.0f}")
        # wpilib.SmartDashboard.putString('DB/String 6', f"Front right deg: {self.calculateDegreesFromAbsoluteEncoderValue(self.absEnc2):.0f}")
        # wpilib.SmartDashboard.putString('DB/String 7', f"Front left deg: {self.calculateDegreesFromAbsoluteEncoderValue(self.absEnc3):.0f}")
        # wpilib.SmartDashboard.putString('DB/String 8', f"Back right deg: {self.calculateDegreesFromAbsoluteEncoderValue(self.absEnc4):.0f}")
        wpilib.SmartDashboard.putString('DB/String 9', f"shooter_pos {self.shooter_absolute_encoder_pos:1.3f}")

       
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

    def disabledExit(self):
        pass

    def autonomousInit(self):
        """ Initialize for autonomous here."""
        self.autonomous_state = self.AUTONOMOUS_STATE_AIMING
        

    def autonomous_periodic_aiming(self, botpose):
            

            x = botpose[0]
            y = botpose[1]
            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 

            desired_direction = self.calculate_desired_direction(desired_yaw, current_yaw)
            wpilib.SmartDashboard.putString("DB/String 0", str(x))    
            wpilib.SmartDashboard.putString("DB/String 1", str(y))
            wpilib.SmartDashboard.putString("DB/String 2", f"{desired_direction:3.1f}")    
            
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
        print("NOT IMPLEMENTED")
        pass


    def autonomousPeriodic(self):
        self.botpose = self.vision.checkBotpose()
        self.shooter_control = 2 # this sets the shooter to always spin at shooting speed
        # during the whole autonomous gamemode.
            
        if None != self.botpose and len(self.botpose) > 0 :
            if self.autonomous_state == self.AUTONOMOUS_STATE_AIMING:
                self.autonomous_periodic_aiming(self.botpose)
            elif self.autonomous_state == self.AUTONOMOUS_STATE_SPEAKER_SHOOTING:
                self.autonomous_periodic_shooting(self.botpose)
        else:
           wpilib.SmartDashboard.putString("DB/String 0", str("noBotpose")) 

        self.swerve.drive(self.x_speed, self.y_speed, self.rot, True)   
        # wrist positions for intake to move towards the requested location remove magic numbers!
        self.intake.periodic(self.wrist_position, self.intake_control)
        if self.botpose is not None and len(self.botpose) > 1:
            speaker_distance_m = self.distance_to_speaker(self.botpose[0], self.botpose[1], self.speaker_x, self.speaker_y)
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

        self.shooter_pivot_start = 1 # this pivots the shooter into a 0 degree angle
        self.shooter_pivot_max = 2 # this pivots the shooter into a 90 degree angle
        self.shooter_pivot_sub = 3 # this pivots the shooter into a 180 degree angle
        self.shooter_pivot_manual_up = 4 # this manually pivots the shooter up
        self.shooter_pivot_manual_down = 5 # this manually pivots the shooter down

        self.shooter_action_intake = 1 # this action moves the shooter motors to intake
        self.shooter_action_outtake = 2 # this action moves the shooter motors to outtake
        self.shooter_action_kicker = 3 # this action moves the kicker motors and feed the note into the shooter
        self.kicker_shoot = 2


        
        self.percent_output = 0.1

       
        # is used to go to else, stopping the motor

    def teleopPeriodic(self):
        self.driveWithJoystick(True)
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

        if self.Xbutton:
            self.shooter_control = self.shooter_action_intake
        elif self.Ybutton:
            self.shooter_control = self.shooter_action_outtake
        else:
            self.shooter_control = 0

        if self.rightTrigger:
            self.kicker_action = self.kicker_outtake
        elif self.leftTrigger:
            self.kicker_action = self.kicker_shoot
        else:
            self.kicker_action = 0


        # we commented out this for now because we dont want any position control for our first robot tests
        if self.leftStickButton:
            self.shooter_pivot_control = self.shooter_pivot_manual_up
        elif self.rightStickButton:
            self.shooter_pivot_control = self.shooter_pivot_manual_down
        else:
            self.shooter_pivot_control = 0

        

        if self.Abutton:
            self.wrist_position = self.wrist_intake_action
            self.intake_control = self.intake_action
        elif self.Bbutton:
            self.intake_control = self.outtake_action
            self.wrist_position = 0
            self.kicker_action = 1
        #     pass
        else:
            self.intake_control = 0 
            self.wrist_position = 0
            # this stops the motor from moving
        
        if self.LeftBumper:
            self.intake_control = self.intake_action
        elif self.RightBumper:
            self.intake_control = self.outtake_action
        # else:
        #     self.intake_control = 0
        

      
        if self.Bbutton:
            self.shooter_pivot_control = 2
        elif self.startButton:
            self.shooter_pivot_control = 3
        # elif self.LeftBumper:
        #     self.shooter_pivot_control = 4
        
        # elif self.LeftBumper:
        #     self.wrist_position = 0
        #     self.intake_control = 0
        # elif not self.Abutton or not self.Bbutton or not self.LeftBumper:
        #     self.wrist_position = 0
        #     self.intake_control = 0

        # if self.Xbutton:
        #     shooter_control = 1
        # elif self.Ybutton:
        #     shooter_control = 2
        # if self.rightTrigger:
        #     shooter_control = 3
        # elif not self.Ybutton:
        #     shooter_control = 0
 

        # wpilib.SmartDashboard.putString('DB/String 2',"intake control {:4.0f}".format( self.intake_control))
        # wpilib.SmartDashboard.putString('DB/String 3',"wrist pos {:4.0f}".format( self.wrist_position))
        wpilib.SmartDashboard.putString('DB/String 6',"shooter action {:4.0f}".format( self.shooter_control))
        wpilib.SmartDashboard.putString('DB/String 2',"shooter action {:4.0f}".format( self.shooter_pivot_control))
        
            
        # wrist positions for intake to move towards the requested location remove magic numbers!
        self.intake.periodic(self.wrist_position, self.intake_control)
        
        if self.botpose is not None and len(self.botpose) > 1:
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

        

        # wpilib.SmartDashboard.putString('DB/String 1',f"Desired angle: {self.desired_angle:.1f}")
        # wpilib.SmartDashboard.putString('DB/String 2', f"Current angle: {self.current_angle:.1f}")
        # wpilib.SmartDashboard.putString('DB/String 3', f"Desired Turn Count: {self.desired_turn_count:.1f}")

        # wpilib.SmartDashboard.putString('DB/String 4', f"abs_encoder_pos {self.correctedEncoderPosition():.3f}")
        

        if None != self.botpose and len(self.botpose) > 0 :
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

            self.speaker_distance = self.distance_to_speaker(bot_x, bot_y, speaker_x, speaker_y)
            #fills the distance to speaker function with its required values for the calculate pitch function

            self.calculate_pitch = self.calculate_desired_pitch(self.speaker_distance, speaker_y)
            #fills the calculate pitch function with necessary values to be properly called
            pitch_in_degrees = self.radians_to_degrees(self.calculate_pitch)
            #converts the pitch shooter angle to degrees from radians

            wpilib.SmartDashboard.putString("DB/String 4", str(pitch_in_degrees))
          
           

            
            desired_direction = self.calculate_desired_direction(desired_yaw, current_yaw)
            wpilib.SmartDashboard.putString("DB/String 2", f"{desired_direction:3.1f}")
            if abs(desired_direction) < 1.0:
                wpilib.SmartDashboard.putString("DB/String 3", "Shoot, you fools!")
            else:
                wpilib.SmartDashboard.putString("DB/String 3", "Hold!"  )
        else:
            # wpilib.SmartDashboard.putString("DB/String 0", "No botpose")
            pass
    
    
    def driveWithJoystick(self, fieldRelativeParam: bool) -> None:
        
        # allow joystick to be off from center without giving input

        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_x = applyDeadband(self.joystick_x , 0.1)
        self.joystick_y = applyDeadband(self.joystick_y , 0.1)

        rot = -self.xbox.getRightX()
        rot = applyDeadband(rot, 0.15)

        x_speed = self.joystickscaling(self.joystick_y) / self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR
        y_speed = self.joystickscaling(self.joystick_x) / self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR

        #Unused : self.magnitude = math.sqrt(self.joystick_x*self.joystick_x + self.joystick_y*self.joystick_y)/3
    
        self.swerve.drive(x_speed, y_speed, rot, fieldRelativeParam)
        '''
        this uses our joystick inputs and accesses a swerve drivetrain function to use field relative and the swerve module to drive the robot.
        '''
        
      

         
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

	