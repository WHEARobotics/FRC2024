
class RobotState:
    def __init__(self, robot):
        pass

    def periodic(self, robot):
        raise Exception("Override this method in the RobotState subclass")
