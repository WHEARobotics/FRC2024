# !/usr/bin/env python3
"""
    WHEA Robotics code for the MAKO robot project.
"""

import wpimath
import wpilib
import wpilib.drive
import rev
from vision import Vision

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
        self.vision = Vision

        # # Create and configure the drive train controllers and motors, all Rev. Robotics SparkMaxes driving NEO motors.
        self.drive_rr = rev.CANSparkMax(1, rev._rev.CANSparkMaxLowLevel.MotorType.kBrushless)
        self.drive_rf = rev.CANSparkMax(3, rev._rev.CANSparkMaxLowLevel.MotorType.kBrushless)
        self.drive_lr = rev.CANSparkMax(2, rev._rev.CANSparkMaxLowLevel.MotorType.kBrushless)
        self.drive_lf = rev.CANSparkMax(4, rev._rev.CANSparkMaxLowLevel.MotorType.kBrushless)

        # Inversion configuration for the 2022 WPILib MecanumDrive code, which removed internal inversion for right-side motors.
        self.drive_rr.setInverted(True) # 
        self.drive_rf.setInverted(True) # 
        self.drive_lr.setInverted(False) # 
        self.drive_lf.setInverted(False) # 

        # Set all motors to coast mode when idle/neutral.
        # Note that this is "IdleMode" rather than the "NeutralMode" nomenclature used by CTRE CANTalons.
        self.drive_rr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.drive_rf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.drive_lr.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.drive_lf.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)

        # # Now that we have motors, we can set up an object that will handle mecanum drive.
        # # From the documentation, North, East, and Down are the three axes.
        # # Positive X is forward, Positive Y is right, Positive Z is down.  Clockwise rotation around Z (as viewed from ___) is positive.
        self.drivetrain = wpilib.drive.MecanumDrive(self.drive_lf, self.drive_lr, self.drive_rf, self.drive_rr)

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
        pass

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.gyro.reset()  # Reset at the beginning of a match, because the robot could have been sitting for a while, gyro drifting.


    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""
        botpose = self.vision.checkBotpose()
            

        if None != botpose and len(botpose) > 0 :
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
           
            current_yaw = botpose[5]#getting the yaw from the self.botpose table
            desired_yaw = 0 #where we want our yaw to go 
            direction_to_travel = self.calculate_desired_direction(desired_yaw, current_yaw)
            if direction_to_travel < -1:
                self.drivetrain.driveCartesian(0, 0, 1, -self.gyro.getAngle())
            elif direction_to_travel > 2:
                self.drivetrain.driveCartesian(0, 0, -1, -self.gyro.getAngle())
            else:
                self.drivetrain.driveCartesian(0, 0, 0, -self.gyro.getAngle())
        else:
           wpilib.SmartDashboard.putString("DB/String 0", str("noBotpose")) 

    def teleopInit(self):
        """This function is run once each time the robot enters teleop mode."""
        self.print_timer.start() # Now it starts counting.
        self.gyro.reset() # Also reset the gyro angle.  This means you should always start in a known orientation.

    def teleopPeriodic(self):
        """This function is called periodically during teleop."""
        
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
        self.drivetrain.driveCartesian(move_y / 4, move_x / 4, move_z / 4, -self.gyro.getAngle())

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
if __name__ == '__main__':
    wpilib.run(MAKORobot)