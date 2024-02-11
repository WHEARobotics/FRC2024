
import math
import cscore
import ntcore

import time # Temporary for diagnostics

class Vision:
                                                     
    
    def __init__(self) -> None:
        self.networktables = ntcore.NetworkTableInstance.getDefault()
        self.limelight_table = self.networktables.getTable("limelight")
        self.botpose = self.limelight_table.getDoubleArrayTopic("botpose").subscribe([])

    def checkBotpose(self):
        return self.botpose.get()

