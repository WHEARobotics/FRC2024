from __future__ import annotations

from wpimath.kinematics import SwerveDrive4Kinematics, SwerveDrive4Odometry, SwerveModulePosition, SwerveModuleState, ChassisSpeeds
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from wpimath.controller import PIDController
from wpilib import Field2d, SmartDashboard
import wpilib
import phoenix6
from phoenix5 import sensors
import wpimath.kinematics._kinematics
import wpimath.geometry._geometry

import math

from CrescendoSwerveModule import CrescendoSwerveModule
# from vision import Vision

class CrescendoSwerveDrivetrain:
    # I'd suggest not try to use the units functionality, and just stick to floats.
    # Whether we use degrees or radians for angle is debatable:
    #  - radians is going to be slightly more efficient, to not be converting back and forth.
    #  - degrees is more familiar, and the performance hit may not be that great.
    MAX_SPEED = 2.0
    MAX_ANGULAR_SPEED = math.pi # 1/2 rotation per second

    # UPDATE NUMBERS
    BACK_LEFT_OFFSET = 0.265   # Back Left
    FRONT_RIGHT_OFFSET = 0.215  # Front Right
    FRONT_LEFT_OFFSET = 0.032   # Front Left
    BACK_RIGHT_OFFSET = 0.858   # Back Right
    """
    these are the absolute position offsets that are constants setting an offset to the absolute encoders and changing the position of an angle.
    if we set the position to zero and set the offset 1 time to zero then 180, it would create a 180 degree difference when the wheel is set.
    """
    

    def __init__(self):

        wheel_base = 26.875 * 0.0254
        track_width = 22.75 * 0.0254
        half_wheel_base = wheel_base / 2
        half_track_width = track_width / 2#2_#TRACK_WIDTH MIGHT NEED TO BE SWICHED ARROUND, BUT THE POSITIVE/NEGATIVE SIGNS ARE IN THE RIGHT LOCATION.

        self.frontLeftLocation = Translation2d(half_wheel_base, half_track_width)
        self.frontRightLocation = Translation2d(half_wheel_base, -half_track_width)
        self.backLeftLocation = Translation2d(-half_wheel_base, half_track_width)
        self.backRightLocation = Translation2d(-half_wheel_base, -half_track_width)
        '''
        this sets up the translation 2d for each swerve module that sets up a translation in a 2d space. when the robot is facing
        at its origin positive x is forward and positive y is left for the 2d translation
        '''

        #2024- CHANGE ALL THESE TO THE CANSPARKMAX MOTOR CONTROLLER NUMBERS SOREN SET IN THE REV CLIENT- I.E. THE LABELS OF EACH MOTOR CONTROLLER
        self.backLeft = CrescendoSwerveModule(4, 6, 3, self.BACK_LEFT_OFFSET)
    
        self.frontRight = CrescendoSwerveModule(8, 13, 0, self.FRONT_RIGHT_OFFSET)  #OG offset was 106.424  
    
        self.frontLeft = CrescendoSwerveModule(5, 3, 2, self.FRONT_LEFT_OFFSET)  #OG offset was 296.543
 
        self.backRight = CrescendoSwerveModule(2, 7, 1, self.BACK_RIGHT_OFFSET)
        
        self.swerve_modules = [ self.frontLeft, self.frontRight, self.backLeft, self.backRight ]
        '''
        this section above creates 4 swerve modules and sets the id's of each of them in this order:
        drivemotor channel, turnmotor channel, absolute encoder channel(from analog input with thrifty encoders) and the absolute pos offset
        then it creates a list for calling all modules at most
        '''

        


        self.swerveModuleStates = [SwerveModuleState() , SwerveModuleState(), SwerveModuleState(), SwerveModuleState()]
        '''
        this initializes the states of the swerve modules, to set the swerve modules to certain speeds and angles periodically 50 times a second
        but this is only the initializaation part.
        '''



        self.gyro = sensors.Pigeon2(14)

        """
        this creates the pigeon gyro object that is used to track the robots yaw angle to be able to use field relative.
        """
         
        '''
        The proper Kinematics and Odometry class to used is determined by the number of modules on the robot.
        For example, this 4 module robot uses SwerveDrive4Kinematics and SwerveDrive4Odometry. this 
        '''
        self.kinematics = SwerveDrive4Kinematics(
            self.frontLeftLocation, self.frontRightLocation, 
            self.backLeftLocation, self.backRightLocation)
        '''
        kinematics sets values for each individual module like its speed and angle working with the swerve module states
        '''
        
        self.odometry = SwerveDrive4Odometry(
            self.kinematics, Rotation2d(),
            (
                self.frontLeft.getPosition(),
                self.frontRight.getPosition(),
                self.backLeft.getPosition(),
                self.backRight.getPosition()
            )
        )
        '''
        odometry is used to track the robots position on the field only after being enabled. with this you can track things
        like how far the robot travelled in meters per second
        '''

        # Where are the swerve modules located on the robot?
        # ? These values of 0.5 are taken from  https://github.com/4201VitruvianBots/2021SwerveSim/blob/main/WPILib_SwerveControllerCommand/src/main/java/frc/robot/Constants.java
        # But they seem odd. What units are they?
        # They are probably meters, but the thing I don't understand is why they are different than the self.frontLeftLocation, etc. above.
        # I suggest changing them to be the above --Rod

        # UPDATE
        self.module_positions = [
            # Front left
            self.frontLeftLocation,
            # Front right
            self.frontRightLocation,
            # Back left
            self.backLeftLocation,
            # Back right
            self.backRightLocation
        ]
        '''
        this creates an object to be used for setting up the 2d position of the robot to be called
        '''

        # The current pose for each swerve module
        # These values are updated in `periodic()`
        self.module_poses = [
            Pose2d(),
            Pose2d(),
            Pose2d(),
            Pose2d()
        ]
        '''
        this creates another list to create a position facing at the x origin
        '''

        # Simulation support
        self.fieldSim = Field2d()
        SmartDashboard.putData('Field', self.fieldSim)

        self.gyro.setYaw(0)#8/3/2023 changed gyro reset to calibrate to possibly stop it from drifting

    def periodic(self):
        self._updateOdometry()

        ## Update for simulation

        # Update module poses
        for i in range(len(self.module_positions)):
            rotate_by = self.module_positions[i].rotateBy(self.get_heading())
            robot_translation = self.get_pose().translation()
            module_position = rotate_by + robot_translation
            # Module's heading is its angle relative to the chassis heading
            module_angle = self.swerve_modules[i].getState().angle + self.get_pose().rotation() 
            self.module_poses[i] = Pose2d(module_position, module_angle)
        '''
        this updates the module position using 2d values to find the robots position with its angle and the x and y position
        '''


        # Update field sim with information
        self.fieldSim.setRobotPose(self.get_pose())
        self.fieldSim.getObject("Swerve Modules").setPoses(self.module_poses)
        '''
        this  gives values of the robots pos into the robot field simulator
        '''


    def drive(self, xSpeed, ySpeed, rot, fieldRelative : bool) -> None:
        chassis_speeds = ChassisSpeeds(xSpeed, ySpeed, rot) if not fieldRelative \
            else ChassisSpeeds.fromFieldRelativeSpeeds(xSpeed, ySpeed, rot, Rotation2d.fromDegrees(self.gyro.getYaw()))
        self.swerveModuleStates = self.kinematics.toSwerveModuleStates(chassis_speeds)

        self.swerveModuleStates = SwerveDrive4Kinematics.desaturateWheelSpeeds(self.swerveModuleStates, self.MAX_SPEED)
        # Desaturate wheel speeds will slow down the speed or angle of a module if it passed the max speed or angle.

        '''
        This function takes in the joystick inputs and sets up the field relative to be able to operate the robot with inputs.
        '''
       
        self.frontLeft.setDesiredState(self.swerveModuleStates[0], True)
        self.frontRight.setDesiredState(self.swerveModuleStates[1], True)
        self.backLeft.setDesiredState(self.swerveModuleStates[2], True)
        self.backRight.setDesiredState(self.swerveModuleStates[3], True)

        #set desired state, updates the speed and angle on which each module has to reach periodically.

    def _updateOdometry(self):
        self.odometry.update(
            Rotation2d.fromDegrees(self.gyro.getYaw()),
            self.frontLeft.getPosition(),
            self.frontRight.getPosition(),
            self.backLeft.getPosition(),
            self.backRight.getPosition()
        )
        '''
        This function updates the robots position and angle periodically every 50 ms
        '''

    def get_heading(self) -> Rotation2d:
        return Rotation2d.fromDegrees(self.gyro.getYaw())

    def get_pose(self) -> Pose2d :
        return self.odometry.getPose()

    @classmethod
    def getMaxSpeed(cls):
        return cls.MAX_SPEED

    def resetSteering(self):
        """Call this to reset turning encoders when ALL wheels are aligned forward."""
        self.frontRight.resetSteering()
        self.frontLeft.resetSteering()
        self.backRight.resetSteering()
        self.backLeft.resetSteering()

    def toggleDriveMotorsInverted(self):
        for module in self.swerve_modules:
            module.toggleDriveMotorInverted()
