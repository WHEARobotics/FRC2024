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


class Myrobot(wpilib.TimedRobot):

 

    def robotInit(self):

        self.xbox = wpilib.XboxController(0)


        self.vision = Vision()
        self.swerve = CrescendoSwerveDrivetrain()



        

        self.motor = rev.CANSparkMax(10, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.motor2 = rev.CANSparkMax(11, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.motor3 = rev.CANSparkMax(9, rev._rev.CANSparkLowLevel.MotorType.kBrushless)

        #self.motor.setInverted(True)
        self.motor.setInverted(False)
        #self.motor2.setInverted(True)  
        self.motor2.setInverted(True)
        self.motor3.setInverted(True)

        self.motor2.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.motor3.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)



        
        

        
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
    
        #It get the values of the internal encoder

    def outputToSmartDashboard(self) :
        """
        This puts the raw values of the encoder
        on the SmartDashboard as DB/String[0-8].
        """
        self.trunNurmal = self.turnmotor4 % 360.0

        wpilib.SmartDashboard.putString('DB/String 0',"Enc Back Left {:4.3f}".format( self.absEnc1))
        wpilib.SmartDashboard.putString('DB/String 3',"Enc Front Right {:4.3f}".format( self.absEnc2))
        wpilib.SmartDashboard.putString('DB/String 2',"Enc Front Left {:4.3f}".format( self.absEnc3))
        wpilib.SmartDashboard.putString('DB/String 1',"Enc Back Right {:4.3f}".format( self.absEnc4))
        # wpilib.SmartDashboard.putString('DB/String 0',"Enc FR angel {:4.3f}".format( self.absEnc2b))


        wpilib.SmartDashboard.putString('DB/String 5',f"Turn motor pos BL  {self.turnmotor1:4.1f}")
        wpilib.SmartDashboard.putString('DB/String 8',f"Turn motor pos FR  {self.turnmotor2:4.1f}")
        wpilib.SmartDashboard.putString('DB/String 7',f"Turn motor pos FL  {self.turnmotor3:4.1f}")
        wpilib.SmartDashboard.putString('DB/String 6',f"Turn motor pos BR  {self.turnmotor4:4.1f}")
        # wpilib.SmartDashboard.putString('DB/String 9',f"Back right Nurmal  {self.trunNurmal:4.1f}")
        wpilib.SmartDashboard.putString('DB/String 9',f"Gyro Angle  {self.pigeon:4.1f}")
        

        
        # This is the internal turning motor encoder position.
        

        # wpilib.SmartDashboard.putString('DB/String 5', f"Back left deg: {self.calculateDegreesFromAbsoluteEncoderValue(self.absEnc1):.0f}")
        # wpilib.SmartDashboard.putString('DB/String 6', f"Front right deg: {self.calculateDegreesFromAbsoluteEncoderValue(self.absEnc2):.0f}")
        # wpilib.SmartDashboard.putString('DB/String 7', f"Front left deg: {self.calculateDegreesFromAbsoluteEncoderValue(self.absEnc3):.0f}")
        # wpilib.SmartDashboard.putString('DB/String 8', f"Back right deg: {self.calculateDegreesFromAbsoluteEncoderValue(self.absEnc4):.0f}")

       
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
        pass

    def disabledExit(self):
        pass

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        botpose = self.vision.checkBotpose()
            

        if None != botpose and len(botpose) > 0 :
            x = botpose[0]
            y = botpose[1]
            wpilib.SmartDashboard.putString("DB/String 0", str(x))    
            wpilib.SmartDashboard.putString("DB/String 1", str(y))    
            
            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 
           
            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 
            direction_to_travel = self.calculate_desired_direction(desired_yaw, current_yaw)
            if direction_to_travel > 2:
                self.swerve.drive(0, 0, 0.2, True)
            elif direction_to_travel < 0:
                self.swerve.drive(0, 0, -0.2, True)
            else:
                self.swerve.drive(0, 0, 0.0, True)
        else:
           wpilib.SmartDashboard.putString("DB/String 0", str("noBotpose")) 
           self.swerve.drive(0, 0, 0.0, True)   

    def autonomousExit(self):
        pass

    def teleopInit(self):
        self.halfSpeed = True
        self.xbox = wpilib.XboxController(0)
        
        self.percent_output = 0.1

    def teleopPeriodic(self):
        self.driveWithJoystick(False)
        self.Abutton = self.xbox.getAButton()
        self.Bbutton = self.xbox.getBButton()
        self.Xbutton = self.xbox.getXButton()
        self.Ybutton = self.xbox.getYButton()
        self.RightBumper = self.xbox.getRightBumper()
        self.LeftBumper = self.xbox.getLeftBumper()

        self.botpose = self.vision.checkBotpose()

        if self.Abutton:
            self.motor2.set(-self.percent_output * -1)
            self.motor.set(-self.percent_output * -1)
    
        elif self.Bbutton:
            self.motor.set(-self.percent_output * 5)
            self.motor2.set(-self.percent_output * 5) 
        
        elif self.RightBumper:
            self.motor3.set(-self.percent_output * 0.1)

        else:
            self.motor2.set(0)
            self.motor.set(0)
            self.motor.set(0)


         # self.botpose = self.vision.checkBotpose()


         # self.current_yaw = self.botpose[5]#getting the yaw from the self.botpose table
         # self.desired_yaw = 0 #where we want our yaw to go 

        self.Abutton = self.xbox.getAButton()
        self.Bbutton = self.xbox.getBButton()

         if self.xbox.getRightBumper() and self.xbox.getLeftBumper():
            self.swerve.gyro.set_yaw(0)

        

        wpilib.SmartDashboard.putString('DB/String 1',"Motor 1 {:4.3f}".format(self.motor.get()))
        wpilib.SmartDashboard.putString('DB/String 2',"Motor 2 {:4.3f}".format(self.motor2.get()))

        if None != self.botpose and len(self.botpose) > 0 :
            x = self.botpose[0]
            y = self.botpose[1]
            wpilib.SmartDashboard.putString("DB/String 0", str(x))    
            wpilib.SmartDashboard.putString("DB/String 1", str(y))    
            
            current_yaw = self.botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 

            speaker_x = 6.5273#the x coordinate of the speaker marked in the field drawings in cm.
            speaker_y = 1.98#height of the speaker in meters.

            bot_x = self.botpose[0]#the x coordinate from the botpose table
            bot_y = self.botpose[1]#the y pos from the botpose table

            self.speaker_distance = self.distance_to_speaker(bot_x, bot_y, speaker_x, speaker_y)
            #fills the distance to speaker function with its required values for the calculate pitch function

            self.calculate_pitch = self.calculate_desired_pitch(self.speaker_distance, bot_y)
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
            wpilib.SmartDashboard.putString("DB/String 0", "No botpose")

        
    def calculate_desired_direction(self,desired_angle,current_angle):
        if current_angle >180:
            current_angle = current_angle - 360
        if desired_angle >180:
            desired_angle = desired_angle - 360
        desired_direction = desired_angle - current_angle
        return desired_direction
    '''
    this function checks to see if the counter clockwise direction has less distance to travel than clockwise and calculates the quickest direction to the disired angle
    '''
    
    def distance_to_speaker(self, bot_x, bot_y, speaker_x, speaker_y):
        '''
        distance to speaker calculates the distance from the robots pos to the speaker in meters. it uses the distance formula subtracting the desired x,y (the speaker)
        by our current x, y and square roots the awnser to get our distance to be used in our shooter angle calculations 
        '''
        distance = math.sqrt(pow(2, speaker_x - bot_x)) + (pow(2, speaker_y - bot_y))
        return distance
    
    
    def calculate_desired_pitch(self, speaker_distance, target_height):
        """
        this function calculates the desired angle for the shooter at different positions. its measured by getting the distance to speaker and the height of the target
        and dividing them and uses the arctan function to calculate the angle needed to shoot into the speaker.
        """
        desired_angle = math.atan2(speaker_distance, target_height) 
        return desired_angle
    
    def radians_to_degrees(self, degrees):
        '''
        calculates radians into degrees
        '''
        return degrees * (180/math.pi)


             
    
    def driveWithJoystick(self, fieldRelativeParam: bool) -> None:
        
        # allow joystick to be off from center without giving input

        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_x = applyDeadband(self.joystick_x , 0.1)
        self.joystick_y = applyDeadband(self.joystick_y , 0.1)

        rot = -self.xbox.getRightX()
        rot = applyDeadband(rot, 0.15)

        x_speed = self.joystickscaling(self.joystick_y)
        y_speed = self.joystickscaling(self.joystick_x)
        
        self.magnitude = math.sqrt(self.joystick_x*self.joystick_x + self.joystick_y*self.joystick_y)/3

       
        self.swerve.drive(x_speed/3, y_speed/3, rot, fieldRelativeParam)
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

	
