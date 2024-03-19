import ntcore
import wpilib
from wpilib import SendableChooser
from wpilib.shuffleboard import Shuffleboard
from wpilib.shuffleboard import BuiltInWidgets
from ntcore._ntcore import Value as ntV


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
                                        .withWidget(BuiltInWidgets.kToggleButton)
                                        .withSize(2, 1)
                                        .withProperties({"color When True": ntV.makeString("green"), "color When False": ntV.makeString("red")})
                                        .getEntry()
                                        )

        # User-edits persist between robot restarts
        self.max_speed = (
            self.tab
            .addPersistent("Persistent Speed", 3.0)
            .withWidget(BuiltInWidgets.kNumberSlider)
            .withSize(4, 1)
            .withProperties({"min": ntV.makeDouble(0), "max": ntV.makeDouble(5)})
            .getEntry()
        )

class ShuffleBoardReadWriteBot(wpilib.TimedRobot):

    def robotInit(self):
        self.shuffle_tab = ShuffleTab("ShuffleBoardReadWriteBot")

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


