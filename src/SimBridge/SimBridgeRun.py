import sys
from PyQt5.QtWidgets import QApplication

from MockLimelight import MockLimelight
from MyXboxController import MyXboxController
from SimBridge import SimBridge
from XrcDirectoryShim import XrcDirectoryShim


def main():
    app = QApplication(sys.argv)

    # The main window is just a container for the game loop and a status label
    window = SimBridge()

    # The controller is the gamepad. It subscribes to the window so that it's
    # on_game_loop method is called every game loop iteration
    #
    # The controller also sets the status label with the set_quick_label method
    controller = MyXboxController(window.set_quick_label)
    window.subscribe_to_game_loop(controller)
    window.set_quick_label("Gamepad connected")

    # Puts robot positions into limelight network tables
    mock_limelight = MockLimelight(window.set_quick_label)

    # This shim reads and writes files to simulate the robot
    # It also writes the robot position to the limelight network tables
    xrc_sim = XrcDirectoryShim("c:\\tmp\\xRCsim", mock_limelight, 20)
    # It listens to the controller for updates. The controller, in turn, listens to the window's game loop
    controller.add_subscriber(xrc_sim)
    # It also listens to the window's game loop. Every game loop, xrc_sim updates files and
    window.subscribe_to_game_loop(xrc_sim)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()