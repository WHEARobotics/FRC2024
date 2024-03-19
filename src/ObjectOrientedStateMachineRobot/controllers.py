from wpilib import XboxController


class Controllers:
    def __init__(self):
        self.xbox = XboxController(0)
        self.xbox_operator = XboxController(1)

    def driveWithJoystick(self):
        # Step 1: Get the joystick values
        joystick_x, joystick_y, joystick_rot = self.getJoystickDriveValues()

        # Step 2: Calculate the speeds for the swerve
        x_speed, y_speed, rot = self.speeds_for_joystick_values(self.joystick_x, self.joystick_y, joystick_rot)

        # Unused : self.magnitude = math.sqrt(self.joystick_x*self.joystick_x + self.joystick_y*self.joystick_y)/3

        # Step 3: Drive the swerve with the desired speeds
        self.swerve.drive(x_speed, y_speed, rot, fieldRelative=True)
        '''
        this uses our joystick inputs and accesses a swerve drivetrain function to use field relative and the swerve module to drive the robot.
        '''

    def getJoystickDriveValues(self) -> (float, float, float):
        # allow joystick to be off from center without giving input

        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_x = applyDeadband(self.joystick_x, 0.1)
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_y = applyDeadband(self.joystick_y, 0.1)
        joystick_rot = -self.xbox.getRightX()
        joystick_rot = applyDeadband(joystick_rot, 0.15)

        return self.joystick_x, self.joystick_y, joystick_rot

    def speeds_for_joystick_values(self, joystick_x, joystick_y, joystick_rot):
        x_speed = self.joystickscaling(joystick_y) / ConfigurableConstants.JOYSTICK_DRIVE_SLOWDOWN_FACTOR
        y_speed = self.joystickscaling(joystick_x) / ConfigurableConstants.JOYSTICK_DRIVE_SLOWDOWN_FACTOR
        rot = joystick_rot  # TODO: Could add a joystickscaling here
        return x_speed, y_speed, rot

    def joystickscaling(self,
                        input):  # this function helps bring an exponential curve in the joystick value and near the zero value it uses less value and is more flat
        a = 1
        output = a * input * input * input + (1 - a) * input
        return output

