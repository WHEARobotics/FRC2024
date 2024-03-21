from robotstate import RobotState


class RobotStateMachine:
    def __init__(self, state: RobotState):
        self.state = state

    def periodic(self, robot):
        robot.read_absolute_encoders_and_output_to_smart_dashboard()
        swerve_state, shooter_state, intake_state, vision_state  = robot.read_component_states()
        robot.makoboard.show(swerve_state, shooter_state, intake_state, vision_state)
        return self.state.periodic(robot)

    def set_state(self, new_state: RobotState):
        self.state = new_state
        return self
