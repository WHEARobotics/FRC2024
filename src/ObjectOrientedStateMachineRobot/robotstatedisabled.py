from robotstate import RobotState


class RobotStateDisabled(RobotState):
    def __init__(self, robot):
        self.robot = robot

    def periodic(self):
        self.robot.encoders.logEncoderValues()
        self.shooter.periodic(0, 0, 0, 0)


        self.readAbsoluteEncodersAndOutputToSmartDashboard()
        self.shooter.periodic(0, 0, 0, 0)

        self.intake.wrist_motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.front_left.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.front_right.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.back_left.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.swerve.back_right.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

        # we can set the motors to make sure they are on break when disabled
        return self

    def finalize(self):
        pass

