import pygame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class SimBridge(QWidget):
    ### This class is a PyQt5 window that runs a game loop and provides a way for other classes to subscribe to the game loop
    def __init__(self, game_loop_target_ms : int =20):
        ### Initializes the window and the game loop
        super().__init__()
        self.init_ui()
        self.init_game_loop(game_loop_target_ms)
        pygame.init()

    def init_ui(self):
        ###
        Initializes a window that has a status label
        that can be used to display messages to the user,
        For example, "Gamepad connected" or events like
        button presses on the controller
        ###
        self.resize(800, 600)
        self.setWindowTitle('SimBridge')

        # Top-level layout is a vertical box
        layout = QVBoxLayout()
        self.setLayout(layout)

        banner = self.init_banner()
        banner.setStyleSheet("background-color: #00fff0; ")
        layout.addWidget(banner)
        # Push content to the top
        layout.addStretch()

        # Create a form
        form = self.init_form()
        form.setStyleSheet("background-color: #fff0f0; ")
        layout.addWidget(form)
        layout.addStretch()


        self.show()

    def init_game_loop(self, target_ms : int = 20):
        ###
        Creates and starts a timer that fires every `target_ms` milliseconds,
        calling the `game_loop` method
        ###
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(target_ms)

        self.game_loop_subscribers = []

    def subscribe_to_game_loop(self, subscriber : object) -> None:
        ### Adds a subscriber to the game loop (Subscriber _must_ implement `on_game_loop` method)
        self.game_loop_subscribers.append(subscriber)

    def unsubscribe_from_game_loop(self, subscriber : object) -> None:
        ### Removes a subscriber from the game loop
        self.game_loop_subscribers.remove(subscriber)

    @staticmethod
    def init_banner():
        ### Initializes the banner
        banner = QLabel("Press 'Esc' key to quit")
        banner.setAlignment(Qt.AlignCenter)  # Center horizontally
        banner.setStyleSheet("font-size: 24pt; font-weight: bold;")  # H1 style
        return banner

    def init_form(self):
        ### Initializes the form that contains the `quick_label`, which
        is used by subscribers to display messages to the user
        ###
        form = QWidget()
        layout = QVBoxLayout()
        form.setLayout(layout)

        # Add a label
        self.quick_label = QLabel("This is a form")
        self.quick_label.setStyleSheet("font-size: 16pt;")
        layout.addWidget(self.quick_label)
        layout.addStretch()

        return form

    def keyPressEvent(self, event : pygame.event.Event) -> None:
        ### Handles key presses
        Exits on "Esc" key press
        ###
        if event.key() == Qt.Key_Escape:
            # Quit the application
            self.close()

    def set_quick_label(self, text : str) -> None:
        ###
        Callback that sets the `quick_label` text. This is used by subscribers to display messages to the user
        ###
        self.quick_label.setText(text)

    def game_loop(self):
        ###
        Standard pygame game loop. The call to `pygame.event.pump()` is necessary to keep the window
        ###
        pygame.event.pump()
        # After the events have been collected, let the subscribers do their thing
        for subscribers in self.game_loop_subscribers:
            subscribers.on_game_loop()
