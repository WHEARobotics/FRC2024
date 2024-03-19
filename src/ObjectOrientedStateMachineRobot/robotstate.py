
class RobotState:
    def __init__(self, robot):
        raise Exception("Override this method in the RobotState subclass")
    def periodic(self, robot):
        raise Exception("Override this method in the RobotState subclass")
    def finalize(self):
        raise Exception("Override this method in the RobotState subclass")


