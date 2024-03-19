from robotstate import RobotState


class RobotStateMachine:
    def __init__(self, robot, state : RobotState):
        self.robot = robot
        self.state = state

    def set_state(self, new_state : RobotState):
        self.state = new_state
        return self

    def initialize(self):
        self.state = self.state.initialize(self.robot)
        self.state.get_next_state(self.robot)
        return self

    def periodic(self) -> RobotState:
        self.state = self.state.periodic(self.robot)
        return self

    def finalize(self):
        self.state.finalize()
        return self