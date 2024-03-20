from wpilib import Field2d
from wpilib.shuffleboard import Shuffleboard, ShuffleboardTab, ComplexWidget
from wpilib.shuffleboard import BuiltInWidgets
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.units import meters, degrees

from intake import IntakeState
from shooter import ShooterState
from vision import VisionState
from crescendodrivetrain import CrescendoSwerveDrivetrain, CrescendoSwerveDrivetrainState
from crescendorswervemodule import CrescendoSwerveModuleState


class SwerveTab:

    @staticmethod
    def init_swerve_module(tab: ShuffleboardTab, name: str, module: CrescendoSwerveModuleState,
                           position: tuple[int, int]) -> ComplexWidget:
        return tab.add(name, module).withWidget(BuiltInWidgets.kDifferentialDrive).withPosition(position[0],
                                                                                                position[1])

    def __init__(self, tab: ShuffleboardTab, swerve: CrescendoSwerveDrivetrain):
        self.front_left = self.init_swerve_module(tab, "Front Left", swerve.front_left, (0, 0))
        self.front_right = self.init_swerve_module(tab, "Front Right", swerve.front_right, (0, 5))
        self.back_left = self.init_swerve_module(tab, "Back Left", swerve.back_left, (1, 0))
        self.back_right = self.init_swerve_module(tab, "Back Right", swerve.back_right, (1, 5))
        self.yaw = tab.add("Yaw", 0).withWidget(BuiltInWidgets.kGyro).withPosition(2, 0)
        self.odometry_rotation = tab.add("Odometry Rotation", 0).withWidget(BuiltInWidgets.Gyro).withPosition(0, 3)
        self.odometry_x = tab.add("Odometry X", 0).withWidget(BuiltInWidgets.kTextView).withPosition(3, 3)
        self.odometry_y = tab.add("Odometry Y", 0).withWidget(BuiltInWidgets.kTextView).withPosition(6, 3)

    def show(self, swerve_state: CrescendoSwerveDrivetrainState):
        self.front_left.getEntry().setValue(swerve_state.front_left)
        self.front_right.getEntry().setValue(swerve_state.front_right)
        self.back_left.getEntry().setValue(swerve_state.back_left)
        self.back_right.getEntry().setValue(swerve_state.back_right)
        self.yaw.getEntry().setValue(swerve_state.yaw)
        odometry_pose = swerve_state.odometry.getPose()
        self.odometry_rotation.getEntry().setValue(odometry_pose.rotation())
        self.odometry_x.getEntry().setValue(f"{odometry_pose.x:1.2f}")
        self.odometry_x.getEntry().setValue(f"{odometry_pose.y:1.2f}")


class IntakeTab:

    def __init__(self, tab: ShuffleboardTab):
        self.wrist_encoder = tab.add("Wrist encoder", 0).withWidget(BuiltInWidgets.kEncoder).withPosition(0,
                                                                                                          0).getEntry()
        self.wrist_limit_switch = tab.add("Wrist limit switch", True).withWidget(
            BuiltInWidgets.kBooleanBox).withPosition(0, 1).getEntry()
        self.wrist_desired_pos = tab.add("Wrist desired position", 0).withWidget(
            BuiltInWidgets.kNumberBar).withPosition(0, 2).getEntry()

    def show(self, intake_state: IntakeState):
        self.wrist_encoder.getEntry().setValue(intake_state.wrist_encoder_pos)
        self.wrist_limit_switch.getEntry().setValue(intake_state.wrist_limit_switch_pos)
        self.wrist_desired_pos.getEntry().setValue(intake_state.wrist_desired_pos)


class ShooterTab:
    def __init__(self, tab: ShuffleboardTab):
        self.shooter_flywheel_speed = (tab.add("Flywheel speed", 0).withWidget(BuiltInWidgets.kNumberBar).
                                       withPosition(0, 0).getEntry())
        self.shooter_desired_pos = (tab.add("Desired position", 0).withWidget(BuiltInWidgets.kNumberBar).
                                    withPosition(0, 1).getEntry())
        self.shooter_pivot_action = (tab.add("Pivot action", 0).withWidget(BuiltInWidgets.kNumberBar).
                                     withPosition(0, 2).getEntry())
        self.shooter_absolute_encoder_pos = tab.add("Absolute encoder position", 0).withWidget(
            BuiltInWidgets.kEncoder).withPosition(0, 3).getEntry()
        self.shooter_pivot_encoder_pos = tab.add("Pivot encoder position", 0).withWidget(
            BuiltInWidgets.kEncoder).withPosition(0, 4).getEntry()
        self.shooter_wheel_encoder_pos = tab.add("Wheel encoder position", 0).withWidget(
            BuiltInWidgets.kEncoder).withPosition(0, 5).getEntry()

    def show(self, shooter_state: ShooterState):
        self.shooter_absolute_encoder_pos.getEntry().setValue(shooter_state.absolute_encoder_pos)
        self.shooter_pivot_encoder_pos.getEntry().setValue(shooter_state.shooter_pivot_encoder_pos)
        self.shooter_wheel_encoder_pos.getEntry().setValue(shooter_state.shooter_wheel_encoder_pos)


class VisionTab:
    def __init__(self, tab: ShuffleboardTab):
        self.vision_desired_x = (tab.add("Desired X", 0).withWidget(BuiltInWidgets.kNumberBar).
                                 withPosition(0, 0).getEntry())
        self.vision_speaker_x = (tab.add("Speaker X", 0).withWidget(BuiltInWidgets.kNumberBar).
                                 withPosition(0, 1).getEntry())
        self.vision_desired_angle = (tab.add("Desired angle", 0).withWidget(BuiltInWidgets.kNumberBar).
                                     withPosition(0, 2).getEntry())
        self.vision_current_angle = (tab.add("Current angle", 0).withWidget(BuiltInWidgets.kNumberBar).
                                     withPosition(0, 3).getEntry())
        self.vision_distance_to_speaker_y = (tab.add("Distance to speaker y", 0).withWidget(BuiltInWidgets.kNumberBar).
                                             withPosition(0, 4).getEntry())
        self.vision_distance_to_wall = (tab.add("Distance to wall", 0).withWidget(BuiltInWidgets.kNumberBar).
                                        withPosition(0, 5).getEntry())
        self.vision_desired_bot_angle = (tab.add("Desired bot angle", 0).withWidget(BuiltInWidgets.kNumberBar).
                                         withPosition(0, 6).getEntry())
        self.vision_direction_to_travel = (tab.add("Direction to travel", 0).withWidget(BuiltInWidgets.kNumberBar).
                                           withPosition(0, 7).getEntry())
        self.vision_x_distance_to_travel = (tab.add("X distance to travel", 0).withWidget(BuiltInWidgets.kNumberBar).
                                            withPosition(0, 8).getEntry())
        self.vision_x_speed = (tab.add("X speed", 0).withWidget(BuiltInWidgets.kNumberBar).
                               withPosition(0, 9).getEntry())
        self.vision_rot = (tab.add("Rotation", 0).withWidget(BuiltInWidgets.kNumberBar).
                           withPosition(0, 10).getEntry())

    def show(self, vision_state: VisionState):
        self.vision_desired_x.getEntry().setValue(vision_state.desired_x_for_autonomous_driving)
        self.vision_speaker_x.getEntry().setValue(vision_state.speaker_x)
        self.vision_desired_angle.getEntry().setValue(vision_state.desired_angle)
        self.vision_current_angle.getEntry().setValue(vision_state.current_angle)
        self.vision_distance_to_speaker_y.getEntry().setValue(vision_state.distance_to_speaker_y)
        self.vision_distance_to_wall.getEntry().setValue(vision_state.distance_to_wall)
        self.vision_desired_bot_angle.getEntry().setValue(vision_state.desired_bot_angle)
        self.vision_direction_to_travel.getEntry().setValue(vision_state.direction_to_travel)
        self.vision_x_distance_to_travel.getEntry().setValue(vision_state.x_distance_to_travel)
        self.vision_x_speed.getEntry().setValue(vision_state.x_speed)
        self.vision_rot.getEntry().setValue(vision_state.rot)


class MainTab:
    def __init__(self, tab: ShuffleboardTab):
        self.activate_climb_solenoid = (tab.add("Activate Climb Lock", True).withWidget(BuiltInWidgets.kToggleSwitch).
                                        withPosition(0, 0).getEntry())
        self.max_speed = (tab.addPersistent("Persistent Speed", 3.0).withWidget(BuiltInWidgets.kNumberSlider).
                          withPosition(0, 1).getEntry())
        self.field_data = Field2d()
        self.field = tab.add("Field", self.field_data).withWidget(BuiltInWidgets.kField).withPosition(0, 2)

    def show(self, swerve_state: CrescendoSwerveDrivetrainState,  vision_state: VisionState):
        botpose = vision_state.botpose
        self.field_data.setRobotPose(botpose[0], botpose[1], swerve_state.yaw)

    def set_bot_position(self, x: meters, y: meters, angle: degrees):
        # Convert bot position to use Limelight-style coordinates (0,0 is the center of the field)
        x = x + 8.27
        y = y + 4.1
        self.field_data.setRobotPose(Pose2d(x, y, Rotation2d(angle)))


class Makoboard:
    def __init__(self, swerve: CrescendoSwerveDrivetrain) -> None:
        self.swerve_tab = Shuffleboard.getTab("drive")
        self.swerve = SwerveTab(self.swerve_tab, swerve)

        self.intake_tab = Shuffleboard.getTab("intake")
        self.intake = IntakeTab(self.intake_tab)

        self.shooter_tab = Shuffleboard.getTab("shooter")
        self.shooter = ShooterTab(self.shooter_tab)

        self.vision_tab = Shuffleboard.getTab("vision")
        self.vision = VisionTab(self.vision_tab)

        self.main_tab = Shuffleboard.getTab("main")
        self.main = MainTab(self.main_tab)

        self.bot_position = (0, 0, 0)

    def read_controls(self) -> dict[str, any]:
        return {
            "activate_climb_solenoid": self.main.activate_climb_solenoid.get().getBoolean(),
            "max_speed": self.main.max_speed.get().getDouble()
        }

    def set_bot_position(self, x: meters, y: meters, angle: degrees):
        self.main.set_bot_position(x, y, angle)
