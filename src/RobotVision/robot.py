import wpilib
import wpilib.drive
import wpimath
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time
import ntcore 
import math

from vision import Vision #Vision file import

class Myrobot(wpilib.TimedRobot):

 

    def robotInit(self):

        self.xbox = wpilib.XboxController(0)

        self.vision = Vision()


    def disabledInit(self):
        pass

    def disabledPeriodic(self):
        pass

    def disabledExit(self):
        pass

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass

    def autonomousExit(self):
        pass

    def teleopInit(self):
        self.halfSpeed = False

    def teleopPeriodic(self):
        self.driveWithJoystick(True)

        # limelight self.botpose values in order: (x, y, z, roll, pitch, yaw)
        self.botpose = self.vision.checkBotpose()
        if None != self.botpose and len(self.botpose) > 0 :
            x = self.botpose[0]
            y = self.botpose[1]
            wpilib.SmartDashboard.putString("DB/String 0", str(x))    
            wpilib.SmartDashboard.putString("DB/String 1", str(y))    
            
            current_yaw = self.botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 

            speaker_x = 6.5273#the x coordinate of the speaker marked in the field drawings in cm.
            speaker_y = 2.18#height of the speaker in meters from the lowest point + 1 ft to get the middle of the speaker on where to aim.

            bot_x = self.botpose[0]#the x coordinate from the botpose table
            bot_y = self.botpose[1]#the y pos from the botpose table

            self.speaker_distance = self.distance_to_speaker(bot_x, bot_y, speaker_x, speaker_y)
            #fills the distance to speaker function with its required values for the calculate pitch function

            self.calculate_pitch = self.calculate_desired_pitch(self.speaker_distance, bot_y)
            #fills the calculate pitch function with necessary values to be properly called
            pitch_in_degrees = self.radians_to_degrees(self.calculate_pitch)
            #converts the pitch shooter angle to degrees from radians

            wpilib.SmartDashboard.putString("DB/String 4", str(pitch_in_degrees))
            wpilib.SmartDashboard.putString("DB/String 5", str(self.speaker_distance))
          
           

            
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

        # self.joystick_x = -self.xbox.getLeftX()
        # self.joystick_y = -self.xbox.getLeftY()
        # self.joystick_x = applyDeadband(self.joystick_x , 0.1)
        # self.joystick_y = applyDeadband(self.joystick_y , 0.1)

        # rot = -self.xbox.getRightX()
        # rot = applyDeadband(rot, 0.05) 
        


        #1/22/2024 commented out whats below for more simplification, we dont need joystickscaling maxspeed etc.

        # # Get the x speed. We are inverting this because Xbox controllers return
        # # negative values when we push forward.
        # joystick_y = self.swerve.joystickscaling(self.joystick_y )
        # xSpeed = self.xSpeedLimiter.calculate(joystick_y) * self.swerve.getMaxSpeed()

        # # Get the y speed. We are inverting this because Xbox controllers return
        # # negative values when we push to the left.
        # joystick_x = self.swerve.joystickscaling(self.joystick_x)
        # ySpeed = self.ySpeedLimiter.calculate(joystick_x) * self.swerve.MAX_SPEED

        # rot = self.swerve.joystickscaling(rot)
        # rot = self.rotLimiter.calculate(rot) * self.swerve.MAX_ANGULAR_SPEED

        # self.swerve.drive(xSpeed, ySpeed, rot, fieldRelativeParam)

        self.angle = Rotation2d(self.xbox.getLeftX(), self.xbox.getLeftY())
        self.state = SwerveModuleState(0.1, self.angle)
    def teleopExit(self):
        pass
    
    


if __name__ == '__main__':
    wpilib.run(Myrobot)
