

# !/usr/bin/env python3
"""
    WHEA Robotics code for the MAKO robot project.
"""

import wpimath
from wpimath import geometry
import wpilib
import wpilib.drive
import rev
from vision import Vision
import math
from wpilib import DriverStation


class MAKORobot(wpilib.TimedRobot):
    def robotInit(self):
        """This function is called upon program startup as part of WPILIB/FRC/RobotPy.
           In it, we should initialize the robot's shared variables and objects.
        """
        self.print_timer = wpilib.Timer() # A timer to help us print info periodically; still need to start it.

        # Gyro measures rate of rotation, and plugs into the "SPI" port on the roboRIO
        # https://wiki.analog.com/first/adxrs450_gyro_board_frc
        # Positive rotation is clockwise.
        self.gyro = wpilib.ADXRS450_Gyro(wpilib._wpilib.SPI.Port.kOnboardCS0) # Calibration happens during initialization, so keep the robot still when powering on.
        # It is best to let the robot warm up so that the sensor reaches a steady temperature before calibrating it.  This may not
        # always be possible in a match situation.  For reference, Rod measured the amount of drift during a 2:30 match by just letting
        # the robot sit still.  I rebooted robot code between measurements, so that recalibration and zeroing would happen.
        # First turned on, and then repeated 2.5-minute tests: 9.9, 1.8, 3.0, 16.8 (!), 1.6, 8.0 degrees.
        # Similar test, after the robot had been on 1/2 hour:  2.4, 1.9, -2.0, 0.3, 0.3, 0.7 degrees.

        # Choose joystick or Xbox controller, also see comment in teleopPeriodic().
        # Rod has a CAD joystick that shows up as 0, hence I use "1" in the argument.
        # Thrustmaster joystick, set as left handed.
        # Positive values for channels 0-3: x, y, z, and throttle correspond to: right, backwards, clockwise, and slid back toward the user.
        # The "twist" channel is the same as z.
        # self.joystick = wpilib.Joystick(1)
        self.xbox = wpilib.XboxController(1)
        self.vision = Vision()

        self.AUTO_NOTE_A = 'a' 
 
        self.AUTO_NOTE_B = 'b' 
 
        self.AUTO_NOTE_C = 'c' 

        self.NOTE_SELECTOR = 'Auto Selector'
        wpilib.SmartDashboard.putStringArray('Auto List', [self.AUTO_NOTE_A, self.AUTO_NOTE_B, self.AUTO_NOTE_C]) 
        # v = wpilib.SmartDashboard.setDefaultStringArray(self.NOTE_SELECTOR, [self.AUTO_NOTE_B])
        # print(f"Value is {v}" if v is not None else "None")
        self.NOTE_POSITION = {
            "a" : [5.42, 0] ,
            "b" : [5.42, 1.44] ,
            "c" : [5.42, 2.88] ,
        }

        # # Create and configure the drive train controllers and motors, all Rev. Robotics SparkMaxes driving NEO motors.
        self.drive_rr = rev.CANSparkMax(1, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.drive_rf = rev.CANSparkMax(3, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.drive_lr = rev.CANSparkMax(2, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.drive_lf = rev.CANSparkMax(4, rev._rev.CANSparkLowLevel.MotorType.kBrushless)

        # Inversion configuration for the 2022 WPILib MecanumDrive code, which removed internal inversion for right-side motors.
        self.drive_rr.setInverted(True) # 
        self.drive_rf.setInverted(True) # 
        self.drive_lr.setInverted(False) # 
        self.drive_lf.setInverted(False) # 

        # Set all motors to coast mode when idle/neutral.
        # Note that this is "IdleMode" rather than the "NeutralMode" nomenclature used by CTRE CANTalons.
        self.drive_rr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_rf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_lr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_lf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

        # # Now that we have motors, we can set up an object that will handle mecanum drive.
        # # From the documentation, North, East, and Down are the three axes.
        # # Positive X is forward, Positive Y is right, Positive Z is down.  Clockwise rotation around Z (as viewed from ___) is positive.
        self.drivetrain = wpilib.drive.MecanumDrive(self.drive_lf, self.drive_lr, self.drive_rf, self.drive_rr)

        self.AUTONOMOUS_STATE_SPEAKER_YAWING = 0
        self.AUTONOMOUS_STATE_SPEAKER_SHOOTING = 1
        self.AUTONOMOUS_STATE_NOTE_YAWING = 2
        self.AUTONOMOUS_STATE_NOTE_DRIVING = 3 
        # Add more variables for additional states in auto 
        self.autonomous_state_active = self.AUTONOMOUS_STATE_NOTE_YAWING

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

    def disabledInit(self):
        """This function gets called once when the robot is disabled.
           In the past, we have not used this function, but it could occasionally
           be useful.  In this case, we reset some SmartDashboard values.
        """
        # wpilib.SmartDashboard.putNumber('DB/Slider 0', 0)
        # wpilib.SmartDashboard.putBoolean('DB/LED 0', False)
        pass

    def disabledPeriodic(self):
        """Another function we have not used in the past.  Adding for completeness."""
        self.drive_rr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.drive_rf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.drive_lr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.drive_lf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)


    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.gyro.reset()  # Reset at the beginning of a match, because the robot could have been sitting for a while, gyro drifting.
        

        
        # get desired note position 
        selected_note =  wpilib.SmartDashboard.getString(self.NOTE_SELECTOR, 'did not find it') 
        print(f"Value of selected_note is {selected_note}")
        if selected_note != "did not find it":
            note_x, note_y = self.NOTE_POSITION [selected_note]
            wpilib.SmartDashboard.putString('DB/String 8', f"Note {selected_note} @ [{note_x}, {note_y}]")
        else:
            wpilib.SmartDashboard.putString('DB/String 8', "Did not find selected note")

        self.autonomous_state_active = self.AUTONOMOUS_STATE_SPEAKER_YAWING

        self.drive_rr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_rf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_lr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_lf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)


    def get_rotation_autonomous_periodic_for_speaker_shot(self, botpose, current_yaw):
        x = botpose[0]
        desired_x = self.desired_x_for_autonomous_driving
        y = botpose[1]
        wpilib.SmartDashboard.putString("DB/String 0", str(x))    
        wpilib.SmartDashboard.putString("DB/String 1", str(y))

        speaker_y = 1.44 # 
        distance_to_wall = (self.speaker_x - x) #Ajd
        distance_to_speaker_y = (speaker_y - y) #Opp
        # speaker_distance = self.distance_to_speaker(x, y, speaker_x, speaker_y) #Hy

        desired_bot_angle = self.calculate_desired_angle(distance_to_speaker_y, distance_to_wall)


        direction_to_travel = self.calculate_desired_direction(desired_bot_angle, current_yaw)
        # direction_to_travel = self.radians_to_degrees(direction_to_travel_rad)
        x_distance_to_travel = (desired_x - x)
        x_kp = 0.007
        x_max_speed = 0.2
        x_speed = x_kp * x_distance_to_travel

        yaw_kp = 0.007
        max_rot_value = 0.3
        rot = yaw_kp * direction_to_travel
        # this acts like the p value in a pid loop for the rotation action

        if x_speed > x_max_speed:
            x_speed = x_max_speed
        elif x_speed < -x_max_speed:
            x_speed = -x_max_speed
        if rot > max_rot_value:
            rot = max_rot_value
        elif rot < -max_rot_value: 
            rot = -max_rot_value
            # this sets makes sure that the rot value does not pass the maximum we give
        wpilib.SmartDashboard.putString("DB/String 5", f"desired_bot_angle {desired_bot_angle:3.1f}")    
        wpilib.SmartDashboard.putString("DB/String 6", f"direction_to_travel {direction_to_travel:3.1f}")    


        return rot, direction_to_travel

    def rotate_towards_speaker_shot_periodic(self, botpose, current_yaw):
        rot, direction_to_travel = self.get_rotation_autonomous_periodic_for_speaker_shot(botpose, current_yaw)

        wpilib.SmartDashboard.putString("DB/String 2", f"current_yaw {current_yaw:3.1f}")   
    
    
        self.drivetrain.driveCartesian(0, 0, -rot, geometry.Rotation2d(-self.gyro.getAngle()))
        wpilib.SmartDashboard.putString("DB/String 3", f"rotation {rot:3.1f}")      

        if abs(direction_to_travel) < 0.25:
            return False
        else:
            return True
        
    def get_current_pitch(self):
        # TODO: this needs to be implemented

        return 0
    
    def pitch_towards_speaker_shot_periodic(self, botpose, current_pitch):
        # TODO: this needs to be implemented

        # False means no more calls necessary to align
        return False


    def autonomousPeriodic(self): 
        """This function is called periodically during autonomous."""
        botpose = self.vision.checkBotpose()

        if None != botpose and len(botpose) > 0 :
            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            if current_yaw < 0:
                current_yaw += 360 

            current_pitch = self.get_current_pitch()

            wpilib.SmartDashboard.putString("DB/String 7", f"Current robot state: {self.autonomous_state_active}")
            self.timer = wpilib.Timer()
            self.timer.reset()
            self.timer.start()

            if self.autonomous_state_active == self.AUTONOMOUS_STATE_SPEAKER_YAWING :
                is_still_rotating = self.rotate_towards_speaker_shot_periodic(botpose, current_yaw) 
                not_rotating_anymore = not is_still_rotating
                is_still_pitching = self.pitch_towards_speaker_shot_periodic(botpose, current_pitch)
                not_pitching_anymore = not is_still_pitching 

                if (not_rotating_anymore and not_pitching_anymore):
                    # rotation is less than 2 degrees and pitch is okay, so shoot
                    self.autonomous_state_active = self.AUTONOMOUS_STATE_SPEAKER_SHOOTING
                    self.timer.reset()
                    self.timer.start()
                wpilib.SmartDashboard.putString("DB/String 4", f"p:{is_still_pitching} y:{is_still_rotating} {not_pitching_anymore and not_rotating_anymore}")

            elif self.autonomous_state_active == self.AUTONOMOUS_STATE_SPEAKER_SHOOTING:
                if self.timer.advanceIfElapsed(1):
                    raise Exception("Implement auto shoot")
                
            elif self.autonomous_state_active == self.AUTONOMOUS_STATE_NOTE_YAWING:
                raise Exception("Implement yaw towards note")
            
            elif self.autonomous_state_active == self.AUTONOMOUS_STATE_NOTE_DRIVING :
                raise Exception("Implement drive towards note")

                 

    def teleopInit(self):
        """This function is run once each time the robot enters teleop mode."""
        self.print_timer.start() # Now it starts counting.
        self.gyro.reset() # Also reset the gyro angle.  This means you should always start in a known orientation.

        self.drive_rr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_rf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_lr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.drive_lf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

    def do_teleop_speaker_align(self):
        wpilib.SmartDashboard.putString("DB/String 0", "do_teleop_speaker_align()")
        botpose = self.vision.checkBotpose()

        if None != botpose and len(botpose) > 0 :
            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            if current_yaw < 0:
                current_yaw += 360 

            is_still_rotating = self.rotate_towards_speaker_shot_periodic(botpose, current_yaw) 
            wpilib.SmartDashboard.putString("DB/String 1", f"Still rotating {is_still_rotating}")

    def teleopPeriodic(self):
        """This function is called periodically during teleop."""
        

        if self.xbox.getAButtonPressed():
            self.do_teleop_speaker_align()

        # Get values from either the joystick or the Xbox controller, and put them into temporary values we can 
        # access later in this method.  This way we can switch between joystick and Xbox by changing comments on two lines
        # in robotInit() and on the relevant sections below
        # Uncomment one section and comment the other.

        # Joystick
        # move_y = -self.joystick.getY()
        # move_x = self.joystick.getX()
        # move_z = self.joystick.getZ()

        # Xbox
        move_y = -self.xbox.getRightY()
        move_x = self.xbox.getRightX()
        move_z = self.xbox.getLeftX()

        # Drive using the joystick inputs for y, x, z, and gyro angle. (note the weird order of x and y)
        # Drive configuration using the 2022 WPILib library code, which changed some definitions.
        # Positive X is right, and is +X on the joystick.
        # Positive Y is forward, and is -Y on the joystick
        # They say positive Z is down, and CW is positive, and CW is +Z on the joystick, and that is
        # what works.  But it is incorrect vector math, because X cross Y = Z, and when using the right hand rule
        # that makes +Z up, and positive angle starting at X and moving toward Y would be CCW when viewed from above the robot.
        # I'm not sure about whether the gyro angle should be negated or not.  We'll have to try.
        # self.drivetrain.driveCartesian(move_y / 4, move_x / 4, move_z / 4, wpimath.geometry._geometry.Rotation2d(0.0))
        DEADBAND = 0.1
        if abs(move_z) > DEADBAND:
            self.drivetrain.driveCartesian(move_x / 4, move_y / 4, move_z / 4, geometry.Rotation2d(-self.gyro.getAngle()))

        # The timer's advanceIfElapsed() method returns true if the time has passed, and updates
        # the timer's internal "start time".  This period is 0.2 seconds.
        if self.print_timer.advanceIfElapsed(0.2):
            # Send a string representing the red component to a field called 'DB/String 0' on the SmartDashboard.
            # The default driver station dashboard's "Basic" tab has some pre-defined keys/fields
            # that it looks for, which is why I chose these.
            wpilib.SmartDashboard.putString('DB/String 0', 'Angle: {:5.1f}'.format(self.gyro.getAngle()))
            wpilib.SmartDashboard.putString('DB/String 1', 'X: {:5.1f}'.format(move_x))
            wpilib.SmartDashboard.putString('DB/String 2', 'Y: {:5.1f}'.format(move_y))
            wpilib.SmartDashboard.putString('DB/String 3', 'Z: {:5.1f}'.format(move_z))

            wpilib.SmartDashboard.putString('DB/String 9 ', 'fr: {:5.1f}'.format(self.drive_rf.get()))
            wpilib.SmartDashboard.putString('DB/String 5', 'br: {:5.1f}'.format(self.drive_rr.get()))
            wpilib.SmartDashboard.putString('DB/String 7', 'fl: {:5.1f}'.format(self.drive_lf.get()))
            wpilib.SmartDashboard.putString('DB/String 8', 'rl: {:5.1f}'.format(self.drive_lr.get()))
            # wpilib.SmartDashboard.putNumber('DB/Slider 0', 4)
            # wpilib.SmartDashboard.putBoolean('DB/LED 0', password) # Light the virtual LED if the password has been entered properly.

            # You can use your mouse to move the DB/Slider 1 slider on the dashboard, and read
            # the value it shows with the command below.  0.0 below is the default value, should
            # the key 'Db/Slider 1' not exist in the SmartDashboard table (for instance, a typo).
            # user_value = wpilib.SmartDashboard.getNumber('DB/Slider 1', 0.0)
            # Send info to the logger and thus console.
            # Note the string format: the part in {} gets replaced by the value of the variable
            # user_value, and is formatted as a floating point (the "f"), with 4 digits and 2 digits
            # after the decimal place. https://docs.python.org/3/library/string.html#formatstrings
            #self.logger.info('Slider 1 is {:4.2f}'.format(user_value))



# The following little bit of code allows us to run the robot program.
# In Python, the special variable __name__ contains the name of the module that it is in,
# or since this file is 'robot.py', it would ordinarily be 'robot'.  The exception
# is when you are executing the module, as in you typed "python robot.py" at a command
# prompt.  In that case, the variable is given the special string value '__main__' to
# denote that it is the main module that is being executed.  And that is effectively
# what RobotPy does: when it boots, it executes the file robot.py.
# When that happens, it will read the class definition above, and then come to this
# statement, and the "if" will be true.  Therefore, it will execute wpilib.run(classname),
# where classname is the robot class we have defined, in this case MAKORobot.  The
# wpilib.run() function does the necessary stuff to call robotInit(), autonomousInit(), etc.
# See: https://stackoverflow.com/questions/419163/what-does-if-name-main-do
            
    def calculate_desired_direction(self,desired_angle,current_angle):
        desired_direction = desired_angle - current_angle
        if desired_direction > 180:
            desired_direction -= 360
        if desired_direction < -180:
            desired_direction += 360
        return desired_direction
    
    def distance_to_speaker(self, bot_x, bot_y, speaker_x, speaker_y):
        '''
        distance to speaker calculates the distance from the robots pos to the speaker in meters. it uses the distance formula subtracting the desired x,y (the speaker)
        by our current x, y and square roots the awnser to get our distance to be used in our shooter angle calculations. returns the distance from the robot to the speaker
        '''
        distance = math.sqrt(pow(2, speaker_x - bot_x)) + (pow(2, speaker_y - bot_y))
        return distance
    def calculate_desired_angle(self, distance_to_speaker_y, distance_to_wall):
        """
        This function calculates the desired angle for the robot's orientation at different positions. It's measured by getting the distance to speaker on the y axis and the distance to the wall using the x axis
        and dividing them and uses the arctan function to calculate the angle needed to for the robot to rotate to into the speaker angle. This function returns the robots needed orientation in degrees.
        distance to speakerY is the adjacent angle
        distance to wall is the opposite angle
        """
        desired_angle_rad = math.atan2(distance_to_speaker_y, distance_to_wall) 
        desired_angle = self.radians_to_degrees(desired_angle_rad)
        if desired_angle < 0:
            desired_angle += 360
        return desired_angle
    
    def radians_to_degrees(self, radians):
        '''
        calculates radians into degrees
        '''
        return radians * (180/math.pi)
    
if __name__ == '__main__':
    wpilib.run(MAKORobot)