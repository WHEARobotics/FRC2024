import wpilib

class HelloRobot(wpilib.TimedRobot):
    def robotInit(self):
        self.print_timer = wpilib.Timer() # A timer to help us print info periodically; still need to start it.
        self.counter = 0

    def teleopInit(self):
        """This function is run once each time the robot enters teleop mode."""
        self.print_timer.start() # Now it starts counting.

    def teleopPeriodic(self):
        """This function is called periodically during teleop."""
        if self.print_timer.advanceIfElapsed(1.0):
            # Send the counter to the area 'DB/String 0' on the SmartDashboard.
            wpilib.SmartDashboard.putString('DB/String 0', 'Count: {:3d}'.format(self.counter))
            self.counter +=1

if __name__ == '__main__':
    wpilib.run(HelloRobot)
