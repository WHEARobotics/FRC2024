from typing import Callable

import pygame

from GameControllerState import GameControllerState
from MockLimelight import MockLimelight


class MyXboxController:
    JOYSTICK_DEADBAND = 0.1 # Might want to change this? Especially for the triggers
    def __init__(self, status_callback : Callable[[str], None], mock_limelight : MockLimelight) -> None:
        # Thumbsticks are said to be one joystick with 4 axes, which is a curious decision
        assert pygame.joystick.get_count() ==1
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        axes_count = self.joystick.get_numaxes()
        assert axes_count == 6

        self.limelight = mock_limelight
        self.controller_state = GameControllerState(a=False, b=False, x=False, y=False,
                                                    dpad_down=False, dpad_up=False, dpad_left=False, dpad_right=False,
                                                    bumper_l=False, bumper_r=False, stop=False, restart=False,
                                                    right_y=0.0, right_x=0.0, left_y=0.0, left_x=0.0,
                                                    trigger_l=-1.0, trigger_r=-1.0)

        self.subscribers = []

        self.status_callback = status_callback
        status_callback("Gamepad connected")

    def on_joystick_moved(self, event : pygame.event.Event) -> None:
        # Triggers are axis 5 & 6, but that should route to on_trigger_moved
        assert event.axis < 4
        axis_names = ["LX", "LY", "RX", "RY"]
        axis_name = axis_names[event.axis]
        self.status_callback(f"Gamepad {axis_name} moved to {event.value}")
        if axis_name == "LX":
            self.controller_state.left_x = event.value
        elif axis_name == "LY":
            self.controller_state.left_y = event.value
        elif axis_name == "RX":
            self.controller_state.right_x = event.value
        elif axis_name == "RY":
            self.controller_state.right_y = event.value

        # Apply deadband on all axes
        self.controller_state.left_x = 0 if abs(self.controller_state.left_x) < MyXboxController.JOYSTICK_DEADBAND else self.controller_state.left_x
        self.controller_state.left_y = 0 if abs(self.controller_state.left_y) < MyXboxController.JOYSTICK_DEADBAND else self.controller_state.left_y
        self.controller_state.right_x = 0 if abs(self.controller_state.right_x) < MyXboxController.JOYSTICK_DEADBAND else self.controller_state.right_x
        self.controller_state.right_y = 0 if abs(self.controller_state.right_y) < MyXboxController.JOYSTICK_DEADBAND else self.controller_state.right_y


    # Triggers are read by pygame as axis 4 and 5
    # Their value is -1 to 1, with resting position being -1 (!)
    def on_trigger_moved(self, event: pygame.event.Event) -> None:
        assert event.axis >= 4

        trigger_name = ['_','_','_','_','LT','RT']
        axis_name = trigger_name[event.axis]
        self.status_callback(f"Gamepad {trigger_name} moved to {event.value}")
        if axis_name == "LT":
            self.controller_state.trigger_l = event.value
        else:
            assert axis_name == "RT"
            self.controller_state.trigger_r = event.value


    def on_game_loop(self) -> None:
        # Handle the events (set the state)
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # The triggers are axis 4 and 5, and they are -1 to 1
                if event.axis == 4 or event.axis == 5:
                    self.on_trigger_moved(event)
                else:
                    self.on_joystick_moved(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self.status_callback(f"Gamepad button {event.button} pressed")
            elif event.type == pygame.JOYBUTTONUP:
                self.status_callback(f"Gamepad button {event.button} released")
            elif event.type == pygame.JOYHATMOTION:
                self.status_callback(f"Gamepad hat {event.hat} value {event.value}")
            elif event.type == pygame.JOYBALLMOTION:
                self.status_callback("Gamepad ball {event.ball} value {event.rel}")
            else:
                self.status_callback(f"Gamepad event {event.type}")

        # Transmit the state to subscribers
        for subscribers in self.subscribers:
            subscribers.update(self.controller_state)


    def add_subscriber(self, subscriber : object) -> None:
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber : object) -> None:
        self.subscribers.remove(subscriber)
