import sys
from PyQt5.QtWidgets import QApplication

from src.SimBridge.MockLimelight import MockLimelight
from src.SimBridge.MyXboxController import MyXboxController
from src.SimBridge.SimBridge import SimBridge
from src.SimBridge.XrcDirectoryShim import XrcDirectoryShim


def main():
    app = QApplication(sys.argv)

    # The main window is just a big rectangle
    window = SimBridge()
    mock_limelight = MockLimelight(window.set_quick_label)
    controller = MyXboxController(window.set_quick_label, mock_limelight)
    window.subscribe_to_game_loop(controller)
    window.set_quick_label("Gamepad connected")

    xrc_sim = XrcDirectoryShim("c:\\tmp\\xRCsim", controller, mock_limelight, 20)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()