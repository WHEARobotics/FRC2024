import ntcore
import wpilib
from wpilib import SendableChooser, Field2d, SmartDashboard
from wpilib.shuffleboard import Shuffleboard
from wpilib.shuffleboard import BuiltInWidgets
from ntcore._ntcore import Value as ntV
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.units import meters, degrees


class ShuffleTab:
    def __init__(self, tab_name : str):
        self.tab = Shuffleboard.getTab(tab_name)

        # Read-only value showing some information
        self.info_entry = (self.tab
                            .add("Info", "Some information")
                            .withWidget(BuiltInWidgets.kTextView)
                            .withSize(2, 1)
                            .withPosition(3, 3)
                            .getEntry()
                          )

        #  Read-write value showing the distance to the target
        ## To set properties, you need to use the ntcore._ntcore.Value.make{type} methods, for instance:
        ## ntV.makeDouble(0) or ntV.makeString("green")
        ## To find the available properties, see https://robotpy.readthedocs.io/projects/robotpy/en/2024.1.1.1/wpilib.shuffleboard/BuiltInWidgets.html
        ## You then need to call `withProperties` on the entry to set the properties
        distance_properties = {
            "min": ntV.makeDouble(0),
            "max": ntV.makeDouble(15),
            "Block increment": ntV.makeDouble(1)
        }

        self.distance_entry = (self.tab
                                .add("Distance to target", -1)
                                .withWidget(BuiltInWidgets.kNumberBar)
                                .withSize(3, 1)
                                .withPosition(1, 2)
                                .withProperties(distance_properties)
                                .getEntry()
                              )

        # User-controllable toggle button
        self.activate_climb_solenoid = (self.tab
                                        .add("Activate Climb Lock", True)
                                        .withWidget(BuiltInWidgets.kToggleSwitch)
                                        .withSize(2, 1)
                                        .withProperties({"color when true": ntV.makeString("#00FF00"), "color when false": ntV.makeString("#FF0000")})
                                        .getEntry()
                                        )

        widget = self.tab.add("Junk", True).withWidget(BuiltInWidgets.kToggleButton)
        c = wpilib.shuffleboard._shuffleboard.SimpleWidget

        # User-edits persist between robot restarts
        self.max_speed = (
            self.tab
            .addPersistent("Persistent Speed", 3.0)
            .withWidget(BuiltInWidgets.kNumberSlider)
            .withSize(4, 1)
            .withProperties({"min": ntV.makeDouble(0), "max": ntV.makeDouble(5)})
            .getEntry()
        )

        self.field_data = Field2d()
        self.field = (
            self.tab
            .add("Field", self.field_data)
            .withWidget(BuiltInWidgets.kField)
            .withSize(7, 3)
            .withPosition(7, 2)
        )

    def setBotPosition(self, x : meters, y : meters, angle : degrees):
        ### Convert bot position to use Limelight-style coordinates (0,0 is the center of the field)
        x = x + 8.27
        y = y + 4.1
        self.field_data.setRobotPose(Pose2d(x, y, Rotation2d(angle)))

class ShuffleBoardReadWriteBot(wpilib.TimedRobot):

    def robotInit(self):
        self.shuffle_tab = ShuffleTab("ShuffleBoardReadWriteBot")
        self.shuffle_tab.setBotPosition(3, 3, 45)

    def teleopInit(self):
        # How to read a value from Shuffleboard
        some_info = self.shuffle_tab.info_entry.get().getString()
        print(f"Info: {some_info}")
        # How to write a value to Shuffleboard
        self.shuffle_tab.info_entry.setString("New information")
        self.shuffle_tab.distance_entry.setDouble(5.0)

    def teleopPeriodic(self):
        # How to read a value from Shuffleboard live
        solenoidEnabled = self.shuffle_tab.activate_climb_solenoid.get().getBoolean()
        print(f"Solenoid enabled {solenoidEnabled}")

from robotpy.main import main
import sys

if __name__ == '__main__':
    sys.argv[0] = 'robotpy sim'
    main()
    #wpilib.run(ShuffleBoardReadWriteBot)


