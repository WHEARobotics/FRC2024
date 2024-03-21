from robotcommand import RobotCommand
from shootercommands import KickerIdleCommand, KickerIntakeCommand


class KickerState:
    def __init__(self):
        pass

    def periodic(self, robot) -> tuple[any, RobotCommand]:
        raise NotImplementedError("Subclasses must implement this method")


class KickerIdle(KickerState):
    def __init__(self):
        super().__init__()

    def periodic(self, robot) -> tuple[KickerState, RobotCommand]:
        return self, KickerIdleCommand()


class KickerIntaking(KickerState):
    def __init__(self):
        super().__init__()

    def periodic(self, robot) -> tuple[KickerState, RobotCommand]:
        # TODO: How do we know when the kicker is done intaking?
        done_intaking = lambda robot: False
        next_state = self if not done_intaking else KickerIntakeComplete()
        return next_state, KickerIntakeCommand()


class KickerIntakeComplete(KickerState):
    def __init__(self):
        super().__init__()

    def periodic(self, robot) -> tuple[KickerState, RobotCommand]:
        return self, KickerIdleCommand()
