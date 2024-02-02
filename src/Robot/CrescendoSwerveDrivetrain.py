from __future__ import annotations

from wpimath.kinematics import SwerveDrive4Kinematics, SwerveDrive4Odometry, SwerveModulePosition, SwerveModuleState, ChassisSpeeds
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from wpimath.controller import PIDController
from wpilib import Field2d, SmartDashboard
import wpilib

import wpimath.kinematics._kinematics
import wpimath.geometry._geometry

import math

from CrescendoSwerveModule import CrescendoSwerveModule

class CrescendoSwerveDrivetrain:
    # I'd suggest not try to use the units functionality, and just stick to floats.
    # Whether we use degrees or radians for angle is debatable:
    #  - radians is going to be slightly more efficient, to not be converting back and forth.
    #  - degrees is more familiar, and the performance hit may not be that great.
    MAX_SPEED = 3.0
    MAX_ANGULAR_SPEED = math.pi # 1/2 rotation per second

    # UPDATE NUMBERS
    ABSOLUTEPOS_3 = 326.1   # Back Right
    ABSOLUTEPOS_4 = 253.2 #-278.788 #106.424  # Front Right
    ABSOLUTEPOS_2 = 152.9  # Back Left
    ABSOLUTEPOS_1 = 326.1  # Front Left
    

    def __init__(self):

        wheel_base = 26.875 * 0.0254
        track_width = 22.75 * 0.0254
        half_wheel_base = wheel_base / 2
        half_track_width = track_width / 2#2_#TRACK_WIDTH MIGHT NEED TO BE SWICHED ARROUND, BUT THE POSITIVE/NEGATIVE SIGNS ARE IN THE RIGHT LOCATION.

        self.frontLeftLocation = Translation2d(half_wheel_base, half_track_width)
        self.frontRightLocation = Translation2d(half_wheel_base, -half_track_width)
        # self.backLeftLocation = Translation2d(-half_wheel_base, half_track_width)
        # self.backRightLocation = Translation2d(-half_wheel_base, -half_track_width)

        #2024- CHANGE ALL THESE TO THE CANSPARKMAX MOTOR CONTROLLER NUMBERS SOREN SET IN THE REV CLIENT- I.E. THE LABELS OF EACH MOTOR CONTROLLER
        # self.backLeft = CrescendoSwerveModule(6, 7, 2, self.ABSOLUTEPOS_2)
    
        self.frontRight = CrescendoSwerveModule(6, 7, 0, 0)  #OG offset was 106.424  
    
        self.frontLeft = CrescendoSwerveModule(5, 4, 0, 0)  #OG offset was 296.543
 
        # self.backRight = CrescendoSwerveModule(8, 9, 3, self.ABSOLUTEPOS_3)
        
        self.swerve_modules = [ self.frontLeft, self.frontRight]#, self.backLeft, self.backRight ]

        


        self.swerveModuleStates = [SwerveModuleState() , SwerveModuleState()]#, SwerveModuleState(), SwerveModuleState()]

        # Instead of an analog gyro, let's use the ADXRS450_Gyro class, like MAKO does in the mecanum folder. 
        # See https://robotpy.readthedocs.io/projects/wpilib/en/stable/wpilib/ADXRS450_Gyro.html#wpilib.ADXRS450_Gyro
        # and https://github.com/WHEARobotics/MAKO/blob/master/code/mecanum/robot.py
        # You need to update here and where ever the gyro is used.  Note that the ADXRS450 outputs negative degrees
        # for CCW, when we need positive.  It also doesn't have a getRotation2d() method, so you'll need to 
        # make one with Rotation2d.fromDegrees().

        self.gyro = wpilib.ADXRS450_Gyro(wpilib._wpilib.SPI.Port.kOnboardCS0) 

        # The proper Kinematics and Odometry class to used is determined by the number of modules on the robot.
        # For example, this 4 module robot uses SwerveDrive4Kinematics and SwerveDrive4Odometry.
        self.kinematics = SwerveDrive4Kinematics(
            self.frontLeftLocation, self.frontRightLocation), 
#            self.backLeftLocation, self.backRightLocation)

        self.odometry = SwerveDrive4Odometry(
            self.kinematics, Rotation2d(),
            (
                self.frontLeft.getPosition(),
                self.frontRight.getPosition()
            )
            
            #     self.backLeft.getPosition(),
            #     self.backRight.getPosition()
            # )
        )

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
            # # Back left
            # self.backLeftLocation,
            # # Back right
            # self.backRightLocation
        ]

        # The current pose for each swerve module
        # These values are updated in `periodic()`
        self.module_poses = [
            Pose2d(),
            Pose2d()
        ]
        
        #     Pose2d(),
        #     Pose2d()
        # ]

        # Simulation support
        self.fieldSim = Field2d()
        SmartDashboard.putData('Field', self.fieldSim)

        self.gyro.calibrate()#8/3/2023 changed gyro reset to calibrate to possibly stop it from drifting

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

        # Update field sim with information
        self.fieldSim.setRobotPose(self.get_pose())
        self.fieldSim.getObject("Swerve Modules").setPoses(self.module_poses)


    def drive(self, xSpeed, ySpeed, rot, fieldRelative : bool) -> None:
        chassis_speeds = ChassisSpeeds(xSpeed, ySpeed, rot) if not fieldRelative \
            else ChassisSpeeds.fromFieldRelativeSpeeds(xSpeed, ySpeed, rot, Rotation2d.fromDegrees(-self.gyro.getAngle()))
        self.swerveModuleStates = self.kinematics.toSwerveModuleStates(chassis_speeds)

        self.swerveModuleStates = SwerveDrive4Kinematics.desaturateWheelSpeeds(self.swerveModuleStates, self.MAX_SPEED)

        self.frontLeft.setDesiredState(self.swerveModuleStates[0], True)
        self.frontRight.setDesiredState(self.swerveModuleStates[1], True)
        # self.backLeft.setDesiredState(self.swerveModuleStates[2], True)
        # self.backRight.setDesiredState(self.swerveModuleStates[3], True)


    def _updateOdometry(self):
        self.odometry.update(
            Rotation2d.fromDegrees(-self.gyro.getAngle()),
            self.frontLeft.getPosition(),
            self.frontRight.getPosition(),
            # self.backLeft.getPosition(),
            # self.backRight.getPosition()
        )

    def get_heading(self) -> Rotation2d:
        return Rotation2d.fromDegrees(-self.gyro.getAngle())

    def get_pose(self) -> Pose2d :
        return self.odometry.getPose()

    @classmethod
    def getMaxSpeed(cls):
        return cls.MAX_SPEED

    def resetSteering(self):
        """Call this to reset turning encoders when ALL wheels are aligned forward."""
        self.frontRight.resetSteering()
        self.frontLeft.resetSteering()
        # self.backRight.resetSteering()
        # self.backLeft.resetSteering()

    def toggleDriveMotorsInverted(self):
        for module in self.swerve_modules:
            module.toggleDriveMotorInverted()

 
    def joystickscaling(input): #this function helps bring an exponential curve in the joystick value and near the zero value it uses less value and is more flat
        a = 1
        output = a * input * input * input + (1 - a) * input
        return output
