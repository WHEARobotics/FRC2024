from __future__ import annotations

import math
from dataclasses import dataclass

import rev
import wpilib
from phoenix6 import hardware
from wpilib import Field2d, SmartDashboard
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics, SwerveDrive4Odometry, SwerveModuleState, ChassisSpeeds

from crescendorswervemodule import CrescendoSwerveModule, CrescendoSwerveModuleState


@dataclass(frozen=True)
class CrescendoSwerveDrivetrainState:
    back_left: CrescendoSwerveModuleState
    front_right: CrescendoSwerveModuleState
    front_left: CrescendoSwerveModuleState
    back_right: CrescendoSwerveModuleState
    yaw: float
    odometry: SwerveDrive4Odometry


class CrescendoSwerveDrivetrain:
    # I'd suggest not try to use the units functionality, and just stick to floats.
    # Whether we use degrees or radians for angle is debatable:
    #  - radians is going to be slightly more efficient, to not be converting back and forth.
    #  - degrees is more familiar, and the performance hit may not be that great.
    MAX_SPEED = 2.0
    MAX_ANGULAR_SPEED = math.pi  # 1/2 rotation per second

    # UPDATE NUMBERS
    BACK_LEFT_OFFSET = 0.708  # Back Left
    FRONT_RIGHT_OFFSET = 0.768  # Front Right
    FRONT_LEFT_OFFSET = 0.363  # Front Left
    BACK_RIGHT_OFFSET = 0.516  # Back Right

    # these are the absolute position offsets that are constants setting an offset to the absolute encoders and
    # changing the position of an angle.
    # if we set the position to zero and set the offset 1 time to zero then 180, it would create a 180 degree difference
    # when the wheel is set.

    # 2024- CHANGE ALL THESE TO THE CANSPARKMAX MOTOR CONTROLLER NUMBERS SOREN SET IN THE REV CLIENT- I.E. THE LABELS
    # OF EACH MOTOR CONTROLLER

    def _init_swerve_module_for(self, name: str, make_inverted=False) -> CrescendoSwerveModule:
        # These are IDs taken from the physical wiring.
        SWERVE_BACK_LEFT_DRIVE = 2
        SWERVE_BACK_LEFT_ANGLE = 3
        SWERVE_BACK_LEFT_ENCODER_CHANNEL = 3

        SWERVE_FRONT_RIGHT_DRIVE = 4
        SWERVE_FRONT_RIGHT_ANGLE = 5
        SWERVE_FRONT_RIGHT_ENCODER_CHANNEL = 0

        SWERVE_FRONT_LEFT_DRIVE = 6
        SWERVE_FRONT_LEFT_ANGLE = 7
        SWERVE_FRONT_LEFT_ENCODER_CHANNEL = 2

        SWERVE_BACK_RIGHT_DRIVE = 9
        SWERVE_BACK_RIGHT_ANGLE = 8
        SWERVE_BACK_RIGHT_ENCODER_CHANNEL = 1

        # Gather the related constants together and associate them with a logical name
        swerve_module_constants = {
            'back_left': [SWERVE_BACK_LEFT_DRIVE, SWERVE_BACK_LEFT_ANGLE, SWERVE_BACK_LEFT_ENCODER_CHANNEL,
                          self.BACK_LEFT_OFFSET],
            'front_right': [SWERVE_FRONT_RIGHT_DRIVE, SWERVE_FRONT_RIGHT_ANGLE, SWERVE_FRONT_RIGHT_ENCODER_CHANNEL,
                            self.FRONT_RIGHT_OFFSET],
            'front_left': [SWERVE_FRONT_LEFT_DRIVE, SWERVE_FRONT_LEFT_ANGLE, SWERVE_FRONT_LEFT_ENCODER_CHANNEL,
                           self.FRONT_LEFT_OFFSET],
            'back_right': [SWERVE_BACK_RIGHT_DRIVE, SWERVE_BACK_RIGHT_ANGLE, SWERVE_BACK_RIGHT_ENCODER_CHANNEL,
                           self.BACK_RIGHT_OFFSET]}

        # Initialize a CrescendoSwerveModule with the constant values for the given name
        drive = swerve_module_constants[name][0]
        angle = swerve_module_constants[name][1]
        channel = swerve_module_constants[name][2]
        offset = swerve_module_constants[name][3]
        module = CrescendoSwerveModule(drive, angle, channel, offset)
        if make_inverted:
            module.toggleDriveMotorInverted()

        # Try to get some debugging information: Did anything go wrong? Is there any way to quickly find a problem
        # at this point?
        if module is None:
            raise Exception(f"Could not initialize Crescendo Swerve Module {name}")
        position = module.getPosition()
        print(f"Initial position of {name} swerve module: angle {position.angle} direction {position.distance}")

        # Return the initialized module
        return module

    def __init__(self):

        wheel_base = 26.875 * 0.0254
        track_width = 22.75 * 0.0254
        half_wheel_base = wheel_base / 2
        half_track_width = track_width / 2  # 2_#TRACK_WIDTH MIGHT NEED TO BE SWITCHED AROUND, BUT THE
        # POSITIVE/NEGATIVE SIGNS ARE IN THE RIGHT LOCATION.

        self.frontLeftLocation = Translation2d(half_wheel_base, half_track_width)
        self.frontRightLocation = Translation2d(half_wheel_base, -half_track_width)
        self.backLeftLocation = Translation2d(-half_wheel_base, half_track_width)
        self.backRightLocation = Translation2d(-half_wheel_base, -half_track_width)
        # this sets up the translation 2d for each swerve module that sets up a translation in a 2d space. when the
        # robot is facing
        # at its origin positive x is forward and positive y is left for the 2d translation

        self.back_left = self._init_swerve_module_for(
            "back_left")  # CrescendoSwerveModule(SWERVE_BACK_LEFT_DRIVE, SWERVE_BACK_LEFT_ANGLE, SWERVE_BACK_LEFT_ENCODER_CHANNEL, self.BACK_LEFT_OFFSET)
        self.front_right = self._init_swerve_module_for(
            "front_right")  # CrescendoSwerveModule(SWERVE_FRONT_RIGHT_DRIVE, SWERVE_FRONT_RIGHT_ANGLE, SWERVE_FRONT_RIGHT_ENCODER_CHANNEL, self.FRONT_RIGHT_OFFSET)  #OG offset was 106.424
        self.front_left = self._init_swerve_module_for(
            "front_left")  # CrescendoSwerveModule(SWERVE_FRONT_LEFT_DRIVE, SWERVE_FRONT_LEFT_ANGLE, SWERVE_FRONT_LEFT_ENCODER_CHANNEL, self.FRONT_LEFT_OFFSET)  #OG offset was 296.543
        self.back_right = self._init_swerve_module_for(
            "back_right")  # CrescendoSwerveModule(SWERVE_BACK_RIGHT_DRIVE, SWERVE_BACK_RIGHT_ANGLE, SWERVE_BACK_RIGHT_ENCODER_CHANNEL, self.BACK_RIGHT_OFFSET)
        wpilib.SmartDashboard.putString("DB/String 9",
                                        f"back_left.encoderPos : {self.back_left.correctedEncoderPosition():.2f}")

        self.swerve_modules = [self.front_left, self.front_right, self.back_left, self.back_right]
        # this section above creates 4 swerve modules and sets the id's of each of them in this order:
        # drivemotor channel, turnmotor channel, absolute encoder channel(from analog input with thrifty encoders)
        # and the absolute pos offset then it creates a list for calling all modules at most

        self.swerveModuleStates = [SwerveModuleState(), SwerveModuleState(), SwerveModuleState(), SwerveModuleState()]
        # this initializes the states of the swerve modules, to set the swerve modules to certain speeds and angles
        # periodically 50 times a second but this is only the initialization part.

        self.gyro = hardware.Pigeon2(14)
        # this creates the pigeon gyro object that is used to track the robots yaw angle to be able to use field
        # relative.

        # The proper Kinematics and Odometry class to used is determined by the number of modules on the robot.
        # For example, this 4 module robot uses SwerveDrive4Kinematics and SwerveDrive4Odometry.
        self.kinematics = SwerveDrive4Kinematics(self.frontLeftLocation, self.frontRightLocation, self.backLeftLocation,
                                                 self.backRightLocation)
        # kinematics sets values for each individual module like its speed and angle working with the swerve module
        # states

        self.odometry = SwerveDrive4Odometry(self.kinematics, Rotation2d(), (
            self.front_left.getPosition(), self.front_right.getPosition(), self.back_left.getPosition(),
            self.back_right.getPosition()))

        # odometry is used to track the robots position on the field only after being enabled. with this you can track
        # things like how far the robot travelled in meters per second

        # Where are the swerve modules located on the robot?
        # ? These values of 0.5 are taken from
        # https://github.com/4201VitruvianBots/2021SwerveSim/blob/main/WPILib_SwerveControllerCommand/src/main/java/frc/robot/Constants.java
        # But they seem odd. What units are they?
        # They are probably meters, but the thing I don't understand is why they are different from the
        # self.frontLeftLocation, etc. above.
        # I suggest changing them to be the above --Rod

        # UPDATE
        self.module_positions = [  # Front left
            self.frontLeftLocation,  # Front right
            self.frontRightLocation,  # Back left
            self.backLeftLocation,  # Back right
            self.backRightLocation]
        '''
        this creates an object to be used for setting up the 2d position of the robot to be called
        '''

        # The current pose for each swerve module
        # These values are updated in `periodic()`
        self.module_poses = [Pose2d(), Pose2d(), Pose2d(), Pose2d()]
        '''
        this creates another list to create a position facing at the x origin
        '''

        # Simulation support
        self.fieldSim = Field2d()
        SmartDashboard.putData('Field', self.fieldSim)

        self.gyro.set_yaw(0)  # 8/3/2023 changed gyro reset to calibrate to possibly stop it from drifting
        self.gyro_yaw = self.gyro.get_yaw().value

    def periodic(self):
        self._update_odometry()

        # Update module poses
        for i in range(len(self.module_positions)):
            rotate_by = self.module_positions[i].rotateBy(self.get_heading())
            robot_translation = self.get_pose().translation()
            module_position = rotate_by + robot_translation
            # Module's heading is its angle relative to the chassis heading
            module_angle = self.swerve_modules[i].getState().angle + self.get_pose().rotation()
            self.module_poses[i] = Pose2d(module_position, module_angle)
        # this updates the module position using 2d values to find the robots position with its angle and
        # the x and y position

        # Update field sim with information
        self.fieldSim.setRobotPose(self.get_pose())
        self.fieldSim.getObject("Swerve Modules").setPoses(self.module_poses)

        # this  gives values of the robots pos into the robot field simulator

    def drive(self, x_speed, y_speed, rot, field_relative: bool) -> None:
        if field_relative:
            chassis_speeds = ChassisSpeeds.fromFieldRelativeSpeeds(x_speed,
                                                                   y_speed,
                                                                   rot,
                                                                   Rotation2d.fromDegrees(self.gyro.get_yaw().value))
        else:
            chassis_speeds = ChassisSpeeds(x_speed, y_speed, rot)

        self.swerveModuleStates = self.kinematics.toSwerveModuleStates(chassis_speeds)

        self.swerveModuleStates = SwerveDrive4Kinematics.desaturateWheelSpeeds(self.swerveModuleStates, self.MAX_SPEED)
        # Desaturate wheel speeds will slow down the speed or angle of a module if it passed the max speed or angle.

        # This function takes in the joystick inputs and sets up the field relative to be able to operate
        # the robot with inputs.

        self.front_left.setDesiredState(self.swerveModuleStates[0], True)
        self.front_right.setDesiredState(self.swerveModuleStates[1], True)
        self.back_left.setDesiredState(self.swerveModuleStates[2], True)
        self.back_right.setDesiredState(self.swerveModuleStates[3], True)

        # set desired state, updates the speed and angle on which each module has to reach periodically.

    def _update_odometry(self):
        self.odometry.update(Rotation2d.fromDegrees(self.gyro.get_yaw().value), self.front_left.getPosition(),
                             self.front_right.getPosition(), self.back_left.getPosition(), self.back_right.getPosition())
        '''
        This function updates the robots position and angle periodically every 50 ms
        '''

    def get_heading(self) -> Rotation2d:
        return Rotation2d.fromDegrees(self.gyro.get_yaw())

    def get_pose(self) -> Pose2d:
        return self.odometry.getPose()

    @classmethod
    def get_max_speed(cls):
        return cls.MAX_SPEED

    def reset_steering(self):
        """Call this to reset turning encoders when ALL wheels are aligned forward."""
        self.front_right.resetSteering()
        self.front_left.resetSteering()
        self.back_right.resetSteering()
        self.back_left.resetSteering()

    def toggle_drive_motors_inverted(self):
        for module in self.swerve_modules:
            module.toggleDriveMotorInverted()

    def set_idle_mode(self, mode: rev.CANSparkMax.IdleMode):
        for module in self.swerve_modules:
            module.set_idle_mode(mode)

    def get_state(self) -> CrescendoSwerveDrivetrainState:
        backLeftState = self.back_left.get_state()
        frontRightState = self.front_right.get_state()
        frontLeftState = self.front_left.get_state()
        backRightState = self.back_right.get_state()

        yaw = self.gyro.get_yaw()

        state = CrescendoSwerveDrivetrainState(back_left=backLeftState, front_right=frontRightState,
                                               front_left=frontLeftState, back_right=backRightState, yaw=yaw,
                                               odometry=self.odometry)

        return state
