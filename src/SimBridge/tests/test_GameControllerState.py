import pytest

from SimBridge.GameControllerState import GameControllerState

def default_state():
    return GameControllerState(
        a=False,
        b=False,
        x=False,
        y=False,
        dpad_down=False,
        dpad_up=False,
        dpad_left=False,
        dpad_right=False,
        bumper_l=False,
        bumper_r=False,
        stop=False,
        restart=False,
        right_y=0,
        right_x=0,
        left_y=0,
        left_x=0,
        trigger_l=-1,
        trigger_r=-1
    )

def test_forward_forward():
    # If the left joystick is pushed forward and the robot is facing forward, the robot should move forward
    robot_rotation_degrees = 0
    swerve_control = default_state()
    swerve_control.left_y = 1
    tank_control = swerve_control.swerve_controls_to_tank_controls(robot_rotation_degrees)
    assert tank_control.left_x == pytest.approx(0)
    assert tank_control.left_y == pytest.approx(1)

def test_forward_left():
    # If the left joystick is pushed forward and the robot is facing right, the robot should move forward
    robot_rotation_degrees = 90
    swerve_control = default_state()
    swerve_control.left_y = 1
    tank_control = swerve_control.swerve_controls_to_tank_controls(robot_rotation_degrees)
    assert tank_control.left_y == pytest.approx(0)
    assert tank_control.left_x == pytest.approx(-1)

def test_forward_angle():
    # If the left joystick is pushed forward and the robot is facing at a 45 degree angle, the robot should move
    # towards its upper left
    robot_rotation_degrees = 45
    swerve_control = default_state()
    swerve_control.left_y = 1
    tank_control = swerve_control.swerve_controls_to_tank_controls(robot_rotation_degrees)
    assert tank_control.left_y == pytest.approx(0.7071068)
    assert tank_control.left_x == pytest.approx(-0.7071068)

def test_forward_backward():
    # If the left joystick is pushed forward and the robot is facing backwards, the robot should move backwards
    robot_rotation_degrees = 180
    swerve_control = default_state()
    swerve_control.left_y = 1
    tank_control = swerve_control.swerve_controls_to_tank_controls(robot_rotation_degrees)
    assert tank_control.left_x == pytest.approx(0)
    assert tank_control.left_y == pytest.approx(-1)

def test_right_forward():
    # If the left joystick is pushed right and the robot is facing forward, the robot should move right
    robot_rotation_degrees = 0
    swerve_control = default_state()
    swerve_control.left_x = 1
    tank_control = swerve_control.swerve_controls_to_tank_controls(robot_rotation_degrees)
    assert tank_control.left_y == pytest.approx(0)
    assert tank_control.left_x == pytest.approx(1)

def test_right_right():
    # If the left joystick is pushed right and the robot is facing right, the robot should move right
    robot_rotation_degrees = 90
    swerve_control = default_state()
    swerve_control.left_x = 1
    swerve_control.left_y = 0
    tank_control = swerve_control.swerve_controls_to_tank_controls(robot_rotation_degrees)
    assert tank_control.left_y == pytest.approx(1)
    assert tank_control.left_x == pytest.approx(0)

def test_right_backward():
    # If the left joystick is pushed right and the robot is facing backwards, the robot should move right
    robot_rotation_degrees = 180
    swerve_control = default_state()
    swerve_control.left_x = 1
    tank_control = swerve_control.swerve_controls_to_tank_controls(robot_rotation_degrees)
    assert tank_control.left_y == pytest.approx(0)
    assert tank_control.left_x == pytest.approx(-1)

def test_right_angle():
    # If the left joystick is pushed right and the robot is facing at a 45 degree angle, the robot should move
    # towards its upper right
    robot_rotation_degrees = 45
    swerve_control = default_state()
    swerve_control.left_x = 1
    tank_control = swerve_control.swerve_controls_to_tank_controls(robot_rotation_degrees)
    assert tank_control.left_y == pytest.approx(0.7071068)
    assert tank_control.left_x == pytest.approx(0.7071068)



