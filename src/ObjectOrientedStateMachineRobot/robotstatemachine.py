from robotstate import RobotState


class RobotStateMachine:
    def __init__(self, state : RobotState):
        self.state = state

    def periodic(self):
        return self.state.periodic()

    def set_state(self, new_state : RobotState):
        self.state = new_state
        return self
